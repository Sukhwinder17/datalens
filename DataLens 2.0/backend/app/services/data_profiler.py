"""Deep, generic DataLens profiling engine.

The profiler intentionally separates raw storage dtype from semantic content.
It uses pandas/numpy for statistics and Matplotlib for on-demand visual plots.
No dataset-specific assumptions are made.
"""
from __future__ import annotations

import math
import re
from typing import Any

import numpy as np
import pandas as pd

from app.core.exceptions import InvalidFileContentError
from app.services import data_loader
from app.models.dataset import DatasetRecord
from app.schemas.dataset import (
    CategoricalColumnStats, CategoricalValue, ColumnProfile, ColumnTypeCounts,
    DataQualityFlags, DatasetPreview, DatasetProfile, DatetimeColumnStats,
    DuplicatesSummary, HistogramBin, MissingDataSummary, NumericColumnStats,
)
from app.utils import dataframe_utils as dfu

HIGH_MISSING_THRESHOLD = 0.50
HIGH_CARDINALITY_THRESHOLD = 0.90
NEAR_CONSTANT_THRESHOLD = 0.95
DATETIME_DETECTION_THRESHOLD = 0.70
NUMERIC_LIKE_THRESHOLD = 0.70
DEFAULT_PREVIEW_PAGE_SIZE = 20
MAX_PREVIEW_PAGE_SIZE = 200

_PLACEHOLDERS = {"", "-", "--", "na", "n/a", "nan", "null", "none", "nil", "unknown", "unk", "?", "."}
_NUMERIC_RE = re.compile(
    r"^\s*[$€£₹]?\s*\(?\s*[-+]?\d[\d,]*(?:\.\d+)?\s*%?\s*\)?\s*\*?\s*$"
)


def _read_raw(record: DatasetRecord) -> pd.DataFrame:
    # Keep all readers in one place so CSV and XLSX use identical behaviour.
    # In particular, XLSX automatically selects the most data-rich worksheet.
    try:
        return data_loader.read_dataframe(record)
    except InvalidFileContentError:
        raise
    except Exception as exc:
        raise InvalidFileContentError(
            "Could not read this dataset while profiling it. The file may be corrupt or unsupported."
        ) from exc


def _numeric_like_values(series: pd.Series) -> tuple[pd.Series, float]:
    """Parse common numeric text without pretending arbitrary text is numeric."""
    raw = series.astype("string")
    cleaned = (
        raw.str.strip()
        .str.replace(r"[$€£₹]", "", regex=True)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
        .str.replace(r"\*$", "", regex=True)
    )
    mask = raw.notna() & raw.map(lambda x: bool(_NUMERIC_RE.match(str(x))) if not raw.empty else False)
    parsed = pd.to_numeric(cleaned.where(mask), errors="coerce")
    denominator = int(raw.notna().sum())
    fraction = float(parsed.notna().sum() / denominator) if denominator else 0.0
    return parsed, fraction


def _prepare_profile_dataframe(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int], dict[str, pd.Series]]:
    df = raw.copy()
    invalid_dates: dict[str, int] = {}
    numeric_like: dict[str, pd.Series] = {}

    for column in df.columns:
        series = df[column]
        name = str(column)
        parsed_num, num_fraction = _numeric_like_values(series)
        if not pd.api.types.is_numeric_dtype(series) and num_fraction >= NUMERIC_LIKE_THRESHOLD:
            numeric_like[name] = parsed_num

        if dfu.is_textlike(series) and series.notna().any():
            # Do not parse columns that are strongly numeric-like; they are better
            # represented by numeric semantic stats.
            if num_fraction < NUMERIC_LIKE_THRESHOLD:
                parsed_date = pd.to_datetime(series, errors="coerce", format="mixed")
                parse_fraction = parsed_date.notna().mean()
                if parse_fraction >= DATETIME_DETECTION_THRESHOLD:
                    invalid_dates[name] = int(series.notna().sum() - parsed_date.notna().sum())
                    df[column] = parsed_date
    return df, invalid_dates, numeric_like


def _numeric_stats(series: pd.Series) -> NumericColumnStats:
    clean = pd.to_numeric(series, errors="coerce")
    finite = clean.replace([np.inf, -np.inf], np.nan).dropna()
    infinities = int(np.isinf(clean.to_numpy(dtype=float, na_value=np.nan)).sum()) if len(clean) else 0
    if finite.empty:
        return NumericColumnStats(infinities=infinities)

    a = finite.to_numpy(dtype=float)
    q = np.percentile(a, [1, 5, 10, 25, 50, 75, 90, 95, 99])
    q01, q05, q10, q25, q50, q75, q90, q95, q99 = map(float, q)
    iqr = q75 - q25
    lower = q25 - 1.5 * iqr
    upper = q75 + 1.5 * iqr
    outlier_mask = (finite < lower) | (finite > upper)
    mode = finite.mode()
    mean = float(np.mean(a))
    std = float(np.std(a, ddof=1)) if len(a) > 1 else 0.0

    if len(a) > 1 and std != 0:
        skew = float(pd.Series(a).skew())
        kurt = float(pd.Series(a).kurt())
        cv = abs(std / mean) if mean != 0 else None
    else:
        skew = kurt = cv = 0.0

    minimum, maximum = float(np.min(a)), float(np.max(a))
    histogram: list[HistogramBin] = []
    if minimum == maximum:
        histogram = [HistogramBin(label=str(dfu.safe_float(minimum)), start=minimum, end=maximum, count=len(a))]
    else:
        bins = min(20, max(5, int(np.sqrt(len(a)))))
        counts, edges = np.histogram(a, bins=bins)
        for start, end, count in zip(edges[:-1], edges[1:], counts):
            histogram.append(HistogramBin(
                label=f"{dfu.safe_float(start)}–{dfu.safe_float(end)}",
                start=float(start), end=float(end), count=int(count)
            ))

    return NumericColumnStats(
        count=int(len(a)), mean=dfu.safe_float(mean), median=dfu.safe_float(q50),
        mode=dfu.safe_float(mode.iloc[0]) if len(mode) else None,
        std=dfu.safe_float(std), variance=dfu.safe_float(np.var(a, ddof=1)) if len(a) > 1 else 0.0,
        min=dfu.safe_float(minimum), max=dfu.safe_float(maximum),
        p01=dfu.safe_float(q01), p05=dfu.safe_float(q05), p10=dfu.safe_float(q10),
        p25=dfu.safe_float(q25), p50=dfu.safe_float(q50), p75=dfu.safe_float(q75),
        p90=dfu.safe_float(q90), p95=dfu.safe_float(q95), p99=dfu.safe_float(q99),
        range=dfu.safe_float(maximum - minimum), iqr=dfu.safe_float(iqr),
        skewness=dfu.safe_float(skew), kurtosis=dfu.safe_float(kurtosis_safe(kurt)),
        coefficient_variation=dfu.safe_float(cv), zeros=int(np.sum(a == 0)),
        negatives=int(np.sum(a < 0)), positives=int(np.sum(a > 0)),
        infinities=infinities, outlier_count=int(outlier_mask.sum()),
        outlier_percentage=round(float(outlier_mask.mean() * 100), 2),
        lower_fence=dfu.safe_float(lower), upper_fence=dfu.safe_float(upper),
        unique=int(pd.Series(a).nunique()), histogram=histogram,
    )


def kurtosis_safe(value: float) -> float:
    return value if np.isfinite(value) else 0.0


def _categorical_stats(series: pd.Series) -> CategoricalColumnStats:
    raw = series.dropna()
    text = raw.astype(str)
    counts = text.value_counts()
    total = int(len(text))
    values = [
        CategoricalValue(value=str(v), frequency=int(freq), percentage=round(freq / total * 100, 2))
        for v, freq in counts.head(20).items()
    ]
    rare = [
        CategoricalValue(value=str(v), frequency=int(freq), percentage=round(freq / total * 100, 2))
        for v, freq in counts[counts <= max(1, int(total * 0.01))].head(20).items()
    ]
    lengths = text.str.len()
    top = values[0] if values else None
    empty = int((text == "").sum())
    whitespace = int(text.str.strip().eq("").sum())
    return CategoricalColumnStats(
        unique=int(text.nunique()), top_value=top.value if top else None,
        top_value_frequency=top.frequency if top else None,
        top_value_percentage=top.percentage if top else None,
        top_values=values, rare_values=rare, missing=int(series.isna().sum()),
        empty_strings=empty, whitespace_only=whitespace,
        min_length=int(lengths.min()) if len(lengths) else None,
        max_length=int(lengths.max()) if len(lengths) else None,
        mean_length=round(float(lengths.mean()), 3) if len(lengths) else None,
        median_length=round(float(lengths.median()), 3) if len(lengths) else None,
    )


def _datetime_stats(series: pd.Series, invalid: int) -> DatetimeColumnStats:
    clean = series.dropna()
    if clean.empty:
        return DatetimeColumnStats(missing_dates=int(series.isna().sum()), invalid_values=invalid)
    earliest, latest = clean.min(), clean.max()
    return DatetimeColumnStats(
        earliest=earliest.isoformat(), latest=latest.isoformat(),
        date_range_days=round((latest - earliest).total_seconds() / 86400, 2),
        unique_dates=int(clean.dt.normalize().nunique()),
        missing_dates=int(series.isna().sum()), invalid_values=invalid,
    )


def _placeholder_counts(series: pd.Series) -> dict[str, int]:
    if not (dfu.is_textlike(series) or series.dtype == "object"):
        return {}
    text = series.dropna().astype(str)
    counts: dict[str, int] = {}
    for value in text:
        normalized = value.strip().lower()
        if normalized in _PLACEHOLDERS:
            counts[normalized or "<empty>"] = counts.get(normalized or "<empty>", 0) + 1
    return counts


def _possible_index(name: str, series: pd.Series, rows: int) -> bool:
    if rows == 0 or not re.search(r"^(unnamed|index|idx|row)", name.strip().lower()):
        return False
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric) != rows:
        return False
    vals = numeric.to_numpy()
    return np.array_equal(vals, np.arange(rows)) or np.array_equal(vals, np.arange(1, rows + 1))


def _possible_id(name: str, series: pd.Series, rows: int, unique: int) -> bool:
    if rows == 0 or unique / rows < 0.95:
        return False
    return bool(re.search(r"(?:^|[_\s-])(id|uuid|key|code|number|no)(?:$|[_\s-])", name.lower()) or name.lower() in {"id", "code", "key"})


def _column_profiles(df: pd.DataFrame, raw: pd.DataFrame, row_count: int, invalid_dates: dict[str, int], numeric_like: dict[str, pd.Series]):
    profiles: list[ColumnProfile] = []
    counts = {dfu.NUMERICAL: 0, dfu.CATEGORICAL: 0, dfu.DATETIME: 0, dfu.BOOLEAN: 0, dfu.OTHER: 0}

    for column in df.columns:
        name = str(column)
        series = df[column]
        original = raw[column]
        parsed = numeric_like.get(name)
        column_type = dfu.classify_column(series)
        if parsed is not None and column_type == dfu.CATEGORICAL:
            column_type = dfu.NUMERICAL
        counts[column_type] += 1

        missing = int(series.isna().sum())
        non_null = int(row_count - missing)
        unique = int(series.nunique(dropna=True))
        placeholder = _placeholder_counts(original)
        blank_count = int(original.astype("string").fillna("").eq("").sum()) if dfu.is_textlike(original) else 0
        whitespace_count = int(original.dropna().astype(str).map(lambda x: x != x.strip()).sum()) if len(original) else 0
        samples = [dfu.json_safe_cell(v) for v in original.dropna().head(8).tolist()]
        samples = [str(v) for v in samples if v is not None]

        numeric_series = parsed if parsed is not None else series
        numeric = _numeric_stats(numeric_series) if column_type == dfu.NUMERICAL else None
        categorical = _categorical_stats(series) if column_type in (dfu.CATEGORICAL, dfu.OTHER, dfu.BOOLEAN) else None
        datetime_stats = _datetime_stats(series, invalid_dates.get(name, 0)) if column_type == dfu.DATETIME else None

        numeric_parse_pct = 0.0
        if parsed is not None:
            numeric_parse_pct = round(float(parsed.notna().sum() / max(non_null, 1) * 100), 2)

        possible_index = _possible_index(name, original, row_count)
        possible_id = _possible_id(name, original, row_count, unique)
        constant = unique <= 1
        top_pct = categorical.top_value_percentage if categorical else None
        near_constant = bool(top_pct is not None and top_pct >= NEAR_CONSTANT_THRESHOLD * 100)
        high_cardinality = bool(row_count and unique / row_count >= HIGH_CARDINALITY_THRESHOLD)

        issues: list[str] = []
        recommendations: list[str] = []
        if missing / max(row_count, 1) >= HIGH_MISSING_THRESHOLD:
            issues.append("High missingness")
            recommendations.append("Review whether missing values should be imputed or the column removed.")
        if constant:
            issues.append("Constant or empty column")
            recommendations.append("Remove if the column carries no analytical information.")
        if possible_index:
            issues.append("Possible imported index column")
            recommendations.append("Review and remove if it is only a row index.")
        if possible_id:
            issues.append("Possible identifier/key")
            recommendations.append("Treat as an identifier; avoid using it as a continuous numeric feature.")
        if high_cardinality and not possible_id:
            issues.append("High cardinality")
            recommendations.append("Review whether this text/category is suitable for grouping or encoding.")
        if placeholder:
            issues.append("Placeholder values detected")
            recommendations.append("Convert placeholders to missing values before analysis.")
        if whitespace_count:
            issues.append("Leading/trailing whitespace detected")
            recommendations.append("Trim text before grouping or matching.")
        if numeric_parse_pct >= 90 and column_type == dfu.NUMERICAL and not pd.api.types.is_numeric_dtype(original):
            issues.append("Numeric values stored as text")
            recommendations.append("Convert the cleaned numeric representation to a numeric dtype.")
        if numeric and numeric.outlier_count:
            issues.append(f"{numeric.outlier_count:,} IQR outliers")
            recommendations.append("Inspect outlier rows before removing or capping values.")
        if categorical and categorical.whitespace_only:
            issues.append("Blank/whitespace-only strings")
            recommendations.append("Normalize blank strings to missing values.")

        profiles.append(ColumnProfile(
            name=name, dtype=column_type, pandas_dtype=str(series.dtype),
            semantic_type=("numeric_like" if parsed is not None and not pd.api.types.is_numeric_dtype(original)
                           else column_type),
            row_count=row_count, non_null_count=non_null, missing_count=missing,
            missing_percentage=round(missing / max(row_count, 1) * 100, 2),
            unique_count=unique, unique_percentage=round(unique / max(row_count, 1) * 100, 2),
            duplicate_count=max(0, non_null - unique), sample_values=samples,
            placeholder_values=placeholder, blank_count=blank_count,
            whitespace_count=whitespace_count, constant=constant,
            near_constant=near_constant, high_cardinality=high_cardinality,
            possible_id=possible_id, possible_index=possible_index,
            numeric_like=parsed is not None,
            numeric_parse_percentage=numeric_parse_pct, issues=issues,
            recommendations=recommendations, numeric_stats=numeric,
            categorical_stats=categorical, datetime_stats=datetime_stats,
        ))
    return profiles, ColumnTypeCounts(**counts)


def _quality_flags(raw: pd.DataFrame, profiles: list[ColumnProfile], invalid_dates: dict[str, int]) -> DataQualityFlags:
    return DataQualityFlags(
        high_missing_columns=[p.name for p in profiles if p.missing_percentage >= HIGH_MISSING_THRESHOLD * 100],
        duplicate_rows_present=False,
        constant_columns=[p.name for p in profiles if p.constant],
        near_constant_columns=[p.name for p in profiles if p.near_constant and not p.constant],
        high_cardinality_columns=[p.name for p in profiles if p.high_cardinality],
        mixed_type_columns=[str(c) for c in raw.columns if dfu.has_mixed_types(raw[c])],
        empty_columns=[str(c) for c in raw.columns if raw[c].isna().all()],
        outlier_columns=[p.name for p in profiles if p.numeric_stats and p.numeric_stats.outlier_count > 0],
        invalid_date_columns=[name for name, count in invalid_dates.items() if count > 0],
        placeholder_columns=[p.name for p in profiles if p.placeholder_values],
        numeric_like_columns=[p.name for p in profiles if p.numeric_like],
        possible_id_columns=[p.name for p in profiles if p.possible_id],
        possible_index_columns=[p.name for p in profiles if p.possible_index],
        whitespace_columns=[p.name for p in profiles if p.whitespace_count],
    )


def _row_quality(df: pd.DataFrame, profiles: list[ColumnProfile]) -> dict[str, Any]:
    missing_per_row = df.isna().sum(axis=1)
    rows_with_missing = int((missing_per_row > 0).sum())
    all_missing = int((missing_per_row == len(df.columns)).sum()) if len(df.columns) else 0
    top = missing_per_row.sort_values(ascending=False).head(20)

    # Count rows affected by any concrete quality signal, not the number of
    # columns carrying a signal.
    problematic = pd.Series(False, index=df.index)
    for column, series in df.items():
        problematic |= series.isna()
        if dfu.is_textlike(series):
            problematic |= series.astype("string").fillna("").str.strip().str.lower().isin(_PLACEHOLDERS)
        numeric = pd.to_numeric(series, errors="coerce")
        finite = numeric.replace([np.inf, -np.inf], np.nan).dropna()
        if len(finite) >= 4:
            q1, q3 = finite.quantile([.25, .75])
            iqr = q3 - q1
            if iqr > 0:
                problematic |= (numeric < q1 - 1.5 * iqr) | (numeric > q3 + 1.5 * iqr)

    return {
        "rows_with_missing": rows_with_missing,
        "rows_with_missing_percentage": round(rows_with_missing / max(len(df), 1) * 100, 2),
        "rows_all_missing": all_missing,
        "max_missing_in_single_row": int(missing_per_row.max()) if len(missing_per_row) else 0,
        "rows_with_most_missing": [{"row_number": int(i) + 1, "missing_cells": int(v)} for i, v in top.items() if v > 0],
        "problematic_row_count": int(problematic.sum()),
        "problematic_row_percentage": round(float(problematic.mean() * 100), 2) if len(problematic) else 0.0,
    }


def _correlation_summary(df: pd.DataFrame, profiles: list[ColumnProfile]) -> dict[str, Any]:
    numeric_names = [p.name for p in profiles if p.numeric_stats and p.numeric_stats.count >= 2]
    if len(numeric_names) < 2:
        return {"columns": numeric_names, "matrix": [], "strongest": []}
    m = df[numeric_names].apply(pd.to_numeric, errors="coerce").corr(method="pearson")
    matrix = []
    for row in numeric_names:
        matrix.append({"row": row, "values": [{"column": col, "value": dfu.safe_float(m.loc[row, col])} for col in numeric_names]})
    pairs = []
    for i, a in enumerate(numeric_names):
        for b in numeric_names[i + 1:]:
            value = m.loc[a, b]
            if pd.notna(value):
                pairs.append({"column_a": a, "column_b": b, "correlation": round(float(value), 4), "absolute": round(abs(float(value)), 4)})
    pairs.sort(key=lambda x: x["absolute"], reverse=True)
    return {"columns": numeric_names, "matrix": matrix, "strongest": pairs[:20]}


def _cleaning_recommendations(profiles: list[ColumnProfile], quality: DataQualityFlags, duplicates: int) -> list[dict]:
    recs = []
    for p in profiles:
        for message in p.recommendations:
            severity = "high" if p.constant or p.missing_percentage >= 50 else "warning"
            recs.append({"severity": severity, "column": p.name, "recommendation": message})
    if duplicates:
        recs.insert(0, {"severity": "high", "column": None, "recommendation": f"Review {duplicates:,} duplicate rows."})
    return recs


def profile_dataset(record: DatasetRecord) -> DatasetProfile:
    raw = _read_raw(record)
    df, invalid_dates, numeric_like = _prepare_profile_dataframe(raw)
    rows, columns = int(len(df)), int(len(df.columns))
    total_cells = rows * columns
    total_missing = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    duplicate_groups = int(df[df.duplicated(keep=False)].drop_duplicates().shape[0]) if duplicate_rows else 0

    profiles, type_counts = _column_profiles(df, raw, rows, invalid_dates, numeric_like)
    quality = _quality_flags(raw, profiles, invalid_dates)
    quality.duplicate_rows_present = duplicate_rows > 0

    row_quality = _row_quality(df, profiles)
    missing = MissingDataSummary(
        total_missing=total_missing,
        missing_percentage=round(total_missing / total_cells * 100, 2) if total_cells else 0.0,
        rows_with_missing=row_quality["rows_with_missing"],
        rows_all_missing=row_quality["rows_all_missing"],
        per_column={str(c): int(df[c].isna().sum()) for c in df.columns},
        per_column_percentage={str(c): round(int(df[c].isna().sum()) / max(rows, 1) * 100, 2) for c in df.columns},
        top_missing_columns=sorted(
            [{"column": str(c), "missing": int(df[c].isna().sum()), "percentage": round(int(df[c].isna().sum()) / max(rows, 1) * 100, 2)} for c in df.columns],
            key=lambda x: x["missing"], reverse=True
        )[:20],
    )

    overview = {
        "file_size_bytes": int(record.size),
        "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
        "numeric_columns": [p.name for p in profiles if p.numeric_stats],
        "categorical_columns": [p.name for p in profiles if p.categorical_stats],
        "datetime_columns": [p.name for p in profiles if p.datetime_stats],
        "boolean_columns": [p.name for p in profiles if p.dtype == dfu.BOOLEAN],
        "text_columns": [p.name for p in profiles if p.dtype == dfu.CATEGORICAL and not p.numeric_like],
        "empty_rows": row_quality["rows_all_missing"],
        "columns_with_missing": sum(1 for p in profiles if p.missing_count),
        "rows_with_missing": row_quality["rows_with_missing"],
        "missing_cell_rate": missing.missing_percentage,
        "data_density": round(100 - missing.missing_percentage, 2),
    }

    overview["selected_sheet"] = record.sheet_name
    overview["available_sheets"] = data_loader.get_excel_sheets(record)
    overview["source_kind"] = "Excel workbook" if record.format == "xlsx" else "CSV file"

    return DatasetProfile(
        dataset_id=record.id, filename=record.filename, format=record.format, size=record.size,
        sheet_name=record.sheet_name, available_sheets=overview["available_sheets"],
        rows=rows, columns=columns, memory_usage_bytes=overview["memory_usage_bytes"],
        total_cells=total_cells, column_types=type_counts, missing_data=missing,
        duplicates=DuplicatesSummary(duplicate_rows=duplicate_rows,
                                     duplicate_percentage=round(duplicate_rows / max(rows, 1) * 100, 2),
                                     duplicate_groups=duplicate_groups),
        column_profiles=profiles, quality_flags=quality, overview=overview,
        row_quality=row_quality, correlation=_correlation_summary(df, profiles),
        cleaning_recommendations=_cleaning_recommendations(profiles, quality, duplicate_rows),
    )


def get_dataset_preview(record: DatasetRecord, page: int = 1, page_size: int = DEFAULT_PREVIEW_PAGE_SIZE) -> DatasetPreview:
    df = _read_raw(record)
    page_size = max(1, min(page_size, MAX_PREVIEW_PAGE_SIZE))
    total_rows = int(len(df))
    total_pages = max(1, math.ceil(total_rows / page_size)) if total_rows else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    page_df = df.iloc[start:start + page_size]
    columns = [str(c) for c in df.columns]
    rows = [{columns[i]: dfu.json_safe_cell(value) for i, value in enumerate(row)} for row in page_df.itertuples(index=False, name=None)]
    return DatasetPreview(dataset_id=record.id, columns=columns, rows=rows, page=page, page_size=page_size,
                          total_rows=total_rows, total_pages=total_pages)


def get_problem_rows(record: DatasetRecord, limit: int = 100) -> list[dict]:
    """Return rows that contain missing/placeholder values or numeric IQR outliers."""
    raw = _read_raw(record)
    df, _, numeric_like = _prepare_profile_dataframe(raw)
    issues_by_index: dict[int, list[str]] = {}

    for col in df.columns:
        name = str(col)
        s = df[col]
        missing_mask = s.isna()
        for idx in raw.index[missing_mask]:
            issues_by_index.setdefault(int(idx), []).append(f"{name}: missing")
        if name in numeric_like:
            n = numeric_like[name].replace([np.inf, -np.inf], np.nan).dropna()
            if len(n) >= 4:
                q1, q3 = n.quantile([.25, .75]); iqr = q3 - q1
                if iqr > 0:
                    mask = (numeric_like[name] < q1 - 1.5 * iqr) | (numeric_like[name] > q3 + 1.5 * iqr)
                    for idx in raw.index[mask.fillna(False)]:
                        issues_by_index.setdefault(int(idx), []).append(f"{name}: outlier")
        if dfu.is_textlike(raw[col]):
            for idx, value in raw[col].items():
                if pd.notna(value) and str(value).strip().lower() in _PLACEHOLDERS:
                    issues_by_index.setdefault(int(idx), []).append(f"{name}: placeholder")

    rows = []
    for idx, issues in sorted(issues_by_index.items(), key=lambda x: (-len(x[1]), x[0]))[:limit]:
        row = {str(c): dfu.json_safe_cell(raw.loc[idx, c]) for c in raw.columns}
        rows.append({"row_number": idx + 1, "issues": issues, "data": row})
    return rows

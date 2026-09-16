"""Shared, generic pandas DataFrame helpers.

Small, reusable helpers used across multiple services (profiling now;
cleaning/analysis in later phases) — not business logic specific to
any single feature.
"""

from __future__ import annotations

import pandas as pd

NUMERICAL = "numerical"
CATEGORICAL = "categorical"
DATETIME = "datetime"
BOOLEAN = "boolean"
OTHER = "other"


def _is_boolean_like_object(series: pd.Series) -> bool:
    """True if an object-dtype column holds only real Python bools (plus nulls).

    A CSV column of True/False values that also has a missing row no
    longer parses to pandas' native bool dtype (that dtype can't hold
    NaN) — it comes back as dtype "object" containing actual `bool`
    instances alongside NaN. Without this check that column would be
    misclassified as categorical instead of boolean.
    """
    non_null = series.dropna()
    if non_null.empty:
        return False
    return all(isinstance(value, bool) for value in non_null)


def classify_column(series: pd.Series) -> str:
    """Classify a column into one of the broad type buckets DataLens reports on."""
    if pd.api.types.is_bool_dtype(series):
        return BOOLEAN
    if pd.api.types.is_datetime64_any_dtype(series):
        return DATETIME
    if pd.api.types.is_numeric_dtype(series):
        return NUMERICAL
    if pd.api.types.is_object_dtype(series) and _is_boolean_like_object(series):
        return BOOLEAN
    if (
        pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
        or isinstance(series.dtype, pd.CategoricalDtype)
    ):
        return CATEGORICAL
    return OTHER


def is_textlike(series: pd.Series) -> bool:
    """True for plain text columns (pandas 3's default string dtype, or legacy object)."""
    return pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)


def safe_float(value) -> float | None:
    """Convert a numpy/pandas scalar to a JSON-safe float, or None for NaN/inf."""
    if value is None:
        return None
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return None
    if as_float != as_float or as_float in (float("inf"), float("-inf")):  # NaN / inf
        return None
    return round(as_float, 6)


def has_mixed_types(series: pd.Series) -> bool:
    """True if a column's values look like a mix of incompatible underlying types.

    Two cases are covered:
    - Legacy/XLSX-style object-dtype columns where individual cells are
      already different Python types (e.g. int and str in the same
      column) — detected by comparing `type()` across non-null values.
    - CSV-sourced text columns. Pandas 3 reads any column that isn't
      fully numeric as its "str" dtype, which collapses a genuinely
      mixed column (e.g. "123", "INV-004", "56") into a single dtype
      and hides the issue from a plain dtype check. This is detected
      by checking whether only *some* (not all, not none) of the
      values parse as numbers — the hallmark of a mixed-content column
      rather than a normal, uniformly non-numeric categorical one.
    """
    non_null = series.dropna()
    if non_null.empty:
        return False

    if pd.api.types.is_object_dtype(series):
        return len({type(value) for value in non_null}) > 1

    if pd.api.types.is_string_dtype(series):
        fraction_numeric = pd.to_numeric(non_null, errors="coerce").notna().mean()
        return 0 < fraction_numeric < 1

    return False


def json_safe_cell(value):
    """Convert a pandas/numpy cell to a JSON-safe primitive for previews."""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    try:
        return value.item()
    except AttributeError:
        return value

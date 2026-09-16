"""Matplotlib plots used by the deep DataLens profiler."""
from __future__ import annotations

from io import BytesIO
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from app.models.dataset import DatasetRecord
from app.services.data_profiler import _read_raw, _numeric_like_values, _PLACEHOLDERS
from app.utils.dataframe_utils import classify_column


_SEABORN_READY = False

def _apply_seaborn_theme():
    global _SEABORN_READY
    if not _SEABORN_READY:
        sns.set_theme(style="darkgrid", context="notebook", palette="husl")
        _SEABORN_READY = True


def _image(fig):
    buffer = BytesIO()
    fig.patch.set_facecolor("#08111f")
    for ax in fig.axes:
        ax.set_facecolor("#0b1424")
        ax.tick_params(colors="#cbd5e1")
        ax.xaxis.label.set_color("#cbd5e1")
        ax.yaxis.label.set_color("#cbd5e1")
        ax.title.set_color("#f8fafc")
        for spine in ax.spines.values(): spine.set_color("#334155")
    fig.tight_layout()
    fig.savefig(buffer, format="png", dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buffer.seek(0)
    return buffer


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(dtype=float)
    s = df[column]
    if not pd.api.types.is_numeric_dtype(s):
        parsed, fraction = _numeric_like_values(s)
        if fraction >= 0.7:
            return parsed
    return pd.to_numeric(s, errors="coerce")


def make_plot(record: DatasetRecord, plot_type: str, column: str | None = None, top_n: int = 20):
    df = _read_raw(record)
    cols = [str(c) for c in df.columns]
    _apply_seaborn_theme()
    if column and column not in cols:
        column = None

    if plot_type == "missing":
        counts = df.isna().sum().sort_values(ascending=False)
        counts = counts[counts > 0].head(30)
        fig, ax = plt.subplots(figsize=(11, 5))
        if counts.empty:
            ax.text(.5, .5, "No missing cells detected", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        else:
            plot_df = pd.DataFrame({"column": counts.index.astype(str), "missing": counts.values})
            sns.barplot(data=plot_df, x="column", y="missing", ax=ax)
            ax.set_ylabel("Missing cells")
            ax.set_title("Missing values by column")
            ax.tick_params(axis="x", rotation=45)
        return _image(fig)

    if plot_type == "heatmap":
        missing = df.isna().astype(int)
        # Keep plots usable for very wide/large datasets.
        row_step = max(1, len(missing) // 250)
        col_step = max(1, len(missing.columns) // 40)
        data = missing.iloc[::row_step, ::col_step]
        fig, ax = plt.subplots(figsize=(12, 6))
        im = ax.imshow(data.to_numpy(), aspect="auto", interpolation="nearest")
        ax.set_title("Missingness heatmap (sampled rows/columns)")
        ax.set_xlabel("Columns")
        ax.set_ylabel("Rows")
        ax.set_xticks(range(len(data.columns)))
        ax.set_xticklabels([str(c) for c in data.columns], rotation=60, ha="right", fontsize=8)
        fig.colorbar(im, ax=ax, label="1 = missing")
        return _image(fig)

    if plot_type == "correlation":
        numeric = {}
        for c in cols:
            s = _numeric_series(df, c)
            if s.notna().sum() >= 2 and s.nunique(dropna=True) > 1:
                numeric[c] = s
        m = pd.DataFrame(numeric).corr()
        fig, ax = plt.subplots(figsize=(max(7, len(m.columns) * .65), max(6, len(m.columns) * .55)))
        if m.empty:
            ax.text(.5, .5, "At least two variable numeric columns are needed", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        else:
            sns.heatmap(m, ax=ax, vmin=-1, vmax=1, center=0, cmap="vlag", annot=len(m.columns) <= 12, fmt=".2f", square=False, cbar_kws={"label": "Correlation"})
            ax.set_xticklabels(ax.get_xticklabels(), rotation=60, ha="right", fontsize=8)
            ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
            ax.set_title("Pearson correlation matrix · Seaborn")
        return _image(fig)

    if not column:
        column = next((c for c in cols if _numeric_series(df, c).notna().sum() >= 2), cols[0] if cols else None)
    if not column:
        fig, ax = plt.subplots(); ax.text(.5, .5, "Dataset has no columns", ha="center", va="center"); ax.set_axis_off()
        return _image(fig)

    if plot_type in {"histogram", "boxplot"}:
        s = _numeric_series(df, column).replace([np.inf, -np.inf], np.nan).dropna()
        fig, ax = plt.subplots(figsize=(11, 5))
        if s.empty:
            ax.text(.5, .5, f"No numeric values available in {column}", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        elif plot_type == "histogram":
            bins = min(30, max(5, int(np.sqrt(len(s)))))
            sns.histplot(s, bins=bins, kde=True, ax=ax)
            ax.set_title(f"Distribution — {column}")
            ax.set_xlabel(column); ax.set_ylabel("Rows")
        else:
            sns.boxplot(x=s, ax=ax, orient="h")
            ax.set_title(f"Box plot — {column}")
            ax.set_xlabel(column)
        return _image(fig)

    if plot_type in {"category", "frequency"}:
        s = df[column].dropna().astype(str)
        counts = s.value_counts().head(max(5, min(top_n, 50))).sort_values()
        fig, ax = plt.subplots(figsize=(11, max(4, min(12, len(counts) * .35 + 1))))
        if counts.empty:
            ax.text(.5, .5, f"No non-empty values in {column}", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
        else:
            plot_df = pd.DataFrame({"value": counts.index.astype(str), "frequency": counts.values})
            sns.barplot(data=plot_df, y="value", x="frequency", ax=ax, orient="h")
            ax.set_title(f"Top values — {column}")
            ax.set_xlabel("Frequency")
        return _image(fig)

    raise ValueError("Unsupported plot type")

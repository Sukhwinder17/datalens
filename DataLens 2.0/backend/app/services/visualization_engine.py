"""Universal visualization engine.

Data preparation uses pandas/NumPy; rendered charts use Matplotlib. The engine
never assumes a particular dataset schema and gracefully handles empty, text,
datetime, numeric-like and mixed columns.
"""
from __future__ import annotations
from io import BytesIO
import math
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from app.services import data_loader
from app.utils.dataframe_utils import classify_column, json_safe_cell, safe_float


def _numeric_series(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return pd.to_numeric(s, errors="coerce")
    text = s.astype("string").str.strip().str.replace(r"[$€£₹]", "", regex=True).str.replace(",", "", regex=False).str.replace("%", "", regex=False)
    return pd.to_numeric(text, errors="coerce")


def _pick_columns(df: pd.DataFrame, x: str | None, y: str | None, chart_type: str):
    cols = [str(c) for c in df.columns]

    def numeric_candidates():
        out = []
        preferred = re.compile(r"(sales|revenue|profit|price|amount|value|score|close|predicted|quantity|count|total)", re.I)
        for c in cols:
            n = _numeric_series(df[c])
            valid = n.notna().sum()
            if valid >= 2 and n.nunique(dropna=True) > 1:
                bonus = 1 if preferred.search(c) else 0
                out.append((bonus, int(valid), c))
        return [c for _, _, c in sorted(out, key=lambda z: (z[0], z[1]), reverse=True)]

    numeric = numeric_candidates()
    date_cols = [c for c in cols if pd.api.types.is_datetime64_any_dtype(df[c]) or
                 (classify_column(df[c]) == "categorical" and pd.to_datetime(df[c], errors="coerce", format="mixed").notna().mean() >= .8)]

    def category_candidates():
        out = []
        id_like = re.compile(r"(?:^|[_\s-])(id|uuid|key|code|number|no)(?:$|[_\s-])", re.I)
        for c in cols:
            s = df[c]
            unique = int(s.nunique(dropna=True))
            if 1 < unique <= 50:
                penalty = 1 if id_like.search(c) or unique / max(len(df), 1) > .8 else 0
                preferred = 1 if re.search(r"(category|segment|region|city|state|product|customer|mode|type|class|date)", c, re.I) else 0
                out.append((preferred, -penalty, -unique, c))
        return [c for *_, c in sorted(out, reverse=True)]

    categories = category_candidates()
    x = x if x in cols else None
    y = y if y in cols else None

    if chart_type in {"scatter", "scatter3d", "regression"}:
        if x not in numeric: x = numeric[0] if numeric else (cols[0] if cols else None)
        if y not in numeric or y == x: y = next((c for c in numeric if c != x), None)
    elif chart_type in {"histogram", "boxplot", "violin", "kde"}:
        if x not in numeric: x = numeric[0] if numeric else (cols[0] if cols else None)
        y = None
    elif chart_type in {"line", "area"}:
        if x not in cols: x = date_cols[0] if date_cols else (categories[0] if categories else (cols[0] if cols else None))
        if y not in numeric or y == x: y = next((c for c in numeric if c != x), None)
    elif chart_type in {"bar", "pie", "donut", "countplot"}:
        if x not in cols: x = categories[0] if categories else (date_cols[0] if date_cols else (cols[0] if cols else None))
        if y not in numeric or y == x: y = next((c for c in numeric if c != x), None)
    return x, y


def chart(dataset_id, chart_type, x=None, y=None, z=None):
    record = data_loader.get_dataset(dataset_id)
    if record is None:
        return None
    df = data_loader.read_dataframe(record)
    cols = [str(c) for c in df.columns]
    _apply_seaborn_theme()
    x, y = _pick_columns(df, x, y, chart_type)
    numeric_cols = [c for c in cols if _numeric_series(df[c]).notna().sum() >= 2]
    if chart_type == "scatter3d":
        if z not in numeric_cols or z in {x, y}:
            z = next((c for c in numeric_cols if c not in {x, y}), None)
    else:
        z = None
    rows = []
    if chart_type == "scatter3d" and x and y and z:
        a = pd.DataFrame({"x": _numeric_series(df[x]), "y": _numeric_series(df[y]), "z": _numeric_series(df[z])}).dropna().head(2000)
        rows = [{"x": safe_float(r.x), "y": safe_float(r.y), "z": safe_float(r.z)} for r in a.itertuples()]
    elif chart_type in ("bar", "pie", "donut") and x:
        if y:
            a = df[[x, y]].copy(); a[y] = _numeric_series(a[y]); a = a.dropna(subset=[x, y])
            g = a.groupby(x, dropna=False)[y].sum().sort_values(ascending=False).head(30)
            rows = [{"label": str(k), "value": safe_float(v)} for k, v in g.items()]
        else:
            vc = df[x].dropna().astype(str).value_counts().head(30)
            rows = [{"label": str(k), "value": int(v)} for k, v in vc.items()]
    elif chart_type == "histogram" and x:
        s = _numeric_series(df[x]).replace([np.inf, -np.inf], np.nan).dropna()
        if not s.empty:
            bins = min(30, max(5, int(np.sqrt(len(s)))))
            counts, edges = np.histogram(s.to_numpy(dtype=float), bins=bins)
            rows = [{"label": f"{edges[i]:.4g}–{edges[i+1]:.4g}", "count": int(counts[i])} for i in range(len(counts))]
    elif chart_type in ("scatter", "regression") and x and y:
        a = pd.DataFrame({"x": _numeric_series(df[x]), "y": _numeric_series(df[y])}).dropna().head(2000)
        rows = [{"x": safe_float(r.x), "y": safe_float(r.y)} for r in a.itertuples()]
    elif chart_type in ("line", "area") and x and y:
        a = df[[x, y]].copy(); a[y] = _numeric_series(a[y]); a = a.dropna(subset=[y]).head(2000)
        rows = [{"label": str(json_safe_cell(r[x])), "value": safe_float(r[y])} for _, r in a.iterrows()]
    elif x:
        vc = df[x].dropna().astype(str).value_counts().head(30)
        rows = [{"label": str(k), "value": int(v)} for k, v in vc.items()]
    return {"dataset_id": dataset_id, "chart_type": chart_type, "x": x, "y": y, "z": z,
            "data": rows, "available_columns": cols, "rows": int(len(df)), "columns": int(len(cols))}


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
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buffer.seek(0)
    return buffer


def make_chart_plot(dataset_id: str, chart_type: str, x: str | None = None, y: str | None = None, z: str | None = None):
    record = data_loader.get_dataset(dataset_id)
    if record is None:
        return None
    df = data_loader.read_dataframe(record)
    cols = [str(c) for c in df.columns]
    if chart_type == "scatter3d":
        numeric = [c for c in cols if _numeric_series(df[c]).notna().sum() >= 2]
        x = x if x in numeric else (numeric[0] if numeric else None)
        y = y if y in numeric and y != x else next((c for c in numeric if c != x), None)
        z = z if z in numeric and z not in {x, y} else next((c for c in numeric if c not in {x, y}), None)
        fig = plt.figure(figsize=(12, 7))
        ax = fig.add_subplot(111, projection="3d")
    else:
        x, y = _pick_columns(df, x, y, chart_type)
        fig, ax = plt.subplots(figsize=(12, 6.5))
    title = f"{chart_type.title()} — {record.filename}"
    if record.format == "xlsx" and record.sheet_name:
        title += f" · {record.sheet_name}"
    ax.set_title(title)

    if not cols:
        ax.text(.5, .5, "This dataset has no columns.", ha="center", va="center", transform=ax.transAxes); ax.set_axis_off(); return _image(fig)

    if chart_type == "scatter3d" and x and y and z:
        a = pd.DataFrame({x: _numeric_series(df[x]), y: _numeric_series(df[y]), z: _numeric_series(df[z])}).dropna().head(5000)
        if a.empty:
            ax.text2D(.5, .5, "No three-column numeric values are available.", ha="center", va="center", transform=ax.transAxes)
        else:
            ax.scatter(a[x], a[y], a[z], alpha=.65, s=18, c=np.arange(len(a)), cmap="viridis")
            ax.set_xlabel(x); ax.set_ylabel(y); ax.set_zlabel(z)
            ax.set_title(f"Multivariate 3D — {x} × {y} × {z}")
    elif chart_type in {"histogram", "boxplot", "violin", "kde"} and x:
        s = _numeric_series(df[x]).replace([np.inf, -np.inf], np.nan).dropna()
        if s.empty:
            ax.text(.5, .5, f"No usable numeric values in '{x}'.", ha="center", va="center", transform=ax.transAxes); ax.set_axis_off()
        elif chart_type == "histogram":
            sns.histplot(s, bins=min(30, max(5, int(np.sqrt(len(s))))), kde=True, ax=ax)
            ax.set_xlabel(x); ax.set_ylabel("Rows")
        elif chart_type == "boxplot":
            sns.boxplot(x=s, ax=ax, orient="h")
            ax.set_xlabel(x)
        elif chart_type == "violin":
            sns.violinplot(x=s, ax=ax, inner="quartile")
            ax.set_xlabel(x)
        else:
            sns.kdeplot(x=s, fill=True, ax=ax)
            ax.set_xlabel(x); ax.set_ylabel("Density")
    elif chart_type in {"scatter", "regression"} and x and y:
        a = pd.DataFrame({x: _numeric_series(df[x]), y: _numeric_series(df[y])}).dropna().head(5000)
        if a.empty:
            ax.text(.5, .5, "No paired numeric values are available.", ha="center", va="center", transform=ax.transAxes); ax.set_axis_off()
        else:
            if chart_type == "regression":
                sns.regplot(data=a, x=x, y=y, ax=ax, scatter_kws={"alpha": .45, "s": 20}, line_kws={"linewidth": 2.5})
            else:
                sns.scatterplot(data=a, x=x, y=y, ax=ax, alpha=.65, s=30)
            ax.set_xlabel(x); ax.set_ylabel(y)
    elif chart_type in {"line", "area"} and x and y:
        a = df[[x, y]].copy(); a[y] = _numeric_series(a[y]); a = a.dropna(subset=[y]).head(2000)
        if a.empty:
            ax.text(.5, .5, "No usable X/Y values are available.", ha="center", va="center", transform=ax.transAxes); ax.set_axis_off()
        else:
            # Convert datetime-like X values when possible; otherwise keep labels.
            parsed = pd.to_datetime(a[x], errors="coerce", format="mixed")
            use_dates = parsed.notna().mean() >= .8
            xx = parsed if use_dates else np.arange(len(a))
            if use_dates:
                sns.lineplot(x=xx, y=a[y].to_numpy(dtype=float), ax=ax)
            else:
                sns.lineplot(x=np.arange(len(a)), y=a[y].to_numpy(dtype=float), ax=ax)
            if chart_type == "area": ax.fill_between(xx, a[y].to_numpy(dtype=float), alpha=.12)
            ax.set_xlabel(x); ax.set_ylabel(y)
            if not use_dates and len(a) <= 40:
                ax.set_xticks(range(len(a))); ax.set_xticklabels(a[x].astype(str), rotation=45, ha="right")
    elif chart_type == "countplot" and x:
        counts = df[x].dropna().astype(str).value_counts().head(20).sort_values()
        if counts.empty:
            ax.text(.5, .5, f"No usable values in '{x}'.", ha="center", va="center", transform=ax.transAxes); ax.set_axis_off()
        else:
            plot_df = pd.DataFrame({"label": counts.index.astype(str), "count": counts.values})
            sns.barplot(data=plot_df, y="label", x="count", ax=ax, orient="h")
            ax.set_title(f"Seaborn count plot — {x}")
            ax.set_xlabel("Count")
    elif chart_type in {"bar", "pie", "donut"} and x:
        if y:
            a = df[[x, y]].copy(); a[y] = _numeric_series(a[y]); a = a.dropna(subset=[x, y])
            g = a.groupby(x, dropna=False)[y].sum().sort_values(ascending=False).head(20)
        else:
            g = df[x].dropna().astype(str).value_counts().head(20).sort_values()
        if g.empty:
            ax.text(.5, .5, f"No usable values in '{x}'.", ha="center", va="center", transform=ax.transAxes); ax.set_axis_off()
        elif chart_type == "bar":
            plot_df = pd.DataFrame({"label": [str(k) for k in g.index], "value": g.to_numpy(dtype=float)})
            sns.barplot(data=plot_df, y="label", x="value", ax=ax, orient="h")
            ax.set_xlabel(y or "Rows")
        else:
            pie_ax = ax
            wedges, texts, autotexts = pie_ax.pie(g.to_numpy(dtype=float), labels=[str(k) for k in g.index], autopct="%1.1f%%")
            for text in [*texts, *autotexts]: text.set_color("#e2e8f0")
            if chart_type == "donut":
                pie_ax.add_artist(plt.Circle((0, 0), .55, fc="#0b1424"))
            pie_ax.set_aspect("equal")
    else:
        ax.text(.5, .5, "Choose a compatible chart and columns.", ha="center", va="center", transform=ax.transAxes); ax.set_axis_off()

    ax.grid(axis="y", alpha=.2)
    return _image(fig)

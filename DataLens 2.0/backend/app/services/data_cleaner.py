from __future__ import annotations
import pandas as pd
from app.services import data_loader

def _df(dataset_id):
    r=data_loader.get_dataset(dataset_id)
    return data_loader.read_dataframe(r) if r else None

def preview(dataset_id, operation, column=None, value=None):
    df=_df(dataset_id)
    if df is None: return None
    cleaned, description=_apply(df,operation,column,value)
    return _summary(df,cleaned,description)

def apply(dataset_id, operation, column=None, value=None):
    df=_df(dataset_id)
    if df is None: return None
    cleaned,description=_apply(df,operation,column,value); data_loader.set_active_dataframe(dataset_id,cleaned); return _summary(df,cleaned,description)

def _apply(df,operation,column,value):
    out=df.copy()
    if operation=="drop_missing_rows": out=out.dropna()
    elif operation=="fill_missing" and column in out.columns:
        fill = value if value is not None and value != "" else (out[column].median() if pd.api.types.is_numeric_dtype(out[column]) else "Unknown")
        if pd.api.types.is_numeric_dtype(out[column]) and value not in (None, ""):
            try: fill = float(value)
            except (TypeError, ValueError): pass
        out[column] = out[column].fillna(fill)
    elif operation=="drop_duplicates": out=out.drop_duplicates()
    elif operation=="trim_text" and column in out.columns: out[column]=out[column].map(lambda x:x.strip() if isinstance(x,str) else x)
    elif operation=="drop_empty_columns": out=out.dropna(axis=1,how="all")
    elif operation=="drop_column" and column in out.columns: out=out.drop(columns=[column])
    else: return out,"No changes applied"
    return out,f"{operation.replace('_',' ').title()}"+(f" on {column}" if column else "")

def _summary(before,after,description): return {"description":description,"before":{"rows":len(before),"columns":len(before.columns),"missing":int(before.isna().sum().sum()),"duplicates":int(before.duplicated().sum())},"after":{"rows":len(after),"columns":len(after.columns),"missing":int(after.isna().sum().sum()),"duplicates":int(after.duplicated().sum())}}

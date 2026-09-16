from __future__ import annotations
import pandas as pd
from app.services import data_loader
from app.utils.dataframe_utils import classify_column, safe_float

def _record(record):
    df = data_loader.read_dataframe(record)
    numeric = [str(c) for c in df.columns if classify_column(df[c]) == "numerical"]
    categorical = [str(c) for c in df.columns if classify_column(df[c]) in ("categorical", "boolean")]
    numeric_stats=[]
    for c in numeric:
        s=pd.to_numeric(df[c],errors="coerce").dropna()
        numeric_stats.append({"column":c,"count":int(s.size),"mean":safe_float(s.mean()),"median":safe_float(s.median()),"std":safe_float(s.std()),"variance":safe_float(s.var()),"min":safe_float(s.min()),"max":safe_float(s.max()),"q1":safe_float(s.quantile(.25)),"q3":safe_float(s.quantile(.75))})
    corr=[]
    if len(numeric)>=2:
        m=df[numeric].apply(pd.to_numeric,errors="coerce").corr()
        corr=[{"row":str(r),"values":[{"column":str(c),"value":safe_float(m.loc[r,c])} for c in numeric]} for r in numeric]
    categorical_stats=[]
    for c in categorical:
        s=df[c].dropna().astype(str); vc=s.value_counts().head(10); total=len(s)
        categorical_stats.append({"column":c,"unique":int(s.nunique()),"top_value":str(vc.index[0]) if len(vc) else None,"top_frequency":int(vc.iloc[0]) if len(vc) else 0,"top_values":[{"value":str(k),"frequency":int(v),"percentage":round(v/total*100,2) if total else 0} for k,v in vc.items()]})
    return {"dataset_id":record.id,"filename":record.filename,"rows":int(len(df)),"columns":int(len(df.columns)),"numeric_columns":numeric,"categorical_columns":categorical,"numeric_stats":numeric_stats,"categorical_stats":categorical_stats,"correlation":corr}

def analyze(dataset_id):
    record=data_loader.get_dataset(dataset_id)
    if record is None: return None
    return _record(record)

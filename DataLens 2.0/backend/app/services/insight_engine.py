from __future__ import annotations
from app.services import data_loader, data_profiler

def get_insights(dataset_id):
    record=data_loader.get_dataset(dataset_id)
    if not record: return None
    p=data_profiler.profile_dataset(record); out=[]
    for c in p.column_profiles:
        if c.missing_percentage>0: out.append({"severity":"warning" if c.missing_percentage<50 else "high","title":f"{c.name} has missing values","message":f"{c.missing_count} of {p.rows} rows are missing ({c.missing_percentage}%).","column":c.name})
        if c.unique_percentage>=90 and p.rows>5: out.append({"severity":"info","title":f"{c.name} is high-cardinality","message":f"{c.unique_count} unique values across {p.rows} rows ({c.unique_percentage}%). It may be an identifier.","column":c.name})
        if c.numeric_stats and c.numeric_stats.count>3 and c.numeric_stats.std is not None and c.numeric_stats.mean is not None:
            s=c.numeric_stats
            if s.max is not None and s.min is not None and s.range is not None and s.p75 is not None and s.p25 is not None:
                iqr=s.p75-s.p25
                if iqr>0 and (s.max>s.p75+1.5*iqr or s.min<s.p25-1.5*iqr): out.append({"severity":"warning","title":f"Possible outliers in {c.name}","message":"The IQR rule flags unusually distant minimum or maximum values.","column":c.name})
        if c.categorical_stats and c.categorical_stats.top_value_percentage is not None and c.categorical_stats.top_value_percentage>=80: out.append({"severity":"info","title":f"{c.name} is dominated by one value","message":f"'{c.categorical_stats.top_value}' occurs in {c.categorical_stats.top_value_percentage}% of non-empty rows.","column":c.name})
    q=p.quality_flags
    if q.constant_columns: out.append({"severity":"warning","title":"Constant columns detected","message":", ".join(q.constant_columns),"column":None})
    if q.empty_columns: out.append({"severity":"high","title":"Completely empty columns detected","message":", ".join(q.empty_columns),"column":None})
    if not out: out.append({"severity":"success","title":"No significant rule-based issues found","message":"The current dataset passes the available quality checks.","column":None})
    return {"dataset_id":dataset_id,"filename":record.filename,"insights":out}

from __future__ import annotations
from app.services import data_loader, data_profiler

def compare(dataset_ids):
    results=[]
    for did in dataset_ids:
        r=data_loader.get_dataset(did)
        if not r: continue
        p=data_profiler.profile_dataset(r)
        completeness=100-p.missing_data.missing_percentage
        duplicate_penalty=p.duplicates.duplicate_percentage
        score=max(0,round(completeness-duplicate_penalty,2))
        results.append({"dataset_id":did,"filename":r.filename,"rows":p.rows,"columns":p.columns,"missing_percentage":p.missing_data.missing_percentage,"duplicates":p.duplicates.duplicate_rows,"numeric":p.column_types.numerical,"categorical":p.column_types.categorical,"datetime":p.column_types.datetime,"quality_score":score})
    return {"datasets":results,"best_dataset_id":max(results,key=lambda x:x["quality_score"])["dataset_id"] if results else None}

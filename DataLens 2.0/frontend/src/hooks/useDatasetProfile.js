import { useCallback, useEffect, useState } from "react";
import { getDatasetPreview, getDatasetProfile, listDatasets } from "../services/api/datasets.js";

export function useDatasetList() {
  const [datasets, setDatasets] = useState([]); const [status, setStatus] = useState("loading"); const [error, setError] = useState("");
  const refresh = useCallback(async () => { setStatus("loading"); setError(""); try { setDatasets(await listDatasets()); setStatus("success"); } catch { setError("Couldn't load your uploaded datasets. Please try again."); setStatus("error"); } }, []);
  useEffect(() => { refresh(); }, [refresh]); return { datasets, status, error, refresh };
}
export function useDatasetProfile(datasetId) {
  const [profile, setProfile] = useState(null); const [status, setStatus] = useState("idle"); const [error, setError] = useState("");
  useEffect(() => { if (!datasetId) { setProfile(null); setStatus("idle"); return; } let cancelled = false; setStatus("loading"); setError("");
    getDatasetProfile(datasetId).then((r) => { if (!cancelled) { setProfile(r); setStatus("success"); } }).catch((err) => { if (cancelled) return; const detail = err?.response?.data?.detail; setError(err?.response?.status === 404 ? "This dataset couldn't be found." : (detail || "Something went wrong while profiling this dataset.")); setStatus(err?.response?.status === 404 ? "not_found" : "error"); });
    return () => { cancelled = true; };
  }, [datasetId]); return { profile, status, error };
}
export function useDatasetPreview(datasetId, page, pageSize) {
  const [preview, setPreview] = useState(null); const [status, setStatus] = useState("idle"); const [error, setError] = useState("");
  useEffect(() => { if (!datasetId) return; let cancelled = false; setStatus("loading");
    getDatasetPreview(datasetId, page, pageSize).then((r) => { if (!cancelled) { setPreview(r); setStatus("success"); } }).catch((err) => { if (!cancelled) { setError(err?.response?.data?.detail || "Couldn't load the data preview."); setStatus("error"); } });
    return () => { cancelled = true; };
  }, [datasetId, page, pageSize]); return { preview, status, error };
}

import apiClient from "./client.js";
export async function getAnalysis(datasetId){ return (await apiClient.post("/analysis",{dataset_id:datasetId})).data; }

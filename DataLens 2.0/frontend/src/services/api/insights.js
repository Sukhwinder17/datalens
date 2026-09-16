import apiClient from "./client.js";
export async function getInsights(datasetId){ return (await apiClient.get("/insights",{params:{dataset_id:datasetId}})).data; }

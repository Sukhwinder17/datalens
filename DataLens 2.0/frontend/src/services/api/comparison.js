import apiClient from "./client.js";
export async function compareDatasets(datasetIds){ return (await apiClient.post("/comparison",{dataset_ids:datasetIds})).data; }

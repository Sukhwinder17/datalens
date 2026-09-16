import apiClient from "./client.js";
export async function getChartData(datasetId, chartConfig){ return (await apiClient.post("/visualization",{dataset_id:datasetId,...chartConfig})).data; }

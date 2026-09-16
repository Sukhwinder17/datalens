import apiClient from "./client.js";

export async function uploadDatasets(files) {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const response = await apiClient.post("/upload", formData, { headers: { "Content-Type": "multipart/form-data" } });
  return response.data;
}
export async function listDatasets() { return (await apiClient.get("/datasets")).data; }
export async function getDatasetProfile(datasetId) { return (await apiClient.get(`/datasets/${datasetId}/profile`)).data; }
export async function getDatasetPreview(datasetId, page = 1, pageSize = 20) {
  return (await apiClient.get(`/datasets/${datasetId}/preview`, { params: { page, page_size: pageSize } })).data;
}

export async function deleteDataset(datasetId) {
  return (await apiClient.delete(`/datasets/${datasetId}`)).data;
}
export async function clearDatasetSession() {
  return (await apiClient.delete("/datasets/session")).data;
}

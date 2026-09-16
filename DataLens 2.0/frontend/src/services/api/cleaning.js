import apiClient from "./client.js";
export async function previewCleaning(payload){ return (await apiClient.post("/cleaning/preview",payload)).data; }
export async function applyCleaning(payload){ return (await apiClient.post("/cleaning/apply",payload)).data; }

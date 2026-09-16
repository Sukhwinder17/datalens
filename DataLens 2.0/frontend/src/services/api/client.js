import axios from "axios";

// TODO: read base URL from a Vite env var (e.g. import.meta.env.VITE_API_URL)
// once environment-specific configuration is set up.
const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;

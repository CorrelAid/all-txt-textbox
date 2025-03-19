import { ApiClient } from "./client/ApiClient";

const apiClient = new ApiClient({
  BASE: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  WITH_CREDENTIALS: true,
});

export const useApiClient = () => {
  return {
    apiClient,
  };
};

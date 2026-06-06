import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  // baseURL: "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
});

export const getSales = async () => {
  const response = await api.get("/sales");
  return response.data;
};

export const getSalesById = async (id) => {
  const response = await api.get(`/sales/${id}`);
  return response.data;
};

export const createSales = async (data) => {
  const response = await api.post("/sales", data);
  return response.data;
};

export const updateSales = async (id, data) => {
  const response = await api.put(`/sales/${id}`, data);
  return response.data;
};

export const deleteSales = async (id) => {
  const response = await api.delete(`/sales/${id}`);
  return response.data;
};

export const getMonthlySales = async () => {
  const response = await api.get("/sales/monthly");
  return response.data;
};

export const runPrediction = async () => {
  const response = await api.get("/sales/predict");
  return response.data;
};

export const getProducts = async () => {
  const response = await api.get("/products");
  return response.data;
};

export const predictProduct = async (data) => {
  const response = await api.post("/predict-product", data);
  return response.data;
};

export const getRestockRecommendation = async (data) => {
  const response = await api.post("/ai/restock-recommendation", data);
  return response.data;
};

export const getTopProducts = async () => {
  const response = await api.get("/ai/top-products");
  return response.data;
};

export const getDeadStock = async () => {
  const response = await api.get("/ai/dead-stock");
  return response.data;
};

export const discountSimulation = async (data) => {
  const response = await api.post("/ai/discount-simulation", data);
  return response.data;
};

export const getInsights = async () => {
  const response = await api.get("/ai/insights");
  return response.data;
};

export const getAnalyticsMonthlySales = async () => {
  const response = await api.get("/analytics/monthly-sales");
  return response.data;
};

export const getAnalyticsProductSales = async () => {
  const response = await api.get("/analytics/product-sales");
  return response.data;
};

export const getAnalyticsRevenueTrend = async () => {
  const response = await api.get("/analytics/revenue-trend");
  return response.data;
};

export const getBranchPerformance = async () => {
  const response = await api.get("/analytics/branch-performance");
  return response.data;
};

export const uploadDataset = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/api/dataset/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const importDataset = async (uploadId, mode) => {
  const response = await api.post("/api/dataset/import", {
    upload_id: uploadId,
    mode: mode,
  });
  return response.data;
};

export const getDatasetHistory = async () => {
  const response = await api.get("/api/dataset/history");
  return response.data;
};

export const getDatasetStatistics = async () => {
  const response = await api.get("/api/dataset/statistics");
  return response.data;
};

export const restoreBackup = async (backupId) => {
  const response = await api.post(`/api/dataset/restore/${backupId}`);
  return response.data;
};

export const restoreLatestBackup = async () => {
  const response = await api.post("/api/dataset/restore-latest");
  return response.data;
};

export const retrainModel = async () => {
  const response = await api.post("/api/model/retrain");
  return response.data;
};

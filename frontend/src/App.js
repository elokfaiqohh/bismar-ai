import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import SalesPage from "./pages/SalesPage";
import PredictionPage from "./pages/PredictionPage";
import AIDashboard from "./pages/AIDashboard";
import DatasetManagement from "./pages/DatasetManagement";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/sales" element={<SalesPage />} />
        <Route path="/prediction" element={<PredictionPage />} />
        <Route path="/ai-dashboard" element={<AIDashboard />} />
        <Route path="/dataset" element={<DatasetManagement />} />
      </Routes>
    </div>
  );
}

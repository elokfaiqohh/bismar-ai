import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import {
  uploadDataset,
  importDataset,
  getDatasetHistory,
  getDatasetStatistics,
  restoreBackup,
  retrainModel,
} from "../services/api";
import { SectionHeader } from "../components/ui/SectionHeader";
import { Card } from "../components/ui/Card";
import { MetricCard } from "../components/ui/MetricCard";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Modal } from "../components/ui/Modal";
import { EmptyState } from "../components/ui/EmptyState";
import { LoadingState } from "../components/ui/LoadingState";
import {
  Upload,
  AlertTriangle,
  RefreshCw,
  FileSpreadsheet,
  CheckCircle,
  Database,
  ArrowRight,
  ShieldCheck,
  History,
  Archive,
  Loader2,
  TrendingUp,
  DollarSign
} from "lucide-react";
import { toast } from "sonner";

function formatCurrency(amount) {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(amount);
}

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function DatasetManagement() {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState({ uploads: [], backups: [] });
  
  // Upload State
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [validationErrors, setValidationErrors] = useState([]);
  
  // Preview State
  const [previewData, setPreviewData] = useState(null);
  const [importMode, setImportMode] = useState("APPEND");
  
  // Safety Dialog / Confirmation
  const [showReplaceModal, setShowReplaceModal] = useState(false);
  const [importLoading, setImportLoading] = useState(false);
  const [importResult, setImportResult] = useState(null);
  
  // Model Retraining State
  const [retrainStatus, setRetrainStatus] = useState("idle"); // idle, training, success, error
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    loadStatsAndHistory(true);
  }, []);

  async function loadStatsAndHistory(isInitial = false) {
    if (isInitial) setInitialLoading(true);
    try {
      const [statsData, historyData] = await Promise.all([
        getDatasetStatistics(),
        getDatasetHistory(),
      ]);
      setStats(statsData);
      setHistory(historyData || { uploads: [], backups: [] });
    } catch (err) {
      console.error("Failed to load statistics/history", err);
      toast.error("Failed to fetch dataset repository stats");
    } finally {
      if (isInitial) setInitialLoading(false);
    }
  }

  // Drag events
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  // Drop event
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith(".csv")) {
        setFile(droppedFile);
        setUploadError(null);
        setValidationErrors([]);
        setPreviewData(null);
        setImportResult(null);
        toast.info(`File selected: ${droppedFile.name}`);
      } else {
        setUploadError("Hanya file CSV (.csv) yang diperbolehkan.");
        toast.error("Invalid file format");
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.endsWith(".csv")) {
        setFile(selectedFile);
        setUploadError(null);
        setValidationErrors([]);
        setPreviewData(null);
        setImportResult(null);
        toast.info(`File selected: ${selectedFile.name}`);
      } else {
        setUploadError("Hanya file CSV (.csv) yang diperbolehkan.");
        toast.error("Invalid file format");
      }
    }
  };

  async function handleUpload() {
    if (!file) return;
    setUploadLoading(true);
    setUploadError(null);
    setValidationErrors([]);
    setPreviewData(null);
    setImportResult(null);

    try {
      const res = await uploadDataset(file);
      setPreviewData(res);
      toast.success("Dataset successfully parsed and validated!");
    } catch (err) {
      console.error(err);
      const errDetail = err.response?.data?.detail;
      if (errDetail && errDetail.errors) {
        setValidationErrors(errDetail.errors);
        setUploadError(errDetail.message || "Schema structure validation failed.");
      } else {
        setUploadError(err.response?.data?.detail || "Gagal mengunggah file. Pastikan struktur CSV sesuai.");
      }
      toast.error("Dataset validation error");
    } finally {
      setUploadLoading(false);
    }
  }

  async function executeImport() {
    if (!previewData) return;
    setImportLoading(true);
    setImportResult(null);

    try {
      const res = await importDataset(previewData.upload_id, importMode);
      setImportResult(res);
      setPreviewData(null);
      setFile(null);
      toast.success("Dataset successfully integrated!");
      await loadStatsAndHistory();
    } catch (err) {
      console.error(err);
      toast.error("Import operation failed");
    } finally {
      setImportLoading(false);
      setShowReplaceModal(false);
    }
  }

  function handleImportSubmit() {
    if (importMode === "REPLACE") {
      setShowReplaceModal(true);
    } else {
      executeImport();
    }
  }

  async function handleRestore(backupId) {
    if (!confirm(`Apakah Anda yakin ingin memulihkan dataset ke backup ${backupId}? Ini akan mencadangkan dataset aktif terlebih dahulu.`)) {
      return;
    }
    try {
      await restoreBackup(backupId);
      toast.success("Dataset database rolled back to target backup");
      await loadStatsAndHistory();
    } catch (err) {
      console.error(err);
      toast.error("Backup restoration failed");
    }
  }

  async function handleRetrain() {
    setRetrainStatus("training");
    toast.info("Triggering model training pipeline...");
    try {
      await retrainModel();
      setRetrainStatus("success");
      toast.success("AI models retrained successfully!");
      setTimeout(() => setRetrainStatus("idle"), 5000);
    } catch (err) {
      console.error(err);
      setRetrainStatus("error");
      toast.error("Retraining pipeline failed");
      setTimeout(() => setRetrainStatus("idle"), 5000);
    }
  }

  if (initialLoading) {
    return (
      <Layout title="Dataset Management">
        <div className="space-y-6">
          <LoadingState type="metric" count={4} />
          <LoadingState type="card" count={2} />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Dataset Center">
      <div className="space-y-6">
        
        {/* SECTION HEADER */}
        <SectionHeader
          title="Dataset & Storage Administration"
          description="Upload new training sets, validate headers schema matching, perform data replace/append operations, and rollback database points."
        />

        {/* METRICS ROW */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Database Total Records"
            value={stats ? stats.total_records.toLocaleString() : "-"}
            subtext="Integrated sales row entries"
            icon={Database}
          />
          <MetricCard
            title="Active Catalog Items"
            value={stats ? stats.total_products.toLocaleString() : "-"}
            subtext="Products modeled by models"
            icon={FileSpreadsheet}
          />
          <MetricCard
            title="Active Data Interval"
            value={stats?.date_range?.start ? `${stats.date_range.start.split("-")[0]} - ${stats.date_range.end.split("-")[0]}` : "-"}
            subtext={`${stats?.date_range?.start || ""} s/d ${stats?.date_range?.end || ""}`}
            icon={Archive}
          />
          <MetricCard
            title="Aggregated Sales Value"
            value={stats ? formatCurrency(stats.total_revenue) : "-"}
            subtext="Sum of clean transacted sales"
            icon={DollarSign}
          />
        </div>

        {/* MODEL RETRAINING CONSOLE */}
        <Card className="border-zinc-800 bg-zinc-950 text-white dark:border-zinc-800 dark:bg-zinc-900/60 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <h3 className="text-sm font-bold flex items-center gap-2">
              <ShieldCheck className="h-4.5 w-4.5 text-indigo-400" />
              Machine Learning Model Alignment
            </h3>
            <p className="text-xs text-zinc-400 max-w-2xl leading-relaxed">
              Whenever you perform replacement or append datasets, it is highly recommended to retrain the ML algorithms to fit tomorrow's patterns.
            </p>
          </div>
          <div>
            <Button
              variant={retrainStatus === "error" ? "danger" : "primary"}
              onClick={handleRetrain}
              disabled={retrainStatus === "training"}
              className="w-full md:w-auto px-6 py-2.5 font-semibold shrink-0"
            >
              {retrainStatus === "training" && (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Retraining AI...
                </>
              )}
              {retrainStatus === "success" && "Model Sync Success!"}
              {retrainStatus === "error" && "Sync Fail - Retry"}
              {retrainStatus === "idle" && "Synchronize AI Models"}
            </Button>
          </div>
        </Card>

        {/* SPLIT SECTION: UPLOAD & PREVIEW */}
        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* UPLOAD PANEL (1/3) */}
          <Card className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50">Upload Data Stream</h3>
            
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`
                p-6 border-2 border-dashed rounded-xl text-center cursor-pointer flex flex-col items-center justify-center min-h-[200px] transition-all
                ${
                  dragActive
                    ? "border-indigo-550 bg-indigo-50/10 dark:border-indigo-400 dark:bg-indigo-950/10"
                    : "border-zinc-250 hover:border-zinc-350 dark:border-zinc-800 dark:hover:border-zinc-700"
                }
              `}
            >
              <Upload className="w-8 h-8 text-zinc-400 mb-3" />
              
              <p className="text-xs font-semibold text-zinc-700 dark:text-zinc-300">Drag & drop dataset CSV here</p>
              <p className="text-[10px] text-zinc-400 mt-1">Accepts strictly structured sales CSV files only</p>
              
              <label className="mt-4 px-3 py-1.5 text-xs font-semibold bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-750 rounded-lg cursor-pointer transition">
                Select File
                <input
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </label>
            </div>

            {/* Selected File Details */}
            {file && (
              <div className="p-3 bg-zinc-50 border border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800 rounded-lg flex items-center justify-between text-xs">
                <div className="truncate pr-2">
                  <span className="font-semibold text-zinc-700 dark:text-zinc-300 block truncate">{file.name}</span>
                  <span className="text-[10px] text-zinc-400">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-xs font-semibold text-zinc-400 hover:text-rose-600 transition"
                >
                  Clear
                </button>
              </div>
            )}

            {/* Error & Validation Cards */}
            {uploadError && (
              <div className="p-4 bg-rose-50 border border-rose-100 text-rose-700 rounded-xl text-xs space-y-2 dark:bg-rose-950/20 dark:border-rose-900/30 dark:text-rose-400">
                <p className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4 shrink-0" />
                  {uploadError}
                </p>
                {validationErrors.length > 0 && (
                  <ul className="list-disc pl-4 space-y-1 text-[10px] text-rose-600 dark:text-rose-450 max-h-[150px] overflow-y-auto">
                    {validationErrors.map((err, idx) => (
                      <li key={idx}>{err}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            <Button
              variant="primary"
              onClick={handleUpload}
              disabled={!file || uploadLoading}
              loading={uploadLoading}
              className="w-full"
            >
              Analyze & Verify Schema
            </Button>
          </Card>

          {/* PREVIEW PANEL (2/3) */}
          <Card className="lg:col-span-2 space-y-4">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50">Verification & Preview Dashboard</h3>

            {!previewData && !importResult && (
              <EmptyState
                title="No Dataset Uploaded"
                description="Upload a CSV dataset from the left panel to verify and inspect the file before integrating it into Bismar AI database."
                icon={Database}
                animate={false}
              />
            )}

            {importResult && (
              <div className="p-5 bg-emerald-50 border border-emerald-100 rounded-xl space-y-4 dark:bg-emerald-950/10 dark:border-emerald-900/30">
                <h4 className="text-sm font-bold text-emerald-800 dark:text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle className="h-5 w-5" />
                  Integration Success
                </h4>
                <div className="grid gap-3 sm:grid-cols-3 text-xs">
                  <div className="p-3 bg-white border border-zinc-150 rounded-lg dark:bg-zinc-950 dark:border-zinc-800">
                    <span className="text-[10px] text-zinc-400 block font-semibold uppercase">Action mode</span>
                    <span className="text-sm font-bold text-zinc-850 dark:text-zinc-200 mt-1 block">{importResult.mode}</span>
                  </div>
                  <div className="p-3 bg-white border border-zinc-150 rounded-lg dark:bg-zinc-950 dark:border-zinc-800">
                    <span className="text-[10px] text-zinc-400 block font-semibold uppercase">Imported rows</span>
                    <span className="text-sm font-bold text-zinc-850 dark:text-zinc-200 mt-1 block">{importResult.imported_rows.toLocaleString()}</span>
                  </div>
                  <div className="p-3 bg-white border border-zinc-150 rounded-lg dark:bg-zinc-950 dark:border-zinc-800">
                    <span className="text-[10px] text-zinc-400 block font-semibold uppercase">Duplicates Skipped</span>
                    <span className="text-sm font-bold text-zinc-850 dark:text-zinc-200 mt-1 block">{importResult.duplicate_rows.toLocaleString()}</span>
                  </div>
                </div>
                {importResult.backup_file && (
                  <p className="text-[10px] text-zinc-400 font-mono">
                    System rollback checkpoint created: {importResult.backup_file}
                  </p>
                )}
                <Button variant="secondary" onClick={() => setImportResult(null)}>
                  Clear Console
                </Button>
              </div>
            )}

            {previewData && (
              <div className="space-y-5">
                {/* Stats cards */}
                <div className="grid gap-3 sm:grid-cols-3 text-xs">
                  <div className="p-3 bg-zinc-50 border border-zinc-150 rounded-lg dark:bg-zinc-950 dark:border-zinc-850">
                    <span className="text-[10px] text-zinc-400 block uppercase">Rows in CSV</span>
                    <span className="text-sm font-bold text-zinc-800 dark:text-zinc-200 block mt-1">
                      {previewData.preview.total_rows.toLocaleString()}
                    </span>
                  </div>
                  <div className="p-3 bg-zinc-50 border border-zinc-150 rounded-lg dark:bg-zinc-950 dark:border-zinc-850">
                    <span className="text-[10px] text-zinc-400 block uppercase">Products Count</span>
                    <span className="text-sm font-bold text-zinc-800 dark:text-zinc-200 block mt-1">
                      {previewData.preview.total_products.toLocaleString()}
                    </span>
                  </div>
                  <div className="p-3 bg-zinc-50 border border-zinc-150 rounded-lg dark:bg-zinc-950 dark:border-zinc-850">
                    <span className="text-[10px] text-zinc-400 block uppercase">Timeline Range</span>
                    <span className="text-xs font-bold text-zinc-800 dark:text-zinc-200 block truncate mt-1">
                      {previewData.preview.date_range.start} - {previewData.preview.date_range.end}
                    </span>
                  </div>
                </div>

                {/* Preview sample Table */}
                <div className="space-y-2">
                  <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">Sample rows from CSV</span>
                  <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead className="bg-zinc-50 border-b border-zinc-200 dark:bg-zinc-950 dark:border-zinc-800">
                        <tr>
                          <th className="p-2.5">Tanggal</th>
                          <th className="p-2.5">Nama Barang</th>
                          <th className="p-2.5">Tx Type</th>
                          <th className="p-2.5">Qty</th>
                          <th className="p-2.5">Kategori</th>
                        </tr>
                      </thead>
                      <tbody>
                        {previewData.preview.sample_rows.map((row, idx) => (
                          <tr key={idx} className="border-b last:border-b-0 hover:bg-zinc-50/50 dark:hover:bg-zinc-900/30">
                            <td className="p-2.5 font-mono text-[10px]">{row.Tanggal}</td>
                            <td className="p-2.5 font-semibold text-zinc-900 dark:text-zinc-250 truncate max-w-[120px]">{row.Nama_Barang}</td>
                            <td className="p-2.5">{row.Tipe_Transaksi}</td>
                            <td className="p-2.5 font-bold text-zinc-800 dark:text-zinc-200">{row.Kuantitas}</td>
                            <td className="p-2.5"><Badge variant="neutral">{row.Kategori || "General"}</Badge></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Import Mode Radio Selectors */}
                <div className="p-4 rounded-xl border border-indigo-100 bg-indigo-50/10 dark:border-indigo-900/20 dark:bg-indigo-950/5 space-y-3.5">
                  <h4 className="text-xs font-bold text-zinc-900 dark:text-zinc-100">Integration Option</h4>
                  
                  <div className="grid gap-3 sm:grid-cols-2">
                    <label className="flex items-start gap-2.5 cursor-pointer p-3 border border-zinc-200 rounded-lg dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900/50">
                      <input
                        type="radio"
                        name="importMode"
                        value="APPEND"
                        checked={importMode === "APPEND"}
                        onChange={() => setImportMode("APPEND")}
                        className="mt-0.5 w-4 h-4 text-indigo-650 focus:ring-indigo-500"
                      />
                      <div>
                        <span className="text-xs font-bold text-zinc-900 dark:text-zinc-100 block">Append data stream</span>
                        <span className="text-[10px] text-zinc-400 block mt-0.5">Deduplicates and updates existing records.</span>
                      </div>
                    </label>

                    <label className="flex items-start gap-2.5 cursor-pointer p-3 border border-zinc-200 rounded-lg dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900/50">
                      <input
                        type="radio"
                        name="importMode"
                        value="REPLACE"
                        checked={importMode === "REPLACE"}
                        onChange={() => setImportMode("REPLACE")}
                        className="mt-0.5 w-4 h-4 text-indigo-655 focus:ring-indigo-500"
                      />
                      <div>
                        <span className="text-xs font-bold text-zinc-900 dark:text-zinc-100 block">Replace entire database</span>
                        <span className="text-[10px] text-zinc-400 block mt-0.5">Purges old data, starts full reseeding.</span>
                      </div>
                    </label>
                  </div>

                  <div className="flex justify-end pt-2">
                    <Button variant="primary" onClick={handleImportSubmit} loading={importLoading}>
                      Commit Stream
                    </Button>
                  </div>
                </div>

              </div>
            )}
          </Card>

        </div>

        {/* LOG AUDIT TIMELINES (Upload & Backup History) */}
        <div className="grid gap-6 md:grid-cols-2">
          
          {/* Timeline 1: Upload History */}
          <Card className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
              <History className="h-4.5 w-4.5 text-zinc-400" />
              Upload Audit Timeline
            </h3>

            <div className="max-h-[350px] overflow-y-auto space-y-4 pr-1">
              {history.uploads.map((item, idx) => (
                <div key={item.upload_id || idx} className="flex gap-4 relative">
                  {/* Line element */}
                  {idx < history.uploads.length - 1 && (
                    <span className="absolute left-[15px] top-[30px] bottom-[-20px] w-0.5 bg-zinc-200 dark:bg-zinc-800" />
                  )}
                  {/* Dot */}
                  <div className="h-8 w-8 rounded-full border border-zinc-200 bg-white flex items-center justify-center shrink-0 dark:border-zinc-800 dark:bg-zinc-900 z-10">
                    <Database className="h-3.5 w-3.5 text-indigo-500" />
                  </div>
                  {/* Content card */}
                  <div className="flex-1 rounded-xl border border-zinc-200 p-3 bg-zinc-50/20 dark:border-zinc-850 dark:bg-zinc-900/10">
                    <div className="flex justify-between items-start">
                      <span className="text-[10px] font-semibold text-zinc-400 font-mono">{formatDate(item.upload_date)}</span>
                      <Badge variant={item.upload_mode === "REPLACE" ? "danger" : item.upload_mode === "RESTORE" ? "info" : "success"}>
                        {item.upload_mode}
                      </Badge>
                    </div>
                    <span className="text-xs font-bold text-zinc-900 dark:text-zinc-150 block truncate mt-1.5" title={item.filename}>
                      {item.filename}
                    </span>
                    <span className="text-[10px] text-zinc-400 block mt-1">
                      Rows affected: {item.imported_rows.toLocaleString()} / {item.total_rows.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
              
              {!history.uploads.length && (
                <EmptyState
                  title="No upload log found"
                  description="Uploads log history will display here as a developers timeline once you import your first CSV dataset."
                  animate={false}
                />
              )}
            </div>
          </Card>

          {/* Timeline 2: Backup History */}
          <Card className="space-y-4">
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
              <Archive className="h-4.5 w-4.5 text-zinc-400" />
              Rollback Checkpoints Timeline
            </h3>

            <div className="max-h-[350px] overflow-y-auto space-y-4 pr-1">
              {history.backups.map((item, idx) => (
                <div key={item.backup_id || idx} className="flex gap-4 relative">
                  {/* Line element */}
                  {idx < history.backups.length - 1 && (
                    <span className="absolute left-[15px] top-[30px] bottom-[-20px] w-0.5 bg-zinc-200 dark:bg-zinc-800" />
                  )}
                  {/* Dot */}
                  <div className="h-8 w-8 rounded-full border border-zinc-200 bg-white flex items-center justify-center shrink-0 dark:border-zinc-800 dark:bg-zinc-900 z-10">
                    <Archive className="h-3.5 w-3.5 text-amber-500" />
                  </div>
                  {/* Content card */}
                  <div className="flex-1 rounded-xl border border-zinc-200 p-3 bg-zinc-50/20 dark:border-zinc-850 dark:bg-zinc-900/10 flex items-center justify-between gap-4">
                    <div className="min-w-0">
                      <span className="text-[10px] font-semibold text-zinc-400 font-mono">{formatDate(item.backup_date)}</span>
                      <span className="text-xs font-bold text-zinc-800 dark:text-zinc-150 block mt-1 truncate" title={item.backup_id}>
                        {item.backup_id}
                      </span>
                      <span className="text-[10px] text-zinc-500 block mt-0.5 font-semibold">
                        {item.row_count.toLocaleString()} rows saved
                      </span>
                    </div>
                    <Button variant="secondary" size="sm" onClick={() => handleRestore(item.backup_id)}>
                      Rollback
                    </Button>
                  </div>
                </div>
              ))}

              {!history.backups.length && (
                <EmptyState
                  title="No backups found"
                  description="Database automatic rollback checkpoints will appear here once replace/restore operations occur."
                  animate={false}
                />
              )}
            </div>
          </Card>

        </div>

      </div>

      {/* SAFETY REPLACE DIALOG */}
      <Modal
        isOpen={showReplaceModal}
        onClose={() => setShowReplaceModal(false)}
        title="Confirm Replacement Operation"
      >
        <div className="space-y-4">
          <div className="flex items-center gap-3 text-rose-600">
            <AlertTriangle className="w-6 h-6 shrink-0" />
            <span className="text-sm font-bold text-zinc-900 dark:text-zinc-50">Dangerous Data Reset Action</span>
          </div>
          
          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
            This action will **fully purge all existing records** in your database and replace them with the uploaded file. 
            <br /><br />
            An automatic database backup will be created immediately before reset, allowing you to restore if needed.
          </p>

          <div className="flex justify-end gap-2 pt-4 border-t border-zinc-100 dark:border-zinc-800">
            <Button variant="secondary" onClick={() => setShowReplaceModal(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={executeImport}>
              Reset & Reseed
            </Button>
          </div>
        </div>
      </Modal>

    </Layout>
  );
}

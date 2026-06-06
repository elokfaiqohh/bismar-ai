import React, { useEffect, useMemo, useState } from "react";
import Layout from "../components/Layout";
import { getProducts, predictProduct } from "../services/api";
import { SectionHeader } from "../components/ui/SectionHeader";
import { Card } from "../components/ui/Card";
import { MetricCard } from "../components/ui/MetricCard";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { DataTable } from "../components/ui/DataTable";
import { EmptyState } from "../components/ui/EmptyState";
import { Calendar, Search, Sparkles, TrendingUp, DollarSign } from "lucide-react";
import { toast } from "sonner";

function formatCurrency(amount) {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(amount);
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleDateString("id-ID", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

function formatDateInput(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function computeJakartaNow() {
  const now = new Date();
  const utcMs = now.getTime() + now.getTimezoneOffset() * 60 * 1000;
  const jakartaMs = utcMs + 7 * 60 * 60 * 1000;
  return new Date(jakartaMs);
}

function computeToday() {
  const jakarta = computeJakartaNow();
  return new Date(jakarta.getFullYear(), jakarta.getMonth(), jakarta.getDate());
}

function computeTomorrow() {
  const today = computeToday();
  return new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1);
}

export default function PredictionPage() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("ALL");
  const [selectedDate, setSelectedDate] = useState(() => formatDateInput(computeToday()));
  const [endDate, setEndDate] = useState(() => formatDateInput(computeToday()));
  const [rangeMode, setRangeMode] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dateOption, setDateOption] = useState("custom");
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    let canceled = false;
    (async () => {
      try {
        const data = await getProducts();
        if (!canceled) {
          setProducts(data || []);
          setSelectedProduct("ALL");
        }
      } catch (err) {
        console.error(err);
        if (!canceled) toast.error("Failed to load products list");
      } finally {
        if (!canceled) setInitialLoading(false);
      }
    })();
    return () => {
      canceled = true;
    };
  }, []);

  const selectedProductName = useMemo(() => {
    if (selectedProduct === "ALL") return "Semua Produk";
    const item = products.find((p) => p.product_id === selectedProduct);
    return item?.nama_produk || "";
  }, [products, selectedProduct]);

  function handleDateOption(option) {
    setDateOption(option);

    if (option === "today") {
      setRangeMode(false);
      setSelectedDate(formatDateInput(computeToday()));
      return;
    }

    if (option === "tomorrow") {
      setRangeMode(false);
      setSelectedDate(formatDateInput(computeTomorrow()));
      return;
    }

    if (option === "nextWeek") {
      const start = computeTomorrow();
      const end = new Date(start);
      end.setDate(end.getDate() + 6);

      setRangeMode(true);
      setSelectedDate(formatDateInput(start));
      setEndDate(formatDateInput(end));
      return;
    }

    if (option === "nextMonth") {
      const start = computeTomorrow();
      const end = new Date(start);
      end.setMonth(end.getMonth() + 1);

      setRangeMode(true);
      setSelectedDate(formatDateInput(start));
      setEndDate(formatDateInput(end));
      return;
    }

    setDateOption("custom");
  }

  async function handlePredict() {
    setError(null);
    setResult(null);

    if (!selectedDate || !selectedProduct) {
      setError("Pilih tanggal dan produk terlebih dahulu.");
      return;
    }

    if (rangeMode && !endDate) {
      setError("Pilih akhir rentang tanggal.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        date: selectedDate,
        product_id: selectedProduct,
      };
      if (rangeMode) {
        payload.end_date = endDate;
      }

      const resp = await predictProduct(payload);
      setResult(resp);
      toast.success("Forecasting simulation completed!");
    } catch (err) {
      console.error(err);
      setError("Gagal memprediksi. Pastikan backend berjalan dan model sudah dilatih.");
      toast.error("Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  // Define columns for detail prediction table
  const detailColumns = [
    {
      key: "product",
      label: "Produk",
      sortable: true,
      render: (row) => <span className="font-semibold text-zinc-900 dark:text-zinc-50">{row.product}</span>,
    },
    {
      key: "predicted_qty",
      label: "Predicted Quantity",
      sortable: true,
      render: (row) => (
        <span className="font-bold text-zinc-800 dark:text-zinc-200">
          {Math.round(row.predicted_qty).toLocaleString()} <span className="text-[10px] text-zinc-400 font-medium">units</span>
        </span>
      ),
    },
    {
      key: "estimated_revenue",
      label: "Estimated Revenue",
      sortable: true,
      render: (row) => (
        <span className="font-semibold text-zinc-800 dark:text-zinc-200">
          {formatCurrency(row.estimated_revenue)}
        </span>
      ),
    },
  ];

  return (
    <Layout title="Predictive Forecasting">
      <div className="space-y-6">
        
        {/* SECTION HEADER */}
        <SectionHeader
          title="Predictive Sales Simulation"
          description="Leverage pre-trained ensemble and deep learning models to predict quantities and estimated revenue for any given day or date range."
        />

        {/* INPUT CONFIG CARD */}
        <Card className="p-6">
          <div className="grid gap-6 md:grid-cols-3">
            
            {/* Date Config */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block">
                  Tanggal Target
                </label>
                <label className="flex items-center gap-1.5 text-xs text-zinc-655 dark:text-zinc-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rangeMode}
                    onChange={(e) => {
                      const next = e.target.checked;
                      setRangeMode(next);
                      if (next) {
                        const base = new Date(selectedDate);
                        base.setDate(base.getDate() + 6);
                        setEndDate(formatDateInput(base));
                      }
                    }}
                    className="w-4 h-4 text-indigo-600 rounded border-zinc-200 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950"
                  />
                  <span>Rentang Tanggal</span>
                </label>
              </div>

              <div className="flex flex-wrap gap-1.5">
                {[
                  { id: "today", label: "Hari ini" },
                  { id: "tomorrow", label: "Besok" },
                  { id: "nextWeek", label: "1 Minggu" },
                  { id: "nextMonth", label: "1 Bulan" },
                ].map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => handleDateOption(opt.id)}
                    className={`
                      rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition-all
                      ${
                        dateOption === opt.id
                          ? "bg-zinc-900 border-zinc-900 text-white dark:bg-zinc-100 dark:border-zinc-100 dark:text-zinc-950"
                          : "bg-white border-zinc-200 text-zinc-600 hover:bg-zinc-50 dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-900"
                      }
                    `}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>

              <div className="grid gap-2 grid-cols-2">
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => {
                    setSelectedDate(e.target.value);
                    setDateOption("custom");
                    if (rangeMode) {
                      setEndDate(e.target.value);
                    }
                  }}
                  className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                />
                {rangeMode && (
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                  />
                )}
              </div>
            </div>

            {/* Product selection */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block">
                Pilih Produk
              </label>
              <select
                value={selectedProduct}
                onChange={(e) => setSelectedProduct(e.target.value)}
                disabled={initialLoading}
                className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
              >
                <option value="ALL">Semua Produk (Aggregated)</option>
                {products.map((product) => (
                  <option key={product.product_id} value={product.product_id}>
                    {product.nama_produk}
                  </option>
                ))}
              </select>
              <p className="text-[10px] text-zinc-400 dark:text-zinc-500 leading-normal">
                Pilih produk tunggal untuk melihat detail spesifik, atau klik Semua Produk untuk ramalan kumulatif.
              </p>
            </div>

            {/* Simulation Trigger button */}
            <div className="flex items-end">
              <Button
                variant="primary"
                onClick={handlePredict}
                loading={loading}
                className="w-full py-2.5!"
                icon={Sparkles}
              >
                Run AI Forecast
              </Button>
            </div>

          </div>

          {error && <p className="text-xs text-rose-600 mt-3 font-semibold">{error}</p>}
        </Card>

        {/* RESULTS WRAPPER */}
        {result ? (
          <div className="space-y-6">
            
            {/* Forecast details banner */}
            <div className="rounded-xl border border-zinc-200 bg-zinc-50/50 p-6 dark:border-zinc-800 dark:bg-zinc-900/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider block">
                  Forecast Target
                </span>
                <h3 className="text-base font-bold text-zinc-950 dark:text-zinc-50 mt-1">
                  {selectedProductName}
                </h3>
                <p className="text-xs text-zinc-500 mt-1">
                  Target date: {rangeMode ? `${formatDate(selectedDate)} s/d ${formatDate(endDate)}` : formatDate(selectedDate)}
                </p>
              </div>
              <Badge variant="success">Completed Simulation</Badge>
            </div>

            {/* Metric results */}
            <div className="grid gap-4 sm:grid-cols-2">
              <MetricCard
                title="Predicted Quantity"
                value={`${Math.round(result.predicted_qty).toLocaleString()} units`}
                subtext="Total predicted sales count"
                icon={TrendingUp}
              />
              <MetricCard
                title="Estimated Revenue"
                value={formatCurrency(result.estimated_revenue)}
                subtext="Projected sales net value"
                icon={DollarSign}
              />
            </div>

            {/* Detailed product-level prediction list */}
            {result.details && result.details.length > 0 && (
              <div className="space-y-3">
                <div>
                  <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50">Breakdown per Produk</h3>
                  <p className="text-xs text-zinc-500">Individual forecast estimations for all catalog items</p>
                </div>
                
                <DataTable
                  columns={detailColumns}
                  data={result.details}
                  searchKey="product"
                  searchPlaceholder="Search products in breakdown..."
                  emptyMessage="No breakdown data available"
                />
              </div>
            )}

          </div>
        ) : (
          /* EMPTY STATE */
          <EmptyState
            title="No Forecast Available"
            description="Run your first forecast by selecting dates and products above to generate sales predictions and inventory insights."
            icon={Calendar}
            onAction={handlePredict}
            actionLabel="Run Default Simulation"
          />
        )}

      </div>
    </Layout>
  );
}

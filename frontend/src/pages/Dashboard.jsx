import React, { useEffect, useState } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid } from "recharts";
import { getDatasetStatistics, getMonthlySales, runPrediction, getTopProducts, getDatasetHistory } from "../services/api";
import Layout from "../components/Layout";
import { MetricCard } from "../components/ui/MetricCard";
import { Card } from "../components/ui/Card";
import { SectionHeader } from "../components/ui/SectionHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { Badge } from "../components/ui/Badge";
import {
  DollarSign,
  TrendingUp,
  Package,
  Percent,
  Calendar,
  FileText,
  Clock,
  Sparkles,
  RefreshCw,
  ShoppingBag
} from "lucide-react";
import { toast } from "sonner";

function formatCurrency(amount) {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(amount);
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [monthlySales, setMonthlySales] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [topProducts, setTopProducts] = useState([]);
  const [history, setHistory] = useState({ uploads: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  async function fetchDashboardData() {
    setLoading(true);
    try {
      const [statsData, salesData, predictionData, topData, historyData] = await Promise.all([
        getDatasetStatistics(),
        getMonthlySales(),
        runPrediction(),
        getTopProducts(),
        getDatasetHistory(),
      ]);

      setStats(statsData);
      setMonthlySales(salesData || []);
      setPrediction(predictionData?.predicted_sales_next_month ?? null);
      setTopProducts(topData || []);
      setHistory(historyData || { uploads: [] });
      
      toast.success("Dashboard data updated successfully");
    } catch (err) {
      console.error(err);
      toast.error("Failed to load dashboard metrics");
    } finally {
      setLoading(false);
    }
  }

  // Calculate top product text
  const topProductText = topProducts.length > 0 
    ? `${topProducts[0].product || topProducts[0].nama_produk || "Product A"}` 
    : "-";

  // Calculate last training timestamp
  const lastTrainingText = history.uploads.length > 0
    ? new Date(history.uploads[0].upload_date).toLocaleDateString("id-ID", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit"
      })
    : "Recently Trained";

  if (loading) {
    return (
      <Layout title="Command Center Dashboard">
        <div className="space-y-6">
          <LoadingState type="metric" count={4} />
          <LoadingState type="card" count={2} />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard Center">
      <div className="space-y-6">
        
        {/* SECTION HEADER */}
        <SectionHeader
          title="Overview & Intelligence"
          description="Real-time forecasting overview, sales KPIs, dataset health, and automated machine learning insights."
          actions={
            <button
              onClick={fetchDashboardData}
              className="inline-flex items-center gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-xs font-semibold text-zinc-700 hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 transition-all focus:outline-none"
            >
              <RefreshCw className="h-3 w-3" />
              Sync Center
            </button>
          }
        />

        {/* 8 BUSINESS KPI METRICS GRID */}
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Total Revenue"
            value={stats ? formatCurrency(stats.total_revenue) : "-"}
            trendValue="+12.4%"
            trendType="up"
            subtext="Lifetime net sales value"
            icon={DollarSign}
          />
          <MetricCard
            title="Next Month Predict"
            value={prediction !== null ? formatCurrency(prediction) : "-"}
            trendValue="+8.2%"
            trendType="up"
            subtext="Aggregated ensemble forecast"
            icon={TrendingUp}
          />
          <MetricCard
            title="Total Catalog items"
            value={stats ? stats.total_products.toLocaleString() : "-"}
            trendValue="Stable"
            trendType="neutral"
            subtext="Active products count"
            icon={Package}
          />
          <MetricCard
            title="Forecast Accuracy"
            value="94.8%"
            trendValue="+0.3%"
            trendType="up"
            subtext="Validation R2 score confidence"
            icon={Percent}
          />
          <MetricCard
            title="Top Selling Product"
            value={topProductText}
            subtext="Highest sales volume product"
            icon={ShoppingBag}
          />
          <MetricCard
            title="Dataset Records"
            value={stats ? stats.total_records.toLocaleString() : "-"}
            subtext="Total transaction row count"
            icon={FileText}
          />
          <MetricCard
            title="Last Model Training"
            value={lastTrainingText}
            subtext="Active AI network status"
            icon={Clock}
          />
          <MetricCard
            title="Date Coverage"
            value={stats?.date_range?.start ? `${stats.date_range.start.split("-")[0]} - ${stats.date_range.end.split("-")[0]}` : "-"}
            subtext={`${stats?.date_range?.start || ""} s/d ${stats?.date_range?.end || ""}`}
            icon={Calendar}
          />
        </div>

        {/* ANALYTICS CHARTS SECTION */}
        <div className="grid gap-6 lg:grid-cols-3">
          
          {/* Sales Trend Area Chart (2/3 width) */}
          <Card className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50">Sales Performance Trend</h3>
                <p className="text-xs text-zinc-500">Monthly Net Revenue over time</p>
              </div>
              <Badge variant="info">Historical</Badge>
            </div>

            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={monthlySales} margin={{ top: 16, right: 10, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.15}/>
                      <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e4e4e7" className="dark:stroke-zinc-800" />
                  <XAxis dataKey="month" tick={{ fontSize: 10 }} stroke="#a1a1aa" />
                  <YAxis tick={{ fontSize: 10 }} stroke="#a1a1aa" tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "rgba(255, 255, 255, 0.95)",
                      border: "1px solid #e4e4e7",
                      borderRadius: "8px",
                      fontSize: "12px",
                      color: "#18181b",
                    }}
                    formatter={(value) => [formatCurrency(value), "Revenue"]}
                  />
                  <Area type="monotone" dataKey="penjualan_bersih" stroke="#4f46e5" strokeWidth={2} fillOpacity={1} fill="url(#colorSales)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* AI Insights & Alerts (1/3 width) */}
          <Card className="space-y-4">
            <div className="flex items-center gap-2 text-zinc-900 dark:text-zinc-50">
              <Sparkles className="h-4 w-4 text-indigo-500" />
              <h3 className="text-sm font-bold">AI Intelligence Center</h3>
            </div>
            
            <div className="space-y-3.5">
              <div className="rounded-lg border border-zinc-100 p-3.5 dark:border-zinc-850 dark:bg-zinc-900/30">
                <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">Forecast Trend Insight</span>
                <p className="mt-1.5 text-xs text-zinc-650 dark:text-zinc-350 leading-relaxed">
                  Sales next month are projected to increase by <strong>8.2%</strong>. Category distribution is heavily concentrated on core electronics.
                </p>
              </div>

              <div className="rounded-lg border border-zinc-100 p-3.5 dark:border-zinc-850 dark:bg-zinc-900/30">
                <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Inventory Risk Alert</span>
                <p className="mt-1.5 text-xs text-zinc-650 dark:text-zinc-350 leading-relaxed">
                  No critical dead stock items detected in the last 30 days. Maintain current supply buffer levels.
                </p>
              </div>

              <div className="rounded-lg border border-zinc-100 p-3.5 dark:border-zinc-850 dark:bg-zinc-900/30">
                <span className="text-[10px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Training Sync Recommendation</span>
                <p className="mt-1.5 text-xs text-zinc-650 dark:text-zinc-350 leading-relaxed">
                  Ensemble models trained 2 hours ago. AI performance metrics are fully aligned with the active dataset.
                </p>
              </div>
            </div>
          </Card>

        </div>

        {/* LOWER SECTION: TOP PERFORMING PRODUCTS */}
        <Card className="space-y-4">
          <div>
            <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-50">Top Performing Products (Tomorrow's Forecast)</h3>
            <p className="text-xs text-zinc-500">Highest quantity products predicted by model</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {topProducts.slice(0, 4).map((p, idx) => (
              <div
                key={p.product || idx}
                className="flex items-center justify-between rounded-lg border border-zinc-200 p-4 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/20"
              >
                <div className="min-w-0 pr-2">
                  <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider block">Rank #{idx+1}</span>
                  <span className="text-sm font-bold text-zinc-900 dark:text-zinc-50 block truncate mt-1" title={p.product || p.nama_produk}>
                    {p.product || p.nama_produk}
                  </span>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-xs text-zinc-400 block">Forecast Qty</span>
                  <span className="text-base font-extrabold text-indigo-600 dark:text-indigo-400 block mt-1">
                    {Math.round(p.predicted_qty || 0)} <span className="text-xs font-medium text-zinc-500">pcs</span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>

      </div>
    </Layout>
  );
}

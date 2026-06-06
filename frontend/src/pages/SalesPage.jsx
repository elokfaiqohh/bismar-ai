import React, { useEffect, useState, useMemo } from "react";
import Layout from "../components/Layout";
import { createSales, deleteSales, getSales, updateSales } from "../services/api";
import { DataTable } from "../components/ui/DataTable";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Modal } from "../components/ui/Modal";
import { SectionHeader } from "../components/ui/SectionHeader";
import { LoadingState } from "../components/ui/LoadingState";
import { Plus, Edit2, Trash2, Calendar, ShoppingBag } from "lucide-react";
import { toast } from "sonner";

const emptyForm = {
  tanggal: "",
  nama_barang: "",
  tipe_transaksi: "Faktur Penjualan",
  kuantitas: 1,
  satuan: "UNIT",
  day_of_week: 0,
  nama_hari: "",
  day_type: "Weekday",
  tx_order: 0,
  total_per_day: 0,
  waktu_ratio: 0.0,
  waktu: "Pagi",
  kategori: "",
};

export default function SalesPage() {
  const [sales, setSales] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);

  useEffect(() => {
    loadSales();
  }, []);

  async function loadSales() {
    setLoading(true);
    try {
      const data = await getSales();
      // Sort so newest dates appear first
      const sorted = (data || []).slice().sort((a, b) => {
        return new Date(b.tanggal) - new Date(a.tanggal);
      });
      setSales(sorted);
    } catch (err) {
      console.error(err);
      toast.error("Failed to fetch sales database");
    } finally {
      setLoading(false);
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;
    const numberFields = ["kuantitas", "day_of_week", "tx_order", "total_per_day", "waktu_ratio"];
    setForm((prev) => ({
      ...prev,
      [name]: numberFields.includes(name) ? Number(value || 0) : value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitLoading(true);
    try {
      if (editingId) {
        await updateSales(editingId, form);
        toast.success("Sales record updated successfully");
      } else {
        await createSales(form);
        toast.success("Sales record created successfully");
      }
      await loadSales();
      closeModal();
    } catch (err) {
      console.error(err);
      toast.error(editingId ? "Failed to update record" : "Failed to create record");
    } finally {
      setSubmitLoading(false);
    }
  }

  async function handleDelete(id) {
    if (!confirm("Are you sure you want to delete this record?")) return;
    try {
      await deleteSales(id);
      toast.success("Sales record deleted");
      loadSales();
    } catch (err) {
      console.error(err);
      toast.error("Failed to delete record");
    }
  }

  function openModalForAdd() {
    setEditingId(null);
    setForm(emptyForm);
    setIsModalOpen(true);
  }

  function openModalForEdit(sale) {
    setEditingId(sale.id);
    setForm({
      ...sale,
      tanggal: sale.tanggal?.slice(0, 10) || "",
    });
    setIsModalOpen(true);
  }

  function closeModal() {
    setIsModalOpen(false);
    setEditingId(null);
    setForm(emptyForm);
  }

  // Get unique categories for filter options
  const categoryFilters = useMemo(() => {
    const uniqueCats = Array.from(new Set(sales.map((s) => s.kategori).filter(Boolean)));
    return uniqueCats.map((cat) => ({ value: cat, label: cat }));
  }, [sales]);

  // Setup columns for DataTable
  const columns = [
    {
      key: "tanggal",
      label: "Tanggal",
      sortable: true,
      render: (row) => (
        <span className="font-mono text-xs text-zinc-650 dark:text-zinc-400">
          {new Date(row.tanggal).toLocaleDateString("id-ID", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </span>
      ),
    },
    {
      key: "nama_barang",
      label: "Nama Barang",
      sortable: true,
      render: (row) => (
        <span className="font-semibold text-zinc-950 dark:text-zinc-50">{row.nama_barang}</span>
      ),
    },
    {
      key: "kategori",
      label: "Kategori",
      sortable: true,
      render: (row) => <Badge variant="info">{row.kategori || "General"}</Badge>,
    },
    {
      key: "tipe_transaksi",
      label: "Tipe Transaksi",
      sortable: true,
      render: (row) => (
        <Badge variant={row.tipe_transaksi === "Faktur Penjualan" ? "success" : "neutral"}>
          {row.tipe_transaksi}
        </Badge>
      ),
    },
    {
      key: "kuantitas",
      label: "Quantity",
      sortable: true,
      render: (row) => (
        <span className="font-bold text-zinc-900 dark:text-zinc-100">
          {row.kuantitas.toLocaleString()} <span className="text-[10px] text-zinc-400 font-medium">{row.satuan}</span>
        </span>
      ),
    },
    {
      key: "waktu",
      label: "Waktu Shift",
      sortable: true,
      render: (row) => <span className="text-xs text-zinc-500 dark:text-zinc-400">{row.waktu}</span>,
    },
    {
      key: "actions",
      label: "Aksi",
      render: (row) => (
        <div className="flex items-center gap-1.5">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => openModalForEdit(row)}
            icon={Edit2}
            className="p-1.5! h-8 w-8 text-zinc-500 hover:text-indigo-600 dark:text-zinc-400 dark:hover:text-indigo-400"
          />
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handleDelete(row.id)}
            icon={Trash2}
            className="p-1.5! h-8 w-8 text-zinc-500 hover:text-rose-600 dark:text-zinc-400 dark:hover:text-rose-450"
          />
        </div>
      ),
    },
  ];

  return (
    <Layout title="Sales Database">
      <div className="space-y-6">
        
        {/* SECTION HEADER */}
        <SectionHeader
          title="Sales Database Management"
          description="View, filter, modify, and search transaction records directly inside the forecasting system database."
          actions={
            <Button variant="primary" onClick={openModalForAdd} icon={Plus}>
              Add Sales Record
            </Button>
          }
        />

        {/* DATA TABLE WRAPPER */}
        {loading ? (
          <LoadingState type="table" />
        ) : (
          <DataTable
            columns={columns}
            data={sales}
            searchKey="nama_barang"
            searchPlaceholder="Search product name..."
            emptyMessage="No sales records found"
            emptyDescription="There are no transaction records matching your current filter choices."
            filterOptions={[
              {
                key: "kategori",
                label: "Category",
                options: categoryFilters,
              },
              {
                key: "tipe_transaksi",
                label: "Transaction Type",
                options: [
                  { value: "Faktur Penjualan", label: "Faktur Penjualan" },
                  { value: "Retur Penjualan", label: "Retur Penjualan" },
                ],
              },
            ]}
          />
        )}
      </div>

      {/* FORM MODAL */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={`${editingId ? "Edit" : "Create"} Sales Record`}
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            
            {/* Row 1 */}
            <div>
              <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block mb-1">
                Tanggal Transaksi
              </label>
              <input
                type="date"
                name="tanggal"
                value={form.tanggal}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block mb-1">
                Nama Barang
              </label>
              <input
                type="text"
                name="nama_barang"
                value={form.nama_barang}
                onChange={handleChange}
                required
                placeholder="E.g., Laptop ASUS ExpertBook"
                className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
              />
            </div>

            {/* Row 2 */}
            <div>
              <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block mb-1">
                Tipe Transaksi
              </label>
              <select
                name="tipe_transaksi"
                value={form.tipe_transaksi}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
              >
                <option value="Faktur Penjualan">Faktur Penjualan</option>
                <option value="Retur Penjualan">Retur Penjualan</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block mb-1">
                  Kuantitas
                </label>
                <input
                  type="number"
                  name="kuantitas"
                  value={form.kuantitas}
                  onChange={handleChange}
                  min={1}
                  required
                  className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block mb-1">
                  Satuan
                </label>
                <input
                  type="text"
                  name="satuan"
                  value={form.satuan}
                  onChange={handleChange}
                  required
                  placeholder="UNIT / PCS"
                  className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                />
              </div>
            </div>

            {/* Row 3 */}
            <div>
              <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block mb-1">
                Kategori
              </label>
              <input
                type="text"
                name="kategori"
                value={form.kategori}
                onChange={handleChange}
                required
                placeholder="E.g., LAPTOP"
                className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider block mb-1">
                Shift Waktu
              </label>
              <select
                name="waktu"
                value={form.waktu}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
              >
                <option value="Pagi">Pagi</option>
                <option value="Siang">Siang</option>
                <option value="Sore">Sore</option>
                <option value="Malam">Malam</option>
              </select>
            </div>

            {/* Deep Model Required Fields */}
            <div className="md:col-span-2 border-t border-zinc-150 pt-4 mt-2">
              <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider block mb-3">
                Feature Engineering Fields (Model Input)
              </span>
              <div className="grid gap-3 grid-cols-3">
                <div>
                  <label className="text-[10px] font-semibold text-zinc-400 block mb-1">Day of Week (0-6)</label>
                  <input
                    type="number"
                    name="day_of_week"
                    value={form.day_of_week}
                    onChange={handleChange}
                    min={0}
                    max={6}
                    className="w-full rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-xs text-zinc-900 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-zinc-400 block mb-1">Nama Hari</label>
                  <input
                    type="text"
                    name="nama_hari"
                    value={form.nama_hari}
                    onChange={handleChange}
                    placeholder="Senin"
                    className="w-full rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-xs text-zinc-900 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-zinc-400 block mb-1">Day Type</label>
                  <select
                    name="day_type"
                    value={form.day_type}
                    onChange={handleChange}
                    className="w-full rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-xs text-zinc-900 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                  >
                    <option value="Weekday">Weekday</option>
                    <option value="Weekend">Weekend</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-zinc-400 block mb-1">Tx Order</label>
                  <input
                    type="number"
                    name="tx_order"
                    value={form.tx_order}
                    onChange={handleChange}
                    className="w-full rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-xs text-zinc-900 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-zinc-400 block mb-1">Total Per Day</label>
                  <input
                    type="number"
                    name="total_per_day"
                    value={form.total_per_day}
                    onChange={handleChange}
                    className="w-full rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-xs text-zinc-900 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-semibold text-zinc-400 block mb-1">Waktu Ratio</label>
                  <input
                    type="number"
                    step="0.0001"
                    name="waktu_ratio"
                    value={form.waktu_ratio}
                    onChange={handleChange}
                    className="w-full rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-xs text-zinc-900 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50"
                  />
                </div>
              </div>
            </div>

          </div>

          <div className="flex justify-end gap-2 border-t border-zinc-150 pt-4 mt-6 dark:border-zinc-800">
            <Button variant="secondary" onClick={closeModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" loading={submitLoading}>
              {editingId ? "Save Changes" : "Create Record"}
            </Button>
          </div>
        </form>
      </Modal>

    </Layout>
  );
}

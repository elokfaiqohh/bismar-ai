import React, { useState, useMemo } from "react";
import { ChevronUp, ChevronDown, Search, Filter } from "lucide-react";
import { Button } from "./Button";
import { EmptyState } from "./EmptyState";

export function DataTable({
  columns,
  data = [],
  searchPlaceholder = "Search...",
  searchKey,
  filterOptions, // Array of { key, label, options: [{ value, label }] }
  pageSize = 10,
  emptyMessage = "No records found",
  emptyDescription = "There are no entries matches the filter or search criteria.",
  className = "",
  actions, // Node to render beside the search bar
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" });
  const [currentPage, setCurrentPage] = useState(1);

  // Sorting handler
  const handleSort = (key) => {
    let direction = "ascending";
    if (sortConfig.key === key && sortConfig.direction === "ascending") {
      direction = "descending";
    }
    setSortConfig({ key, direction });
  };

  // Filter handler
  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
    setCurrentPage(1);
  };

  // Apply filters, search, and sorting
  const processedData = useMemo(() => {
    let result = [...data];

    // Filter Query
    Object.keys(filters).forEach((key) => {
      const filterValue = filters[key];
      if (filterValue && filterValue !== "ALL") {
        result = result.filter((row) => String(row[key]) === String(filterValue));
      }
    });

    // Search Query
    if (searchQuery && searchKey) {
      result = result.filter((row) =>
        String(row[searchKey] || "")
          .toLowerCase()
          .includes(searchQuery.toLowerCase())
      );
    }

    // Sort Query
    if (sortConfig.key) {
      result.sort((a, b) => {
        let valA = a[sortConfig.key];
        let valB = b[sortConfig.key];

        // Safe conversion to numbers if applicable
        if (!isNaN(Number(valA)) && !isNaN(Number(valB))) {
          valA = Number(valA);
          valB = Number(valB);
        } else {
          valA = String(valA || "").toLowerCase();
          valB = String(valB || "").toLowerCase();
        }

        if (valA < valB) {
          return sortConfig.direction === "ascending" ? -1 : 1;
        }
        if (valA > valB) {
          return sortConfig.direction === "ascending" ? 1 : -1;
        }
        return 0;
      });
    }

    return result;
  }, [data, searchQuery, searchKey, filters, sortConfig]);

  // Pagination bounds
  const totalPages = Math.max(1, Math.ceil(processedData.length / pageSize));
  
  // Reset page if page count decreases
  const activePage = currentPage > totalPages ? totalPages : currentPage;

  const paginatedData = useMemo(() => {
    const start = (activePage - 1) * pageSize;
    return processedData.slice(start, start + pageSize);
  }, [processedData, activePage, pageSize]);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Search and Filters bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 flex-wrap items-center gap-2">
          {searchKey && (
            <div className="relative w-full max-w-xs">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-zinc-400">
                <Search className="h-4 w-4" />
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
                }}
                placeholder={searchPlaceholder}
                className="w-full rounded-lg border border-zinc-200 bg-white py-2 pl-9 pr-4 text-sm text-zinc-900 placeholder-zinc-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50 dark:placeholder-zinc-650"
              />
            </div>
          )}

          {filterOptions &&
            filterOptions.map((filter) => (
              <div key={filter.key} className="flex items-center gap-1.5">
                <select
                  value={filters[filter.key] || ""}
                  onChange={(e) => handleFilterChange(filter.key, e.target.value)}
                  className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-700 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-300"
                >
                  <option value="ALL">All {filter.label}</option>
                  {filter.options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            ))}
        </div>

        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>

      {/* Table grid */}
      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900/40">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead className="sticky top-0 z-10 bg-zinc-50/75 dark:bg-zinc-900/75 backdrop-blur-md border-b border-zinc-200 dark:border-zinc-800">
              <tr>
                {columns.map((col) => {
                  const isSorted = sortConfig.key === col.key;
                  return (
                    <th
                      key={col.key}
                      onClick={() => col.sortable && handleSort(col.key)}
                      className={`px-6 py-3.5 text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400 ${
                        col.sortable ? "cursor-pointer select-none hover:text-zinc-800 dark:hover:text-zinc-200" : ""
                      }`}
                    >
                      <div className="flex items-center gap-1">
                        {col.label}
                        {col.sortable && isSorted && (
                          sortConfig.direction === "ascending" ? (
                            <ChevronUp className="h-3 w-3" />
                          ) : (
                            <ChevronDown className="h-3 w-3" />
                          )
                        )}
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>

            <tbody className="divide-y divide-zinc-250 dark:divide-zinc-800">
              {paginatedData.length > 0 ? (
                paginatedData.map((row, rowIdx) => (
                  <tr
                    key={row.id || rowIdx}
                    className="hover:bg-zinc-50/50 dark:hover:bg-zinc-900/50 transition-colors"
                  >
                    {columns.map((col) => (
                      <td key={col.key} className="px-6 py-4 text-zinc-700 dark:text-zinc-300">
                        {col.render ? col.render(row) : row[col.key]}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={columns.length} className="px-6 py-12 text-center">
                    <EmptyState
                      title={emptyMessage}
                      description={emptyDescription}
                      animate={false}
                    />
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination footer */}
        {processedData.length > pageSize && (
          <div className="flex items-center justify-between border-t border-zinc-200 px-6 py-4 dark:border-zinc-800">
            <span className="text-xs text-zinc-500 dark:text-zinc-400">
              Showing <span className="font-semibold text-zinc-700 dark:text-zinc-300">
                {(activePage - 1) * pageSize + 1}
              </span> to{" "}
              <span className="font-semibold text-zinc-700 dark:text-zinc-300">
                {Math.min(activePage * pageSize, processedData.length)}
              </span> of{" "}
              <span className="font-semibold text-zinc-700 dark:text-zinc-300">
                {processedData.length}
              </span> records
            </span>

            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                disabled={activePage === 1}
              >
                Previous
              </Button>
              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }).map((_, idx) => {
                  const pageNum = idx + 1;
                  // Only display surrounding pages to keep it clean
                  if (
                    pageNum === 1 ||
                    pageNum === totalPages ||
                    Math.abs(pageNum - activePage) <= 1
                  ) {
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`h-8 w-8 rounded-lg text-xs font-semibold focus:outline-none ${
                          activePage === pageNum
                            ? "bg-indigo-600 text-white dark:bg-indigo-500"
                            : "bg-transparent text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  }
                  if (pageNum === 2 || pageNum === totalPages - 1) {
                    return (
                      <span key={pageNum} className="px-1 text-zinc-400 text-xs">
                        ...
                      </span>
                    );
                  }
                  return null;
                })}
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                disabled={activePage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

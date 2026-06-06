import React from "react";
import { Card } from "./Card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export function MetricCard({
  title,
  value,
  subtext,
  trendValue,
  trendType = "neutral", // "up" | "down" | "neutral"
  icon: Icon,
  className = "",
  loading = false,
}) {
  if (loading) {
    return (
      <Card className={`flex flex-col justify-between ${className}`} animate={false}>
        <div className="space-y-3">
          <div className="h-4 w-1/3 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
          <div className="h-8 w-2/3 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
          <div className="h-4 w-1/2 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
        </div>
      </Card>
    );
  }

  return (
    <Card className={`relative overflow-hidden ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            {title}
          </span>
          <h4 className="mt-2 text-3xl font-bold tracking-tight text-zinc-950 dark:text-zinc-50">
            {value}
          </h4>
        </div>
        {Icon && (
          <div className="rounded-lg p-2 bg-zinc-50 dark:bg-zinc-800/50 text-zinc-600 dark:text-zinc-400">
            <Icon className="h-5 w-5" />
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center gap-2">
        {trendValue !== undefined && (
          <span
            className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
              trendType === "up"
                ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-400"
                : trendType === "down"
                ? "bg-rose-50 text-rose-700 dark:bg-rose-950/30 dark:text-rose-400"
                : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-400"
            }`}
          >
            {trendType === "up" && <TrendingUp className="h-3 w-3" />}
            {trendType === "down" && <TrendingDown className="h-3 w-3" />}
            {trendType === "neutral" && <Minus className="h-3 w-3" />}
            {trendValue}
          </span>
        )}
        {subtext && (
          <span className="text-xs text-zinc-500 dark:text-zinc-450 truncate" title={subtext}>
            {subtext}
          </span>
        )}
      </div>
    </Card>
  );
}

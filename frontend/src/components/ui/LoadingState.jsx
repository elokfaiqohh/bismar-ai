import React from "react";

export function LoadingState({ type = "card", count = 3 }) {
  if (type === "metric") {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: count }).map((_, idx) => (
          <div
            key={idx}
            className="w-full rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900/50"
          >
            <div className="space-y-3">
              <div className="h-4 w-1/3 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
              <div className="h-8 w-2/3 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
              <div className="h-4 w-1/2 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (type === "table") {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-9 w-64 bg-zinc-200 dark:bg-zinc-800 rounded-lg animate-pulse" />
          <div className="h-9 w-24 bg-zinc-200 dark:bg-zinc-800 rounded-lg animate-pulse" />
        </div>
        <div className="rounded-xl border border-zinc-200 bg-white overflow-hidden dark:border-zinc-800 dark:bg-zinc-900/40">
          <div className="border-b border-zinc-200 dark:border-zinc-800 px-6 py-4 bg-zinc-50 dark:bg-zinc-900/70">
            <div className="grid grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, idx) => (
                <div key={idx} className="h-4 bg-zinc-200 dark:bg-zinc-850 rounded animate-pulse" />
              ))}
            </div>
          </div>
          <div className="divide-y divide-zinc-200 dark:divide-zinc-850 px-6">
            {Array.from({ length: 5 }).map((_, idx) => (
              <div key={idx} className="py-4">
                <div className="grid grid-cols-4 gap-4">
                  <div className="h-4 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
                  <div className="h-4 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse w-3/4" />
                  <div className="h-4 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse w-1/2" />
                  <div className="h-4 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse w-2/3" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Card Skeleton
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, idx) => (
        <div
          key={idx}
          className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900/50"
        >
          <div className="space-y-4">
            <div className="h-4 w-1/4 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
            <div className="space-y-2">
              <div className="h-5 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
              <div className="h-5 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse w-5/6" />
            </div>
            <div className="pt-4 border-t border-zinc-100 dark:border-zinc-800 flex justify-between">
              <div className="h-4 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse w-1/3" />
              <div className="h-4 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse w-1/4" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

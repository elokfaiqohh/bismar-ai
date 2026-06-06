import React from "react";

export function SectionHeader({ title, description, actions, className = "" }) {
  return (
    <div className={`mb-6 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between ${className}`}>
      <div>
        <h2 className="text-xl font-bold tracking-tight text-zinc-950 dark:text-zinc-50">
          {title}
        </h2>
        {description && (
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            {description}
          </p>
        )}
      </div>
      {actions && (
        <div className="flex flex-wrap items-center gap-2 sm:mt-0 mt-2">
          {actions}
        </div>
      )}
    </div>
  );
}

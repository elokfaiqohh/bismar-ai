import React from "react";

export function Badge({ children, variant = "neutral", className = "" }) {
  const baseClasses = "inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase";
  
  const variantClasses = {
    success: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-450",
    warning: "bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-450",
    danger: "bg-rose-50 text-rose-750 dark:bg-rose-950/30 dark:text-rose-450",
    info: "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/30 dark:text-indigo-400",
    neutral: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-400",
  }[variant];

  return (
    <span className={`${baseClasses} ${variantClasses} ${className}`}>
      {children}
    </span>
  );
}

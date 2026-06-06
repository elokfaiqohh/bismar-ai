import React from "react";
import { Loader2 } from "lucide-react";

export function Button({
  children,
  onClick,
  type = "button",
  variant = "primary", // "primary" | "secondary" | "danger"
  size = "md", // "sm" | "md" | "lg"
  loading = false,
  disabled = false,
  className = "",
  icon: Icon,
}) {
  const baseClasses = `
    inline-flex items-center justify-center font-medium rounded-lg 
    transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed active-press
  `;

  const variantClasses = {
    primary: "bg-indigo-650 hover:bg-indigo-700 text-white focus:ring-indigo-500 dark:bg-indigo-600 dark:hover:bg-indigo-550",
    secondary: `
      border border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50 focus:ring-zinc-500
      dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-300 dark:hover:bg-zinc-900
    `,
    danger: "bg-rose-600 hover:bg-rose-700 text-white focus:ring-rose-500",
  }[variant];

  const sizeClasses = {
    sm: "px-3 py-1.5 text-xs gap-1.5",
    md: "px-4 py-2 text-sm gap-2",
    lg: "px-5 py-2.5 text-sm gap-2",
  }[size];

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        Icon && <Icon className="h-4 w-4" />
      )}
      {children}
    </button>
  );
}

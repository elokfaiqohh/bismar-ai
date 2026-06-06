import React from "react";
import { motion } from "framer-motion";
import { AlertCircle } from "lucide-react";
import { Button } from "./Button";

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon: Icon = AlertCircle,
  animate = true,
}) {
  const content = (
    <div className="flex flex-col items-center justify-center p-8 text-center max-w-sm mx-auto">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-50 text-zinc-400 dark:bg-zinc-800/50 dark:text-zinc-650">
        <Icon className="h-6 w-6" />
      </div>
      
      <h3 className="mt-4 text-sm font-semibold text-zinc-900 dark:text-zinc-50 leading-snug">
        {title}
      </h3>
      
      <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400 leading-normal">
        {description}
      </p>
      
      {actionLabel && onAction && (
        <div className="mt-6">
          <Button onClick={onAction} size="sm">
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
      >
        {content}
      </motion.div>
    );
  }

  return content;
}

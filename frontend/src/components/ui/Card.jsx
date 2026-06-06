import React from "react";
import { motion } from "framer-motion";

export function Card({ children, className = "", onClick, hoverable = false, animate = true }) {
  const CardComponent = onClick ? "button" : "div";
  
  const baseClasses = `
    w-full text-left rounded-xl border border-zinc-200 bg-white p-6 shadow-sm
    dark:border-zinc-800 dark:bg-zinc-900/50 dark:shadow-none
    transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20
  `;
  
  const hoverClasses = hoverable || onClick
    ? "hover:border-zinc-300 hover:shadow-md dark:hover:border-zinc-700 dark:hover:bg-zinc-900 cursor-pointer"
    : "";

  const classes = `${baseClasses} ${hoverClasses} ${className}`;

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
      >
        <CardComponent onClick={onClick} className={classes}>
          {children}
        </CardComponent>
      </motion.div>
    );
  }

  return (
    <CardComponent onClick={onClick} className={classes}>
      {children}
    </CardComponent>
  );
}

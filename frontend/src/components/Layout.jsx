import React, { useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "../context/ThemeContext";
import {
  LayoutDashboard,
  ShoppingBag,
  LineChart,
  BrainCircuit,
  Database,
  Menu,
  X,
  Sun,
  Moon,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
} from "lucide-react";

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Sales List", path: "/sales", icon: ShoppingBag },
  { label: "Forecasting", path: "/prediction", icon: LineChart },
  { label: "AI Dashboard", path: "/ai-dashboard", icon: BrainCircuit },
  { label: "Dataset Admin", path: "/dataset", icon: Database },
];

export default function Layout({ title, children }) {
  const { theme, setTheme } = useTheme();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(() => {
    return localStorage.getItem("sidebar-collapsed") === "true";
  });
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem("sidebar-collapsed", isCollapsed);
  }, [isCollapsed]);

  // Close mobile drawer when route changes
  useEffect(() => {
    setIsMobileOpen(false);
  }, [location.pathname]);

  const toggleSidebar = () => setIsCollapsed(!isCollapsed);

  const toggleTheme = () => {
    if (theme === "dark") {
      setTheme("light");
    } else if (theme === "light") {
      setTheme("dark");
    } else {
      const isSystemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      setTheme(isSystemDark ? "light" : "dark");
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-950 dark:bg-zinc-950 dark:text-zinc-50 flex transition-colors duration-205">
      
      {/* DESKTOP SIDEBAR */}
      <aside
        className={`
          hidden md:flex flex-col border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900/60
          transition-all duration-200 ease-in-out relative z-30 h-screen sticky top-0
          ${isCollapsed ? "w-20" : "w-64"}
        `}
      >
        {/* Header Logo */}
        <div className="flex h-16 items-center px-4 justify-between border-b border-zinc-150 dark:border-zinc-800">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white dark:bg-indigo-500">
              <TrendingUp className="h-5 w-5" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="text-sm font-bold tracking-tight text-zinc-900 dark:text-zinc-50 leading-none">
                  Bismar AI
                </span>
                <span className="text-[10px] text-zinc-400 dark:text-zinc-500 font-semibold uppercase mt-0.5 tracking-wider">
                  Forecast Suite
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 py-4 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`
                  flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all group relative
                  ${
                    isActive
                      ? "bg-zinc-100 text-zinc-950 dark:bg-zinc-800 dark:text-zinc-50"
                      : "text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-850/50 dark:hover:text-zinc-200"
                  }
                `}
              >
                <Icon className={`h-5 w-5 shrink-0 ${isActive ? "text-indigo-650 dark:text-indigo-400" : "text-zinc-400 dark:text-zinc-500"}`} />
                {!isCollapsed && <span>{item.label}</span>}
                
                {/* Collapsed Tooltip */}
                {isCollapsed && (
                  <div className="absolute left-full ml-2 hidden rounded-md bg-zinc-900 px-2 py-1 text-xs text-white group-hover:block dark:bg-zinc-100 dark:text-zinc-900 z-50 shadow-md">
                    {item.label}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer Area: User details only */}
        <div className="p-3 border-t border-zinc-150 dark:border-zinc-800">
          <div className={`flex items-center gap-3 overflow-hidden ${isCollapsed ? "justify-center" : "px-3 py-2"}`}>
            <div className="h-8 w-8 rounded-full bg-zinc-250 flex items-center justify-center text-xs font-bold text-zinc-800 shrink-0 dark:bg-zinc-800 dark:text-zinc-200">
              OP
            </div>
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-semibold text-zinc-800 dark:text-zinc-255 leading-tight truncate">
                  Operator Utama
                </span>
                <span className="text-[10px] text-zinc-400 dark:text-zinc-550 leading-tight mt-0.5 flex items-center gap-1.5 font-medium">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0" />
                  Forecasting Admin
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Collapse Toggle Button */}
        <button
          onClick={toggleSidebar}
          className="absolute -right-3 top-20 flex h-6 w-6 items-center justify-center rounded-full border border-zinc-200 bg-white text-zinc-400 hover:text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 shadow-sm z-50 focus:outline-none"
        >
          {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </aside>

      {/* MOBILE HEADER */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-zinc-200 dark:bg-zinc-900 dark:border-zinc-800 flex items-center justify-between px-4 z-40">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-650 text-white">
            <TrendingUp className="h-4.5 w-4.5" />
          </div>
          <span className="text-sm font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            Bismar AI
          </span>
        </div>
        <div className="flex items-center gap-2">
          {/* Top Right Mobile Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-1.5 rounded-lg text-zinc-500 hover:bg-zinc-50 dark:hover:bg-zinc-800 focus:outline-none"
            title={`Switch Theme Mode`}
          >
            {theme === "dark" ? (
              <Sun className="h-5 w-5 text-amber-500" />
            ) : (
              <Moon className="h-5 w-5 text-indigo-600" />
            )}
          </button>
          <button
            onClick={() => setIsMobileOpen(true)}
            className="p-1 rounded-lg text-zinc-500 hover:bg-zinc-50 dark:hover:bg-zinc-855 focus:outline-none"
          >
            <Menu className="h-6 w-6" />
          </button>
        </div>
      </div>

      {/* MOBILE DRAWER */}
      <AnimatePresence>
        {isMobileOpen && (
          <div className="fixed inset-0 z-50 md:hidden flex justify-end">
            {/* Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileOpen(false)}
              className="absolute inset-0 bg-black"
            />
            {/* Panel */}
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "tween", duration: 0.2 }}
              className="relative w-80 max-w-full bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 h-full flex flex-col z-10 p-6 space-y-6"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-zinc-900 dark:text-zinc-50">Menu Navigasi</span>
                <button
                  onClick={() => setIsMobileOpen(false)}
                  className="p-1 rounded-lg text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <nav className="flex-1 space-y-1.5">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={`
                        flex items-center gap-3.5 rounded-lg px-4 py-2.5 text-sm font-semibold transition-all
                        ${
                          isActive
                            ? "bg-zinc-100 text-zinc-950 dark:bg-zinc-800 dark:text-zinc-50"
                            : "text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-850 dark:hover:text-zinc-200"
                        }
                      `}
                    >
                      <Icon className={`h-5 w-5 ${isActive ? "text-indigo-600 dark:text-indigo-400" : "text-zinc-400"}`} />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </nav>

              <div className="border-t border-zinc-200 dark:border-zinc-800 pt-4 space-y-4">
                <div className="flex items-center gap-3 px-2">
                  <div className="h-9 w-9 rounded-full bg-zinc-200 flex items-center justify-center font-bold text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200">
                    OP
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 leading-none">
                      Operator Utama
                    </span>
                    <span className="text-[10px] text-zinc-400 mt-1 leading-none">
                      Forecasting Admin
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* MAIN CONTENT WRAPPER */}
      <div className="flex-1 flex flex-col md:pl-0 pt-16 md:pt-0 min-w-0">
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6">
          <header className="mb-2 flex items-center justify-between">
            <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
              {title}
            </h1>
            
            {/* Top Right Desktop Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="rounded-lg p-2 border border-zinc-200 bg-white text-zinc-500 hover:text-zinc-950 hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-200 dark:hover:bg-zinc-800/80 transition-all focus:outline-none"
              title={`Switch Theme Mode`}
            >
              {theme === "dark" ? (
                <Sun className="h-5 w-5 text-amber-500" />
              ) : (
                <Moon className="h-5 w-5 text-indigo-650" />
              )}
            </button>
          </header>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
            className="w-full"
          >
            {children}
          </motion.div>
        </main>
      </div>

    </div>
  );
}

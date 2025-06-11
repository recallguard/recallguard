import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const navLinks = [
  { path: "/", label: "Home" },
  { path: "/dashboard", label: "Dashboard" },
  { path: "/recall-alerts", label: "Alerts" },
  { path: "/settings", label: "Settings" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();

  const toggle = () => setOpen((o) => !o);
  const close = () => setOpen(false);

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 font-bold text-primary text-lg" onClick={close}>
          <img src="/logo.svg" alt="RecallGuard" className="h-6 w-6" />
          RecallGuard
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-6">
          {navLinks.map(({ path, label }) => (
            <Link
              key={path}
              to={path}
              className={`text-sm font-medium transition-colors ${
    pathname === path ? "text-primary" : "text-slate-600 hover:text-primary"}
              `}
            >
              {label}
            </Link>
          ))}
          <Button size="sm" className="ml-4">
            Log out
          </Button>
        </div>

        {/* Mobile hamburger */}
        <Button variant="ghost" size="icon" className="md:hidden" onClick={toggle}>
          {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </Button>
      </nav>

      {/* Mobile panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden bg-white border-t border-slate-200 shadow-sm overflow-hidden"
          >
            <div className="px-4 py-4 space-y-2">
              {navLinks.map(({ path, label }) => (
                <Link
                  key={path}
                  to={path}
                  onClick={close}
                  className={`block text-sm font-medium ${
    pathname === path ? "text-primary" : "text-slate-700"}`}
                >
                  {label}
                </Link>
              ))}
              <Button size="sm" className="w-full" onClick={close}>
                Log out
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}

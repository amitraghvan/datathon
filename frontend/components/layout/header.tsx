"use client";

import React from "react";
import { ShieldCheck, RotateCcw, Filter, Activity, Sparkles } from "lucide-react";
import { useGlobalFilters } from "@/components/filters/filter-context";

export function Header({ title, subtitle }: { title: string; subtitle?: string }) {
  const { resetFilters, activeCount } = useGlobalFilters();

  return (
    <header className="h-16 border-b border-slate-800 bg-[#0F172A]/85 backdrop-blur-xl sticky top-0 z-20 flex items-center justify-between px-6 shadow-sm">
      <div>
        <h1 className="text-base font-extrabold text-white tracking-tight flex items-center gap-2">
          <span>{title}</span>
        </h1>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        {/* Live System Telemetry Status */}
        <div className="hidden sm:flex items-center gap-2 bg-slate-900/80 border border-slate-800 px-3 py-1 rounded-lg text-[11px] text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping shrink-0" />
          <span className="text-slate-300 font-medium">DuckDB Mart</span>
          <span className="text-slate-500 font-mono text-[10px]">&bull; sub-10ms query</span>
        </div>

        {/* Active Filters Pill */}
        {activeCount > 0 && (
          <div className="flex items-center gap-2 bg-sky-500/15 border border-sky-500/30 text-sky-400 px-2.5 py-1 rounded-lg text-xs font-semibold shadow-sm">
            <Filter className="w-3.5 h-3.5" />
            <span>
              {activeCount} Filter{activeCount > 1 ? "s" : ""} Active
            </span>
            <button
              onClick={resetFilters}
              className="ml-1 text-slate-400 hover:text-white transition-colors"
              title="Reset All Filters"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* Data Trust Score Pill */}
        <div className="flex items-center gap-2 bg-gradient-to-r from-emerald-950/40 to-slate-900/90 border border-emerald-500/30 px-3 py-1.5 rounded-lg shadow-sm">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="text-xs text-slate-400 font-medium">Data Trust:</span>
          <span className="text-xs font-black text-emerald-400">94.6</span>
          <span className="text-[10px] font-bold text-emerald-400/80 bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/20 hidden md:inline">
            GOVERNED
          </span>
        </div>
      </div>
    </header>
  );
}

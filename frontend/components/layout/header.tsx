"use client";

import React from "react";
import { ShieldCheck, RotateCcw, Filter, Activity } from "lucide-react";
import { useGlobalFilters } from "@/components/filters/filter-context";

export function Header({ title, subtitle }: { title: string; subtitle?: string }) {
  const { resetFilters, activeCount } = useGlobalFilters();

  return (
    <header className="h-15 border-b border-slate-200 bg-white sticky top-0 z-20 flex items-center justify-between px-6 shadow-xs">
      <div>
        <h1 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
          {title}
        </h1>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-2.5">
        {/* Active Filters Pill */}
        {activeCount > 0 && (
          <div className="flex items-center gap-1.5 bg-sky-50 border border-sky-200 text-sky-800 px-2.5 py-1 rounded text-xs font-medium">
            <Filter className="w-3.5 h-3.5 text-sky-600" />
            <span>
              {activeCount} Filter{activeCount > 1 ? "s" : ""}
            </span>
            <button
              onClick={resetFilters}
              className="ml-1 text-slate-400 hover:text-slate-700 transition-colors"
              title="Reset Filters"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* System Telemetry Status */}
        <div className="hidden sm:flex items-center gap-1.5 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-md text-xs text-slate-600">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[11px] font-medium text-slate-700">Live Telemetry</span>
        </div>

        {/* Data Trust Score Pill */}
        <div className="flex items-center gap-1.5 bg-emerald-50 border border-emerald-200 text-emerald-800 px-2.5 py-1 rounded text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span className="text-slate-600 font-normal">Data Trust:</span>
          <span>94.6 / 100</span>
        </div>
      </div>
    </header>
  );
}

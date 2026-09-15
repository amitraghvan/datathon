"use client";

import React from "react";
import { Database, RotateCcw, AlertCircle } from "lucide-react";
import { useGlobalFilters } from "@/components/filters/filter-context";

export function SkeletonCard() {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4.5 animate-pulse space-y-3">
      <div className="h-3 w-20 bg-slate-200 rounded" />
      <div className="h-7 w-28 bg-slate-200 rounded" />
      <div className="h-2.5 w-36 bg-slate-100 rounded" />
    </div>
  );
}

export function SkeletonChart({ height = "h-64" }: { height?: string }) {
  return (
    <div className={`bg-white border border-slate-200 rounded-xl p-5 ${height} animate-pulse flex flex-col justify-between`}>
      <div className="space-y-2">
        <div className="h-4 w-40 bg-slate-200 rounded" />
        <div className="h-3 w-60 bg-slate-100 rounded" />
      </div>
      <div className="flex items-end gap-3 h-36 pt-4">
        {[40, 65, 80, 50, 95, 70, 85, 60].map((h, i) => (
          <div
            key={i}
            className="flex-1 bg-slate-100 rounded-t"
            style={{ height: `${h}%` }}
          />
        ))}
      </div>
      <div className="h-2 w-full bg-slate-100 rounded" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 animate-pulse space-y-4">
      <div className="h-4 w-48 bg-slate-200 rounded" />
      <div className="space-y-2.5">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-9 bg-slate-50 border border-slate-100 rounded w-full flex items-center justify-between px-3">
            <div className="h-3 w-32 bg-slate-200 rounded" />
            <div className="h-3 w-16 bg-slate-200 rounded" />
            <div className="h-3 w-20 bg-slate-200 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function EmptyFilterState({
  message = "No schools matched the selected filter criteria.",
  submessage = "Try clearing specific district or driver filters to expand the monitored cohort.",
}: {
  message?: string;
  submessage?: string;
}) {
  const { resetFilters, activeCount } = useGlobalFilters();

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 text-center flex flex-col items-center justify-center space-y-3 shadow-2xs">
      <div className="w-12 h-12 rounded-full bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-500">
        <Database className="w-6 h-6 text-slate-400" />
      </div>
      <div className="space-y-1">
        <div className="text-sm font-semibold text-slate-900 flex items-center justify-center gap-1.5">
          <AlertCircle className="w-4 h-4 text-amber-600" />
          <span>{message}</span>
        </div>
        <p className="text-xs text-slate-500 max-w-md mx-auto">{submessage}</p>
      </div>
      {activeCount > 0 && (
        <button
          onClick={resetFilters}
          className="mt-2 px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-xs font-semibold text-slate-700 rounded-lg flex items-center gap-1.5 transition-colors shadow-2xs"
        >
          <RotateCcw className="w-3 h-3 text-slate-500" />
          <span>Reset All Active Filters</span>
        </button>
      )}
    </div>
  );
}

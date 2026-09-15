"use client";

import React from "react";
import { Filter, RotateCcw, ChevronDown, X, MapPin } from "lucide-react";
import { useGlobalFilters } from "./filter-context";
import { useDimensionOptions } from "@/lib/api/queries";

export function GlobalFilterBar({ showRiskFilters = false }: { showRiskFilters?: boolean }) {
  const { filters, setFilterValue, resetFilters, activeCount } = useGlobalFilters();
  const { data: dims } = useDimensionOptions();

  const availableBlocks =
    filters.district && dims?.blocks_by_district
      ? dims.blocks_by_district[filters.district] || []
      : [];

  const selectBaseClass =
    "shrink-0 appearance-none bg-white border rounded-lg pl-3 pr-7 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-sky-500/20 transition-all cursor-pointer shadow-2xs";

  const getSelectClass = (isActive: boolean) =>
    isActive
      ? `${selectBaseClass} border-sky-600 bg-sky-50 text-sky-900 font-semibold ring-1 ring-sky-500/20`
      : `${selectBaseClass} border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50/60`;

  return (
    <div className="bg-white border-b border-slate-200 px-6 py-2.5 space-y-2 shrink-0 shadow-2xs">
      {/* Primary Filter Strip */}
      <div className="flex items-center gap-2 text-xs overflow-x-auto whitespace-nowrap">
        {/* Label & Active Counter */}
        <div className="flex items-center gap-1.5 text-slate-500 font-bold tracking-wider mr-1 shrink-0">
          <span className="p-1 rounded-md bg-slate-100 border border-slate-200 text-slate-600">
            <Filter className="w-3.5 h-3.5" />
          </span>
          <span className="text-[11px] uppercase tracking-wider text-slate-700 font-bold">Filters:</span>
          {activeCount > 0 && (
            <span className="bg-sky-50 text-sky-700 border border-sky-200 text-[10px] font-bold px-2 py-0.5 rounded-full">
              {activeCount} active
            </span>
          )}
        </div>

        {/* District Dropdown */}
        <div className="relative shrink-0">
          <select
            value={filters.district || "ALL"}
            onChange={(e) => setFilterValue("district", e.target.value)}
            className={getSelectClass(Boolean(filters.district && filters.district !== "ALL"))}
          >
            <option value="ALL">All Districts ({dims?.districts?.length || 0})</option>
            {dims?.districts?.map((d) => (
              <option key={d} value={d}>
                {d === "Unknown" ? "State Pool / Unassigned" : d}
              </option>
            ))}
          </select>
          <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>

        {/* Block Dropdown (Cascading) */}
        <div className="relative shrink-0">
          <select
            value={filters.block || "ALL"}
            disabled={!filters.district || filters.district === "ALL"}
            onChange={(e) => setFilterValue("block", e.target.value)}
            className={`${getSelectClass(
              Boolean(filters.block && filters.block !== "ALL")
            )} disabled:opacity-40 disabled:cursor-not-allowed`}
          >
            <option value="ALL">
              {filters.district && filters.district !== "ALL"
                ? `All Blocks in ${filters.district}`
                : "Select District First"}
            </option>
            {availableBlocks.map((b) => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
          <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>

        {/* Divider */}
        <div className="h-4 w-px bg-slate-200 shrink-0 mx-0.5" />

        {/* School Type */}
        <div className="relative shrink-0">
          <select
            value={filters.school_type || "ALL"}
            onChange={(e) => setFilterValue("school_type", e.target.value)}
            className={getSelectClass(Boolean(filters.school_type && filters.school_type !== "ALL"))}
          >
            <option value="ALL">All School Types</option>
            {dims?.school_types?.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
          <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>

        {/* Medium */}
        <div className="relative shrink-0">
          <select
            value={filters.medium || "ALL"}
            onChange={(e) => setFilterValue("medium", e.target.value)}
            className={getSelectClass(Boolean(filters.medium && filters.medium !== "ALL"))}
          >
            <option value="ALL">All Mediums</option>
            {dims?.mediums?.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
          <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>

        {/* Optional Risk & Driver Filters */}
        {showRiskFilters && (
          <>
            <div className="h-4 w-px bg-slate-200 shrink-0 mx-0.5" />

            <div className="relative shrink-0">
              <select
                value={filters.risk_tier || "ALL"}
                onChange={(e) => setFilterValue("risk_tier", e.target.value)}
                className={getSelectClass(Boolean(filters.risk_tier && filters.risk_tier !== "ALL"))}
              >
                <option value="ALL">All Risk Tiers</option>
                {dims?.risk_tiers?.map((rt) => (
                  <option key={rt} value={rt}>
                    {rt} Severity
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            <div className="relative shrink-0">
              <select
                value={filters.primary_driver || "ALL"}
                onChange={(e) => setFilterValue("primary_driver", e.target.value)}
                className={getSelectClass(
                  Boolean(filters.primary_driver && filters.primary_driver !== "ALL")
                )}
              >
                <option value="ALL">All Primary Drivers</option>
                {dims?.drivers?.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>

            <div className="relative shrink-0">
              <select
                value={filters.welfare_quadrant || "ALL"}
                onChange={(e) => setFilterValue("welfare_quadrant", e.target.value)}
                className={getSelectClass(
                  Boolean(filters.welfare_quadrant && filters.welfare_quadrant !== "ALL")
                )}
              >
                <option value="ALL">All Welfare Quadrants</option>
                {dims?.welfare_quadrants?.map((wq) => (
                  <option key={wq} value={wq}>
                    {wq}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </>
        )}

        {/* Reset Action */}
        {activeCount > 0 && (
          <button
            onClick={resetFilters}
            className="shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 text-xs font-semibold transition-all ml-auto shadow-2xs"
          >
            <RotateCcw className="w-3 h-3 text-slate-500" />
            <span>Reset All</span>
          </button>
        )}
      </div>

      {/* Active Filter Dismissible Pills Strip */}
      {activeCount > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 pt-1 text-xs border-t border-slate-100">
          <span className="text-[10.5px] text-slate-400 font-semibold uppercase tracking-wider mr-1">
            Active Scope:
          </span>
          {filters.district && filters.district !== "ALL" && (
            <button
              onClick={() => setFilterValue("district", "ALL")}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-sky-50 text-sky-800 border border-sky-200 hover:bg-sky-100 text-[11px] font-medium transition-colors"
            >
              <MapPin className="w-3 h-3 text-sky-600" />
              <span>District: {filters.district}</span>
              <X className="w-3 h-3 text-sky-500 hover:text-sky-800" />
            </button>
          )}
          {filters.block && filters.block !== "ALL" && (
            <button
              onClick={() => setFilterValue("block", "ALL")}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-sky-50 text-sky-800 border border-sky-200 hover:bg-sky-100 text-[11px] font-medium transition-colors"
            >
              <span>Block: {filters.block}</span>
              <X className="w-3 h-3 text-sky-500 hover:text-sky-800" />
            </button>
          )}
          {filters.school_type && filters.school_type !== "ALL" && (
            <button
              onClick={() => setFilterValue("school_type", "ALL")}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200 text-[11px] font-medium transition-colors"
            >
              <span>Type: {filters.school_type}</span>
              <X className="w-3 h-3 text-slate-500" />
            </button>
          )}
          {filters.medium && filters.medium !== "ALL" && (
            <button
              onClick={() => setFilterValue("medium", "ALL")}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 hover:bg-slate-200 text-[11px] font-medium transition-colors"
            >
              <span>Medium: {filters.medium}</span>
              <X className="w-3 h-3 text-slate-500" />
            </button>
          )}
          {filters.risk_tier && filters.risk_tier !== "ALL" && (
            <button
              onClick={() => setFilterValue("risk_tier", "ALL")}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100 text-[11px] font-medium transition-colors"
            >
              <span>Risk: {filters.risk_tier}</span>
              <X className="w-3 h-3 text-amber-600" />
            </button>
          )}
          {filters.primary_driver && filters.primary_driver !== "ALL" && (
            <button
              onClick={() => setFilterValue("primary_driver", "ALL")}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100 text-[11px] font-medium transition-colors"
            >
              <span>Driver: {filters.primary_driver}</span>
              <X className="w-3 h-3 text-amber-600" />
            </button>
          )}
          {filters.welfare_quadrant && filters.welfare_quadrant !== "ALL" && (
            <button
              onClick={() => setFilterValue("welfare_quadrant", "ALL")}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100 text-[11px] font-medium transition-colors"
            >
              <span>Quadrant: {filters.welfare_quadrant}</span>
              <X className="w-3 h-3 text-emerald-600" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}

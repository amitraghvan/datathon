"use client";

import React from "react";
import { Filter, RotateCcw, ChevronDown, Check } from "lucide-react";
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
    "shrink-0 appearance-none bg-slate-900/90 border rounded-lg pl-3 pr-7 py-1.5 text-xs font-medium focus:outline-none transition-all cursor-pointer shadow-sm";

  const getSelectClass = (isActive: boolean) =>
    isActive
      ? `${selectBaseClass} border-sky-500/60 bg-sky-950/30 text-sky-200 ring-1 ring-sky-500/30 font-semibold`
      : `${selectBaseClass} border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/80`;

  return (
    <div className="bg-gradient-to-r from-[#111827] via-[#0F172A] to-[#111827] border-b border-slate-800/90 px-6 py-2.5 flex items-center gap-2.5 text-xs overflow-x-auto whitespace-nowrap shrink-0 shadow-md backdrop-blur-md">
      {/* Label & Active Counter */}
      <div className="flex items-center gap-2 text-slate-400 font-bold tracking-wider mr-1 shrink-0">
        <span className="p-1 rounded-md bg-sky-500/10 border border-sky-500/20 text-sky-400">
          <Filter className="w-3.5 h-3.5" />
        </span>
        <span className="text-[11px] uppercase tracking-wider text-slate-300">Filters:</span>
        {activeCount > 0 && (
          <span className="bg-sky-500/20 text-sky-400 border border-sky-500/40 text-[10px] font-extrabold px-1.5 py-0.5 rounded-full">
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
          className="shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/40 text-xs font-semibold transition-all ml-auto shadow-sm"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset All</span>
        </button>
      )}
    </div>
  );
}

"use client";

import React from "react";
import { Header } from "@/components/layout/header";
import { GlobalFilterBar } from "@/components/filters/global-filter-bar";
import { useGlobalFilters } from "@/components/filters/filter-context";
import { useOverview } from "@/lib/api/queries";
import { MetricCard } from "@/components/kpi/metric-card";
import { AlertBanner } from "@/components/kpi/alert-banner";
import { DistrictRankingChart } from "@/components/charts/district-ranking-chart";
import { WelfareGapScatter } from "@/components/charts/welfare-gap-scatter";
import { AttendanceAcademicScatter } from "@/components/charts/attendance-academic-scatter";
import { PrioritySchoolsTable } from "@/components/tables/priority-schools-table";
import {
  Database,
  ArrowRight,
  FileSpreadsheet,
  Layers,
  Wrench,
  ShieldAlert,
  CheckCircle2,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";

import { SkeletonCard, SkeletonChart, EmptyFilterState } from "@/components/layout/skeletons";

export default function ExecutiveCommandCenter() {
  const { filters } = useGlobalFilters();
  const { data: overview, isLoading, error } = useOverview(filters);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#0B0F19]">
      <Header
        title="Executive Command Center"
        subtitle="Trusted decision intelligence for school welfare, performance monitoring, and administrative intervention."
      />
      <GlobalFilterBar showRiskFilters={true} />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Loading State with Pulse Skeletons */}
        {isLoading && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SkeletonChart />
              <SkeletonChart />
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-300">
            <strong>Query Error:</strong> Failed to fetch executive overview data. Check backend connectivity at{" "}
            <code className="font-mono bg-slate-900 px-1 py-0.5 rounded">http://localhost:8000/api/v1</code>.
          </div>
        )}

        {/* Empty Filter State */}
        {overview && overview.kpis.schools_monitored.value === 0 && (
          <EmptyFilterState />
        )}

        {overview && overview.kpis.schools_monitored.value > 0 && (
          <>
            {/* 1. Six Core KPIs Row */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
              <MetricCard
                title="Schools Monitored"
                metricCtx={overview.kpis.schools_monitored}
                variant="neutral"
                subtitle="100% census coverage"
              />
              <MetricCard
                title="Avg Attendance"
                metricCtx={overview.kpis.average_attendance}
                variant="sky"
                subtitle="Present / Enrolled"
              />
              <MetricCard
                title="Academic FLN Score"
                metricCtx={overview.kpis.average_academic_score}
                variant="emerald"
                subtitle="Foundational test score"
              />
              <MetricCard
                title="Priority Schools"
                metricCtx={overview.kpis.priority_schools}
                variant="amber"
                subtitle="Intervention review queue"
              />
              <MetricCard
                title="Infra Readiness"
                metricCtx={overview.kpis.infrastructure_readiness}
                variant="neutral"
                subtitle="5-amenity state index"
              />
              <MetricCard
                title="Data Trust Score"
                metricCtx={overview.kpis.data_quality_coverage}
                variant="emerald"
                subtitle="10-gate composite index"
              />
            </div>

            {/* 2. Executive Alert Strip */}
            <AlertBanner alerts={overview.alerts} />

            {/* 3. Main Analytical Grid: District Ranking & Welfare Matrix */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <DistrictRankingChart data={overview.district_ranking} />
              <WelfareGapScatter data={overview.welfare_matrix} />
            </div>

            {/* 4. Attendance x Academics & Top Priority Table */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-5">
                <AttendanceAcademicScatter summary={overview.attendance_academic_summary} />
              </div>
              <div className="lg:col-span-7">
                <PrioritySchoolsTable schools={overview.top_priorities} />
              </div>
            </div>

            {/* 5. Governed Data Trust Pipeline Flow */}
            <div className="bg-gradient-to-b from-[#151D2E]/95 to-[#0F172A]/95 border border-slate-800/90 hover:border-slate-700/80 rounded-xl p-5 shadow-lg backdrop-blur-md transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                <div className="flex items-center gap-2">
                  <span className="p-1 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                    <Database className="w-4 h-4" />
                  </span>
                  <div>
                    <h2 className="text-sm font-bold text-white tracking-wide">
                      Governed Data Trust Pipeline (10 Quality Gates)
                    </h2>
                    <p className="text-xs text-slate-400">
                      Deterministic progression from raw heterogeneous files to validated analytical views.
                    </p>
                  </div>
                </div>
                <Link
                  href="/quality"
                  className="inline-flex items-center gap-1.5 text-xs text-sky-400 hover:text-sky-300 font-bold transition-colors bg-sky-500/10 border border-sky-500/20 px-3 py-1.5 rounded-lg shrink-0"
                >
                  <span>Audit All 10 Gates</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* Connected Pipeline Stages */}
              <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 relative">
                {/* Stage 1 */}
                <div className="relative bg-slate-900/90 p-3.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-extrabold uppercase tracking-wider mb-1">
                      <span>1. Raw Ingest</span>
                      <FileSpreadsheet className="w-3.5 h-3.5 text-sky-400" />
                    </div>
                    <div className="text-xl font-black text-white mt-1">45,010</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">Multi-format records</div>
                  </div>
                  <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500">
                    CSV, JSON, XML, SQLite
                  </div>
                </div>

                {/* Stage 2 */}
                <div className="relative bg-slate-900/90 p-3.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-extrabold uppercase tracking-wider mb-1">
                      <span>2. Deduplication</span>
                      <Layers className="w-3.5 h-3.5 text-amber-400" />
                    </div>
                    <div className="text-xl font-black text-amber-400 mt-1">-1,334</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">Exact & key duplicates</div>
                  </div>
                  <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500">
                    Deterministic primary keys
                  </div>
                </div>

                {/* Stage 3 */}
                <div className="relative bg-slate-900/90 p-3.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-extrabold uppercase tracking-wider mb-1">
                      <span>3. Traceable Rescue</span>
                      <Wrench className="w-3.5 h-3.5 text-sky-400" />
                    </div>
                    <div className="text-xl font-black text-sky-400 mt-1">7,965</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">Dates, units, scale</div>
                  </div>
                  <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500">
                    Audit log maintained
                  </div>
                </div>

                {/* Stage 4 */}
                <div className="relative bg-slate-900/90 p-3.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-extrabold uppercase tracking-wider mb-1">
                      <span>4. Quarantined</span>
                      <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                    </div>
                    <div className="text-xl font-black text-rose-400 mt-1">600</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">Proxy marks isolated</div>
                  </div>
                  <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500">
                    Zero contamination
                  </div>
                </div>

                {/* Stage 5 */}
                <div className="relative bg-gradient-to-br from-emerald-950/30 to-slate-900/90 p-3.5 rounded-xl border border-emerald-500/40 shadow-emerald-500/10 transition-all flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between text-[10px] text-emerald-400 font-extrabold uppercase tracking-wider mb-1">
                      <span>5. Production Mart</span>
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    </div>
                    <div className="text-xl font-black text-emerald-400 mt-1">94.6 / 100</div>
                    <div className="text-[11px] text-emerald-300 mt-0.5">Master Data Trust Score</div>
                  </div>
                  <div className="mt-3 pt-2 border-t border-emerald-500/20 text-[10px] text-emerald-400 font-semibold">
                    100% Governed SQL
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

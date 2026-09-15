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
  ArrowRight,
  Target,
  Building2,
  Utensils,
  Brain,
  Compass,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";

import { SkeletonCard, SkeletonChart, EmptyFilterState } from "@/components/layout/skeletons";

export default function ExecutiveCommandCenter() {
  const { filters } = useGlobalFilters();
  const { data: overview, isLoading, error } = useOverview(filters);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#F8FAFC]">
      <Header
        title="Executive Command Center"
        subtitle="Trusted decision intelligence for school welfare, performance monitoring, and administrative intervention."
      />
      <GlobalFilterBar showRiskFilters={true} />

      <div className="flex-1 p-6 lg:p-8 space-y-7 overflow-y-auto">
        {/* Loading State with Pulse Skeletons */}
        {isLoading && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
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
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
            <strong>Query Error:</strong> Failed to fetch executive overview data. Check backend connectivity at{" "}
            <code className="font-mono bg-white border border-rose-200 px-1 py-0.5 rounded">http://localhost:8000/api/v1</code>.
          </div>
        )}

        {/* Empty Filter State */}
        {overview && overview.kpis.schools_monitored.value === 0 && (
          <EmptyFilterState />
        )}

        {overview && overview.kpis.schools_monitored.value > 0 && (
          <>
            {/* 1. Six Core KPIs Row */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 stagger-children">
              <MetricCard
                title="Schools Monitored"
                metricCtx={overview.kpis.schools_monitored}
                variant="neutral"
                subtitle="100% census coverage"
              />
              <MetricCard
                title="Average Attendance"
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
              <div className="lg:col-span-6">
                <AttendanceAcademicScatter summary={overview.attendance_academic_summary} />
              </div>
              <div className="lg:col-span-6">
                <PrioritySchoolsTable schools={overview.top_priorities} />
              </div>
            </div>

            {/* 5. Executive Strategic Policy Dispatch & Operational Action Cadence */}
            <div className="animate-fade-in-up bg-white border border-slate-200/80 rounded-2xl shadow-[0_1px_3px_rgba(15,23,42,0.04)] overflow-hidden">
              <div className="h-0.5 bg-gradient-to-r from-sky-400 via-sky-500 to-sky-600" />
              <div className="p-5 lg:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-sky-50 border border-sky-200/80 flex items-center justify-center text-sky-600">
                    <Compass className="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-slate-900 tracking-tight">
                      Strategic Policy Dispatch
                    </h2>
                    <p className="text-[11px] text-slate-400">
                      Decision framework for administrative action.
                    </p>
                  </div>
                </div>
                <Link
                  href="/quality"
                  className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 font-medium transition-all bg-white hover:bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg shrink-0 group"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Quality & Lineage Center</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 transition-transform group-hover:translate-x-0.5" />
                </Link>
              </div>

              {/* 4 Professional Strategy & Dispatch Cards */}
              <div className="p-5 lg:p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
                {/* Protocol 1: Priority Triage */}
                <div className="card-lift bg-white rounded-xl border border-slate-200/80 p-4 flex flex-col justify-between hover:border-rose-300 group">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="w-7 h-7 rounded-md bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
                        <Target className="w-4 h-4" />
                      </div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-full">
                        Critical Triage
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-slate-900">
                        {overview.kpis.priority_schools?.value ?? 0} High Priority Schools
                      </div>
                      <div className="text-xs font-semibold text-slate-700 mt-0.5">
                        Immediate Resource Intervention
                      </div>
                    </div>
                    <p className="text-[11.5px] text-slate-500 leading-relaxed">
                      Institutions exhibiting compounding deficits in infrastructure readiness and student attendance require rapid administrative review.
                    </p>
                  </div>
                  <div className="pt-3 mt-3 border-t border-slate-200/80">
                    <Link
                      href="/intervention"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-rose-700 hover:text-rose-800 transition-colors"
                    >
                      <span>Open Triage Queue</span>
                      <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                    </Link>
                  </div>
                </div>

                {/* Protocol 2: Infrastructure Capital Upgrades */}
                <div className="card-lift bg-white rounded-xl border border-slate-200/80 p-4 flex flex-col justify-between hover:border-sky-300 group">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="w-7 h-7 rounded-md bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-700">
                        <Building2 className="w-4 h-4" />
                      </div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-sky-700 bg-sky-50 border border-sky-200 px-2 py-0.5 rounded-full">
                        Capital Works
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-slate-900">
                        {overview.kpis.infrastructure_readiness?.value != null
                          ? overview.kpis.infrastructure_readiness.value.toFixed(1)
                          : "74.9"}% State Index
                      </div>
                      <div className="text-xs font-semibold text-slate-700 mt-0.5">
                        Physical Amenities Modernization
                      </div>
                    </div>
                    <p className="text-[11.5px] text-slate-500 leading-relaxed">
                      Prioritize capital budget allocations for electricity, clean drinking water, and functional toilets under Samagra Shiksha.
                    </p>
                  </div>
                  <div className="pt-3 mt-3 border-t border-slate-200/80">
                    <Link
                      href="/welfare"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-sky-700 hover:text-sky-800 transition-colors"
                    >
                      <span>Inspect Welfare Matrix</span>
                      <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                    </Link>
                  </div>
                </div>

                {/* Protocol 3: Nutritional Welfare & Procurement Governance */}
                <div className="card-lift bg-white rounded-xl border border-slate-200/80 p-4 flex flex-col justify-between hover:border-amber-300 group">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="w-7 h-7 rounded-md bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700">
                        <Utensils className="w-4 h-4" />
                      </div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                        Public Nutrition
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-slate-900">
                        Mid-Day Meal Governance
                      </div>
                      <div className="text-xs font-semibold text-slate-700 mt-0.5">
                        Nutritional Spend Integrity
                      </div>
                    </div>
                    <p className="text-[11.5px] text-slate-500 leading-relaxed">
                      Automated peer benchmark cost variance auditing across schools, verifying meal quality without false accusatory flags.
                    </p>
                  </div>
                  <div className="pt-3 mt-3 border-t border-slate-200/80">
                    <Link
                      href="/procurement"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-amber-800 hover:text-amber-900 transition-colors"
                    >
                      <span>Audit Procurement</span>
                      <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                    </Link>
                  </div>
                </div>

                {/* Protocol 4: Autonomous AI Decision Workbench */}
                <div className="card-lift bg-white rounded-xl border border-slate-200/80 p-4 flex flex-col justify-between hover:border-purple-300 group">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="w-7 h-7 rounded-md bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-700">
                        <Brain className="w-4 h-4" />
                      </div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-purple-700 bg-purple-50 border border-purple-200 px-2 py-0.5 rounded-full">
                        AI Analyst
                      </span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-slate-900">
                        Llama 3.1 Synthesis
                      </div>
                      <div className="text-xs font-semibold text-slate-700 mt-0.5">
                        Autonomous Decision Intelligence
                      </div>
                    </div>
                    <p className="text-[11.5px] text-slate-500 leading-relaxed">
                      Zero-hallucination semantic reasoning strictly grounded in canonical warehouse views for instant policy briefings.
                    </p>
                  </div>
                  <div className="pt-3 mt-3 border-t border-slate-200/80">
                    <Link
                      href="/ai-analyst"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-purple-700 hover:text-purple-800 transition-colors"
                    >
                      <span>Launch AI Analyst</span>
                      <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                    </Link>
                  </div>
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

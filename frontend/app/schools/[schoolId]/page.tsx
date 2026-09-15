"use client";

import React, { use } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/header";
import {
  useSchoolProfile,
  useSchoolAttendance,
  useSchoolAcademics,
  useSchoolProcurement,
} from "@/lib/api/queries";
import { formatPercent, formatINR, formatKG, formatGap } from "@/lib/utils/formatters";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertTriangle,
  FileText,
  Building2,
  Zap,
  Droplets,
  Shield,
  Trees,
  GraduationCap,
  UserCheck,
  Compass,
  AlertCircle,
  Sparkles,
  ShieldCheck,
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
  Area,
  AreaChart,
} from "recharts";

/* ─── Reusable Premium Metric Card ─── */
function MetricCard({
  label,
  value,
  icon: Icon,
  benchmark,
  gap,
  unit = "",
  color = "slate",
  delay = 0,
}: {
  label: string;
  value: string;
  icon: React.ElementType;
  benchmark?: string;
  gap?: { value: string; positive: boolean };
  unit?: string;
  color?: string;
  delay?: number;
}) {
  const colorMap: Record<string, string> = {
    sky: "text-sky-600 bg-sky-50 border-sky-100",
    emerald: "text-emerald-600 bg-emerald-50 border-emerald-100",
    amber: "text-amber-600 bg-amber-50 border-amber-100",
    rose: "text-rose-600 bg-rose-50 border-rose-100",
    slate: "text-slate-600 bg-slate-50 border-slate-100",
  };

  return (
    <div
      className="card-lift bg-white border border-slate-200/80 rounded-2xl p-5 shadow-[0_1px_3px_rgba(15,23,42,0.04)] flex flex-col justify-between group"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-[0.08em]">{label}</span>
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center border ${colorMap[color] || colorMap.slate}`}>
            <Icon className="w-3.5 h-3.5" />
          </div>
        </div>
        <div className="metric-value text-[28px] font-extrabold text-slate-900">
          {value}<span className="text-base font-semibold text-slate-400 ml-0.5">{unit}</span>
        </div>
      </div>
      {(benchmark || gap) && (
        <div className="mt-3 pt-3 border-t border-slate-100/80 flex items-center justify-between">
          {benchmark && <span className="text-[11px] text-slate-400 font-medium">{benchmark}</span>}
          {gap && (
            <span className={`text-[11px] font-bold inline-flex items-center gap-0.5 ${gap.positive ? "text-emerald-600" : "text-amber-600"}`}>
              {gap.positive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {gap.value}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── Score Ring Visual Component ─── */
function ScoreRing({ score, label, sublabel, color }: { score: number; label: string; sublabel: string; color: string }) {
  const circumference = 2 * Math.PI * 28;
  const offset = circumference - (score / 100) * circumference;
  const colorMap: Record<string, { stroke: string; text: string; bg: string }> = {
    amber: { stroke: "#D97706", text: "text-amber-700", bg: "text-amber-100" },
    slate: { stroke: "#334155", text: "text-slate-900", bg: "text-slate-100" },
    emerald: { stroke: "#059669", text: "text-emerald-700", bg: "text-emerald-100" },
    sky: { stroke: "#0284C7", text: "text-sky-700", bg: "text-sky-100" },
  };
  const c = colorMap[color] || colorMap.slate;

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-[72px] h-[72px]">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 64 64">
          <circle cx="32" cy="32" r="28" fill="none" strokeWidth="4" className={c.bg} stroke="currentColor" />
          <circle
            cx="32" cy="32" r="28" fill="none" strokeWidth="4"
            stroke={c.stroke}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="animate-progress"
            style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.16, 1, 0.3, 1)" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-sm font-black tabular-nums ${c.text}`}>{score.toFixed(0)}</span>
        </div>
      </div>
      <div className="text-center">
        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{label}</div>
        <div className="text-[9px] text-slate-400 mt-0.5">{sublabel}</div>
      </div>
    </div>
  );
}

export default function School360Page({
  params,
}: {
  params: Promise<{ schoolId: string }>;
}) {
  const { schoolId } = use(params);
  const { data: school, isLoading, error } = useSchoolProfile(schoolId);
  const { data: attendanceSeries } = useSchoolAttendance(schoolId);
  const { data: academics } = useSchoolAcademics(schoolId);
  const { data: procurement } = useSchoolProcurement(schoolId);

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen text-xs text-slate-500 bg-[#F8FAFC]">
        <div className="w-8 h-8 border-2 border-sky-600 border-t-transparent rounded-full animate-spin mb-3" />
        <span className="font-medium text-slate-600">Loading School 360 Decision Profile</span>
        <span className="text-[10px] text-slate-400 mt-1 font-mono">{schoolId}</span>
      </div>
    );
  }

  if (error || !school) {
    return (
      <div className="p-8 text-center text-xs text-rose-700 bg-[#F8FAFC] min-h-screen flex flex-col items-center justify-center">
        <AlertTriangle className="w-8 h-8 mb-2 text-rose-600" />
        <p className="text-sm font-semibold text-slate-900">School Identifier Not Found</p>
        <p className="text-xs text-slate-500 mt-1">
          Institution <span className="font-mono font-bold text-slate-900">{schoolId}</span> was not found in canonical census records.
        </p>
        <div className="mt-4">
          <Link href="/schools" className="inline-flex items-center gap-1.5 text-xs text-sky-700 hover:text-sky-800 font-semibold bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-2xs">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to School Directory</span>
          </Link>
        </div>
      </div>
    );
  }

  // 5 Statutory Physical Amenities Mapping
  const amenitiesList = [
    { label: "Electricity", value: school.amenities.electricity, icon: Zap, verifiedNote: "Continuous grid power connection" },
    { label: "Drinking Water", value: school.amenities.drinking_water, icon: Droplets, verifiedNote: "Safe potable water point" },
    { label: "Functional Toilet", value: school.amenities.functional_toilet, icon: Sparkles, verifiedNote: "Sanitary gender-separated toilets" },
    { label: "Boundary Wall", value: school.amenities.boundary_wall, icon: Shield, verifiedNote: "Pucca perimeter safety wall" },
    { label: "Playground", value: school.amenities.playground, icon: Trees, verifiedNote: "Outdoor recreational space" },
  ];

  const amenitiesAvailable = amenitiesList.filter(a => a.value === true).length;
  const amenitiesMissing = amenitiesList.filter(a => a.value === false).length;

  return (
    <div className="flex-1 flex flex-col min-h-screen pb-16 bg-[#F8FAFC]">
      <Header
        title={`School 360: ${school.school_name}`}
        subtitle={`UDISE ID: ${school.school_id} | ${school.district} District | ${school.block} Block`}
      />

      <div className="p-6 lg:p-8 space-y-7 overflow-y-auto max-w-7xl w-full mx-auto">
        {/* Top Navigation & Status Breadcrumb */}
        <div className="flex items-center justify-between animate-fade-in">
          <Link
            href="/schools"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-700 transition-all font-medium group"
          >
            <ArrowLeft className="w-3.5 h-3.5 transition-transform group-hover:-translate-x-0.5" />
            <span>Back to School Directory</span>
          </Link>

          <span
            className={`text-[10px] px-3 py-1 rounded-full font-bold uppercase tracking-[0.08em] border ${
              school.intervention_priority_tier === "HIGH"
                ? "bg-rose-50 text-rose-700 border-rose-200 pulse-live"
                : school.intervention_priority_tier === "MEDIUM"
                ? "bg-amber-50 text-amber-800 border-amber-200"
                : "bg-emerald-50 text-emerald-700 border-emerald-200"
            }`}
          >
            {school.intervention_priority_tier} Priority
          </span>
        </div>

        {/* ═══ PREMIUM HERO SECTION ═══ */}
        <div className="animate-fade-in-up bg-white border border-slate-200/80 rounded-2xl overflow-hidden shadow-[0_1px_3px_rgba(15,23,42,0.04)]">
          {/* Subtle accent gradient bar at top */}
          <div className="h-1 bg-gradient-to-r from-sky-500 via-sky-600 to-sky-700" />

          <div className="p-6 lg:p-8 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-3 flex-1 min-w-0">
              {/* Metadata Tags */}
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="font-mono text-[10px] font-bold text-sky-700 bg-sky-50 border border-sky-200/80 px-2 py-0.5 rounded-md tracking-wide">
                  {school.school_id}
                </span>
                <span className="text-[10px] text-slate-500 font-medium bg-slate-100/80 px-2 py-0.5 rounded-md border border-slate-200/80">
                  {school.school_type}
                </span>
                <span className="text-[10px] text-slate-500 font-medium bg-slate-100/80 px-2 py-0.5 rounded-md border border-slate-200/80">
                  {school.medium} Medium
                </span>
              </div>

              {/* School Name */}
              <h1 className="text-2xl sm:text-[28px] font-extrabold text-slate-900 leading-tight tracking-tight">
                {school.school_name}
              </h1>

              {/* Location Metadata */}
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                <span className="inline-flex items-center gap-1">
                  <Building2 className="w-3 h-3 text-slate-400" />
                  <span>{school.district} District</span>
                </span>
                <span className="text-slate-300">|</span>
                <span>{school.block} Block</span>
                <span className="text-slate-300">|</span>
                <span>
                  <strong className="text-slate-800 font-bold">{school.enrollment}</strong> enrolled pupils
                </span>
              </div>
            </div>

            {/* Score Rings */}
            <div className="flex items-center gap-6 shrink-0">
              <ScoreRing
                score={school.intervention_priority_score * 10}
                label="Priority"
                sublabel="Intervention Urgency"
                color="amber"
              />
              <div className="w-px h-16 bg-slate-200" />
              <ScoreRing
                score={school.risk_score * 10}
                label="Risk"
                sublabel="Deficit Magnitude"
                color="slate"
              />
              <div className="w-px h-16 bg-slate-200" />
              <ScoreRing
                score={school.data_coverage_score}
                label="Coverage"
                sublabel="Data Quality"
                color="emerald"
              />
            </div>
          </div>
        </div>

        {/* ═══ 6 CORE PERFORMANCE METRICS ═══ */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 stagger-children">
          <MetricCard
            label="Attendance"
            value={formatPercent(school.attendance_rate_pct)}
            icon={UserCheck}
            color="sky"
            benchmark={`BM ${school.district_benchmark.district_avg_attendance.toFixed(1)}%`}
            gap={{
              value: `${formatGap(school.attendance_rate_pct - school.district_benchmark.district_avg_attendance)} pts`,
              positive: school.attendance_rate_pct >= school.district_benchmark.district_avg_attendance,
            }}
            delay={0}
          />
          <MetricCard
            label="Academic FLN"
            value={formatPercent(school.academic_score)}
            icon={GraduationCap}
            color="emerald"
            benchmark={`BM ${school.district_benchmark.district_avg_academic.toFixed(1)}%`}
            gap={{
              value: `${formatGap(school.academic_score - school.district_benchmark.district_avg_academic)} pts`,
              positive: school.academic_score >= school.district_benchmark.district_avg_academic,
            }}
            delay={50}
          />
          <MetricCard
            label="Infra Readiness"
            value={formatPercent(school.infrastructure_readiness_pct)}
            icon={Zap}
            color={school.infrastructure_readiness_pct < 50 ? "rose" : "amber"}
            benchmark={`BM ${school.district_benchmark.district_avg_infrastructure.toFixed(1)}%`}
            gap={{
              value: `${formatGap(school.infrastructure_readiness_pct - school.district_benchmark.district_avg_infrastructure)} pts`,
              positive: school.infrastructure_readiness_pct >= school.district_benchmark.district_avg_infrastructure,
            }}
            delay={100}
          />

          {/* Welfare Quadrant (Non-Numeric) */}
          <div
            className="card-lift bg-white border border-slate-200/80 rounded-2xl p-5 shadow-[0_1px_3px_rgba(15,23,42,0.04)] flex flex-col justify-between"
            style={{ animationDelay: "150ms" }}
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-[0.08em]">Welfare Quadrant</span>
                <div className="w-7 h-7 rounded-lg flex items-center justify-center border text-rose-600 bg-rose-50 border-rose-100">
                  <Compass className="w-3.5 h-3.5" />
                </div>
              </div>
              <div className="text-xs font-extrabold text-rose-700 uppercase tracking-wide leading-snug">
                {school.welfare_quadrant}
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100/80 text-[10px] text-slate-400 leading-snug">
              {school.quadrant_action || "Targeted review required"}
            </div>
          </div>

          {/* Primary Driver (Non-Numeric) */}
          <div
            className="card-lift bg-white border border-slate-200/80 rounded-2xl p-5 shadow-[0_1px_3px_rgba(15,23,42,0.04)] flex flex-col justify-between"
            style={{ animationDelay: "200ms" }}
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-[0.08em]">Primary Driver</span>
                <div className="w-7 h-7 rounded-lg flex items-center justify-center border text-sky-600 bg-sky-50 border-sky-100">
                  <AlertCircle className="w-3.5 h-3.5" />
                </div>
              </div>
              <div className="text-sm font-bold text-sky-800 leading-snug">
                {school.primary_driver}
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100/80 text-[10px] text-slate-400">
              Primary constraint vector
            </div>
          </div>

          {/* Data Coverage with visual bar */}
          <div
            className="card-lift bg-white border border-slate-200/80 rounded-2xl p-5 shadow-[0_1px_3px_rgba(15,23,42,0.04)] flex flex-col justify-between"
            style={{ animationDelay: "250ms" }}
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-[0.08em]">Data Coverage</span>
                <div className="w-7 h-7 rounded-lg flex items-center justify-center border text-emerald-600 bg-emerald-50 border-emerald-100">
                  <ShieldCheck className="w-3.5 h-3.5" />
                </div>
              </div>
              <div className="metric-value text-[28px] font-extrabold text-emerald-700">
                {school.data_coverage_score.toFixed(0)}<span className="text-base font-semibold text-emerald-400 ml-0.5">%</span>
              </div>
            </div>
            {/* Visual Progress Bar */}
            <div className="mt-3 pt-3 border-t border-slate-100/80 space-y-1.5">
              <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-emerald-500 h-1.5 rounded-full animate-progress"
                  style={{ width: `${Math.min(100, school.data_coverage_score)}%` }}
                />
              </div>
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-slate-400">Confidence</span>
                <span className="font-bold text-slate-600 tabular-nums">{school.confidence_score.toFixed(0)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* ═══ DETERMINISTIC RECOMMENDATION BANNER ═══ */}
        <div className="animate-fade-in-up bg-white border border-slate-200/80 rounded-2xl overflow-hidden shadow-[0_1px_3px_rgba(15,23,42,0.04)]" style={{ animationDelay: "100ms" }}>
          <div className="h-0.5 bg-gradient-to-r from-sky-400 to-sky-600" />
          <div className="p-5 lg:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-sky-50 border border-sky-200/80 flex items-center justify-center text-sky-600 shrink-0 mt-0.5">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <div className="text-[10px] uppercase font-semibold tracking-[0.08em] text-slate-400 mb-1">Recommended Policy Action</div>
                <div className="text-sm font-bold text-slate-900">{school.recommended_action}</div>
                <div className="text-xs text-slate-500 mt-1.5 leading-relaxed max-w-2xl">{school.recommendation_details}</div>
              </div>
            </div>
            <div className="shrink-0">
              <span className="text-[9px] font-mono font-semibold text-slate-400 bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200/80 uppercase tracking-wider">
                Deterministic Engine
              </span>
            </div>
          </div>
        </div>

        {/* ═══ INFRASTRUCTURE AMENITIES CHECKLIST ═══ */}
        <div className="animate-fade-in-up bg-white border border-slate-200/80 rounded-2xl shadow-[0_1px_3px_rgba(15,23,42,0.04)]" style={{ animationDelay: "150ms" }}>
          <div className="p-5 lg:p-6 border-b border-slate-100">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h2 className="text-sm font-bold text-slate-900 tracking-tight">
                  Physical Infrastructure Amenities
                </h2>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  5 statutory amenities audit. <span className="font-medium">UNKNOWN</span> is strictly preserved and never coerced.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                  {amenitiesAvailable} Available
                </span>
                {amenitiesMissing > 0 && (
                  <span className="text-[10px] font-medium text-rose-700 bg-rose-50 px-2 py-0.5 rounded-md border border-rose-200">
                    {amenitiesMissing} Missing
                  </span>
                )}
                <span className="text-[11px] font-bold text-slate-600 bg-slate-50 px-2.5 py-0.5 rounded-md border border-slate-200">
                  Readiness: <span className="tabular-nums">{school.infrastructure_readiness_pct}%</span>
                </span>
              </div>
            </div>
          </div>

          <div className="p-5 lg:p-6">
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 stagger-children">
              {amenitiesList.map((a) => {
                const isTrue = a.value === true;
                const isFalse = a.value === false;
                const Icon = a.icon;

                return (
                  <div
                    key={a.label}
                    className={`card-lift rounded-xl border p-4 flex flex-col justify-between ${
                      isTrue
                        ? "bg-emerald-50/40 border-emerald-200/60"
                        : isFalse
                        ? "bg-rose-50/40 border-rose-200/60"
                        : "bg-slate-50/40 border-slate-200/60"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        isTrue ? "bg-emerald-100 text-emerald-600" : isFalse ? "bg-rose-100 text-rose-600" : "bg-slate-100 text-slate-500"
                      }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-bold text-slate-800">{a.label}</span>
                    </div>

                    <div>
                      {isTrue ? (
                        <span className="inline-flex items-center gap-1.5 text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-md">
                          <CheckCircle2 className="w-3 h-3" />
                          AVAILABLE
                        </span>
                      ) : isFalse ? (
                        <span className="inline-flex items-center gap-1.5 text-[10px] font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-md">
                          <XCircle className="w-3 h-3" />
                          MISSING
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-[10px] font-bold text-slate-600 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded-md">
                          <HelpCircle className="w-3 h-3" />
                          UNKNOWN
                        </span>
                      )}
                    </div>

                    <div className="text-[10px] text-slate-400 mt-3 pt-2.5 border-t border-slate-100/80 leading-snug">
                      {isTrue
                        ? a.verifiedNote
                        : isFalse
                        ? "Capital works required"
                        : "Field verification pending"}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* ═══ ATTENDANCE TIMESERIES CHART ═══ */}
        <div className="animate-fade-in-up bg-white border border-slate-200/80 rounded-2xl shadow-[0_1px_3px_rgba(15,23,42,0.04)]" style={{ animationDelay: "200ms" }}>
          <div className="p-5 lg:p-6 border-b border-slate-100">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-sky-600" />
                  <h2 className="text-sm font-bold text-slate-900 tracking-tight">
                    Daily Attendance Timeseries
                  </h2>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Temporal stability analysis with proxy record monitoring.
                </p>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-slate-500">
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-0.5 bg-sky-600 rounded-full" />
                  <span>Attendance %</span>
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-0.5 bg-amber-500 rounded-full border-b border-dashed" />
                  <span>District BM ({school.district_benchmark.district_avg_attendance.toFixed(1)}%)</span>
                </span>
                <span className="font-mono text-[10px] text-slate-400 bg-slate-50 px-2 py-0.5 rounded-md border border-slate-200/80 tabular-nums">
                  N={attendanceSeries?.length || 0}
                </span>
              </div>
            </div>
          </div>

          <div className="p-5 lg:p-6">
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={attendanceSeries || []} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                  <defs>
                    <linearGradient id="attendanceGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0284C7" stopOpacity={0.08} />
                      <stop offset="95%" stopColor="#0284C7" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: "#94A3B8", fontSize: 10, fontFamily: "Inter" }}
                    tickFormatter={(d) => d.slice(5)}
                    axisLine={{ stroke: "#E2E8F0" }}
                    tickLine={false}
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: "#94A3B8", fontSize: 10, fontFamily: "Inter" }}
                    tickFormatter={(v) => `${v}%`}
                    axisLine={false}
                    tickLine={false}
                    width={40}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const d = payload[0].payload;
                        return (
                          <div className="bg-white border border-slate-200 p-3.5 rounded-xl text-xs shadow-lg backdrop-blur-sm">
                            <div className="font-bold text-slate-900 text-sm">{d.date}</div>
                            <div className="text-sky-700 font-semibold mt-1.5 flex items-center justify-between gap-4">
                              <span>Attendance</span>
                              <span className="metric-value text-base font-extrabold">{d.attendance_pct}%</span>
                            </div>
                            <div className="text-slate-500 mt-1">
                              Present: <strong className="text-slate-700">{d.present}</strong> / {d.total} pupils
                            </div>
                            {d.has_proxy_record && (
                              <div className="text-amber-700 font-semibold mt-2 bg-amber-50 px-2 py-1 rounded-md text-[10px] border border-amber-200 inline-flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3" />
                                Proxy Record Isolated
                              </div>
                            )}
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <ReferenceLine
                    y={school.district_benchmark.district_avg_attendance}
                    stroke="#D97706"
                    strokeDasharray="6 3"
                    strokeWidth={1.5}
                  />
                  <Area
                    type="monotone"
                    dataKey="attendance_pct"
                    stroke="#0284C7"
                    strokeWidth={2}
                    fill="url(#attendanceGradient)"
                    dot={false}
                    activeDot={{ r: 5, fill: "#0369A1", stroke: "#fff", strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* ═══ ACADEMICS & PROCUREMENT SIDE-BY-SIDE ═══ */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* FLN Subject Breakdown */}
          <div className="animate-fade-in-up bg-white border border-slate-200/80 rounded-2xl shadow-[0_1px_3px_rgba(15,23,42,0.04)]" style={{ animationDelay: "250ms" }}>
            <div className="p-5 lg:p-6 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-emerald-600" />
                <h2 className="text-sm font-bold text-slate-900 tracking-tight">
                  FLN Subject Assessments
                </h2>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Normalized score distributions across evaluated grades.
              </p>
            </div>

            <div className="p-5 lg:p-6">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="text-[10px] text-slate-400 uppercase font-semibold tracking-[0.06em]">
                    <tr className="border-b border-slate-100">
                      <th className="py-2.5 px-3 font-semibold">Subject</th>
                      <th className="py-2.5 px-3 font-semibold">Grade</th>
                      <th className="py-2.5 px-3 text-right font-semibold">Avg Score</th>
                      <th className="py-2.5 px-3 text-right font-semibold">Tests</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {academics?.map((a, i) => (
                      <tr key={i} className="hover:bg-slate-50/60 transition-colors">
                        <td className="py-3 px-3 font-semibold text-slate-800">{a.subject}</td>
                        <td className="py-3 px-3 text-slate-500">Grade {a.grade}</td>
                        <td className="py-3 px-3 text-right">
                          <div className="flex items-center justify-end gap-2.5">
                            <div className="w-16 bg-slate-100 rounded-full h-1.5 overflow-hidden hidden sm:block">
                              <div
                                className="bg-emerald-500 h-1.5 rounded-full animate-progress"
                                style={{ width: `${Math.min(100, a.avg_score)}%` }}
                              />
                            </div>
                            <span className="font-bold text-emerald-700 tabular-nums">{a.avg_score.toFixed(1)}%</span>
                          </div>
                        </td>
                        <td className="py-3 px-3 text-right text-slate-500 font-medium tabular-nums">{a.assessment_count}</td>
                      </tr>
                    ))}
                    {(!academics || academics.length === 0) && (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-slate-400 text-xs">
                          No assessment records on file for this school.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* MDM Procurement Profile */}
          <div className="animate-fade-in-up bg-white border border-slate-200/80 rounded-2xl shadow-[0_1px_3px_rgba(15,23,42,0.04)]" style={{ animationDelay: "300ms" }}>
            <div className="p-5 lg:p-6 border-b border-slate-100">
              <h2 className="text-sm font-bold text-slate-900 tracking-tight">
                Mid-Day Meal Welfare & Procurement
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Commodity delivery volume, unit costs, and peer outlier benchmarking.
              </p>
            </div>

            <div className="p-5 lg:p-6">
              {procurement ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 stagger-children">
                    {[
                      { label: "Total Spend", value: formatINR(procurement.total_spend_inr), color: "text-slate-900" },
                      { label: "Total Grain", value: formatKG(procurement.total_quantity_kg), color: "text-slate-900" },
                      { label: "Cost / Student", value: `₹${procurement.avg_cost_per_student.toFixed(1)}`, color: "text-sky-700" },
                      { label: "Cost / KG", value: `₹${procurement.avg_cost_per_kg.toFixed(1)}`, color: "text-slate-900" },
                    ].map((item) => (
                      <div key={item.label} className="card-lift bg-slate-50/80 p-3.5 rounded-xl border border-slate-200/80">
                        <div className="text-[10px] text-slate-400 uppercase font-semibold tracking-wider">{item.label}</div>
                        <div className={`text-sm font-bold ${item.color} mt-1.5 tabular-nums`}>{item.value}</div>
                      </div>
                    ))}
                  </div>

                  {procurement.is_procurement_outlier ? (
                    <div className="bg-amber-50/60 border border-amber-200/80 rounded-xl p-4 text-xs text-amber-800">
                      <div className="font-bold flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-600" />
                        <span>Peer Benchmark Exception (1.5 IQR)</span>
                      </div>
                      <div className="text-[11px] text-amber-700/80 mt-1.5 leading-relaxed">
                        {procurement.procurement_anomaly_reason || "Spend per student exceeds 75th percentile + 1.5 IQR peer group threshold."}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-emerald-50/50 border border-emerald-200/80 rounded-xl p-4 text-xs text-emerald-800 flex items-center gap-2.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>Procurement spend is within normal peer variance threshold (≤ 1.5 IQR).</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-10 text-center text-xs text-slate-400">
                  No MDM delivery transactions recorded for this school.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

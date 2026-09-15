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
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

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
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen text-xs text-[#94A3B8]">
        <div className="w-8 h-8 border-2 border-[#0284C7] border-t-transparent rounded-full animate-spin mb-3" />
        Loading School 360 Decision Profile for {schoolId}...
      </div>
    );
  }

  if (error || !school) {
    return (
      <div className="p-8 text-center text-xs text-[#FCA5A5]">
        <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-[#EF4444]" />
        School <span className="font-mono font-bold text-white">{schoolId}</span> was not found in canonical records.
        <div className="mt-4">
          <Link href="/schools" className="text-[#38BDF8] hover:underline">
            ← Return to Schools Directory
          </Link>
        </div>
      </div>
    );
  }

  // 5 Amenities Map
  const amenitiesList = [
    { label: "Electricity", value: school.amenities.electricity },
    { label: "Drinking Water", value: school.amenities.drinking_water },
    { label: "Functional Toilet", value: school.amenities.functional_toilet },
    { label: "Boundary Wall", value: school.amenities.boundary_wall },
    { label: "Playground", value: school.amenities.playground },
  ];

  return (
    <div className="flex-1 flex flex-col min-h-screen pb-12">
      <Header
        title={`School 360: ${school.school_name}`}
        subtitle={`UDISE ID: ${school.school_id} | ${school.district} District | ${school.block} Block`}
      />

      <div className="p-6 space-y-6 overflow-y-auto">
        {/* Back Link & Profile Hero */}
        <div className="flex items-center justify-between">
          <Link
            href="/schools"
            className="inline-flex items-center gap-1.5 text-xs text-[#94A3B8] hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Schools Directory</span>
          </Link>

          <span
            className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider border ${
              school.intervention_priority_tier === "HIGH"
                ? "bg-[#EF4444]/15 text-[#FCA5A5] border-[#EF4444]/30"
                : school.intervention_priority_tier === "MEDIUM"
                ? "bg-[#F59E0B]/15 text-[#FCD34D] border-[#F59E0B]/30"
                : "bg-[#10B981]/15 text-[#6EE7B7] border-[#10B981]/30"
            }`}
          >
            {school.intervention_priority_tier} Intervention Priority
          </span>
        </div>

        {/* Hero Card */}
        <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs bg-[#0B0F19] text-[#38BDF8] px-2 py-0.5 rounded border border-[#2A364F]">
                {school.school_id}
              </span>
              <span className="text-xs text-[#94A3B8]">{school.school_type} &bull; {school.medium} Medium</span>
            </div>
            <h1 className="text-xl font-bold text-white mt-1.5">{school.school_name}</h1>
            <div className="text-xs text-[#94A3B8] mt-1">
              {school.district} District &bull; {school.block} Block &bull; Enrollment:{" "}
              <strong className="text-white">{school.enrollment} pupils</strong>
            </div>
          </div>

          <div className="flex items-center gap-4 bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F]">
            <div className="text-right">
              <div className="text-[10px] uppercase font-bold text-[#94A3B8]">Intervention Priority</div>
              <div className="text-2xl font-black text-[#F59E0B]">
                {school.intervention_priority_score.toFixed(1)}
              </div>
            </div>
            <div className="w-px h-8 bg-[#2A364F]" />
            <div className="text-right">
              <div className="text-[10px] uppercase font-bold text-[#94A3B8]">Risk Severity</div>
              <div className="text-2xl font-black text-[#38BDF8]">
                {school.risk_score.toFixed(1)}
              </div>
            </div>
          </div>
        </div>

        {/* 6 Metric Performance Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-3.5">
            <span className="text-[11px] font-semibold text-[#94A3B8] uppercase">Attendance</span>
            <div className="text-xl font-black text-white mt-1">{formatPercent(school.attendance_rate_pct)}</div>
            <div className="text-[10px] text-[#64748B] mt-1">
              BM: {school.district_benchmark.district_avg_attendance.toFixed(1)}% ({formatGap(school.attendance_rate_pct - school.district_benchmark.district_avg_attendance)} pts)
            </div>
          </div>
          <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-3.5">
            <span className="text-[11px] font-semibold text-[#94A3B8] uppercase">Academic FLN</span>
            <div className="text-xl font-black text-white mt-1">{formatPercent(school.academic_score)}</div>
            <div className="text-[10px] text-[#64748B] mt-1">
              BM: {school.district_benchmark.district_avg_academic.toFixed(1)}% ({formatGap(school.academic_score - school.district_benchmark.district_avg_academic)} pts)
            </div>
          </div>
          <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-3.5">
            <span className="text-[11px] font-semibold text-[#94A3B8] uppercase">Infra Readiness</span>
            <div className="text-xl font-black text-white mt-1">{formatPercent(school.infrastructure_readiness_pct)}</div>
            <div className="text-[10px] text-[#64748B] mt-1">
              BM: {school.district_benchmark.district_avg_infrastructure.toFixed(1)}% ({formatGap(school.infrastructure_readiness_pct - school.district_benchmark.district_avg_infrastructure)} pts)
            </div>
          </div>
          <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-3.5">
            <span className="text-[11px] font-semibold text-[#94A3B8] uppercase">Welfare Quadrant</span>
            <div className="text-xs font-black text-[#F59E0B] mt-2">{school.welfare_quadrant}</div>
            <div className="text-[10px] text-[#64748B] mt-1">{school.quadrant_action || "Targeted review"}</div>
          </div>
          <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-3.5">
            <span className="text-[11px] font-semibold text-[#94A3B8] uppercase">Primary Driver</span>
            <div className="text-xs font-black text-[#38BDF8] mt-2">{school.primary_driver}</div>
            <div className="text-[10px] text-[#64748B] mt-1">Dominant constraint</div>
          </div>
          <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-3.5">
            <span className="text-[11px] font-semibold text-[#94A3B8] uppercase">Data Coverage</span>
            <div className="text-xl font-black text-[#10B981] mt-1">{school.data_coverage_score.toFixed(0)}%</div>
            <div className="text-[10px] text-[#64748B] mt-1">Confidence: {school.confidence_score.toFixed(0)}%</div>
          </div>
        </div>

        {/* Deterministic Recommendation Banner */}
        <div className="bg-[#0B0F19] border-l-4 border-l-[#0284C7] border border-[#2A364F] rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-[#38BDF8] flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5" />
              <span>Recommended Operational Policy Action:</span>
              <span className="text-white font-black">{school.recommended_action}</span>
            </div>
            <div className="text-xs text-[#94A3B8] mt-1">{school.recommendation_details}</div>
          </div>
          <span className="text-[10px] text-[#64748B] italic shrink-0">
            Deterministic Engine Rule
          </span>
        </div>

        {/* 5 Physical Amenities (Strictly preserving TRUE, FALSE, UNKNOWN) */}
        <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
          <h2 className="text-sm font-bold text-white mb-1">
            Physical Infrastructure Amenities Checklist
          </h2>
          <p className="text-xs text-[#94A3B8] mb-4">
            Auditing 5 statutory amenities. UNKNOWN is strictly preserved and never coerced to FALSE.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {amenitiesList.map((a) => {
              const isTrue = a.value === true;
              const isFalse = a.value === false;

              return (
                <div
                  key={a.label}
                  className={`p-3.5 rounded-lg border flex flex-col justify-between ${
                    isTrue
                      ? "bg-[#10B981]/10 border-[#10B981]/30 text-[#6EE7B7]"
                      : isFalse
                      ? "bg-[#EF4444]/10 border-[#EF4444]/30 text-[#FCA5A5]"
                      : "bg-[#64748B]/10 border-[#64748B]/30 text-[#94A3B8]"
                  }`}
                >
                  <span className="text-xs font-semibold text-white">{a.label}</span>
                  <div className="flex items-center gap-1.5 mt-2 font-bold text-xs">
                    {isTrue ? (
                      <>
                        <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                        <span>AVAILABLE</span>
                      </>
                    ) : isFalse ? (
                      <>
                        <XCircle className="w-4 h-4 text-[#EF4444]" />
                        <span>MISSING</span>
                      </>
                    ) : (
                      <>
                        <HelpCircle className="w-4 h-4 text-[#94A3B8]" />
                        <span>UNKNOWN</span>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Daily Attendance Trend */}
        <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                Daily Student Attendance Timeseries
              </h2>
              <p className="text-xs text-[#94A3B8]">
                Evaluating temporal stability and monitoring proxy/flagged records.
              </p>
            </div>
            <div className="text-xs text-[#94A3B8]">
              Total Records: <strong className="text-white">{attendanceSeries?.length || 0}</strong> days
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={attendanceSeries || []} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis
                  dataKey="date"
                  tick={{ fill: "#64748B", fontSize: 10 }}
                  tickFormatter={(d) => d.slice(5)}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fill: "#64748B", fontSize: 10 }}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-[#0B0F19] border border-[#2A364F] p-3 rounded-lg text-xs shadow-xl">
                          <div className="font-bold text-white">{d.date}</div>
                          <div className="text-[#38BDF8]">
                            Attendance: <span className="font-bold">{d.attendance_pct}%</span>
                          </div>
                          <div className="text-[#94A3B8]">
                            Present: {d.present} / {d.total} pupils
                          </div>
                          {d.has_proxy_record && (
                            <div className="text-[#F59E0B] font-semibold mt-1">⚠️ Proxy Attendance Mark</div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="attendance_pct"
                  stroke="#0284C7"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: "#38BDF8" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Academics & Procurement Side-by-Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* FLN Subject Breakdown */}
          <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
            <h2 className="text-sm font-bold text-white mb-1">
              Foundational FLN Subject Assessments
            </h2>
            <p className="text-xs text-[#94A3B8] mb-3">
              Normalized score distributions across evaluated grades.
            </p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-[#94A3B8]">
                <thead className="bg-[#0B0F19] border-b border-[#2A364F] text-[11px] text-[#64748B] uppercase">
                  <tr>
                    <th className="py-2 px-3">Subject</th>
                    <th className="py-2 px-3">Grade</th>
                    <th className="py-2 px-3 text-right">Avg Score</th>
                    <th className="py-2 px-3 text-right">Tests Count</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1E293B]">
                  {academics?.map((a, i) => (
                    <tr key={i}>
                      <td className="py-2.5 px-3 font-semibold text-white">{a.subject}</td>
                      <td className="py-2.5 px-3">Grade {a.grade}</td>
                      <td className="py-2.5 px-3 text-right font-bold text-[#10B981]">
                        {a.avg_score.toFixed(1)}%
                      </td>
                      <td className="py-2.5 px-3 text-right">{a.assessment_count}</td>
                    </tr>
                  ))}
                  {(!academics || academics.length === 0) && (
                    <tr>
                      <td colSpan={4} className="py-4 text-center text-[#64748B]">
                        No assessment score logs on file for this school.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* MDM Procurement Profile */}
          <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
            <h2 className="text-sm font-bold text-white mb-1">
              Mid-Day Meal Welfare & Procurement
            </h2>
            <p className="text-xs text-[#94A3B8] mb-3">
              Commodity delivery volume, unit costs, and peer outlier benchmarking.
            </p>

            {procurement ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <div className="bg-[#0B0F19] p-2.5 rounded border border-[#2A364F]">
                    <div className="text-[10px] text-[#94A3B8] uppercase">Total Spend</div>
                    <div className="text-sm font-bold text-white">{formatINR(procurement.total_spend_inr)}</div>
                  </div>
                  <div className="bg-[#0B0F19] p-2.5 rounded border border-[#2A364F]">
                    <div className="text-[10px] text-[#94A3B8] uppercase">Total Grain</div>
                    <div className="text-sm font-bold text-white">{formatKG(procurement.total_quantity_kg)}</div>
                  </div>
                  <div className="bg-[#0B0F19] p-2.5 rounded border border-[#2A364F]">
                    <div className="text-[10px] text-[#94A3B8] uppercase">Cost / Student</div>
                    <div className="text-sm font-bold text-[#38BDF8]">₹{procurement.avg_cost_per_student.toFixed(1)}</div>
                  </div>
                  <div className="bg-[#0B0F19] p-2.5 rounded border border-[#2A364F]">
                    <div className="text-[10px] text-[#94A3B8] uppercase">Cost / KG</div>
                    <div className="text-sm font-bold text-white">₹{procurement.avg_cost_per_kg.toFixed(1)}</div>
                  </div>
                </div>

                {procurement.is_procurement_outlier && (
                  <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-lg p-3 text-xs text-[#FCD34D]">
                    <div className="font-bold flex items-center gap-1.5">
                      <AlertTriangle className="w-4 h-4" />
                      <span>Peer Benchmark Exception (1.5 IQR Deviation)</span>
                    </div>
                    <div className="text-[11px] text-[#94A3B8] mt-1">
                      {procurement.procurement_anomaly_reason || "Spend per student exceeds 75th percentile + 1.5 IQR."}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-[#64748B]">
                No MDM delivery transactions recorded for this school.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

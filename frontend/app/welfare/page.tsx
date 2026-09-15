"use client";

import React from "react";
import { Header } from "@/components/layout/header";
import { GlobalFilterBar } from "@/components/filters/global-filter-bar";
import { useGlobalFilters } from "@/components/filters/filter-context";
import { useWelfareOverview } from "@/lib/api/queries";
import { WelfareGapScatter } from "@/components/charts/welfare-gap-scatter";
import { Zap, Building2 } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";

export default function WelfarePage() {
  const { filters } = useGlobalFilters();
  const { data: welfare, isLoading } = useWelfareOverview(filters);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#F8FAFC]">
      <Header
        title="Welfare & Infrastructure Intelligence"
        subtitle="Physical infrastructure readiness, 5 amenity distribution, and electricity impact analysis."
      />
      <GlobalFilterBar showRiskFilters={false} />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {isLoading && (
          <div className="p-8 text-center text-xs text-slate-400">
            Loading welfare & physical infrastructure intelligence...
          </div>
        )}

        {welfare && (
          <>
            {/* Top Cards: 5 Amenity Statuses */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-sky-700" />
                  <span>Five Core Physical Amenities Availability (N = {welfare.total_schools} Schools)</span>
                </h2>
                <span className="text-xs text-slate-500">
                  State Average Readiness: <strong className="text-slate-900 font-semibold">{welfare.avg_infrastructure_readiness}%</strong>
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
                {welfare.amenity_distributions.map((a) => (
                  <div
                    key={a.amenity_name}
                    className="relative rounded-xl border border-slate-200 bg-white p-4 shadow-2xs overflow-hidden flex flex-col justify-between hover:border-slate-300 transition-all"
                  >
                    <div>
                      <div className="text-xs font-bold text-slate-700 tracking-wide">{a.amenity_name}</div>
                      <div className="text-2xl font-bold text-emerald-700 mt-1.5">
                        {a.availability_rate_pct.toFixed(1)}%
                      </div>

                      {/* Mini availability bar */}
                      <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2.5 overflow-hidden">
                        <div
                          className="bg-emerald-600 h-1.5 rounded-full"
                          style={{ width: `${a.availability_rate_pct}%` }}
                        />
                      </div>
                    </div>

                    <div className="text-[11px] text-slate-500 mt-3 pt-2.5 border-t border-slate-100 space-y-1">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Available:</span>
                        <span className="text-emerald-700 font-bold">{a.available_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Missing:</span>
                        <span className="text-rose-700 font-bold">{a.missing_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Unknown:</span>
                        <span className="text-slate-600 font-medium">{a.unknown_count}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Competition Required Analysis: Electricity vs Academic Scores */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div>
                  <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Zap className="w-4 h-4 text-amber-600" />
                    <span>Competition Benchmark: Electricity Availability vs. FLN Test Scores</span>
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Comparing average test performance across schools with and without functional electricity.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-7 h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={welfare.electricity_comparison}
                      margin={{ top: 10, right: 30, left: 20, bottom: 20 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis
                        dataKey="electricity_label"
                        tick={{ fill: "#334155", fontSize: 11 }}
                      />
                      <YAxis
                        domain={[0, 100]}
                        tick={{ fill: "#64748B", fontSize: 11 }}
                        tickFormatter={(v) => `${v}%`}
                      />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const d = payload[0].payload;
                            return (
                              <div className="bg-white border border-slate-200 p-3 rounded-lg text-xs shadow-lg text-slate-900">
                                <div className="font-bold mb-1">{d.electricity_label}</div>
                                <div className="text-slate-600">Schools: <span className="text-slate-900 font-bold">{d.school_count}</span></div>
                                <div className="text-slate-600">Avg Academic Score: <span className="text-emerald-700 font-bold">{d.avg_academic_score}%</span></div>
                                <div className="text-slate-600">Avg Attendance: <span className="text-sky-700 font-bold">{d.avg_attendance_rate}%</span></div>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Bar dataKey="avg_academic_score" radius={[4, 4, 0, 0]}>
                        {welfare.electricity_comparison.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={
                              entry.electricity === "TRUE"
                                ? "#059669"
                                : entry.electricity === "FALSE"
                                ? "#DC2626"
                                : "#94A3B8"
                            }
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="lg:col-span-5 flex flex-col justify-between bg-slate-50 p-4 rounded-lg border border-slate-200 text-xs">
                  <div>
                    <div className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                      Observational Findings
                    </div>
                    <ul className="space-y-2 text-slate-600">
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 shrink-0" />
                        <span>
                          Schools with <strong className="text-slate-900 font-semibold">Functional Electricity</strong> demonstrate an average FLN score of{" "}
                          <strong className="text-emerald-700 font-bold">
                            {welfare.electricity_comparison.find((e) => e.electricity === "TRUE")?.avg_academic_score || 0}%
                          </strong>{" "}
                          (N = {welfare.electricity_comparison.find((e) => e.electricity === "TRUE")?.school_count || 0}).
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-600 mt-1.5 shrink-0" />
                        <span>
                          Schools <strong className="text-slate-900 font-semibold">Without Electricity</strong> show an average score of{" "}
                          <strong className="text-rose-700 font-bold">
                            {welfare.electricity_comparison.find((e) => e.electricity === "FALSE")?.avg_academic_score || 0}%
                          </strong>{" "}
                          (N = {welfare.electricity_comparison.find((e) => e.electricity === "FALSE")?.school_count || 0}).
                        </span>
                      </li>
                    </ul>
                  </div>

                  <div className="border-t border-slate-200 pt-3 text-[11px] text-slate-500 italic">
                    🛡️ <strong>Governance Rule:</strong> {welfare.non_causal_disclaimer}
                  </div>
                </div>
              </div>
            </div>

            {/* 2x2 Welfare Gap Matrix */}
            <WelfareGapScatter data={welfare.welfare_gap_matrix} />
          </>
        )}
      </div>
    </div>
  );
}

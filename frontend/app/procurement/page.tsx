"use client";

import React from "react";
import { Header } from "@/components/layout/header";
import { GlobalFilterBar } from "@/components/filters/global-filter-bar";
import { useGlobalFilters } from "@/components/filters/filter-context";
import { useProcurementOverview } from "@/lib/api/queries";
import { formatINR, formatKG } from "@/lib/utils/formatters";
import { AlertTriangle } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function ProcurementPage() {
  const { filters } = useGlobalFilters();
  const { data: proc, isLoading } = useProcurementOverview(filters);

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Mid-Day Meal Nutritional Welfare & Procurement"
        subtitle="Commodity expenditure, grain volumes, unit costs, and statistical peer benchmark outliers."
      />
      <GlobalFilterBar showRiskFilters={false} />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {isLoading && (
          <div className="p-8 text-center text-xs text-[#94A3B8]">
            Loading MDM procurement operational intelligence...
          </div>
        )}

        {proc && (
          <>
            {/* Top KPIs */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
              <div className="relative rounded-xl border border-slate-800 bg-gradient-to-b from-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-sky-500 to-sky-300" />
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total Expenditure</span>
                <div className="text-2xl font-black text-white mt-1.5">{formatINR(proc.total_spend_inr)}</div>
                <div className="text-[11px] text-slate-500 mt-1">{proc.schools_covered} schools covered</div>
              </div>

              <div className="relative rounded-xl border border-slate-800 bg-gradient-to-b from-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-emerald-500 to-emerald-300" />
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total Volume</span>
                <div className="text-2xl font-black text-emerald-400 mt-1.5">{formatKG(proc.total_quantity_kg)}</div>
                <div className="text-[11px] text-slate-500 mt-1">Food grains delivered</div>
              </div>

              <div className="relative rounded-xl border border-slate-800 bg-gradient-to-b from-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-sky-500 to-sky-300" />
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Cost / Student</span>
                <div className="text-2xl font-black text-sky-400 mt-1.5">₹{proc.avg_cost_per_student.toFixed(1)}</div>
                <div className="text-[11px] text-slate-500 mt-1">Per enrolled pupil</div>
              </div>

              <div className="relative rounded-xl border border-slate-800 bg-gradient-to-b from-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-slate-500 to-slate-400" />
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Avg Cost / KG</span>
                <div className="text-2xl font-black text-white mt-1.5">₹{proc.avg_cost_per_kg.toFixed(1)}</div>
                <div className="text-[11px] text-slate-500 mt-1">Weighted procurement rate</div>
              </div>

              <div className="relative rounded-xl border border-amber-500/30 bg-gradient-to-b from-amber-950/20 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-amber-500 to-amber-300" />
                <span className="text-[11px] font-bold text-amber-300 uppercase tracking-wider">Peer Exceptions</span>
                <div className="text-2xl font-black text-amber-400 mt-1.5">{proc.outlier_count}</div>
                <div className="text-[11px] text-slate-400 mt-1">1.5 IQR spend outliers</div>
              </div>
            </div>

            {/* Spend by District & Quantity by Grain */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Spend by District */}
              <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-1">
                  Procurement Spend by District
                </h2>
                <p className="text-xs text-[#94A3B8] mb-4">
                  Financial outlays distributed across district education offices.
                </p>

                <div className="h-60 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={proc.spend_by_district} layout="vertical" margin={{ left: 30, right: 30 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
                      <XAxis type="number" tickFormatter={(v) => formatINR(v)} tick={{ fill: "#64748B", fontSize: 10 }} />
                      <YAxis type="category" dataKey="district" tick={{ fill: "#F8FAFC", fontSize: 11 }} width={70} />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const d = payload[0].payload;
                            return (
                              <div className="bg-[#0B0F19] border border-[#2A364F] p-2.5 rounded text-xs shadow-xl">
                                <div className="font-bold text-white">{d.district}</div>
                                <div className="text-[#38BDF8]">Spend: {formatINR(d.total_spend_inr)}</div>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Bar dataKey="total_spend_inr" fill="#0284C7" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Grain Volumes */}
              <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-1">
                  Commodity Volume Breakdown
                </h2>
                <p className="text-xs text-[#94A3B8] mb-4">
                  Food grain distribution: Rice, Wheat, Pulses, and Cooking Oil.
                </p>

                <div className="space-y-3 pt-2">
                  {proc.quantity_by_grain.map((g) => (
                    <div key={g.grain_name} className="bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F] flex items-center justify-between">
                      <div>
                        <div className="font-semibold text-white text-xs">{g.grain_name}</div>
                        <div className="text-[11px] text-[#94A3B8] mt-0.5">Total Outlay: {formatINR(g.total_spend_inr)}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-[#10B981]">{formatKG(g.quantity_kg)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Peer Benchmark Exceptions Table */}
            <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                <div>
                  <h2 className="text-sm font-bold text-white flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-[#F59E0B]" />
                    <span>Peer Benchmark Exceptions (N = {proc.anomalies.length} Schools)</span>
                  </h2>
                  <p className="text-xs text-[#94A3B8]">
                    Schools with cost per student exceeding the 75th percentile + 1.5 IQR peer group threshold.
                  </p>
                </div>
              </div>

              <div className="bg-[#F59E0B]/10 border border-[#F59E0B]/30 rounded-lg p-3 text-xs text-[#FCD34D] mb-4">
                🛡️ <strong>Governance Notice:</strong> {proc.governance_notice}
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#94A3B8]">
                  <thead className="bg-[#0B0F19] border-y border-[#2A364F] text-[11px] text-[#64748B] uppercase">
                    <tr>
                      <th className="py-2.5 px-3">School</th>
                      <th className="py-2.5 px-3">District</th>
                      <th className="py-2.5 px-3 text-right">Enrollment</th>
                      <th className="py-2.5 px-3 text-right">Spend / Student</th>
                      <th className="py-2.5 px-3 text-right">Threshold</th>
                      <th className="py-2.5 px-3">Probable Operational Context</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1E293B]">
                    {proc.anomalies.map((a) => (
                      <tr key={a.school_id} className="hover:bg-[#1A2438] transition-colors">
                        <td className="py-2.5 px-3">
                          <div className="font-semibold text-white truncate max-w-[200px]">{a.school_name}</div>
                          <div className="text-[10px] text-[#64748B]">{a.school_id}</div>
                        </td>
                        <td className="py-2.5 px-3 text-[#F8FAFC]">{a.district}</td>
                        <td className="py-2.5 px-3 text-right text-white font-medium">{a.enrollment}</td>
                        <td className="py-2.5 px-3 text-right font-bold text-[#F59E0B]">
                          ₹{a.avg_cost_per_student.toFixed(1)}
                        </td>
                        <td className="py-2.5 px-3 text-right text-[#64748B]">
                          ₹{a.spend_per_student_iqr_threshold.toFixed(1)}
                        </td>
                        <td className="py-2.5 px-3 text-[#94A3B8]">
                          {a.operational_context}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

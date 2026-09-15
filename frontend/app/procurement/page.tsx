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
    <div className="flex-1 flex flex-col min-h-screen bg-[#F8FAFC]">
      <Header
        title="Mid-Day Meal Nutritional Welfare & Procurement"
        subtitle="Commodity expenditure, grain volumes, unit costs, and statistical peer benchmark outliers."
      />
      <GlobalFilterBar showRiskFilters={false} />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {isLoading && (
          <div className="p-8 text-center text-xs text-slate-400">
            Loading MDM procurement operational intelligence...
          </div>
        )}

        {proc && (
          <>
            {/* Top KPIs */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Total Expenditure</span>
                <div className="text-2xl font-bold text-slate-900 mt-1.5">{formatINR(proc.total_spend_inr)}</div>
                <div className="text-[11px] text-slate-500 mt-1">{proc.schools_covered} schools covered</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Total Volume</span>
                <div className="text-2xl font-bold text-emerald-700 mt-1.5">{formatKG(proc.total_quantity_kg)}</div>
                <div className="text-[11px] text-slate-500 mt-1">Food grains delivered</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Cost / Student</span>
                <div className="text-2xl font-bold text-sky-700 mt-1.5">₹{proc.avg_cost_per_student.toFixed(1)}</div>
                <div className="text-[11px] text-slate-500 mt-1">Per enrolled pupil</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Avg Cost / KG</span>
                <div className="text-2xl font-bold text-slate-900 mt-1.5">₹{proc.avg_cost_per_kg.toFixed(1)}</div>
                <div className="text-[11px] text-slate-500 mt-1">Weighted procurement rate</div>
              </div>

              <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wider">Peer Exceptions</span>
                <div className="text-2xl font-bold text-amber-700 mt-1.5">{proc.outlier_count}</div>
                <div className="text-[11px] text-amber-700 mt-1">1.5 IQR spend outliers</div>
              </div>
            </div>

            {/* Spend by District & Quantity by Grain */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Spend by District */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
                <h2 className="text-sm font-bold text-slate-900 mb-1">
                  Procurement Spend by District
                </h2>
                <p className="text-xs text-slate-500 mb-4">
                  Financial outlays distributed across district education offices.
                </p>

                <div className="h-60 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={proc.spend_by_district} layout="vertical" margin={{ left: 30, right: 30 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
                      <XAxis type="number" tickFormatter={(v) => formatINR(v)} tick={{ fill: "#64748B", fontSize: 10 }} />
                      <YAxis type="category" dataKey="district" tick={{ fill: "#334155", fontSize: 11 }} width={70} />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const d = payload[0].payload;
                            return (
                              <div className="bg-white border border-slate-200 p-2.5 rounded text-xs shadow-lg text-slate-900">
                                <div className="font-bold">{d.district}</div>
                                <div className="text-sky-700 font-semibold">Spend: {formatINR(d.total_spend_inr)}</div>
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
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
                <h2 className="text-sm font-bold text-slate-900 mb-1">
                  Commodity Volume Breakdown
                </h2>
                <p className="text-xs text-slate-500 mb-4">
                  Food grain distribution: Rice, Wheat, Pulses, and Cooking Oil.
                </p>

                <div className="space-y-3 pt-2">
                  {proc.quantity_by_grain.map((g) => (
                    <div key={g.grain_name} className="bg-slate-50 p-3 rounded-lg border border-slate-200 flex items-center justify-between">
                      <div>
                        <div className="font-bold text-slate-900 text-xs">{g.grain_name}</div>
                        <div className="text-[11px] text-slate-500 mt-0.5">Total Outlay: {formatINR(g.total_spend_inr)}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-emerald-700">{formatKG(g.quantity_kg)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Peer Benchmark Exceptions Table */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                <div>
                  <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span>Peer Benchmark Exceptions (N = {proc.anomalies.length} Schools)</span>
                  </h2>
                  <p className="text-xs text-slate-500">
                    Schools with cost per student exceeding the 75th percentile + 1.5 IQR peer group threshold.
                  </p>
                </div>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800 mb-4">
                🛡️ <strong>Governance Notice:</strong> {proc.governance_notice}
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-50 border-y border-slate-200 text-[10px] text-slate-500 uppercase font-extrabold tracking-wider">
                    <tr>
                      <th className="py-2.5 px-3">School</th>
                      <th className="py-2.5 px-3">District</th>
                      <th className="py-2.5 px-3 text-right">Enrollment</th>
                      <th className="py-2.5 px-3 text-right">Spend / Student</th>
                      <th className="py-2.5 px-3 text-right">Threshold</th>
                      <th className="py-2.5 px-3">Probable Operational Context</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {proc.anomalies.map((a) => (
                      <tr key={a.school_id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-2.5 px-3">
                          <div className="font-bold text-slate-900 truncate max-w-[200px]">{a.school_name}</div>
                          <div className="text-[10px] text-slate-400 font-mono">{a.school_id}</div>
                        </td>
                        <td className="py-2.5 px-3 text-slate-700">{a.district}</td>
                        <td className="py-2.5 px-3 text-right text-slate-900 font-medium">{a.enrollment}</td>
                        <td className="py-2.5 px-3 text-right font-bold text-amber-700">
                          ₹{a.avg_cost_per_student.toFixed(1)}
                        </td>
                        <td className="py-2.5 px-3 text-right text-slate-500 font-medium">
                          ₹{a.spend_per_student_iqr_threshold.toFixed(1)}
                        </td>
                        <td className="py-2.5 px-3 text-slate-600">
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

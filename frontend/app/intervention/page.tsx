"use client";

import React from "react";
import { Header } from "@/components/layout/header";
import { GlobalFilterBar } from "@/components/filters/global-filter-bar";
import { useGlobalFilters } from "@/components/filters/filter-context";
import { useRiskSummary, usePrioritySchools } from "@/lib/api/queries";
import { PrioritySchoolsTable } from "@/components/tables/priority-schools-table";
import { Scale, CheckCircle2 } from "lucide-react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function InterventionPage() {
  const { filters } = useGlobalFilters();
  const { data: risk, isLoading: isRiskLoading } = useRiskSummary(filters);
  const { data: priorities, isLoading: isPriLoading } = usePrioritySchools(filters, 50);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#F8FAFC]">
      <Header
        title="Intervention & Risk Command Center"
        subtitle="Operational triaging separating Risk Severity (vulnerabilities) from Intervention Priority (review urgency)."
      />
      <GlobalFilterBar showRiskFilters={true} />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {(isRiskLoading || isPriLoading) && (
          <div className="p-8 text-center text-xs text-slate-400">
            Loading risk and intervention operational intelligence...
          </div>
        )}

        {risk && (
          <>
            {/* Top Operational Triaging Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
              <div className="rounded-xl border border-amber-200 bg-amber-50/40 p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wider">Priority Queue</span>
                <div className="text-3xl font-bold text-amber-700 mt-1.5">{risk.priority_school_count}</div>
                <div className="text-[11px] text-slate-500 mt-1">Schools requiring review (&ge; 35 pts)</div>
              </div>

              <div className="rounded-xl border border-rose-200 bg-rose-50/40 p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-rose-800 uppercase tracking-wider">High Priority</span>
                <div className="text-3xl font-bold text-rose-700 mt-1.5">{risk.high_priority_count}</div>
                <div className="text-[11px] text-slate-500 mt-1">Urgent immediate action (&ge; 45 pts)</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Critical Risk Severity</span>
                <div className="text-3xl font-bold text-slate-900 mt-1.5">{risk.critical_risk_count}</div>
                <div className="text-[11px] text-slate-500 mt-1">Observed severe deficits (&ge; 70 pts)</div>
              </div>

              <div className="rounded-xl border border-purple-200 bg-purple-50/40 p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-purple-800 uppercase tracking-wider">Welfare Disparity</span>
                <div className="text-3xl font-bold text-purple-700 mt-1.5">{risk.critical_welfare_quadrant_count}</div>
                <div className="text-[11px] text-slate-500 mt-1">Critical quadrant (Infra &lt; 50%, FLN &lt; 65%)</div>
              </div>
            </div>

            {/* Critical Analytical Rule Notice */}
            <div className="bg-white border border-slate-200 p-4 rounded-xl text-xs text-slate-600 flex items-start gap-3 shadow-2xs">
              <Scale className="w-5 h-5 text-sky-700 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-900">Critical Analytical Governance:</strong> The platform distinguishes between{" "}
                <strong className="text-sky-700">Risk Score</strong> (magnitude of observed deficits) and{" "}
                <strong className="text-amber-700">Intervention Priority</strong> (administrative queue ordering factoring relative district gaps).
                While the observed cohort shows <strong>0 schools in Critical Risk Severity</strong>,{" "}
                <strong>{risk.priority_school_count} schools require targeted intervention review</strong>.
              </div>
            </div>

            {/* Risk vs Priority Scatter & Driver Taxonomy */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Risk vs Priority Scatter */}
              <div className="lg:col-span-7 bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
                <h2 className="text-sm font-bold text-slate-900 mb-1">
                  Risk Severity vs. Intervention Priority Matrix
                </h2>
                <p className="text-xs text-slate-500 mb-3">
                  X: Risk Severity (0-100) &bull; Y: Intervention Priority (0-100). Explicit separation of concepts.
                </p>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                      <XAxis
                        type="number"
                        dataKey="risk_score"
                        domain={[20, 80]}
                        tick={{ fill: "#64748B", fontSize: 11 }}
                        label={{
                          value: "Risk Severity Score (0-100) →",
                          position: "bottom",
                          fill: "#475569",
                          fontSize: 11,
                          offset: 5,
                        }}
                      />
                      <YAxis
                        type="number"
                        dataKey="intervention_priority_score"
                        domain={[10, 60]}
                        tick={{ fill: "#64748B", fontSize: 11 }}
                        label={{
                          value: "↑ Intervention Priority Score",
                          angle: -90,
                          position: "insideLeft",
                          fill: "#475569",
                          fontSize: 11,
                        }}
                      />
                      <ZAxis type="number" dataKey="enrollment" range={[20, 80]} />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const d = payload[0].payload;
                            return (
                              <div className="bg-white border border-slate-200 p-3 rounded-lg text-xs shadow-lg text-slate-900">
                                <div className="font-bold">{d.school_name}</div>
                                <div className="text-slate-500 mb-1 font-mono text-[11px]">{d.district} &bull; {d.school_id}</div>
                                <div className="text-slate-600">Intervention Priority: <span className="font-bold text-amber-700">{d.intervention_priority_score.toFixed(1)}</span></div>
                                <div className="text-slate-600">Risk Severity: <span className="font-bold text-sky-700">{d.risk_score.toFixed(1)}</span></div>
                                <div className="text-slate-500 mt-1">Driver: <span className="text-slate-900 font-semibold">{d.primary_driver}</span></div>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Scatter data={risk.risk_vs_priority_points} fill="#D97706" fillOpacity={0.7} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Driver Taxonomy */}
              <div className="lg:col-span-5 bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
                <h2 className="text-sm font-bold text-slate-900 mb-1">
                  Primary Risk Driver Taxonomy
                </h2>
                <p className="text-xs text-slate-500 mb-4">
                  Distribution of dominant constraint driving school prioritization.
                </p>

                <div className="space-y-3">
                  {risk.driver_distribution.map((d) => (
                    <div key={d.driver} className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <div className="flex items-center justify-between text-xs mb-1.5">
                        <span className="font-bold text-slate-800">{d.driver} Deficit</span>
                        <span className="font-semibold text-slate-600">{d.school_count} schools ({d.percentage}%)</span>
                      </div>
                      <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            d.driver === "Infrastructure"
                              ? "bg-purple-600"
                              : d.driver === "Academic"
                              ? "bg-emerald-600"
                              : d.driver === "Attendance"
                              ? "bg-sky-600"
                              : "bg-amber-600"
                          }`}
                          style={{ width: `${d.percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Top Priorities Queue Table */}
            {priorities && <PrioritySchoolsTable schools={priorities} />}

            {/* Deterministic Action Catalog & Methodological Proof */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Action Catalog */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
                <h2 className="text-sm font-bold text-slate-900 mb-1">
                  Deterministic Policy Action Catalog
                </h2>
                <p className="text-xs text-slate-500 mb-3">
                  Administrative response protocol mapped deterministically to primary drivers.
                </p>

                <div className="space-y-2.5 text-xs">
                  {risk.policy_action_catalog.map((c) => (
                    <div key={c.driver} className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <div className="font-bold text-slate-900 flex items-center justify-between">
                        <span>{c.driver}: {c.action}</span>
                        <span className="text-[10px] text-sky-800 bg-sky-50 px-1.5 py-0.5 rounded border border-sky-200 font-semibold">Standard Protocol</span>
                      </div>
                      <div className="text-[11px] text-slate-600 mt-1">{c.protocol}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sensitivity Proof */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
                <h2 className="text-sm font-bold text-slate-900 mb-1">
                  Methodological Robustness & Sensitivity Proof
                </h2>
                <p className="text-xs text-slate-500 mb-3">
                  Validation of analytical stability under varying policy assumptions.
                </p>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded-lg border border-emerald-200 bg-emerald-50/50">
                    <div className="font-bold text-emerald-800 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Policy Weight Shifts Stability</span>
                    </div>
                    <div className="text-[11px] text-slate-600 mt-1">
                      {risk.sensitivity_proof.policy_weight_stability}
                    </div>
                  </div>

                  <div className="p-3 rounded-lg border border-emerald-200 bg-emerald-50/50">
                    <div className="font-bold text-emerald-800 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Letter-Grade Midpoint Imputation</span>
                    </div>
                    <div className="text-[11px] text-slate-600 mt-1">
                      {risk.sensitivity_proof.letter_grade_imputation_stability}
                    </div>
                  </div>

                  <div className="p-3 rounded-lg border border-slate-200 bg-slate-50">
                    <div className="font-bold text-slate-900">Honest Prediction Disclaimer</div>
                    <div className="text-[11px] text-slate-600 mt-1">
                      {risk.sensitivity_proof.non_causal_classification}
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

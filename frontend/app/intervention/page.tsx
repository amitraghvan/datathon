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
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Intervention & Risk Command Center"
        subtitle="Operational triaging separating Risk Severity (vulnerabilities) from Intervention Priority (review urgency)."
      />
      <GlobalFilterBar showRiskFilters={true} />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {(isRiskLoading || isPriLoading) && (
          <div className="p-8 text-center text-xs text-[#94A3B8]">
            Loading risk and intervention operational intelligence...
          </div>
        )}

        {risk && (
          <>
            {/* Top Operational Triaging Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
              <div className="relative rounded-xl border border-amber-500/30 bg-gradient-to-b from-amber-950/20 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-amber-500 to-amber-300" />
                <span className="text-[11px] font-bold text-amber-300 uppercase tracking-wider">Priority Queue</span>
                <div className="text-3xl font-black text-amber-400 mt-1.5">{risk.priority_school_count}</div>
                <div className="text-[11px] text-slate-400 mt-1">Schools requiring review (&ge; 35 pts)</div>
              </div>

              <div className="relative rounded-xl border border-rose-500/30 bg-gradient-to-b from-rose-950/20 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-rose-500 to-rose-300" />
                <span className="text-[11px] font-bold text-rose-300 uppercase tracking-wider">High Priority</span>
                <div className="text-3xl font-black text-rose-400 mt-1.5">{risk.high_priority_count}</div>
                <div className="text-[11px] text-slate-400 mt-1">Urgent immediate action (&ge; 45 pts)</div>
              </div>

              <div className="relative rounded-xl border border-sky-500/30 bg-gradient-to-b from-sky-950/20 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-sky-500 to-sky-300" />
                <span className="text-[11px] font-bold text-sky-300 uppercase tracking-wider">Critical Risk Severity</span>
                <div className="text-3xl font-black text-white mt-1.5">{risk.critical_risk_count}</div>
                <div className="text-[11px] text-slate-400 mt-1">Observed severe deficits (&ge; 70 pts)</div>
              </div>

              <div className="relative rounded-xl border border-purple-500/30 bg-gradient-to-b from-purple-950/20 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-purple-500 to-purple-300" />
                <span className="text-[11px] font-bold text-purple-300 uppercase tracking-wider">Welfare Disparity</span>
                <div className="text-3xl font-black text-purple-400 mt-1.5">{risk.critical_welfare_quadrant_count}</div>
                <div className="text-[11px] text-slate-400 mt-1">Critical quadrant (Infra &lt; 50%, FLN &lt; 65%)</div>
              </div>
            </div>

            {/* Critical Analytical Rule Notice */}
            <div className="bg-[#0B0F19] border border-[#2A364F] p-4 rounded-xl text-xs text-[#94A3B8] flex items-start gap-3">
              <Scale className="w-5 h-5 text-[#0284C7] shrink-0 mt-0.5" />
              <div>
                <strong className="text-white">Critical Analytical Governance:</strong> The platform distinguishes between{" "}
                <strong className="text-[#38BDF8]">Risk Score</strong> (magnitude of observed deficits) and{" "}
                <strong className="text-[#F59E0B]">Intervention Priority</strong> (administrative queue ordering factoring relative district gaps).
                While the observed cohort shows <strong>0 schools in Critical Risk Severity</strong>,{" "}
                <strong>{risk.priority_school_count} schools require targeted intervention review</strong>.
              </div>
            </div>

            {/* Risk vs Priority Scatter & Driver Taxonomy */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Risk vs Priority Scatter */}
              <div className="lg:col-span-7 bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-1">
                  Risk Severity vs. Intervention Priority Matrix
                </h2>
                <p className="text-xs text-[#94A3B8] mb-3">
                  X: Risk Severity (0-100) &bull; Y: Intervention Priority (0-100). Explicit separation of concepts.
                </p>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                      <XAxis
                        type="number"
                        dataKey="risk_score"
                        domain={[20, 80]}
                        tick={{ fill: "#64748B", fontSize: 11 }}
                        label={{
                          value: "Risk Severity Score (0-100) →",
                          position: "bottom",
                          fill: "#94A3B8",
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
                          fill: "#94A3B8",
                          fontSize: 11,
                        }}
                      />
                      <ZAxis type="number" dataKey="enrollment" range={[20, 80]} />
                      <Tooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const d = payload[0].payload;
                            return (
                              <div className="bg-[#0B0F19] border border-[#2A364F] p-3 rounded-lg text-xs shadow-xl">
                                <div className="font-bold text-white">{d.school_name}</div>
                                <div className="text-[#94A3B8] mb-1">{d.district} &bull; {d.school_id}</div>
                                <div className="text-white">Intervention Priority: <span className="font-bold text-[#F59E0B]">{d.intervention_priority_score.toFixed(1)}</span></div>
                                <div className="text-white">Risk Severity: <span className="font-bold text-[#38BDF8]">{d.risk_score.toFixed(1)}</span></div>
                                <div className="text-[#94A3B8] mt-1">Driver: <span className="text-white font-semibold">{d.primary_driver}</span></div>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Scatter data={risk.risk_vs_priority_points} fill="#F59E0B" fillOpacity={0.7} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Driver Taxonomy */}
              <div className="lg:col-span-5 bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-1">
                  Primary Risk Driver Taxonomy
                </h2>
                <p className="text-xs text-[#94A3B8] mb-4">
                  Distribution of dominant constraint driving school prioritization.
                </p>

                <div className="space-y-3">
                  {risk.driver_distribution.map((d) => (
                    <div key={d.driver} className="bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F]">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="font-semibold text-white">{d.driver} Deficit</span>
                        <span className="font-bold text-[#38BDF8]">{d.school_count} schools ({d.percentage}%)</span>
                      </div>
                      <div className="w-full bg-[#1E293B] h-2 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            d.driver === "Infrastructure"
                              ? "bg-[#8B5CF6]"
                              : d.driver === "Academic"
                              ? "bg-[#10B981]"
                              : d.driver === "Attendance"
                              ? "bg-[#0284C7]"
                              : "bg-[#F59E0B]"
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
              <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-1">
                  Deterministic Policy Action Catalog
                </h2>
                <p className="text-xs text-[#94A3B8] mb-3">
                  Administrative response protocol mapped deterministically to primary drivers.
                </p>

                <div className="space-y-2.5 text-xs">
                  {risk.policy_action_catalog.map((c) => (
                    <div key={c.driver} className="bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F]">
                      <div className="font-bold text-white flex items-center justify-between">
                        <span>{c.driver}: {c.action}</span>
                        <span className="text-[10px] text-[#38BDF8] bg-[#0284C7]/15 px-1.5 py-0.5 rounded border border-[#0284C7]/30">Standard Protocol</span>
                      </div>
                      <div className="text-[11px] text-[#94A3B8] mt-1">{c.protocol}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sensitivity Proof */}
              <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-1">
                  Methodological Robustness & Sensitivity Proof
                </h2>
                <p className="text-xs text-[#94A3B8] mb-3">
                  Validation of analytical stability under varying policy assumptions.
                </p>

                <div className="space-y-3 text-xs">
                  <div className="bg-[#0B0F19] p-3 rounded-lg border border-[#10B981]/30 bg-[#10B981]/5">
                    <div className="font-bold text-[#10B981] flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Policy Weight Shifts Stability</span>
                    </div>
                    <div className="text-[11px] text-[#94A3B8] mt-1">
                      {risk.sensitivity_proof.policy_weight_stability}
                    </div>
                  </div>

                  <div className="bg-[#0B0F19] p-3 rounded-lg border border-[#10B981]/30 bg-[#10B981]/5">
                    <div className="font-bold text-[#10B981] flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Letter-Grade Midpoint Imputation</span>
                    </div>
                    <div className="text-[11px] text-[#94A3B8] mt-1">
                      {risk.sensitivity_proof.letter_grade_imputation_stability}
                    </div>
                  </div>

                  <div className="bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F]">
                    <div className="font-bold text-white">Honest Prediction Disclaimer</div>
                    <div className="text-[11px] text-[#94A3B8] mt-1">
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

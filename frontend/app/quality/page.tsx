"use client";

import React, { useState } from "react";
import { Header } from "@/components/layout/header";
import { useQualitySummary } from "@/lib/api/queries";
import { CheckCircle2 } from "lucide-react";

export default function QualityPage() {
  const { data: quality, isLoading } = useQualitySummary();
  const [selectedLineage, setSelectedLineage] = useState<number>(0);

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <Header
        title="Data Trust & Governance Center"
        subtitle="Auditing 10 automated quality gates, dataset reconciliation, and end-to-end KPI lineage."
      />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {isLoading && (
          <div className="p-8 text-center text-xs text-[#94A3B8]">
            Loading data trust audit and governance records...
          </div>
        )}

        {quality && (
          <>
            {/* Top Quality KPIs */}
            <div className="grid grid-cols-2 sm:grid-cols-6 gap-3.5">
              <div className="relative rounded-xl border border-emerald-500/40 bg-gradient-to-b from-emerald-950/25 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-emerald-500 to-emerald-300" />
                <span className="text-[11px] font-bold text-emerald-300 uppercase tracking-wider">Trust Score</span>
                <div className="text-2xl font-black text-emerald-400 mt-1.5">{quality.data_trust_score} / 100</div>
                <div className="text-[10px] text-slate-400 mt-1">Weighted compliance</div>
              </div>

              <div className="relative rounded-xl border border-slate-800 bg-gradient-to-b from-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-slate-500 to-slate-400" />
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Operational Records</span>
                <div className="text-2xl font-black text-white mt-1.5">{quality.total_operational_records.toLocaleString()}</div>
                <div className="text-[10px] text-slate-500 mt-1">Attendance & tests</div>
              </div>

              <div className="relative rounded-xl border border-slate-800 bg-gradient-to-b from-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-emerald-500 to-emerald-300" />
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Trusted Records</span>
                <div className="text-2xl font-black text-emerald-400 mt-1.5">{quality.trusted_records.toLocaleString()}</div>
                <div className="text-[10px] text-slate-500 mt-1">Validated clean</div>
              </div>

              <div className="relative rounded-xl border border-amber-500/30 bg-gradient-to-b from-amber-950/20 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-amber-500 to-amber-300" />
                <span className="text-[11px] font-bold text-amber-300 uppercase tracking-wider">Flagged Records</span>
                <div className="text-2xl font-black text-amber-400 mt-1.5">{quality.flagged_records.toLocaleString()}</div>
                <div className="text-[10px] text-slate-400 mt-1">Traceably repaired</div>
              </div>

              <div className="relative rounded-xl border border-rose-500/30 bg-gradient-to-b from-rose-950/20 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-rose-500 to-rose-300" />
                <span className="text-[11px] font-bold text-rose-300 uppercase tracking-wider">Quarantined</span>
                <div className="text-2xl font-black text-rose-400 mt-1.5">{quality.excluded_records.toLocaleString()}</div>
                <div className="text-[10px] text-slate-400 mt-1">Isolated from means</div>
              </div>

              <div className="relative rounded-xl border border-sky-500/30 bg-gradient-to-b from-sky-950/20 via-[#151D2E]/90 to-[#0F172A]/90 p-4 shadow-md backdrop-blur-md overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-sky-500 to-sky-300" />
                <span className="text-[11px] font-bold text-sky-300 uppercase tracking-wider">Duplicates Cleared</span>
                <div className="text-2xl font-black text-sky-400 mt-1.5">{quality.duplicates_removed.toLocaleString()}</div>
                <div className="text-[10px] text-slate-400 mt-1">Exact & composite dedupe</div>
              </div>
            </div>

            {/* Quality Flow Visual */}
            <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
              <h2 className="text-sm font-bold text-white mb-1">
                Automated Trust Pipeline Architecture
              </h2>
              <p className="text-xs text-[#94A3B8] mb-4">
                Progression from raw ingestion to verified decision intelligence.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 text-center">
                <div className="bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F]">
                  <div className="text-xs font-bold text-white">1. RAW DATA</div>
                  <div className="text-xs text-[#94A3B8] mt-1">45,010 records</div>
                  <div className="text-[10px] text-[#64748B] mt-0.5">CSV, Excel, JSON</div>
                </div>
                <div className="bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F]">
                  <div className="text-xs font-bold text-[#38BDF8]">2. RESCUED</div>
                  <div className="text-xs text-[#94A3B8] mt-1">7,965 values</div>
                  <div className="text-[10px] text-[#64748B] mt-0.5">Units & multi-date format</div>
                </div>
                <div className="bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F]">
                  <div className="text-xs font-bold text-[#F59E0B]">3. VALIDATED</div>
                  <div className="text-xs text-[#94A3B8] mt-1">10 Quality Gates</div>
                  <div className="text-[10px] text-[#64748B] mt-0.5">Boundary & parity tests</div>
                </div>
                <div className="bg-[#0B0F19] p-3 rounded-lg border border-[#2A364F]">
                  <div className="text-xs font-bold text-[#10B981]">4. TRUSTED</div>
                  <div className="text-xs text-[#94A3B8] mt-1">42,994 records</div>
                  <div className="text-[10px] text-[#64748B] mt-0.5">Deduplicated & canonical</div>
                </div>
                <div className="bg-[#0B0F19] p-3 rounded-lg border border-[#10B981]/40 bg-[#10B981]/5">
                  <div className="text-xs font-bold text-[#10B981]">5. ANALYTICS READY</div>
                  <div className="text-xs text-[#94A3B8] mt-1">DuckDB Marts</div>
                  <div className="text-[10px] text-[#6EE7B7] mt-0.5">Star-Schema & Views</div>
                </div>
              </div>
            </div>

            {/* 10 Quality Gates Audit Checklist */}
            <div className="bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
              <h2 className="text-sm font-bold text-white mb-1">
                Ten Governed Data Quality Gates (100% Pass)
              </h2>
              <p className="text-xs text-[#94A3B8] mb-4">
                Automated regression controls executed prior to warehouse materialization.
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-[#94A3B8]">
                  <thead className="bg-[#0B0F19] border-y border-[#2A364F] text-[11px] text-[#64748B] uppercase">
                    <tr>
                      <th className="py-2.5 px-3">Gate #</th>
                      <th className="py-2.5 px-3">Quality Check</th>
                      <th className="py-2.5 px-3">Dataset</th>
                      <th className="py-2.5 px-3 text-right">Evaluated</th>
                      <th className="py-2.5 px-3 text-right">Flagged</th>
                      <th className="py-2.5 px-3">Resolution Method</th>
                      <th className="py-2.5 px-3 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1E293B]">
                    {quality.quality_gates.map((g) => (
                      <tr key={g.gate_number} className="hover:bg-[#1A2438] transition-colors">
                        <td className="py-2.5 px-3 font-bold text-white">{g.gate_number}</td>
                        <td className="py-2.5 px-3 font-semibold text-white">{g.check_name}</td>
                        <td className="py-2.5 px-3 font-mono text-[11px]">{g.dataset}</td>
                        <td className="py-2.5 px-3 text-right text-white">{g.records_evaluated.toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-right text-[#F59E0B] font-semibold">{g.records_flagged.toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-[#94A3B8] max-w-[320px]">{g.resolution_method}</td>
                        <td className="py-2.5 px-3 text-center">
                          <span className="inline-flex items-center gap-1 bg-[#10B981]/15 text-[#6EE7B7] border border-[#10B981]/30 px-2 py-0.5 rounded text-[10px] font-bold">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>{g.pass_status}</span>
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Reconciliation & KPI Lineage Explorer */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Dataset Reconciliation Matrix */}
              <div className="lg:col-span-6 bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-1">
                  Dataset Reconciliation Matrix
                </h2>
                <p className="text-xs text-[#94A3B8] mb-3">
                  Reconciling record transitions across source files.
                </p>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-[#94A3B8]">
                    <thead className="bg-[#0B0F19] border-y border-[#2A364F] text-[11px] text-[#64748B] uppercase">
                      <tr>
                        <th className="py-2 px-3">Dataset</th>
                        <th className="py-2 px-3 text-right">Raw</th>
                        <th className="py-2 px-3 text-right">Dedupe</th>
                        <th className="py-2 px-3 text-right">Rescued</th>
                        <th className="py-2 px-3 text-right">Trusted</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1E293B]">
                      {quality.reconciliation_matrix.map((r, i) => (
                        <tr key={i} className="hover:bg-[#1A2438]">
                          <td className="py-2.5 px-3 font-semibold text-white">{r.dataset}</td>
                          <td className="py-2.5 px-3 text-right">{r.raw_records.toLocaleString()}</td>
                          <td className="py-2.5 px-3 text-right text-[#F59E0B]">-{r.exact_duplicates}</td>
                          <td className="py-2.5 px-3 text-right text-[#38BDF8]">+{r.rescued_records.toLocaleString()}</td>
                          <td className="py-2.5 px-3 text-right text-[#10B981] font-bold">{r.trusted_records.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* End-to-End KPI Lineage Contract */}
              <div className="lg:col-span-6 bg-[#151D2E] border border-[#2A364F] rounded-xl p-5">
                <h2 className="text-sm font-bold text-white mb-1">
                  Traceable KPI Lineage Contracts
                </h2>
                <p className="text-xs text-[#94A3B8] mb-3">
                  Mathematical definitions and exclusion rules for governed metrics.
                </p>

                {/* Metric Selector Tabs */}
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {quality.lineage_catalog.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedLineage(idx)}
                      className={`text-xs px-2.5 py-1 rounded transition-colors ${
                        selectedLineage === idx
                          ? "bg-[#0284C7] text-white font-semibold"
                          : "bg-[#0B0F19] text-[#94A3B8] hover:text-white border border-[#2A364F]"
                      }`}
                    >
                      {item.metric_name}
                    </button>
                  ))}
                </div>

                {quality.lineage_catalog[selectedLineage] && (
                  <div className="bg-[#0B0F19] p-4 rounded-lg border border-[#2A364F] space-y-2.5 text-xs">
                    <div>
                      <span className="text-[#64748B] font-semibold uppercase text-[10px]">Formula:</span>
                      <div className="font-mono text-white text-xs bg-[#151D2E] p-2 rounded mt-0.5 border border-[#2A364F]">
                        {quality.lineage_catalog[selectedLineage].formula}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-[#64748B] font-semibold uppercase text-[10px]">Source Table:</span>
                        <div className="text-white font-mono mt-0.5">{quality.lineage_catalog[selectedLineage].source_table}</div>
                      </div>
                      <div>
                        <span className="text-[#64748B] font-semibold uppercase text-[10px]">Governed View:</span>
                        <div className="text-[#38BDF8] font-mono mt-0.5">{quality.lineage_catalog[selectedLineage].governed_view}</div>
                      </div>
                    </div>
                    <div>
                      <span className="text-[#64748B] font-semibold uppercase text-[10px]">Filters Applied:</span>
                      <div className="text-white mt-0.5">{quality.lineage_catalog[selectedLineage].filters_applied}</div>
                    </div>
                    <div>
                      <span className="text-[#64748B] font-semibold uppercase text-[10px]">Exclusions:</span>
                      <div className="text-[#F59E0B] mt-0.5">{quality.lineage_catalog[selectedLineage].exclusions}</div>
                    </div>
                    <div>
                      <span className="text-[#64748B] font-semibold uppercase text-[10px]">Aggregation Policy:</span>
                      <div className="text-[#10B981] mt-0.5">{quality.lineage_catalog[selectedLineage].aggregation_policy}</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

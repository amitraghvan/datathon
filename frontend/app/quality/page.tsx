"use client";

import React, { useState } from "react";
import { Header } from "@/components/layout/header";
import { useQualitySummary } from "@/lib/api/queries";
import { CheckCircle2 } from "lucide-react";

export default function QualityPage() {
  const { data: quality, isLoading } = useQualitySummary();
  const [selectedLineage, setSelectedLineage] = useState<number>(0);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#F8FAFC]">
      <Header
        title="Data Trust & Governance Center"
        subtitle="Auditing 10 automated quality gates, dataset reconciliation, and end-to-end KPI lineage."
      />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {isLoading && (
          <div className="p-8 text-center text-xs text-slate-400">
            Loading data trust audit and governance records...
          </div>
        )}

        {quality && (
          <>
            {/* Top Quality KPIs */}
            <div className="grid grid-cols-2 sm:grid-cols-6 gap-3.5">
              <div className="rounded-xl border border-emerald-300 bg-emerald-50/40 p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider">Trust Score</span>
                <div className="text-2xl font-bold text-emerald-800 mt-1.5">{quality.data_trust_score} / 100</div>
                <div className="text-[10px] text-emerald-700 mt-1 font-medium">Weighted compliance</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Operational Records</span>
                <div className="text-2xl font-bold text-slate-900 mt-1.5">{quality.total_operational_records.toLocaleString()}</div>
                <div className="text-[10px] text-slate-500 mt-1">Attendance & tests</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Trusted Records</span>
                <div className="text-2xl font-bold text-emerald-700 mt-1.5">{quality.trusted_records.toLocaleString()}</div>
                <div className="text-[10px] text-slate-500 mt-1">Validated clean</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Flagged Records</span>
                <div className="text-2xl font-bold text-amber-700 mt-1.5">{quality.flagged_records.toLocaleString()}</div>
                <div className="text-[10px] text-slate-500 mt-1">Traceably repaired</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Quarantined</span>
                <div className="text-2xl font-bold text-rose-700 mt-1.5">{quality.excluded_records.toLocaleString()}</div>
                <div className="text-[10px] text-slate-500 mt-1">Isolated from means</div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Duplicates Cleared</span>
                <div className="text-2xl font-bold text-sky-700 mt-1.5">{quality.duplicates_removed.toLocaleString()}</div>
                <div className="text-[10px] text-slate-500 mt-1">Exact & composite dedupe</div>
              </div>
            </div>

            {/* Quality Flow Visual */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
              <h2 className="text-sm font-bold text-slate-900 mb-1">
                Automated Trust Pipeline Architecture
              </h2>
              <p className="text-xs text-slate-500 mb-4">
                Progression from raw ingestion to verified decision intelligence.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 text-center">
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <div className="text-xs font-bold text-slate-900">1. RAW DATA</div>
                  <div className="text-xs text-slate-600 font-semibold mt-1">45,010 records</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">CSV, Excel, JSON</div>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <div className="text-xs font-bold text-sky-700">2. RESCUED</div>
                  <div className="text-xs text-slate-600 font-semibold mt-1">7,965 values</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Units & multi-date format</div>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <div className="text-xs font-bold text-amber-700">3. VALIDATED</div>
                  <div className="text-xs text-slate-600 font-semibold mt-1">10 Quality Gates</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Boundary & parity tests</div>
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <div className="text-xs font-bold text-emerald-700">4. TRUSTED</div>
                  <div className="text-xs text-slate-600 font-semibold mt-1">42,994 records</div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Deduplicated & canonical</div>
                </div>
                <div className="bg-emerald-50/50 p-3 rounded-lg border border-emerald-200">
                  <div className="text-xs font-bold text-emerald-800">5. ANALYTICS READY</div>
                  <div className="text-xs text-emerald-700 font-semibold mt-1">DuckDB Marts</div>
                  <div className="text-[10px] text-emerald-600 mt-0.5">Star-Schema & Views</div>
                </div>
              </div>
            </div>

            {/* 10 Quality Gates Audit Checklist */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
              <h2 className="text-sm font-bold text-slate-900 mb-1">
                Ten Governed Data Quality Gates (100% Pass)
              </h2>
              <p className="text-xs text-slate-500 mb-4">
                Automated regression controls executed prior to warehouse materialization.
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-50 border-y border-slate-200 text-[10px] text-slate-500 uppercase font-extrabold tracking-wider">
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
                  <tbody className="divide-y divide-slate-100">
                    {quality.quality_gates.map((g) => (
                      <tr key={g.gate_number} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-2.5 px-3 font-bold text-slate-900">{g.gate_number}</td>
                        <td className="py-2.5 px-3 font-semibold text-slate-900">{g.check_name}</td>
                        <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600">{g.dataset}</td>
                        <td className="py-2.5 px-3 text-right text-slate-900 font-medium">{g.records_evaluated.toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-right text-amber-700 font-semibold">{g.records_flagged.toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-slate-600 max-w-[320px]">{g.resolution_method}</td>
                        <td className="py-2.5 px-3 text-center">
                          <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded text-[10px] font-bold">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
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
              <div className="lg:col-span-6 bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
                <h2 className="text-sm font-bold text-slate-900 mb-1">
                  Dataset Reconciliation Matrix
                </h2>
                <p className="text-xs text-slate-500 mb-3">
                  Reconciling record transitions across source files.
                </p>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-700">
                    <thead className="bg-slate-50 border-y border-slate-200 text-[10px] text-slate-500 uppercase font-extrabold tracking-wider">
                      <tr>
                        <th className="py-2 px-3">Dataset</th>
                        <th className="py-2 px-3 text-right">Raw</th>
                        <th className="py-2 px-3 text-right">Dedupe</th>
                        <th className="py-2 px-3 text-right">Rescued</th>
                        <th className="py-2 px-3 text-right">Trusted</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {quality.reconciliation_matrix.map((r, i) => (
                        <tr key={i} className="hover:bg-slate-50/80">
                          <td className="py-2.5 px-3 font-semibold text-slate-900">{r.dataset}</td>
                          <td className="py-2.5 px-3 text-right text-slate-600">{r.raw_records.toLocaleString()}</td>
                          <td className="py-2.5 px-3 text-right text-amber-700 font-medium">-{r.exact_duplicates}</td>
                          <td className="py-2.5 px-3 text-right text-sky-700 font-medium">+{r.rescued_records.toLocaleString()}</td>
                          <td className="py-2.5 px-3 text-right text-emerald-700 font-bold">{r.trusted_records.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* End-to-End KPI Lineage Contract */}
              <div className="lg:col-span-6 bg-white border border-slate-200 rounded-xl p-5 shadow-2xs">
                <h2 className="text-sm font-bold text-slate-900 mb-1">
                  Traceable KPI Lineage Contracts
                </h2>
                <p className="text-xs text-slate-500 mb-3">
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
                          ? "bg-sky-700 text-white font-semibold"
                          : "bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 font-medium"
                      }`}
                    >
                      {item.metric_name}
                    </button>
                  ))}
                </div>

                {quality.lineage_catalog[selectedLineage] && (
                  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2.5 text-xs">
                    <div>
                      <span className="text-slate-500 font-bold uppercase text-[10px]">Formula:</span>
                      <div className="font-mono text-slate-900 text-xs bg-white p-2 rounded mt-0.5 border border-slate-200">
                        {quality.lineage_catalog[selectedLineage].formula}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-slate-500 font-bold uppercase text-[10px]">Source Table:</span>
                        <div className="text-slate-900 font-mono mt-0.5">{quality.lineage_catalog[selectedLineage].source_table}</div>
                      </div>
                      <div>
                        <span className="text-slate-500 font-bold uppercase text-[10px]">Governed View:</span>
                        <div className="text-sky-700 font-mono font-medium mt-0.5">{quality.lineage_catalog[selectedLineage].governed_view}</div>
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-500 font-bold uppercase text-[10px]">Filters Applied:</span>
                      <div className="text-slate-800 mt-0.5">{quality.lineage_catalog[selectedLineage].filters_applied}</div>
                    </div>
                    <div>
                      <span className="text-slate-500 font-bold uppercase text-[10px]">Exclusions:</span>
                      <div className="text-amber-800 mt-0.5">{quality.lineage_catalog[selectedLineage].exclusions}</div>
                    </div>
                    <div>
                      <span className="text-slate-500 font-bold uppercase text-[10px]">Aggregation Policy:</span>
                      <div className="text-emerald-800 mt-0.5 font-medium">{quality.lineage_catalog[selectedLineage].aggregation_policy}</div>
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

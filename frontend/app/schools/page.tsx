"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Header } from "@/components/layout/header";
import { GlobalFilterBar } from "@/components/filters/global-filter-bar";
import { useGlobalFilters } from "@/components/filters/filter-context";
import { useSchools } from "@/lib/api/queries";
import { formatPercent } from "@/lib/utils/formatters";
import { Search, ArrowRight } from "lucide-react";

export default function SchoolsDirectoryPage() {
  const { filters } = useGlobalFilters();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = useSchools(filters, page, 20, search);

  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#F8FAFC]">
      <Header
        title="School Directory & Search"
        subtitle="Explore all 600 canonical schools, search by UDISE ID, or filter by district."
      />
      <GlobalFilterBar showRiskFilters={true} />

      <div className="flex-1 p-6 space-y-4 overflow-y-auto">
        {/* Search Bar */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-2xs">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search school name or ID (e.g. SCH0050)..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full bg-white border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all"
            />
          </div>

          <div className="text-xs text-slate-500">
            Total Matched: <span className="text-slate-900 font-bold">{data?.total || 0}</span> schools
          </div>
        </div>

        {/* Directory Table */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-2xs">
          {isLoading ? (
            <div className="p-12 text-center text-xs text-slate-400">Loading schools directory...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="text-[10px] text-slate-500 uppercase font-extrabold tracking-wider bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-4">School ID</th>
                    <th className="py-2.5 px-4">School Name</th>
                    <th className="py-2.5 px-4">District</th>
                    <th className="py-2.5 px-4">Block</th>
                    <th className="py-2.5 px-4">Type</th>
                    <th className="py-2.5 px-4 text-right">Enrollment</th>
                    <th className="py-2.5 px-4 text-right">Attendance</th>
                    <th className="py-2.5 px-4 text-right">Academic</th>
                    <th className="py-2.5 px-4 text-right">Infra</th>
                    <th className="py-2.5 px-4 text-right">Priority</th>
                    <th className="py-2.5 px-4 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data?.items?.map((s) => (
                    <tr key={s.school_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-sky-700">{s.school_id}</td>
                      <td className="py-3 px-4 font-bold text-slate-900 max-w-[220px] truncate">
                        {s.school_name}
                      </td>
                      <td className="py-3 px-4 text-slate-700">{s.district}</td>
                      <td className="py-3 px-4 text-slate-500">{s.block}</td>
                      <td className="py-3 px-4 text-[11px] text-slate-600">{s.school_type}</td>
                      <td className="py-3 px-4 text-right text-slate-900 font-medium">{s.enrollment}</td>
                      <td className="py-3 px-4 text-right text-slate-900 font-medium">
                        {formatPercent(s.attendance_rate_pct)}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-900 font-medium">
                        {formatPercent(s.academic_score)}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-900 font-medium">
                        {formatPercent(s.infrastructure_readiness_pct)}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-amber-700">
                        {s.intervention_priority_score.toFixed(1)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Link
                          href={`/schools/${s.school_id}`}
                          className="inline-flex items-center gap-1 bg-slate-100 hover:bg-sky-600 text-slate-700 hover:text-white px-2.5 py-1 rounded text-xs font-semibold border border-slate-200 hover:border-sky-600 transition-all shadow-2xs"
                        >
                          <span>Profile</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination Controls */}
          {data && data.total_pages > 1 && (
            <div className="p-4 border-t border-slate-200 flex items-center justify-between text-xs bg-slate-50">
              <span className="text-slate-500">
                Page {data.page} of {data.total_pages}
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1 bg-white border border-slate-200 rounded text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:border-sky-500 font-medium shadow-2xs"
                >
                  Previous
                </button>
                <button
                  disabled={page >= data.total_pages}
                  onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                  className="px-3 py-1 bg-white border border-slate-200 rounded text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:border-sky-500 font-medium shadow-2xs"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

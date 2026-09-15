"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, AlertTriangle, Building2, Zap, GraduationCap, UserCheck, Shield } from "lucide-react";
import { formatPercent } from "@/lib/utils/formatters";

interface PrioritySchoolRow {
  rank: number;
  school_id: string;
  school_name: string;
  district: string;
  enrollment: number;
  intervention_priority_score: number;
  intervention_priority_tier: string;
  risk_score: number;
  risk_tier: string;
  primary_driver: string;
  attendance_rate_pct: number;
  academic_score: number;
  infrastructure_readiness_pct: number;
  recommended_action: string;
}

export function PrioritySchoolsTable({
  schools,
  title = "Top Intervention Priority Schools",
  subtitle = "Deterministic priority sequence based on composite multi-factor deficits.",
}: {
  schools: PrioritySchoolRow[];
  title?: string;
  subtitle?: string;
}) {
  const getDriverBadge = (driver: string) => {
    const d = (driver || "").toLowerCase();
    if (d.includes("infra")) {
      return (
        <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full font-bold bg-purple-500/15 text-purple-300 border border-purple-500/30">
          <Zap className="w-2.5 h-2.5" />
          <span>Infrastructure</span>
        </span>
      );
    }
    if (d.includes("acad")) {
      return (
        <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
          <GraduationCap className="w-2.5 h-2.5" />
          <span>Academic</span>
        </span>
      );
    }
    if (d.includes("attend")) {
      return (
        <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full font-bold bg-sky-500/15 text-sky-300 border border-sky-500/30">
          <UserCheck className="w-2.5 h-2.5" />
          <span>Attendance</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
        <Shield className="w-2.5 h-2.5" />
        <span>Multi-factor</span>
      </span>
    );
  };

  return (
    <div className="bg-gradient-to-b from-[#151D2E]/95 to-[#0F172A]/95 border border-slate-800/90 hover:border-slate-700/80 rounded-xl p-5 shadow-lg backdrop-blur-md transition-all overflow-hidden">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            <span className="p-1 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
            </span>
            <span>{title}</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
        </div>
        <div className="text-xs text-slate-400 bg-slate-900/90 border border-slate-800 px-2.5 py-1 rounded-lg shrink-0">
          Queue Size: <strong className="text-amber-400 font-bold">{schools.length}</strong> schools
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider bg-slate-950/80 border-y border-slate-800">
            <tr>
              <th className="py-2.5 px-3">#</th>
              <th className="py-2.5 px-3">School Name</th>
              <th className="py-2.5 px-3">District</th>
              <th className="py-2.5 px-3 text-right">Priority Score</th>
              <th className="py-2.5 px-3 text-right">Risk Score</th>
              <th className="py-2.5 px-3">Primary Driver</th>
              <th className="py-2.5 px-3 text-right">Attendance</th>
              <th className="py-2.5 px-3 text-right">Academic</th>
              <th className="py-2.5 px-3 text-right">Infra</th>
              <th className="py-2.5 px-3">Mandated Action</th>
              <th className="py-2.5 px-3 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80">
            {schools.map((s, idx) => (
              <tr
                key={s.school_id}
                className="hover:bg-slate-800/40 transition-colors group"
              >
                <td className="py-3 px-3">
                  <span
                    className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-black ${
                      idx === 0
                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                        : idx === 1
                        ? "bg-slate-400/20 text-slate-200 border border-slate-400/40"
                        : idx === 2
                        ? "bg-amber-700/20 text-amber-400 border border-amber-700/40"
                        : "text-slate-400"
                    }`}
                  >
                    {s.rank}
                  </span>
                </td>
                <td className="py-3 px-3">
                  <div className="font-bold text-white group-hover:text-sky-300 transition-colors truncate max-w-[190px]">
                    {s.school_name}
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">{s.school_id}</div>
                </td>
                <td className="py-3 px-3 text-slate-300 font-medium">
                  {s.district === "Unknown" ? "State Pool" : s.district}
                </td>
                <td className="py-3 px-3 text-right">
                  <span className="font-black text-amber-400 text-sm">
                    {s.intervention_priority_score.toFixed(1)}
                  </span>
                </td>
                <td className="py-3 px-3 text-right">
                  <span
                    className={`font-semibold ${
                      s.risk_score >= 50 ? "text-amber-400" : "text-sky-400"
                    }`}
                  >
                    {s.risk_score.toFixed(1)}
                  </span>
                </td>
                <td className="py-3 px-3">
                  {getDriverBadge(s.primary_driver)}
                </td>
                <td className="py-3 px-3 text-right">
                  <span
                    className={
                      s.attendance_rate_pct < 70
                        ? "text-rose-400 font-bold"
                        : "text-white"
                    }
                  >
                    {formatPercent(s.attendance_rate_pct)}
                  </span>
                </td>
                <td className="py-3 px-3 text-right">
                  <span
                    className={
                      s.academic_score < 60
                        ? "text-rose-400 font-bold"
                        : "text-white"
                    }
                  >
                    {formatPercent(s.academic_score)}
                  </span>
                </td>
                <td className="py-3 px-3 text-right">
                  <span
                    className={
                      s.infrastructure_readiness_pct < 50
                        ? "text-rose-400 font-bold"
                        : "text-white"
                    }
                  >
                    {formatPercent(s.infrastructure_readiness_pct)}
                  </span>
                </td>
                <td className="py-3 px-3">
                  <span className="text-sky-300 font-semibold text-[11px] bg-sky-950/40 px-2 py-0.5 rounded border border-sky-500/20">
                    {s.recommended_action || "Facility Remediation"}
                  </span>
                </td>
                <td className="py-3 px-3 text-center">
                  <Link
                    href={`/schools/${s.school_id}`}
                    className="inline-flex items-center gap-1 bg-sky-600/20 hover:bg-sky-600 text-sky-300 hover:text-white px-2.5 py-1 rounded-lg text-[11px] font-bold border border-sky-500/30 transition-all shadow-sm"
                  >
                    <span>360</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

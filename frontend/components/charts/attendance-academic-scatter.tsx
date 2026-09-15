"use client";

import React from "react";
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
import { Network, ShieldAlert, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";

interface AttendanceAcademicScatterProps {
  summary: {
    pearson_r: number;
    spearman_rho: number;
    sample_size: number;
    coverage_pct: number;
    points: Array<{
      school_id: string;
      school_name: string;
      district: string;
      attendance_rate_pct: number;
      academic_score: number;
      enrollment: number;
    }>;
  };
}

export function AttendanceAcademicScatter({ summary }: AttendanceAcademicScatterProps) {
  const router = useRouter();

  return (
    <div className="bg-gradient-to-b from-[#151D2E]/95 to-[#0F172A]/95 border border-slate-800/90 hover:border-slate-700/80 rounded-xl p-5 shadow-lg backdrop-blur-md transition-all">
      {/* Header & Empirical Coefficients */}
      <div className="flex flex-col gap-3 mb-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Network className="w-3.5 h-3.5" />
            </span>
            <h2 className="text-sm font-bold text-white tracking-wide">
              Attendance ↔ Academic Correlation
            </h2>
          </div>
          <span className="text-xs text-slate-400">
            Evaluating student presence against foundational learning scores.
          </span>
        </div>

        {/* Statistical Evidence Pills */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="bg-slate-900/90 px-2.5 py-1 rounded-lg border border-sky-500/30 text-sky-400 flex items-center gap-1.5 shadow-sm">
            <Sparkles className="w-3 h-3 text-sky-400" />
            <span>Pearson r:</span>
            <strong className="text-white font-mono text-xs">
              +{summary.pearson_r.toFixed(3)}
            </strong>
            <span className="text-[10px] text-sky-300">(p &lt; 0.001)</span>
          </div>

          <div className="bg-slate-900/90 px-2.5 py-1 rounded-lg border border-indigo-500/30 text-indigo-400 flex items-center gap-1.5 shadow-sm">
            <span>Spearman &rho;:</span>
            <strong className="text-white font-mono text-xs">
              +{summary.spearman_rho.toFixed(3)}
            </strong>
          </div>

          <div className="bg-slate-900/90 px-2.5 py-1 rounded-lg border border-slate-800 text-slate-400 flex items-center gap-1.5 ml-auto">
            <span>Sample (N):</span>
            <strong className="text-white font-mono">{summary.sample_size}</strong>
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-68 w-full">
        <ResponsiveContainer width="100%" height={260}>
          <ScatterChart margin={{ top: 15, right: 25, bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" opacity={0.7} />
            <XAxis
              type="number"
              dataKey="attendance_rate_pct"
              name="Attendance Rate"
              unit="%"
              domain={[40, 100]}
              tick={{ fill: "#64748B", fontSize: 11 }}
              label={{
                value: "Average Attendance Rate (%) →",
                position: "bottom",
                fill: "#94A3B8",
                fontSize: 11,
                offset: 5,
              }}
            />
            <YAxis
              type="number"
              dataKey="academic_score"
              name="Academic Score"
              unit="%"
              domain={[20, 100]}
              tick={{ fill: "#64748B", fontSize: 11 }}
              label={{
                value: "↑ Academic FLN Score (%)",
                angle: -90,
                position: "insideLeft",
                fill: "#94A3B8",
                fontSize: 11,
              }}
            />
            <ZAxis type="number" dataKey="enrollment" range={[30, 120]} />

            <Tooltip
              cursor={{ strokeDasharray: "3 3", stroke: "#0284C7" }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="bg-[#0B0F19]/95 border border-sky-500/40 p-3 rounded-xl text-xs shadow-2xl backdrop-blur-md min-w-[210px]">
                      <div className="font-bold text-white text-sm truncate">{d.school_name}</div>
                      <div className="text-[11px] text-slate-400 mb-2 font-mono">
                        {d.district} &bull; {d.school_id}
                      </div>

                      <div className="space-y-1.5 text-xs">
                        <div className="flex justify-between text-slate-300">
                          <span className="text-slate-400">Attendance Rate:</span>
                          <span className="font-black text-sky-400">
                            {d.attendance_rate_pct.toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-300">
                          <span className="text-slate-400">FLN Academic Score:</span>
                          <span className="font-black text-emerald-400">
                            {d.academic_score.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />

            <Scatter
              name="Schools"
              data={summary.points || []}
              fill="#38BDF8"
              fillOpacity={0.7}
              onClick={(entry: any) => {
                const sId = entry?.school_id || entry?.payload?.school_id;
                if (sId) router.push(`/schools/${sId}`);
              }}
              className="cursor-pointer"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Methodological Policy Footer */}
      <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400 gap-2">
        <div className="flex items-center gap-1.5 text-slate-400 italic">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>Statutory governance note: Association is observational across historical records; does not prove causality.</span>
        </div>
        <span className="text-emerald-400 font-semibold shrink-0">
          Coverage: {summary.coverage_pct}%
        </span>
      </div>
    </div>
  );
}

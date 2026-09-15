"use client";

import React, { useState } from "react";
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
import {
  UserCheck,
  GraduationCap,
  Zap,
  AlertTriangle,
  Award,
  TrendingUp,
} from "lucide-react";

interface DistrictRankingChartProps {
  data: Array<{
    district: string;
    school_count: number;
    avg_attendance_rate: number;
    avg_academic_score: number;
    avg_infrastructure_readiness: number;
    priority_school_rate_pct: number;
  }>;
}

type MetricKey =
  | "avg_attendance_rate"
  | "avg_academic_score"
  | "avg_infrastructure_readiness"
  | "priority_school_rate_pct";

export function DistrictRankingChart({ data }: DistrictRankingChartProps) {
  const [metric, setMetric] = useState<MetricKey>("avg_attendance_rate");

  const metricConfigs: Record<
    MetricKey,
    {
      label: string;
      unit: string;
      startColor: string;
      endColor: string;
      icon: React.ComponentType<{ className?: string }>;
    }
  > = {
    avg_attendance_rate: {
      label: "Average Attendance",
      unit: "%",
      startColor: "#0284C7",
      endColor: "#38BDF8",
      icon: UserCheck,
    },
    avg_academic_score: {
      label: "Academic FLN Score",
      unit: "%",
      startColor: "#059669",
      endColor: "#34D399",
      icon: GraduationCap,
    },
    avg_infrastructure_readiness: {
      label: "Infrastructure Readiness",
      unit: "%",
      startColor: "#7C3AED",
      endColor: "#A78BFA",
      icon: Zap,
    },
    priority_school_rate_pct: {
      label: "Priority Review Rate",
      unit: "%",
      startColor: "#D97706",
      endColor: "#FBBF24",
      icon: AlertTriangle,
    },
  };

  // Format data: Sort descending, and label "Unknown" gracefully as "State Pool / Unassigned"
  const sortedData = [...data]
    .map((d) => ({
      ...d,
      displayName:
        d.district === "Unknown" ? "State Pool" : d.district,
      isUnknown: d.district === "Unknown",
    }))
    .sort((a, b) => b[metric] - a[metric]);

  const activeConfig = metricConfigs[metric];
  const ActiveIcon = activeConfig.icon;

  // Calculate state mean for benchmark comparison in tooltip
  const stateAvg =
    sortedData.length > 0
      ? sortedData.reduce((acc, curr) => acc + curr[metric], 0) / sortedData.length
      : 0;

  return (
    <div className="bg-gradient-to-b from-[#151D2E]/95 to-[#0F172A]/95 border border-slate-800/90 hover:border-slate-700/80 rounded-xl p-5 shadow-lg backdrop-blur-md transition-all">
      {/* Header & Segmented Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-sky-500/10 border border-sky-500/30 text-sky-400">
              <ActiveIcon className="w-3.5 h-3.5" />
            </span>
            <h2 className="text-sm font-bold text-white tracking-wide">
              District Performance Benchmarking
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Ranked comparison across 9 state administrative jurisdictions.
          </p>
        </div>

        {/* Modern Segmented Control Pills */}
        <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-slate-800">
          {(Object.keys(metricConfigs) as MetricKey[]).map((key) => {
            const conf = metricConfigs[key];
            const isSelected = metric === key;
            const Icon = conf.icon;
            return (
              <button
                key={key}
                onClick={() => setMetric(key)}
                className={`inline-flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-md font-semibold transition-all ${
                  isSelected
                    ? "bg-sky-600 text-white shadow-sm shadow-sky-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <Icon className="w-3 h-3" />
                <span>
                  {key === "avg_attendance_rate"
                    ? "Attendance"
                    : key === "avg_academic_score"
                    ? "Academic"
                    : key === "avg_infrastructure_readiness"
                    ? "Infra"
                    : "Priority"}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Chart Canvas with SVG Gradients */}
      <div className="h-68 w-full">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart
            data={sortedData}
            layout="vertical"
            margin={{ top: 5, right: 35, left: 30, bottom: 5 }}
          >
            <defs>
              <linearGradient id="activeMetricGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor={activeConfig.startColor} stopOpacity={0.85} />
                <stop offset="100%" stopColor={activeConfig.endColor} stopOpacity={1} />
              </linearGradient>
              <linearGradient id="unknownMetricGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#475569" stopOpacity={0.6} />
                <stop offset="100%" stopColor="#64748B" stopOpacity={0.8} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, 100]}
              tick={{ fill: "#64748B", fontSize: 11 }}
              tickFormatter={(v) => `${v}%`}
            />
            <YAxis
              type="category"
              dataKey="displayName"
              tick={{ fill: "#E2E8F0", fontSize: 11, fontWeight: 500 }}
              width={90}
            />
            <Tooltip
              cursor={{ fill: "rgba(30, 41, 59, 0.4)" }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  const rank = sortedData.findIndex((x) => x.district === d.district) + 1;
                  const val = d[metric];
                  const deltaToAvg = val - stateAvg;

                  return (
                    <div className="bg-[#0B0F19]/95 border border-slate-700/80 p-3 rounded-xl text-xs shadow-2xl backdrop-blur-md min-w-[210px]">
                      <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-2 mb-2">
                        <div className="flex items-center gap-1.5 font-bold text-white text-sm">
                          {rank === 1 && <Award className="w-4 h-4 text-amber-400" />}
                          <span>{d.displayName}</span>
                        </div>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                          Rank #{rank}
                        </span>
                      </div>

                      <div className="space-y-1.5">
                        <div className="flex justify-between text-slate-300">
                          <span className="text-slate-400">Schools:</span>
                          <span className="font-semibold text-white">{d.school_count}</span>
                        </div>
                        <div className="flex justify-between text-slate-300">
                          <span className="text-slate-400">{activeConfig.label}:</span>
                          <span className="font-black text-sky-400 text-sm">
                            {val.toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-[10px] pt-1 border-t border-slate-800/80">
                          <span className="text-slate-500">Vs State Average ({stateAvg.toFixed(1)}%):</span>
                          <span
                            className={`font-bold ${
                              deltaToAvg >= 0 ? "text-emerald-400" : "text-rose-400"
                            }`}
                          >
                            {deltaToAvg >= 0 ? `+${deltaToAvg.toFixed(1)}%` : `${deltaToAvg.toFixed(1)}%`}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey={metric} radius={[0, 6, 6, 0]} maxBarSize={20}>
              {sortedData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.isUnknown ? "url(#unknownMetricGrad)" : "url(#activeMetricGrad)"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Info Strip */}
      <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5">
          <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
          <span>
            Top Performer: <strong className="text-white">{sortedData[0]?.displayName}</strong> ({sortedData[0]?.[metric].toFixed(1)}%)
          </span>
        </div>
        <span className="text-slate-500">
          State Baseline: <strong className="text-slate-300">{stateAvg.toFixed(1)}%</strong>
        </span>
      </div>
    </div>
  );
}

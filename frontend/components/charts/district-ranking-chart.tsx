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
      color: string;
      icon: React.ComponentType<{ className?: string }>;
    }
  > = {
    avg_attendance_rate: {
      label: "Average Attendance",
      unit: "%",
      color: "#0284C7",
      icon: UserCheck,
    },
    avg_academic_score: {
      label: "Academic FLN Score",
      unit: "%",
      color: "#059669",
      icon: GraduationCap,
    },
    avg_infrastructure_readiness: {
      label: "Infrastructure Readiness",
      unit: "%",
      color: "#6366F1",
      icon: Zap,
    },
    priority_school_rate_pct: {
      label: "Priority Review Rate",
      unit: "%",
      color: "#D97706",
      icon: AlertTriangle,
    },
  };

  // Format data: Sort descending, and label "Unknown" gracefully as "State Pool"
  const sortedData = [...data]
    .map((d) => ({
      ...d,
      displayName: d.district === "Unknown" ? "State Pool" : d.district,
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
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs transition-all">
      {/* Header & Segmented Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-slate-100 border border-slate-200 text-slate-700">
              <ActiveIcon className="w-3.5 h-3.5" />
            </span>
            <h2 className="text-sm font-bold text-slate-900 tracking-wide">
              District Performance Benchmarking
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Ranked comparison across 9 state administrative jurisdictions.
          </p>
        </div>

        {/* Consulting Segmented Control */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
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
                    ? "bg-white text-slate-900 shadow-2xs border border-slate-200/80"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
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

      {/* Chart Canvas */}
      <div className="h-68 w-full">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart
            data={sortedData}
            layout="vertical"
            margin={{ top: 5, right: 35, left: 30, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, 100]}
              tick={{ fill: "#64748B", fontSize: 11 }}
              tickFormatter={(v) => `${v}%`}
            />
            <YAxis
              type="category"
              dataKey="displayName"
              tick={{ fill: "#334155", fontSize: 11, fontWeight: 500 }}
              width={90}
            />
            <Tooltip
              cursor={{ fill: "rgba(241, 245, 249, 0.6)" }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  const rank = sortedData.findIndex((x) => x.district === d.district) + 1;
                  const val = d[metric];
                  const deltaToAvg = val - stateAvg;

                  return (
                    <div className="bg-white border border-slate-200 p-3 rounded-xl text-xs shadow-lg min-w-[210px]">
                      <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-2 mb-2">
                        <div className="flex items-center gap-1.5 font-bold text-slate-900 text-sm">
                          {rank === 1 && <Award className="w-4 h-4 text-amber-500" />}
                          <span>{d.displayName}</span>
                        </div>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                          Rank #{rank}
                        </span>
                      </div>

                      <div className="space-y-1.5">
                        <div className="flex justify-between text-slate-600">
                          <span>Schools:</span>
                          <span className="font-semibold text-slate-900">{d.school_count}</span>
                        </div>
                        <div className="flex justify-between text-slate-600">
                          <span>{activeConfig.label}:</span>
                          <span className="font-bold text-slate-900 text-sm">
                            {val.toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-[10.5px] pt-1 border-t border-slate-100">
                          <span className="text-slate-500">Vs State Avg ({stateAvg.toFixed(1)}%):</span>
                          <span
                            className={`font-bold ${
                              deltaToAvg >= 0 ? "text-emerald-600" : "text-rose-600"
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
            <Bar dataKey={metric} radius={[0, 4, 4, 0]} maxBarSize={18}>
              {sortedData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.isUnknown ? "#94A3B8" : activeConfig.color}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Info Strip */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
        <div className="flex items-center gap-1.5">
          <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
          <span>
            Top Performer: <strong className="text-slate-900">{sortedData[0]?.displayName}</strong> ({sortedData[0]?.[metric].toFixed(1)}%)
          </span>
        </div>
        <span>
          State Baseline: <strong className="text-slate-700">{stateAvg.toFixed(1)}%</strong>
        </span>
      </div>
    </div>
  );
}

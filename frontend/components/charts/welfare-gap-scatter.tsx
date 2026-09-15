"use client";

import React, { useMemo } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid,
  Cell,
} from "recharts";
import { Grid, ExternalLink } from "lucide-react";
import { useRouter } from "next/navigation";

interface WelfareGapScatterProps {
  data: Array<{
    school_id: string;
    school_name: string;
    district: string;
    infrastructure_readiness_pct: number;
    academic_score: number;
    welfare_quadrant: string;
    intervention_priority_score: number;
    enrollment?: number;
  }>;
  onSchoolClick?: (schoolId: string) => void;
}

const quadrantConfig: Record<
  string,
  {
    name: string;
    color: string;
    bgBadge: string;
    borderBadge: string;
    textColor: string;
    desc: string;
  }
> = {
  MODEL: {
    name: "Model",
    color: "#059669",
    bgBadge: "bg-emerald-50",
    borderBadge: "border-emerald-200",
    textColor: "text-emerald-700",
    desc: "Infra ≥50% & FLN ≥65%",
  },
  RESILIENT: {
    name: "Resilient",
    color: "#0284C7",
    bgBadge: "bg-sky-50",
    borderBadge: "border-sky-200",
    textColor: "text-sky-700",
    desc: "Infra <50% & FLN ≥65%",
  },
  "ACADEMIC INTERVENTION": {
    name: "Academic Gap",
    color: "#D97706",
    bgBadge: "bg-amber-50",
    borderBadge: "border-amber-200",
    textColor: "text-amber-700",
    desc: "Infra ≥50% & FLN <65%",
  },
  "CRITICAL INTERVENTION": {
    name: "Critical Risk",
    color: "#DC2626",
    bgBadge: "bg-rose-50",
    borderBadge: "border-rose-200",
    textColor: "text-rose-700",
    desc: "Infra <50% & FLN <65%",
  },
};

export function WelfareGapScatter({ data, onSchoolClick }: WelfareGapScatterProps) {
  const router = useRouter();

  // Compute quadrant counts
  const counts = useMemo(() => {
    const c: Record<string, number> = {
      MODEL: 0,
      RESILIENT: 0,
      "ACADEMIC INTERVENTION": 0,
      "CRITICAL INTERVENTION": 0,
    };
    for (const d of data) {
      if (c[d.welfare_quadrant] !== undefined) {
        c[d.welfare_quadrant]++;
      }
    }
    return c;
  }, [data]);

  const handlePointClick = (schoolId: string) => {
    if (onSchoolClick) {
      onSchoolClick(schoolId);
    } else {
      router.push(`/schools/${schoolId}`);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs transition-all">
      {/* Header & Quadrant Filter Pills */}
      <div className="flex flex-col gap-2.5 mb-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-slate-100 border border-slate-200 text-slate-700">
              <Grid className="w-3.5 h-3.5" />
            </span>
            <h2 className="text-sm font-bold text-slate-900 tracking-wide">
              2×2 School Welfare Gap Matrix
            </h2>
          </div>
          <p className="text-xs text-slate-500">
            Physical infrastructure readiness vs. academic foundational learning score.
          </p>
        </div>

        {/* Quadrant Count Badges (Flex-wrap to prevent truncation) */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          {Object.entries(quadrantConfig).map(([qKey, conf]) => (
            <div
              key={qKey}
              title={conf.desc}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs cursor-default transition-colors ${conf.bgBadge} ${conf.borderBadge}`}
            >
              <span
                className="w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: conf.color }}
              />
              <span className="font-semibold text-slate-700 text-[11px] whitespace-nowrap">
                {conf.name}:
              </span>
              <span className={`font-bold text-xs shrink-0 ${conf.textColor}`}>
                {counts[qKey] || 0}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Scatter Chart Canvas */}
      <div className="h-68 w-full">
        <ResponsiveContainer width="100%" height={260}>
          <ScatterChart margin={{ top: 15, right: 25, bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" opacity={0.9} />
            <XAxis
              type="number"
              dataKey="infrastructure_readiness_pct"
              name="Infrastructure Readiness"
              unit="%"
              domain={[0, 100]}
              tick={{ fill: "#64748B", fontSize: 11 }}
              label={{
                value: "Infrastructure Readiness (%) →",
                position: "bottom",
                fill: "#475569",
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
                fill: "#475569",
                fontSize: 11,
              }}
            />
            <ZAxis type="number" dataKey="enrollment" range={[35, 180]} name="Enrollment" />

            {/* Statutory Threshold Reference Lines */}
            <ReferenceLine
              x={50}
              stroke="#DC2626"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: "50% Infra Threshold",
                fill: "#B91C1C",
                fontSize: 10,
                position: "insideTopLeft",
              }}
            />
            <ReferenceLine
              y={65}
              stroke="#D97706"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: "65% FLN Cutoff",
                fill: "#B45309",
                fontSize: 10,
                position: "insideBottomRight",
              }}
            />

            <Tooltip
              cursor={{ strokeDasharray: "3 3", stroke: "#94A3B8" }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  const conf = quadrantConfig[d.welfare_quadrant] || {
                    color: "#0284C7",
                    name: d.welfare_quadrant,
                  };

                  return (
                    <div className="bg-white border border-slate-200 p-3 rounded-xl text-xs shadow-lg min-w-[220px]">
                      <div className="font-bold text-slate-900 text-sm truncate">{d.school_name}</div>
                      <div className="text-[11px] text-slate-500 mb-2 font-mono">
                        {d.district} &bull; {d.school_id}
                      </div>

                      <div className="space-y-1.5 text-xs">
                        <div className="flex justify-between text-slate-600">
                          <span>Infrastructure:</span>
                          <span className="text-slate-900 font-bold">
                            {d.infrastructure_readiness_pct.toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-600">
                          <span>Academic FLN:</span>
                          <span className="text-slate-900 font-bold">
                            {d.academic_score.toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-600">
                          <span>Priority Score:</span>
                          <span className="text-amber-700 font-bold">
                            {d.intervention_priority_score.toFixed(1)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center pt-1.5 border-t border-slate-100">
                          <span className="text-slate-500">Quadrant:</span>
                          <span
                            className="font-bold px-2 py-0.5 rounded text-[10px]"
                            style={{
                              backgroundColor: `${conf.color}15`,
                              color: conf.color,
                            }}
                          >
                            {d.welfare_quadrant}
                          </span>
                        </div>
                      </div>

                      <div className="mt-2 pt-1.5 border-t border-slate-100 text-[10.5px] text-sky-700 flex items-center gap-1 font-semibold">
                        <ExternalLink className="w-3 h-3" />
                        <span>Click dot to view School 360 profile</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />

            <Scatter
              name="Schools"
              data={data}
              onClick={(entry: any) => {
                const schoolId = entry?.school_id || entry?.payload?.school_id;
                if (schoolId) handlePointClick(schoolId);
              }}
              className="cursor-pointer"
            >
              {data.map((entry, index) => {
                const conf = quadrantConfig[entry.welfare_quadrant];
                return (
                  <Cell
                    key={`cell-${index}`}
                    fill={conf?.color || "#0284C7"}
                    fillOpacity={0.8}
                    stroke={entry.welfare_quadrant === "CRITICAL INTERVENTION" ? "#991B1B" : "transparent"}
                    strokeWidth={entry.welfare_quadrant === "CRITICAL INTERVENTION" ? 1 : 0}
                  />
                );
              })}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Instructions */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
        <span>
          Dot size proportional to student enrollment (30–200 range).
        </span>
        <span className="text-rose-700 font-semibold">
          {counts["CRITICAL INTERVENTION"] || 0} Priority Focus Institutions
        </span>
      </div>
    </div>
  );
}

import React from "react";
import { formatNumber, formatPercent, formatGap } from "@/lib/utils/formatters";
import type { MetricContext } from "@/lib/types";
import {
  Building2,
  UserCheck,
  GraduationCap,
  AlertTriangle,
  Zap,
  ShieldCheck,
  TrendingUp,
  TrendingDown,
  Database,
  CheckCircle2,
} from "lucide-react";

interface MetricCardProps {
  title: string;
  metricCtx?: MetricContext;
  customValue?: string | number;
  subtitle?: string;
  variant?: "neutral" | "emerald" | "amber" | "rose" | "sky";
  icon?: React.ComponentType<{ className?: string }>;
}

export function MetricCard({
  title,
  metricCtx,
  customValue,
  subtitle,
  variant = "neutral",
  icon: CustomIcon,
}: MetricCardProps) {
  const displayValue =
    customValue !== undefined
      ? customValue
      : metricCtx
      ? metricCtx.unit === "%"
        ? formatPercent(metricCtx.value)
        : formatNumber(metricCtx.value)
      : "—";

  const sub = subtitle || (metricCtx ? `${metricCtx.coverage_pct}% coverage` : undefined);

  const delta =
    metricCtx?.benchmark !== undefined && metricCtx?.benchmark !== null
      ? metricCtx.value - metricCtx.benchmark
      : null;

  // Domain icon inference if not explicitly provided
  const DefaultIcon = () => {
    const t = title.toLowerCase();
    if (t.includes("school")) return <Building2 className="w-4 h-4 text-sky-700" />;
    if (t.includes("attend")) return <UserCheck className="w-4 h-4 text-cyan-700" />;
    if (t.includes("fln") || t.includes("acad")) return <GraduationCap className="w-4 h-4 text-emerald-700" />;
    if (t.includes("prior")) return <AlertTriangle className="w-4 h-4 text-amber-700" />;
    if (t.includes("infra")) return <Zap className="w-4 h-4 text-indigo-700" />;
    if (t.includes("trust") || t.includes("qual")) return <ShieldCheck className="w-4 h-4 text-emerald-700" />;
    return <Database className="w-4 h-4 text-slate-500" />;
  };

  const IconComponent = CustomIcon || DefaultIcon;

  // Variant styling configurations - consulting white palette
  const variantStyles = {
    neutral: {
      card: "border-slate-200 bg-white hover:border-slate-300",
      iconBox: "bg-slate-50 border-slate-200 text-slate-600",
    },
    sky: {
      card: "border-slate-200 bg-white hover:border-sky-300",
      iconBox: "bg-sky-50 border-sky-200 text-sky-700",
    },
    emerald: {
      card: "border-slate-200 bg-white hover:border-emerald-300",
      iconBox: "bg-emerald-50 border-emerald-200 text-emerald-700",
    },
    amber: {
      card: "border-slate-200 bg-white hover:border-amber-300",
      iconBox: "bg-amber-50 border-amber-200 text-amber-700",
    },
    rose: {
      card: "border-slate-200 bg-white hover:border-rose-300",
      iconBox: "bg-rose-50 border-rose-200 text-rose-700",
    },
  }[variant];

  return (
    <div
      className={`relative card-lift rounded-2xl border p-5 shadow-[0_1px_3px_rgba(15,23,42,0.04)] flex flex-col justify-between overflow-hidden ${variantStyles.card}`}
    >
      {/* Top Section: Category Label & Primary Value */}
      <div>
        <div className="flex items-center gap-2.5 mb-3 min-h-[26px]">
          <div className={`w-7 h-7 rounded-lg border flex items-center justify-center shrink-0 ${variantStyles.iconBox}`}>
            <IconComponent />
          </div>
          <span className="text-[10px] font-semibold text-slate-400 tracking-[0.08em] uppercase leading-tight">
            {title}
          </span>
        </div>

        {/* Primary Value + Delta Pill */}
        <div className="flex items-baseline gap-2 flex-wrap mt-1">
          <span className="metric-value text-[28px] font-extrabold text-slate-900">
            {displayValue}
          </span>

          {delta !== null && (
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                delta >= 0
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : "bg-rose-50 text-rose-700 border-rose-200"
              }`}
            >
              {delta >= 0 ? (
                <TrendingUp className="w-3 h-3 text-emerald-600" />
              ) : (
                <TrendingDown className="w-3 h-3 text-rose-600" />
              )}
              {formatGap(delta)} pts vs BM
            </span>
          )}
        </div>
      </div>

      {/* Bottom Status / Subtitle Strip */}
      <div className="pt-2.5 mt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
        <div className="flex items-center gap-1.5 font-medium text-emerald-700 truncate">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
          <span className="truncate">{sub || "Verified Clean"}</span>
        </div>

        {/* Retain metric source accessibly for audit/tests without visual clutter */}
        {metricCtx?.source && (
          <span className="sr-only">{metricCtx.source}</span>
        )}
      </div>
    </div>
  );
}

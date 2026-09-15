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
    if (t.includes("school")) return <Building2 className="w-4 h-4 text-sky-400" />;
    if (t.includes("attend")) return <UserCheck className="w-4 h-4 text-cyan-400" />;
    if (t.includes("fln") || t.includes("acad")) return <GraduationCap className="w-4 h-4 text-emerald-400" />;
    if (t.includes("prior")) return <AlertTriangle className="w-4 h-4 text-amber-400" />;
    if (t.includes("infra")) return <Zap className="w-4 h-4 text-indigo-400" />;
    if (t.includes("trust") || t.includes("qual")) return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
    return <Database className="w-4 h-4 text-slate-400" />;
  };

  const IconComponent = CustomIcon || DefaultIcon;

  // Variant styling configurations
  const variantStyles = {
    neutral: {
      card: "border-slate-800/80 hover:border-slate-700 bg-gradient-to-b from-[#151D2E]/90 to-[#0F172A]/90",
      topAccent: "bg-gradient-to-r from-slate-500/40 via-sky-500/40 to-transparent",
      iconBox: "bg-slate-800/60 border-slate-700/60 text-slate-300",
    },
    sky: {
      card: "border-sky-500/30 hover:border-sky-500/60 bg-gradient-to-b from-sky-950/20 via-[#151D2E]/90 to-[#0F172A]/90 shadow-sky-500/5",
      topAccent: "bg-gradient-to-r from-sky-500 via-sky-400 to-transparent",
      iconBox: "bg-sky-500/10 border-sky-500/30 text-sky-400",
    },
    emerald: {
      card: "border-emerald-500/30 hover:border-emerald-500/60 bg-gradient-to-b from-emerald-950/20 via-[#151D2E]/90 to-[#0F172A]/90 shadow-emerald-500/5",
      topAccent: "bg-gradient-to-r from-emerald-500 via-emerald-400 to-transparent",
      iconBox: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
    },
    amber: {
      card: "border-amber-500/30 hover:border-amber-500/60 bg-gradient-to-b from-amber-950/20 via-[#151D2E]/90 to-[#0F172A]/90 shadow-amber-500/5",
      topAccent: "bg-gradient-to-r from-amber-500 via-amber-400 to-transparent",
      iconBox: "bg-amber-500/10 border-amber-500/30 text-amber-400",
    },
    rose: {
      card: "border-rose-500/30 hover:border-rose-500/60 bg-gradient-to-b from-rose-950/20 via-[#151D2E]/90 to-[#0F172A]/90 shadow-rose-500/5",
      topAccent: "bg-gradient-to-r from-rose-500 via-rose-400 to-transparent",
      iconBox: "bg-rose-500/10 border-rose-500/30 text-rose-400",
    },
  }[variant];

  return (
    <div
      className={`relative group rounded-xl border backdrop-blur-md p-4 transition-all duration-200 shadow-md hover:shadow-lg flex flex-col justify-between overflow-hidden ${variantStyles.card}`}
    >
      {/* Sleek top glowing hairline accent */}
      <div className={`absolute top-0 left-0 right-0 h-[2px] opacity-80 ${variantStyles.topAccent}`} />

      {/* Header: Icon + Title */}
      <div>
        <div className="flex items-center gap-2 mb-2 min-h-[32px]">
          <div className={`w-7 h-7 rounded-lg border flex items-center justify-center shrink-0 ${variantStyles.iconBox}`}>
            <IconComponent />
          </div>
          <span className="text-[10.5px] font-bold text-slate-300 tracking-wider uppercase leading-snug">
            {title}
          </span>
        </div>

        {/* Primary Value + Delta Pill */}
        <div className="flex items-baseline gap-2 flex-wrap mt-1">
          <span className="text-2xl sm:text-3xl font-black text-white tracking-tight drop-shadow-sm">
            {displayValue}
          </span>

          {delta !== null && (
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full border ${
                delta >= 0
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                  : "bg-rose-500/10 text-rose-400 border-rose-500/30"
              }`}
            >
              {delta >= 0 ? (
                <TrendingUp className="w-3 h-3 text-emerald-400" />
              ) : (
                <TrendingDown className="w-3 h-3 text-rose-400" />
              )}
              {formatGap(delta)} pts vs BM
            </span>
          )}
        </div>
      </div>

      {/* Bottom Lineage & Quality Strip */}
      <div className="pt-2 mt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400 gap-1">
        <div className="flex items-center gap-1 truncate text-slate-400 font-medium">
          <CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />
          <span className="truncate">{sub || "Canonical Mart"}</span>
        </div>

        {metricCtx?.source && (
          <div
            title={`Governed Source Table: ${metricCtx.source}`}
            className="flex items-center gap-1 font-mono text-[8.5px] text-slate-400 bg-slate-900/90 border border-slate-800 px-1 py-0.5 rounded shrink-0"
          >
            <Database className="w-2.5 h-2.5 text-sky-400 shrink-0" />
            <span className="max-w-[75px] truncate">{metricCtx.source}</span>
          </div>
        )}
      </div>
    </div>
  );
}

import React from "react";
import type { DynamicAlert } from "@/lib/types";
import {
  AlertOctagon,
  AlertTriangle,
  Lightbulb,
  ShieldCheck,
  ArrowUpRight,
  TrendingUp,
} from "lucide-react";
import Link from "next/link";

export function AlertBanner({ alerts }: { alerts: DynamicAlert[] }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 my-2">
      {alerts.map((alert, idx) => {
        const isCritical = alert.level === "critical";
        const isWarning = alert.level === "warning";

        const config = isCritical
          ? {
              card: "border-rose-500/30 bg-gradient-to-br from-rose-950/20 via-[#151D2E]/90 to-[#0F172A]/90 hover:border-rose-500/50 shadow-rose-950/20",
              badge: "bg-rose-500/15 text-rose-300 border-rose-500/30",
              badgeText: "CRITICAL WELFARE",
              icon: AlertOctagon,
              iconColor: "text-rose-400",
              accentBorder: "border-l-4 border-l-rose-500",
              linkHref: "/intervention",
              linkText: "Review Intervention Queue",
            }
          : isWarning
          ? {
              card: "border-amber-500/30 bg-gradient-to-br from-amber-950/20 via-[#151D2E]/90 to-[#0F172A]/90 hover:border-amber-500/50 shadow-amber-950/20",
              badge: "bg-amber-500/15 text-amber-300 border-amber-500/30",
              badgeText: "FACILITY BOTTLENECK",
              icon: AlertTriangle,
              iconColor: "text-amber-400",
              accentBorder: "border-l-4 border-l-amber-500",
              linkHref: "/welfare",
              linkText: "Inspect Infrastructure Gap",
            }
          : {
              card: "border-sky-500/30 bg-gradient-to-br from-sky-950/20 via-[#151D2E]/90 to-[#0F172A]/90 hover:border-sky-500/50 shadow-sky-950/20",
              badge: "bg-sky-500/15 text-sky-300 border-sky-500/30",
              badgeText: "EMPIRICAL INSIGHT",
              icon: Lightbulb,
              iconColor: "text-sky-400",
              accentBorder: "border-l-4 border-l-sky-500",
              linkHref: "/schools",
              linkText: "Audit School Performance",
            };

        const Icon = config.icon;

        return (
          <div
            key={idx}
            className={`relative rounded-xl border p-4 backdrop-blur-md transition-all duration-200 shadow-lg flex flex-col justify-between overflow-hidden group ${config.card} ${config.accentBorder}`}
          >
            {/* Header: Badge + Category Title */}
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span
                  className={`inline-flex items-center gap-1.5 text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider ${config.badge}`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      isCritical ? "bg-rose-400 animate-ping" : isWarning ? "bg-amber-400" : "bg-sky-400"
                    }`}
                  />
                  {config.badgeText}
                </span>

                <span className="text-[11px] font-semibold text-slate-400 truncate">
                  {alert.title}
                </span>
              </div>

              {/* Core Finding Headline */}
              <div className="text-sm font-bold text-white tracking-tight leading-snug mt-1 flex items-start gap-2">
                <Icon className={`w-4 h-4 shrink-0 mt-0.5 ${config.iconColor}`} />
                <span>{alert.finding}</span>
              </div>

              {/* Structured Metadata: Evidence & Strategic Interpretation */}
              <div className="mt-3 space-y-2 text-xs">
                <div className="bg-slate-900/70 border border-slate-800/80 rounded-lg p-2.5">
                  <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1 mb-1">
                    <TrendingUp className="w-3 h-3 text-sky-400" />
                    Analytical Evidence
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    {alert.evidence}
                  </p>
                </div>

                <div className="bg-slate-900/50 border border-slate-800/60 rounded-lg p-2.5">
                  <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1 mb-1">
                    <Lightbulb className="w-3 h-3 text-amber-400" />
                    Executive Guidance
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    {alert.interpretation}
                  </p>
                </div>
              </div>
            </div>

            {/* Footer with statutory limitation & drilldown link */}
            <div className="pt-3 mt-3 border-t border-slate-800/80 flex items-center justify-between gap-2 text-[10px]">
              <div className="flex items-center gap-1.5 text-slate-400 italic truncate" title={alert.limitation}>
                <ShieldCheck className="w-3 h-3 text-emerald-400 shrink-0" />
                <span className="truncate">{alert.limitation}</span>
              </div>

              <Link
                href={config.linkHref}
                className="inline-flex items-center gap-1 font-semibold text-sky-400 hover:text-sky-300 shrink-0 transition-colors"
              >
                <span>Action</span>
                <ArrowUpRight className="w-3 h-3" />
              </Link>
            </div>
          </div>
        );
      })}
    </div>
  );
}

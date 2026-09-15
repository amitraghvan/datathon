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
              card: "border-slate-200 bg-white hover:border-rose-300",
              badge: "bg-rose-50 text-rose-700 border-rose-200",
              badgeText: "CRITICAL WELFARE",
              icon: AlertOctagon,
              iconColor: "text-rose-600",
              accentBorder: "border-l-4 border-l-rose-500",
              linkHref: "/intervention",
              linkText: "Review Intervention Queue",
            }
          : isWarning
          ? {
              card: "border-slate-200 bg-white hover:border-amber-300",
              badge: "bg-amber-50 text-amber-700 border-amber-200",
              badgeText: "FACILITY BOTTLENECK",
              icon: AlertTriangle,
              iconColor: "text-amber-600",
              accentBorder: "border-l-4 border-l-amber-500",
              linkHref: "/welfare",
              linkText: "Inspect Infrastructure Gap",
            }
          : {
              card: "border-slate-200 bg-white hover:border-sky-300",
              badge: "bg-sky-50 text-sky-700 border-sky-200",
              badgeText: "EMPIRICAL INSIGHT",
              icon: Lightbulb,
              iconColor: "text-sky-600",
              accentBorder: "border-l-4 border-l-sky-600",
              linkHref: "/schools",
              linkText: "Audit School Performance",
            };

        const Icon = config.icon;

        return (
          <div
            key={idx}
            className={`relative rounded-xl border p-4.5 transition-all duration-150 shadow-2xs flex flex-col justify-between overflow-hidden group ${config.card} ${config.accentBorder}`}
          >
            {/* Header: Badge + Category Title */}
            <div>
              <div className="flex items-center justify-between gap-2 mb-2.5">
                <span
                  className={`inline-flex items-center gap-1.5 text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider ${config.badge}`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      isCritical ? "bg-rose-500" : isWarning ? "bg-amber-500" : "bg-sky-600"
                    }`}
                  />
                  {config.badgeText}
                </span>

                <span className="text-[11px] font-semibold text-slate-500 truncate">
                  {alert.title}
                </span>
              </div>

              {/* Core Finding Headline */}
              <div className="text-sm font-bold text-slate-900 tracking-tight leading-snug flex items-start gap-2">
                <Icon className={`w-4 h-4 shrink-0 mt-0.5 ${config.iconColor}`} />
                <span>{alert.finding}</span>
              </div>

              {/* Sleek Briefing Body */}
              <div className="mt-3 bg-slate-50/70 border border-slate-200/70 rounded-lg p-3 space-y-2">
                <div className="flex items-start gap-2 text-xs">
                  <span className="text-[10px] uppercase font-bold text-sky-700 bg-sky-50 border border-sky-200/80 px-1.5 py-0.5 rounded shrink-0">
                    Evidence
                  </span>
                  <p className="text-slate-600 text-[11.5px] leading-relaxed">
                    {alert.evidence}
                  </p>
                </div>

                <div className="flex items-start gap-2 text-xs pt-2 border-t border-slate-200/60">
                  <span className="text-[10px] uppercase font-bold text-amber-700 bg-amber-50 border border-amber-200/80 px-1.5 py-0.5 rounded shrink-0">
                    Guidance
                  </span>
                  <p className="text-slate-600 text-[11.5px] leading-relaxed">
                    {alert.interpretation}
                  </p>
                </div>
              </div>
            </div>

            {/* Footer with statutory limitation & action link */}
            <div className="pt-2.5 mt-3 border-t border-slate-100 flex items-center justify-between gap-2 text-[10.5px]">
              <div className="flex items-center gap-1.5 text-slate-400 text-[10px] truncate" title={alert.limitation}>
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span className="truncate">{alert.limitation}</span>
              </div>

              <Link
                href={config.linkHref}
                className="inline-flex items-center gap-1 text-[11px] font-bold text-sky-700 hover:text-sky-800 shrink-0 transition-colors px-2 py-0.5 rounded bg-sky-50 hover:bg-sky-100 border border-sky-200"
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

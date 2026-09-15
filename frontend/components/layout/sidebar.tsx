"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  GraduationCap,
  Building2,
  Utensils,
  AlertTriangle,
  ShieldCheck,
  Bot,
  Layers,
  CheckCircle2,
  Database,
} from "lucide-react";
import { cn } from "@/lib/utils/formatters";

const navigationItems = [
  { name: "Executive Overview", href: "/", icon: LayoutDashboard },
  { name: "School 360", href: "/schools", icon: GraduationCap },
  { name: "Welfare & Infrastructure", href: "/welfare", icon: Building2 },
  { name: "Mid-Day Meals", href: "/procurement", icon: Utensils },
  { name: "Intervention Command", href: "/intervention", icon: AlertTriangle },
  { name: "Data Trust & Governance", href: "/quality", icon: ShieldCheck },
  { name: "AI Analyst (Phase 6)", href: "/ai-analyst", icon: Bot },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gradient-to-b from-[#0F172A] to-[#0B0F19] border-r border-slate-800 flex flex-col h-screen sticky top-0 select-none z-30 shrink-0">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800 shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-500 to-blue-700 flex items-center justify-center text-white font-bold shadow-md shadow-sky-500/20 ring-1 ring-sky-400/40">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-white text-base tracking-wide flex items-center gap-1.5">
              EDUPULSE AI
              <span className="text-[9px] font-extrabold bg-sky-500/20 text-sky-400 px-1.5 py-0.5 rounded border border-sky-500/40">
                PRO
              </span>
            </div>
            <div className="text-[10px] font-medium text-slate-400 tracking-tight">
              Welfare Command Center
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
          Decision Intelligence
        </div>
        {navigationItems.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "relative flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-200 group",
                isActive
                  ? "bg-gradient-to-r from-sky-500/20 to-sky-600/10 text-sky-400 border border-sky-500/40 shadow-sm shadow-sky-500/10"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              )}
            >
              {isActive && (
                <span className="absolute left-0 top-2 bottom-2 w-1 bg-sky-500 rounded-r-full" />
              )}
              <Icon
                className={cn(
                  "w-4 h-4 shrink-0 transition-colors",
                  isActive ? "text-sky-400" : "text-slate-400 group-hover:text-slate-200"
                )}
              />
              <span className="truncate">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer Status Widget - Robust, Non-clipping, Production Polish */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/60 shrink-0">
        <div className="bg-slate-900/90 rounded-xl p-3 border border-slate-800/80 shadow-inner">
          <div className="flex items-center justify-between gap-1 mb-1.5">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Data Trust Index</span>
            </div>
            <span className="text-[9px] font-extrabold px-1.5 py-0.2 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              VERIFIED
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div className="text-base font-black text-white flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
              <span>94.6</span>
              <span className="text-xs text-slate-400 font-normal">/ 100</span>
            </div>
            <div className="text-[10px] text-slate-400 flex items-center gap-1 font-mono">
              <Database className="w-3 h-3 text-sky-400" />
              <span>DuckDB</span>
            </div>
          </div>

          {/* Mini progress bar */}
          <div className="w-full bg-slate-800 rounded-full h-1 mt-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-emerald-500 to-sky-400 h-1 rounded-full transition-all duration-500"
              style={{ width: "94.6%" }}
            />
          </div>

          <div className="mt-2 pt-1.5 border-t border-slate-800/60 flex items-center justify-between text-[9px] text-slate-400">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />
              <span>10 Quality Gates Pass</span>
            </span>
            <span className="text-sky-400 font-semibold">Live Mart</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

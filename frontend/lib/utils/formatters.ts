import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatNumber(val: number | null | undefined, decimals: number = 0): string {
  if (val === null || val === undefined || isNaN(val)) return "-";
  return val.toLocaleString("en-IN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatPercent(val: number | null | undefined, decimals: number = 1): string {
  if (val === null || val === undefined || isNaN(val)) return "-";
  return `${val.toFixed(decimals)}%`;
}

export function formatINR(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "₹0";
  if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
  if (val >= 100000) return `₹${(val / 100000).toFixed(2)} Lakh`;
  if (val >= 1000) return `₹${(val / 1000).toFixed(1)}k`;
  return `₹${val.toFixed(0)}`;
}

export function formatKG(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "0 kg";
  if (val >= 1000) return `${(val / 1000).toFixed(1)} MT`;
  return `${val.toFixed(0)} kg`;
}

export function formatGap(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "0.0";
  const prefix = val > 0 ? "+" : "";
  return `${prefix}${val.toFixed(1)}`;
}

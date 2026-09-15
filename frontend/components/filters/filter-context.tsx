"use client";

import React, { createContext, useContext, useState } from "react";
import type { FilterState } from "@/lib/types";

interface FilterContextType {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  setFilterValue: (key: keyof FilterState, value: string | undefined) => void;
  resetFilters: () => void;
  activeCount: number;
}

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export function FilterProvider({ children }: { children: React.ReactNode }) {
  const [filters, setFilters] = useState<FilterState>({});

  const setFilterValue = (key: keyof FilterState, value: string | undefined) => {
    setFilters((prev) => {
      const next = { ...prev };
      if (value === undefined || value === "" || value === "ALL") {
        delete next[key];
      } else {
        next[key] = value;
      }
      // If district changed, reset child block
      if (key === "district") {
        delete next.block;
      }
      return next;
    });
  };

  const resetFilters = () => setFilters({});

  const activeCount = Object.keys(filters).filter(
    (k) => filters[k as keyof FilterState] !== undefined && filters[k as keyof FilterState] !== "ALL"
  ).length;

  return (
    <FilterContext.Provider
      value={{
        filters,
        setFilters,
        setFilterValue,
        resetFilters,
        activeCount,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useGlobalFilters() {
  const ctx = useContext(FilterContext);
  if (!ctx) {
    throw new Error("useGlobalFilters must be used within a FilterProvider");
  }
  return ctx;
}

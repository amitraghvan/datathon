/**
 * TanStack Query Hooks for Governed API endpoints
 */

import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "./client";
import type {
  AssessmentSubjectItem,
  AttendanceAcademicAssociationResponse,
  AttendanceTimeseriesPoint,
  DimensionOptionsResponse,
  DistrictDetailResponse,
  DistrictListResponse,
  ExecutiveOverviewResponse,
  FilterState,
  PrioritySchoolItem,
  ProcurementOverviewResponse,
  QualitySummaryResponse,
  RiskSummaryResponse,
  SchoolProcurementSummary,
  SchoolProfileResponse,
  SchoolSummaryItem,
  WelfareOverviewResponse,
} from "../types";

export function useOverview(filters: FilterState) {
  return useQuery<ExecutiveOverviewResponse>({
    queryKey: ["overview", filters],
    queryFn: () => fetchApi<ExecutiveOverviewResponse>("/overview", filters),
    staleTime: 60 * 1000,
  });
}

export function useDistricts() {
  return useQuery<DistrictListResponse>({
    queryKey: ["districts"],
    queryFn: () => fetchApi<DistrictListResponse>("/districts"),
    staleTime: 5 * 60 * 1000,
  });
}

export function useDistrictDetail(district: string) {
  return useQuery<DistrictDetailResponse>({
    queryKey: ["district", district],
    queryFn: () => fetchApi<DistrictDetailResponse>(`/districts/${encodeURIComponent(district)}`),
    enabled: Boolean(district),
  });
}

export function useDimensionOptions() {
  return useQuery<DimensionOptionsResponse>({
    queryKey: ["dimensions"],
    queryFn: () => fetchApi<DimensionOptionsResponse>("/schools/dimensions"),
    staleTime: 10 * 60 * 1000,
  });
}

export function useSchools(
  filters: FilterState,
  page: number = 1,
  pageSize: number = 25,
  search?: string
) {
  return useQuery<{
    items: SchoolSummaryItem[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }>({
    queryKey: ["schools", filters, page, pageSize, search],
    queryFn: () =>
      fetchApi("/schools", {
        ...filters,
        page,
        page_size: pageSize,
        search,
      }),
  });
}

export function useSchoolProfile(schoolId: string) {
  return useQuery<SchoolProfileResponse>({
    queryKey: ["school", schoolId],
    queryFn: () => fetchApi<SchoolProfileResponse>(`/schools/${schoolId}`),
    enabled: Boolean(schoolId),
  });
}

export function useSchoolAttendance(schoolId: string) {
  return useQuery<AttendanceTimeseriesPoint[]>({
    queryKey: ["school", schoolId, "attendance"],
    queryFn: () => fetchApi<AttendanceTimeseriesPoint[]>(`/schools/${schoolId}/attendance`),
    enabled: Boolean(schoolId),
  });
}

export function useSchoolAcademics(schoolId: string) {
  return useQuery<AssessmentSubjectItem[]>({
    queryKey: ["school", schoolId, "academics"],
    queryFn: () => fetchApi<AssessmentSubjectItem[]>(`/schools/${schoolId}/academics`),
    enabled: Boolean(schoolId),
  });
}

export function useSchoolProcurement(schoolId: string) {
  return useQuery<SchoolProcurementSummary | null>({
    queryKey: ["school", schoolId, "procurement"],
    queryFn: () => fetchApi<SchoolProcurementSummary | null>(`/schools/${schoolId}/procurement`),
    enabled: Boolean(schoolId),
  });
}

export function useWelfareOverview(filters: FilterState) {
  return useQuery<WelfareOverviewResponse>({
    queryKey: ["welfare", filters],
    queryFn: () => fetchApi<WelfareOverviewResponse>("/welfare/overview", filters),
    staleTime: 60 * 1000,
  });
}

export function useProcurementOverview(filters: FilterState) {
  return useQuery<ProcurementOverviewResponse>({
    queryKey: ["procurement", filters],
    queryFn: () => fetchApi<ProcurementOverviewResponse>("/procurement/overview", filters),
    staleTime: 60 * 1000,
  });
}

export function useRiskSummary(filters: FilterState) {
  return useQuery<RiskSummaryResponse>({
    queryKey: ["risk", filters],
    queryFn: () => fetchApi<RiskSummaryResponse>("/risk/summary", filters),
    staleTime: 60 * 1000,
  });
}

export function usePrioritySchools(filters: FilterState, limit: number = 50) {
  return useQuery<PrioritySchoolItem[]>({
    queryKey: ["priorities", filters, limit],
    queryFn: () => fetchApi<PrioritySchoolItem[]>("/risk/priorities", { ...filters, limit }),
    staleTime: 60 * 1000,
  });
}

export function useQualitySummary() {
  return useQuery<QualitySummaryResponse>({
    queryKey: ["quality"],
    queryFn: () => fetchApi<QualitySummaryResponse>("/quality/summary"),
    staleTime: 5 * 60 * 1000,
  });
}

export function useInsightsAssociation() {
  return useQuery<AttendanceAcademicAssociationResponse>({
    queryKey: ["insights", "association"],
    queryFn: () => fetchApi<AttendanceAcademicAssociationResponse>("/insights/association"),
    staleTime: 10 * 60 * 1000,
  });
}

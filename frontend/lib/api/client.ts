/**
 * Governed API Client for EduPulse AI backend services.
 */

export function getApiBaseUrl(): string {
  let envUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  // Auto-correct common typo (datathon-gaqq -> datathon-qaqq)
  if (envUrl && envUrl.includes("datathon-gaqq.onrender.com")) {
    envUrl = envUrl.replace("datathon-gaqq.onrender.com", "datathon-qaqq.onrender.com");
  }

  // If envUrl is explicitly set to a valid non-localhost URL, use it
  if (envUrl && !envUrl.includes("localhost") && !envUrl.includes("127.0.0.1")) {
    return envUrl.replace(/\/+$/, "");
  }

  // In production browser (e.g. Vercel deployment), always fall back to live Render backend
  if (typeof window !== "undefined" && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
    return "https://datathon-qaqq.onrender.com/api/v1";
  }

  return (envUrl || "http://localhost:8000/api/v1").replace(/\/+$/, "");
}

export const API_BASE_URL = getApiBaseUrl();

export class ApiError extends Error {
  code: string;
  status: number;
  details: any;

  constructor(message: string, code: string = "API_ERROR", status: number = 500, details: any = null) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export async function fetchApi<T>(
  endpoint: string,
  params?: Record<string, any>,
  options?: RequestInit
): Promise<T> {
  const baseUrl = getApiBaseUrl();
  let url = `${baseUrl}${endpoint}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== "" && val !== "ALL") {
        searchParams.append(key, String(val));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += (url.includes("?") ? "&" : "?") + queryString;
    }
  }

  try {
    const res = await fetch(url, {
      method: options?.method || "GET",
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
      body: options?.body,
      next: { revalidate: 0 }, // dynamic updates
    });

    if (!res.ok) {
      let errJson: any = null;
      try {
        errJson = await res.json();
      } catch {
        // Not JSON
      }

      const message = errJson?.error?.message || `Request failed with status ${res.status}`;
      const code = errJson?.error?.code || "HTTP_ERROR";
      throw new ApiError(message, code, res.status, errJson?.error?.details);
    }

    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(err.message || "Network connection failed", "NETWORK_ERROR", 0);
  }
}

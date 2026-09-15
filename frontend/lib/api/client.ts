/**
 * Governed API Client for EduPulse AI backend services.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

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
  let url = `${API_BASE_URL}${endpoint}`;

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

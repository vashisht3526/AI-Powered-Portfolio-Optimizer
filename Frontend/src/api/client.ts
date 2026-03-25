// Centralized API base for the FastAPI backend.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function parseError(response: Response) {
  try {
    const data = await response.json();
    if (typeof data === "string") return data;
    if (data?.detail) return data.detail;
    return JSON.stringify(data);
  } catch (error) {
    return response.statusText || "Request failed";
  }
}

export async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await parseError(response);
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export { API_BASE_URL };

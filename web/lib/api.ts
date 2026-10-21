export type ClientSettings = {
  apiUrl: string;
  workspace: string;
  apiKey: string;
};

const defaults: ClientSettings = {
  apiUrl: process.env.NEXT_PUBLIC_TUNEFORGE_API_URL || "http://localhost:8000",
  workspace: "default",
  apiKey: "",
};

export function getSettings(): ClientSettings {
  if (typeof window === "undefined") return defaults;

  return {
    apiUrl: localStorage.getItem("tuneforge.apiUrl") || defaults.apiUrl,
    workspace: localStorage.getItem("tuneforge.workspace") || defaults.workspace,
    apiKey: localStorage.getItem("tuneforge.apiKey") || "",
  };
}

export function saveSettings(settings: ClientSettings) {
  localStorage.setItem("tuneforge.apiUrl", settings.apiUrl);
  localStorage.setItem("tuneforge.workspace", settings.workspace);
  localStorage.setItem("tuneforge.apiKey", settings.apiKey);
}

export async function api<T>(
  path: string,
  init: RequestInit = {},
  override?: ClientSettings,
): Promise<T> {
  const settings = override || getSettings();
  const headers = new Headers(init.headers || {});
  headers.set("Content-Type", "application/json");
  headers.set("X-TuneForge-Workspace", settings.workspace);
  if (settings.apiKey) headers.set("X-TuneForge-API-Key", settings.apiKey);

  const response = await fetch(`${settings.apiUrl}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

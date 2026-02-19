import type { Message } from "./types";

const API_BASE_URL = (import.meta.env.VITE_BACKEND_URL ?? "").trim();

const buildUrl = (path: string): string =>
  API_BASE_URL ? `${API_BASE_URL}${path}` : path;

const authHeaders = (authKey: string): Record<string, string> => ({
  "Content-Type": "application/json",
  ...(authKey ? { Authorization: `Bearer ${authKey}` } : {}),
});

export async function fetchMessages(
  chatId: string,
  authKey: string,
): Promise<Message[]> {
  const res = await fetch(buildUrl(`/api/conversations/${chatId}/messages`), {
    headers: authHeaders(authKey),
  });
  if (!res.ok) throw new Error(`Failed to fetch messages (${res.status})`);
  return res.json();
}

export async function sendMessage(
  chatId: string,
  message: string,
  metadata: {
    systemInstruction?: string | null;
    datastorePath?: string | null;
    parameters?: Record<string, unknown> | null;
  },
  authKey: string,
): Promise<{ text: string }> {
  const res = await fetch(buildUrl("/api/chat"), {
    method: "POST",
    headers: authHeaders(authKey),
    body: JSON.stringify({
      chatId,
      message,
      systemInstruction: metadata.systemInstruction ?? null,
      datastorePath: metadata.datastorePath ?? null,
      parameters: metadata.parameters ?? null,
    }),
  });
  if (!res.ok) throw new Error(`Request failed with status ${res.status}`);
  return res.json();
}

export async function saveMessages(
  chatId: string,
  messages: Message[],
  authKey: string,
): Promise<void> {
  const res = await fetch(buildUrl(`/api/conversations/${chatId}/messages`), {
    method: "POST",
    headers: authHeaders(authKey),
    body: JSON.stringify(messages),
  });
  if (!res.ok) throw new Error(`Failed to save messages (${res.status})`);
}

export async function deleteMessages(
  chatId: string,
  authKey: string,
): Promise<void> {
  const res = await fetch(buildUrl(`/api/conversations/${chatId}`), {
    method: "DELETE",
    headers: authHeaders(authKey),
  });
  if (!res.ok) throw new Error(`Failed to delete conversation (${res.status})`);
}

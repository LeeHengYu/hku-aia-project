import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  fetchMessages,
  sendMessage,
  saveMessages,
  deleteMessages,
} from "../../lib/api";
import type { Message } from "../../lib/types";

const AUTH_KEY = "test-bearer-token";
const CHAT_ID = "chat-123";

// Helpers to stub global fetch with a canned response.
const stubFetch = (status: number, body: unknown) => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(body),
    }),
  );
};

const lastCall = () =>
  (fetch as ReturnType<typeof vi.fn>).mock.calls[0] as [string, RequestInit];

beforeEach(() => {
  vi.restoreAllMocks();
});

// ─── fetchMessages ────────────────────────────────────────────────────────────

describe("fetchMessages", () => {
  it("calls the correct endpoint and returns parsed messages", async () => {
    const messages: Message[] = [
      { id: "1", role: "user", content: "hi", createdAt: "2024-01-01T00:00:00Z" },
    ];
    stubFetch(200, messages);

    const result = await fetchMessages(CHAT_ID, AUTH_KEY);

    const [url, opts] = lastCall();
    expect(url).toBe(`/api/conversations/${CHAT_ID}/messages`);
    expect(opts.headers).toMatchObject({ Authorization: `Bearer ${AUTH_KEY}` });
    expect(result).toEqual(messages);
  });

  it("omits the Authorization header when authKey is empty", async () => {
    stubFetch(200, []);

    await fetchMessages(CHAT_ID, "");

    const [, opts] = lastCall();
    expect((opts.headers as Record<string, string>)["Authorization"]).toBeUndefined();
  });

  it("throws when the response is not ok", async () => {
    stubFetch(403, {});

    await expect(fetchMessages(CHAT_ID, AUTH_KEY)).rejects.toThrow("403");
  });

  it("throws with the response status in the message", async () => {
    stubFetch(500, {});

    await expect(fetchMessages(CHAT_ID, AUTH_KEY)).rejects.toThrow("500");
  });
});

// ─── sendMessage ──────────────────────────────────────────────────────────────

describe("sendMessage", () => {
  it("POSTs to /api/chat with the correct body", async () => {
    stubFetch(200, { text: "AI reply" });

    const result = await sendMessage(
      CHAT_ID,
      "Hello",
      { systemInstruction: "Be helpful", datastorePath: "/store/v1", parameters: null },
      AUTH_KEY,
    );

    const [url, opts] = lastCall();
    expect(url).toBe("/api/chat");
    expect(opts.method).toBe("POST");

    const body = JSON.parse(opts.body as string);
    expect(body).toEqual({
      chatId: CHAT_ID,
      message: "Hello",
      systemInstruction: "Be helpful",
      datastorePath: "/store/v1",
      parameters: null,
    });
    expect(result).toEqual({ text: "AI reply" });
  });

  it("coerces undefined metadata fields to null", async () => {
    stubFetch(200, { text: "ok" });

    await sendMessage(CHAT_ID, "Hello", {}, AUTH_KEY);

    const [, opts] = lastCall();
    const body = JSON.parse(opts.body as string);
    expect(body.systemInstruction).toBeNull();
    expect(body.datastorePath).toBeNull();
    expect(body.parameters).toBeNull();
  });

  it("includes the Authorization header", async () => {
    stubFetch(200, { text: "ok" });

    await sendMessage(CHAT_ID, "Hello", {}, AUTH_KEY);

    const [, opts] = lastCall();
    expect(opts.headers).toMatchObject({ Authorization: `Bearer ${AUTH_KEY}` });
  });

  it("throws on a non-ok response", async () => {
    stubFetch(500, {});

    await expect(sendMessage(CHAT_ID, "Hello", {}, AUTH_KEY)).rejects.toThrow("500");
  });
});

// ─── saveMessages ─────────────────────────────────────────────────────────────

describe("saveMessages", () => {
  const messages: Message[] = [
    { id: "m1", role: "user", content: "hi", createdAt: "2024-01-01T00:00:00Z" },
  ];

  it("POSTs messages to the conversations endpoint", async () => {
    stubFetch(200, null);

    await saveMessages(CHAT_ID, messages, AUTH_KEY);

    const [url, opts] = lastCall();
    expect(url).toBe(`/api/conversations/${CHAT_ID}/messages`);
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body as string)).toEqual(messages);
  });

  it("throws on failure", async () => {
    stubFetch(422, {});

    await expect(saveMessages(CHAT_ID, [], AUTH_KEY)).rejects.toThrow("422");
  });
});

// ─── deleteMessages ───────────────────────────────────────────────────────────

describe("deleteMessages", () => {
  it("sends DELETE to the conversation endpoint", async () => {
    stubFetch(200, null);

    await deleteMessages(CHAT_ID, AUTH_KEY);

    const [url, opts] = lastCall();
    expect(url).toBe(`/api/conversations/${CHAT_ID}`);
    expect(opts.method).toBe("DELETE");
  });

  it("includes the Authorization header", async () => {
    stubFetch(200, null);

    await deleteMessages(CHAT_ID, AUTH_KEY);

    const [, opts] = lastCall();
    expect(opts.headers).toMatchObject({ Authorization: `Bearer ${AUTH_KEY}` });
  });

  it("throws on failure", async () => {
    stubFetch(404, {});

    await expect(deleteMessages(CHAT_ID, AUTH_KEY)).rejects.toThrow("404");
  });
});

import { render, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { ChatStoreProvider } from "../../controllers/chatStoreProvider";
import { useChatState, useChatActions } from "../../controllers/useChatStore";
import * as api from "../../lib/api";
import type { Message } from "../../lib/types";

// ─── Module mocks ─────────────────────────────────────────────────────────────

vi.mock("../../lib/api", () => ({
  fetchMessages: vi.fn().mockResolvedValue([]),
  sendMessage: vi.fn(),
  saveMessages: vi.fn().mockResolvedValue(undefined),
  deleteMessages: vi.fn().mockResolvedValue(undefined),
}));

vi.mock("../../lib/storage", () => ({
  loadChats: vi.fn().mockReturnValue([]),
  saveChats: vi.fn(),
  loadActiveChatId: vi.fn().mockReturnValue(null),
  saveActiveChatId: vi.fn(),
  loadUserKey: vi.fn().mockReturnValue(""),
  saveUserKey: vi.fn(),
  hydrateChatFromExport: vi.fn().mockReturnValue({
    chat: {
      id: "imported-id",
      title: "Imported Chat",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    messages: [
      { id: "m1", role: "user", content: "Hello", createdAt: new Date().toISOString() },
      { id: "m2", role: "model", content: "Hi there", createdAt: new Date().toISOString() },
    ],
  }),
  extractMessages: vi.fn(),
}));

// ─── Test harness ─────────────────────────────────────────────────────────────

/** Captures the latest context value on every render. */
type CombinedCtx = ReturnType<typeof useChatState> & ReturnType<typeof useChatActions>;
let ctxRef: CombinedCtx;

function ContextCapture() {
  const state = useChatState();
  const actions = useChatActions();
  ctxRef = { ...state, ...actions };
  return null;
}

const setupProvider = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  render(
    <QueryClientProvider client={queryClient}>
      <ChatStoreProvider>
        <ContextCapture />
      </ChatStoreProvider>
    </QueryClientProvider>,
  );

  return { queryClient };
};

// ─── Shared setup ─────────────────────────────────────────────────────────────

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(api.fetchMessages).mockResolvedValue([]);
  vi.mocked(api.saveMessages).mockResolvedValue(undefined);
  vi.mocked(api.deleteMessages).mockResolvedValue(undefined);
});

// ─── handleSend ───────────────────────────────────────────────────────────────

describe("handleSend", () => {
  it("does nothing when there is no active chat", async () => {
    setupProvider();
    // No chat created — activeChat is null
    await act(async () => { await ctxRef.handleSend(); });
    expect(api.sendMessage).not.toHaveBeenCalled();
  });

  it("does nothing when the input is empty or whitespace-only", async () => {
    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { ctxRef.setInput("   "); });
    await act(async () => { await ctxRef.handleSend(); });

    expect(api.sendMessage).not.toHaveBeenCalled();
  });

  it("optimistically adds the user message and appends the AI response", async () => {
    vi.mocked(api.sendMessage).mockResolvedValue({ text: "AI response" });

    const { queryClient } = setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { ctxRef.setInput("Hello AI"); });

    const chatId = ctxRef.activeChatId!;
    await act(async () => { await ctxRef.handleSend(); });

    const cached = queryClient.getQueryData<Message[]>(["messages", chatId]);
    expect(cached).toHaveLength(2);
    expect(cached![0]).toMatchObject({ role: "user", content: "Hello AI" });
    expect(cached![1]).toMatchObject({ role: "model", content: "AI response" });
  });

  it("calls sendMessage with the chat ID, trimmed input, and auth key", async () => {
    vi.mocked(api.sendMessage).mockResolvedValue({ text: "ok" });

    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    await act(async () => { ctxRef.setUserKeyInput("my-key"); });
    await act(async () => { ctxRef.setInput("  What is AI?  "); });

    const chatId = ctxRef.activeChatId!;
    await act(async () => { await ctxRef.handleSend(); });

    expect(api.sendMessage).toHaveBeenCalledWith(
      chatId,
      "What is AI?",
      expect.objectContaining({ datastorePaths: expect.any(Array) }),
      "my-key",
    );
  });

  it("appends an error message to the cache when sendMessage rejects", async () => {
    vi.mocked(api.sendMessage).mockRejectedValue(new Error("Network error"));

    const { queryClient } = setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { ctxRef.setInput("Hello"); });

    const chatId = ctxRef.activeChatId!;
    await act(async () => { await ctxRef.handleSend(); });
    await waitFor(() => expect(ctxRef.isLoading).toBe(false));

    const cached = queryClient.getQueryData<Message[]>(["messages", chatId]);
    expect(cached).toHaveLength(2);
    expect(cached![1]).toMatchObject({
      role: "model",
      content: expect.stringContaining("Network error"),
    });
  });

  it("updates the chat title from 'New chat' using the first message", async () => {
    vi.mocked(api.sendMessage).mockResolvedValue({ text: "ok" });

    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { ctxRef.setInput("My first message"); });
    await act(async () => { await ctxRef.handleSend(); });

    await waitFor(() => {
      const chat = ctxRef.chats.find((c) => c.id === ctxRef.activeChatId);
      expect(chat?.title).toBe("My first message");
    });
  });

  it("clears the input field after sending", async () => {
    vi.mocked(api.sendMessage).mockResolvedValue({ text: "ok" });

    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { ctxRef.setInput("Hello"); });
    await act(async () => { await ctxRef.handleSend(); });

    await waitFor(() => expect(ctxRef.input).toBe(""));
  });

  it("resets isLoading to false after a successful send", async () => {
    vi.mocked(api.sendMessage).mockResolvedValue({ text: "ok" });

    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { ctxRef.setInput("Hello"); });
    await act(async () => { await ctxRef.handleSend(); });

    await waitFor(() => expect(ctxRef.isLoading).toBe(false));
  });

  it("resets isLoading to false even when sendMessage rejects", async () => {
    vi.mocked(api.sendMessage).mockRejectedValue(new Error("oops"));

    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { ctxRef.setInput("Hello"); });
    await act(async () => { await ctxRef.handleSend(); });

    await waitFor(() => expect(ctxRef.isLoading).toBe(false));
  });
});

// ─── handleImport ─────────────────────────────────────────────────────────────

describe("handleImport", () => {
  it("adds the imported chat to the list and makes it active", async () => {
    setupProvider();

    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { await ctxRef.handleImport({ title: "Import", messages: [] }); });

    await waitFor(() => {
      expect(ctxRef.chats.some((c) => c.id === "imported-id")).toBe(true);
      expect(ctxRef.activeChatId).toBe("imported-id");
    });
  });

  it("calls saveMessages with the imported messages and auth key", async () => {
    setupProvider();

    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { await ctxRef.handleImport({ title: "Import", messages: [] }); });

    expect(api.saveMessages).toHaveBeenCalledWith(
      "imported-id",
      expect.arrayContaining([expect.objectContaining({ role: "user" })]),
      "test-key",
    );
  });

  it("seeds the query cache with the imported messages", async () => {
    const { queryClient } = setupProvider();

    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { await ctxRef.handleImport({ title: "Import", messages: [] }); });

    await waitFor(() => {
      const cached = queryClient.getQueryData<Message[]>(["messages", "imported-id"]);
      expect(cached).toHaveLength(2);
    });
  });

  it("skips saveMessages when authKey is not set", async () => {
    setupProvider();

    // No userKeyInput set — authKey is ""
    await act(async () => { await ctxRef.handleImport({ title: "Import", messages: [] }); });

    expect(api.saveMessages).not.toHaveBeenCalled();
  });
});

// ─── handleDeleteChat ─────────────────────────────────────────────────────────

describe("handleDeleteChat", () => {
  it("removes the deleted chat from the chats list", async () => {
    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    const chatId = ctxRef.activeChatId!;
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { await ctxRef.handleDeleteChat(chatId); });

    await waitFor(() => {
      expect(ctxRef.chats.some((c) => c.id === chatId)).toBe(false);
    });
  });

  it("calls deleteMessages on the server", async () => {
    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    const chatId = ctxRef.activeChatId!;
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { await ctxRef.handleDeleteChat(chatId); });

    expect(api.deleteMessages).toHaveBeenCalledWith(chatId, "test-key");
  });

  it("selects the next available chat when the active chat is deleted", async () => {
    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    const firstId = ctxRef.activeChatId!;
    await act(async () => { ctxRef.handleNewChat(); });
    const secondId = ctxRef.activeChatId!;

    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { await ctxRef.handleDeleteChat(secondId); });

    await waitFor(() => expect(ctxRef.activeChatId).toBe(firstId));
  });

  it("sets activeChatId to null when the last chat is deleted", async () => {
    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    const chatId = ctxRef.activeChatId!;
    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { await ctxRef.handleDeleteChat(chatId); });

    await waitFor(() => expect(ctxRef.activeChatId).toBeNull());
  });

  it("skips the deleteMessages API call when authKey is not set", async () => {
    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    const chatId = ctxRef.activeChatId!;
    // No key set
    await act(async () => { await ctxRef.handleDeleteChat(chatId); });

    expect(api.deleteMessages).not.toHaveBeenCalled();
  });

  it("removes the chat's messages from the query cache", async () => {
    const { queryClient } = setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    const chatId = ctxRef.activeChatId!;

    // Seed some messages in the cache
    queryClient.setQueryData<Message[]>(["messages", chatId], [
      { id: "m1", role: "user", content: "hi", createdAt: "" },
    ]);

    await act(async () => { ctxRef.setUserKeyInput("test-key"); });
    await act(async () => { await ctxRef.handleDeleteChat(chatId); });

    await waitFor(() => {
      expect(queryClient.getQueryData(["messages", chatId])).toBeUndefined();
    });
  });
});

// ─── handleRenameChat ─────────────────────────────────────────────────────────

describe("handleRenameChat", () => {
  it("updates the chat title", async () => {
    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    const chatId = ctxRef.activeChatId!;
    await act(async () => { ctxRef.handleRenameChat(chatId, "My Renamed Chat"); });

    await waitFor(() => {
      const chat = ctxRef.chats.find((c) => c.id === chatId);
      expect(chat?.title).toBe("My Renamed Chat");
    });
  });

  it("ignores a rename with a whitespace-only title", async () => {
    setupProvider();

    await act(async () => { ctxRef.handleNewChat(); });
    const chatId = ctxRef.activeChatId!;
    const originalTitle = ctxRef.chats.find((c) => c.id === chatId)?.title;

    await act(async () => { ctxRef.handleRenameChat(chatId, "   "); });

    expect(ctxRef.chats.find((c) => c.id === chatId)?.title).toBe(originalTitle);
  });
});

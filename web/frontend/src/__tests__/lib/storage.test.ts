import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  loadChats,
  saveChats,
  loadActiveChatId,
  saveActiveChatId,
  loadUserKey,
  saveUserKey,
  extractMessages,
  hydrateChatFromExport,
} from "../../lib/storage";
import type { Chat, VertexPromptExport } from "../../lib/types";

const CHATS_KEY = "gemini-lite.chats";
const ACTIVE_CHAT_KEY = "gemini-lite.activeChat";
const AUTH_KEY_LS = "gemini-lite.authKey";

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

// ─── loadChats / saveChats ────────────────────────────────────────────────────

describe("loadChats", () => {
  it("returns an empty array when the key is absent", () => {
    expect(loadChats()).toEqual([]);
  });

  it("returns an empty array for invalid JSON", () => {
    localStorage.setItem(CHATS_KEY, "not-json{{");
    expect(loadChats()).toEqual([]);
  });

  it("returns an empty array when the stored value is not an array", () => {
    localStorage.setItem(CHATS_KEY, JSON.stringify({ id: "1" }));
    expect(loadChats()).toEqual([]);
  });

  it("filters out chat objects that are missing required fields", () => {
    const raw = JSON.stringify([
      { id: "1", title: "Chat", createdAt: "now", updatedAt: "now" }, // valid
      { id: "2" }, // missing title / createdAt / updatedAt
      null,
      "string",
    ]);
    localStorage.setItem(CHATS_KEY, raw);

    const result = loadChats();
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe("1");
  });

  it("preserves an optional systemInstruction field", () => {
    const raw = JSON.stringify([
      {
        id: "1",
        title: "Chat",
        createdAt: "now",
        updatedAt: "now",
        systemInstruction: "Be concise",
      },
    ]);
    localStorage.setItem(CHATS_KEY, raw);

    expect(loadChats()[0].systemInstruction).toBe("Be concise");
  });

  it("strips extraneous fields (e.g. messages) from stored chats", () => {
    const raw = JSON.stringify([
      {
        id: "1",
        title: "Chat",
        createdAt: "now",
        updatedAt: "now",
        messages: [{ id: "m1" }],
      },
    ]);
    localStorage.setItem(CHATS_KEY, raw);

    expect(loadChats()[0]).not.toHaveProperty("messages");
  });
});

describe("saveChats", () => {
  it("persists the chats array to localStorage", () => {
    const chats: Chat[] = [
      { id: "1", title: "Chat", createdAt: "now", updatedAt: "now" },
    ];
    saveChats(chats);

    const stored = JSON.parse(localStorage.getItem(CHATS_KEY)!);
    expect(stored).toEqual(chats);
  });

  it("round-trips through loadChats", () => {
    const chats: Chat[] = [
      { id: "a", title: "Alpha", createdAt: "t1", updatedAt: "t1", systemInstruction: "SI" },
      { id: "b", title: "Beta", createdAt: "t2", updatedAt: "t2" },
    ];
    saveChats(chats);
    expect(loadChats()).toEqual(chats);
  });
});

// ─── loadActiveChatId / saveActiveChatId ──────────────────────────────────────

describe("loadActiveChatId", () => {
  it("returns null when the key is absent", () => {
    expect(loadActiveChatId()).toBeNull();
  });

  it("returns the stored chat ID", () => {
    localStorage.setItem(ACTIVE_CHAT_KEY, "chat-xyz");
    expect(loadActiveChatId()).toBe("chat-xyz");
  });
});

describe("saveActiveChatId", () => {
  it("writes a chat ID to localStorage", () => {
    saveActiveChatId("chat-abc");
    expect(localStorage.getItem(ACTIVE_CHAT_KEY)).toBe("chat-abc");
  });

  it("removes the key when null is passed", () => {
    localStorage.setItem(ACTIVE_CHAT_KEY, "chat-abc");
    saveActiveChatId(null);
    expect(localStorage.getItem(ACTIVE_CHAT_KEY)).toBeNull();
  });
});

// ─── loadUserKey / saveUserKey ────────────────────────────────────────────────

describe("loadUserKey", () => {
  it("returns an empty string when the key is absent", () => {
    expect(loadUserKey()).toBe("");
  });

  it("returns the stored key", () => {
    localStorage.setItem(AUTH_KEY_LS, "my-secret");
    expect(loadUserKey()).toBe("my-secret");
  });
});

describe("saveUserKey", () => {
  it("persists the key to localStorage", () => {
    saveUserKey("my-secret");
    expect(localStorage.getItem(AUTH_KEY_LS)).toBe("my-secret");
  });

  it("round-trips through loadUserKey", () => {
    saveUserKey("abc123");
    expect(loadUserKey()).toBe("abc123");
  });
});

// ─── extractMessages ──────────────────────────────────────────────────────────

const makeExport = (overrides: Partial<VertexPromptExport> = {}): VertexPromptExport => ({
  title: "Test",
  messages: [
    { content: { role: "user", parts: [{ text: "Hello" }] } },
    { content: { role: "model", parts: [{ text: "Hi there" }] } },
  ],
  ...overrides,
});

describe("extractMessages", () => {
  it("converts Vertex messages to the app Message format", () => {
    const result = extractMessages(makeExport());

    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({ role: "user", content: "Hello" });
    expect(result[1]).toMatchObject({ role: "model", content: "Hi there" });
  });

  it("assigns a unique id and createdAt to every message", () => {
    const result = extractMessages(makeExport());

    expect(result[0].id).toBeTruthy();
    expect(result[0].createdAt).toBeTruthy();
    // IDs are unique across messages
    expect(result[0].id).not.toBe(result[1].id);
  });

  it("filters out thought parts and keeps only visible text", () => {
    const data = makeExport({
      messages: [
        {
          content: {
            role: "model",
            parts: [
              { text: "Internal reasoning...", thought: true },
              { text: "Actual answer" },
            ],
          },
        },
      ],
    });

    const result = extractMessages(data);
    expect(result).toHaveLength(1);
    expect(result[0].content).toBe("Actual answer");
  });

  it("skips messages whose only parts are thoughts or empty text", () => {
    const data = makeExport({
      messages: [{ content: { role: "user", parts: [{ text: "  ", thought: false }] } }],
    });
    expect(extractMessages(data)).toHaveLength(0);
  });

  it("falls back to message.author when content.role is absent", () => {
    const data: VertexPromptExport = {
      messages: [{ author: "user", content: { parts: [{ text: "Hey" }] } }],
    };
    expect(extractMessages(data)[0].role).toBe("user");
  });

  it("normalises unknown roles to 'model'", () => {
    const data: VertexPromptExport = {
      messages: [{ author: "assistant", content: { parts: [{ text: "Hello" }] } }],
    };
    expect(extractMessages(data)[0].role).toBe("model");
  });

  it("returns an empty array when messages is absent", () => {
    expect(extractMessages({})).toEqual([]);
  });
});

// ─── hydrateChatFromExport ────────────────────────────────────────────────────

describe("hydrateChatFromExport", () => {
  it("creates a Chat from the export title", () => {
    const { chat } = hydrateChatFromExport(makeExport({ title: "My Session" }));

    expect(chat.title).toBe("My Session");
    expect(chat.id).toMatch(/^[0-9a-f-]{36}$/); // UUID shape
    expect(chat.createdAt).toBeTruthy();
    expect(chat.updatedAt).toBeTruthy();
  });

  it("falls back to 'Imported Chat' when title is absent", () => {
    const { chat } = hydrateChatFromExport(makeExport({ title: undefined }));
    expect(chat.title).toBe("Imported Chat");
  });

  it("falls back to 'Imported Chat' for a blank title", () => {
    const { chat } = hydrateChatFromExport(makeExport({ title: "   " }));
    expect(chat.title).toBe("Imported Chat");
  });

  it("extracts a systemInstruction from the export", () => {
    const data = makeExport({
      systemInstruction: { parts: [{ text: "Be concise" }] },
    });
    const { chat } = hydrateChatFromExport(data);
    expect(chat.systemInstruction).toBe("Be concise");
  });

  it("concatenates multiple system-instruction parts with a newline", () => {
    const data = makeExport({
      systemInstruction: { parts: [{ text: "Part 1" }, { text: "Part 2" }] },
    });
    const { chat } = hydrateChatFromExport(data);
    expect(chat.systemInstruction).toBe("Part 1\nPart 2");
  });

  it("leaves systemInstruction undefined when no parts contain text", () => {
    const data = makeExport({
      systemInstruction: { parts: [{ text: "  " }] },
    });
    const { chat } = hydrateChatFromExport(data);
    expect(chat.systemInstruction).toBeUndefined();
  });

  it("returns the extracted messages alongside the chat", () => {
    const { messages } = hydrateChatFromExport(makeExport());
    expect(messages).toHaveLength(2);
    expect(messages[0].role).toBe("user");
    expect(messages[1].role).toBe("model");
  });
});

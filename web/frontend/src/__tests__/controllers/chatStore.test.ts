import { describe, it, expect } from "vitest";
import {
  chatReducer,
  createChat,
  createInitialState,
  titleFromMessage,
  type ChatAction,
  type ChatState,
} from "../../controllers/chatStore";

// ─── titleFromMessage ─────────────────────────────────────────────────────────

describe("titleFromMessage", () => {
  it("returns 'New chat' for an empty string", () => {
    expect(titleFromMessage("")).toBe("New chat");
  });

  it("returns 'New chat' for a whitespace-only string", () => {
    expect(titleFromMessage("   ")).toBe("New chat");
  });

  it("returns the trimmed message for short inputs", () => {
    expect(titleFromMessage("  Hello world  ")).toBe("Hello world");
  });

  it("does not truncate a message that is exactly 44 characters", () => {
    const exact = "A".repeat(44);
    expect(titleFromMessage(exact)).toBe(exact);
    expect(titleFromMessage(exact)).toHaveLength(44);
  });

  it("truncates to 44 characters when the message is longer", () => {
    const long = "B".repeat(80);
    const result = titleFromMessage(long);
    expect(result).toHaveLength(44);
    expect(result).toBe("B".repeat(44));
  });
});

// ─── createChat ───────────────────────────────────────────────────────────────

describe("createChat", () => {
  it("produces a UUID-shaped id", () => {
    const { id } = createChat();
    expect(id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/,
    );
  });

  it("uses the default title 'New chat'", () => {
    expect(createChat().title).toBe("New chat");
  });

  it("accepts a custom title", () => {
    expect(createChat("My session").title).toBe("My session");
  });

  it("sets createdAt and updatedAt to valid ISO date strings", () => {
    const { createdAt, updatedAt } = createChat();
    expect(() => new Date(createdAt)).not.toThrow();
    expect(() => new Date(updatedAt)).not.toThrow();
    expect(Number.isNaN(new Date(createdAt).getTime())).toBe(false);
  });

  it("generates unique IDs on each call", () => {
    expect(createChat().id).not.toBe(createChat().id);
  });
});

// ─── chatReducer ──────────────────────────────────────────────────────────────

const mkState = (overrides: Partial<ChatState> = {}): ChatState => ({
  ...createInitialState(),
  ...overrides,
});

const chat1 = createChat("Alpha");
const chat2 = createChat("Beta");

describe("chatReducer — HYDRATE", () => {
  it("sets isHydrated to true and merges the payload", () => {
    const next = chatReducer(mkState(), {
      type: "HYDRATE",
      payload: { chats: [chat1], activeChatId: chat1.id, userKeyInput: "k", userKey: "k" },
    });
    expect(next.isHydrated).toBe(true);
    expect(next.chats).toEqual([chat1]);
    expect(next.activeChatId).toBe(chat1.id);
    expect(next.userKey).toBe("k");
  });

  it("does not mutate other state fields", () => {
    const state = mkState({ selectedGroup: "gp3", input: "draft" });
    const next = chatReducer(state, {
      type: "HYDRATE",
      payload: { chats: [], activeChatId: null, userKeyInput: "", userKey: "" },
    });
    expect(next.selectedGroup).toBe("gp3");
    expect(next.input).toBe("draft");
  });
});

describe("chatReducer — SET_INPUT", () => {
  it("updates input", () => {
    expect(chatReducer(mkState(), { type: "SET_INPUT", value: "Hello" }).input).toBe("Hello");
  });

  it("allows clearing input to empty string", () => {
    const state = mkState({ input: "existing" });
    expect(chatReducer(state, { type: "SET_INPUT", value: "" }).input).toBe("");
  });
});

describe("chatReducer — SET_LOADING", () => {
  it("sets isLoading to true", () => {
    expect(chatReducer(mkState(), { type: "SET_LOADING", value: true }).isLoading).toBe(true);
  });

  it("sets isLoading to false", () => {
    const state = mkState({ isLoading: true });
    expect(chatReducer(state, { type: "SET_LOADING", value: false }).isLoading).toBe(false);
  });
});

describe("chatReducer — SET_ACTIVE_CHAT", () => {
  it("updates activeChatId", () => {
    const next = chatReducer(mkState(), { type: "SET_ACTIVE_CHAT", chatId: chat1.id });
    expect(next.activeChatId).toBe(chat1.id);
  });

  it("accepts null to deselect all chats", () => {
    const state = mkState({ activeChatId: chat1.id });
    const next = chatReducer(state, { type: "SET_ACTIVE_CHAT", chatId: null });
    expect(next.activeChatId).toBeNull();
  });
});

describe("chatReducer — SET_CHATS", () => {
  it("replaces the chats array", () => {
    const state = mkState({ chats: [chat1] });
    const next = chatReducer(state, { type: "SET_CHATS", chats: [chat2] });
    expect(next.chats).toEqual([chat2]);
  });

  it("accepts an empty array", () => {
    const state = mkState({ chats: [chat1] });
    expect(chatReducer(state, { type: "SET_CHATS", chats: [] }).chats).toEqual([]);
  });
});

describe("chatReducer — SET_USER_KEY_INPUT", () => {
  it("updates userKeyInput", () => {
    const next = chatReducer(mkState(), { type: "SET_USER_KEY_INPUT", value: "secret" });
    expect(next.userKeyInput).toBe("secret");
  });
});

describe("chatReducer — SET_USER_KEY", () => {
  it("updates userKey", () => {
    const next = chatReducer(mkState(), { type: "SET_USER_KEY", value: "trimmed-secret" });
    expect(next.userKey).toBe("trimmed-secret");
  });
});

describe("chatReducer — SET_SELECTED_GROUP", () => {
  it("switches from gp2 to gp3", () => {
    expect(chatReducer(mkState(), { type: "SET_SELECTED_GROUP", value: "gp3" }).selectedGroup).toBe("gp3");
  });

  it("switches from gp3 back to gp2", () => {
    const state = mkState({ selectedGroup: "gp3" });
    expect(chatReducer(state, { type: "SET_SELECTED_GROUP", value: "gp2" }).selectedGroup).toBe("gp2");
  });
});

describe("chatReducer — SET_SYSTEM_INSTRUCTION", () => {
  it("updates systemInstruction on the matching chat only", () => {
    const state = mkState({ chats: [chat1, chat2] });
    const next = chatReducer(state, {
      type: "SET_SYSTEM_INSTRUCTION",
      chatId: chat1.id,
      value: "Be brief",
    });
    expect(next.chats.find((c) => c.id === chat1.id)?.systemInstruction).toBe("Be brief");
    expect(next.chats.find((c) => c.id === chat2.id)?.systemInstruction).toBeUndefined();
  });

  it("accepts undefined to clear the instruction", () => {
    const state = mkState({ chats: [{ ...chat1, systemInstruction: "old" }] });
    const next = chatReducer(state, {
      type: "SET_SYSTEM_INSTRUCTION",
      chatId: chat1.id,
      value: undefined,
    });
    expect(next.chats[0].systemInstruction).toBeUndefined();
  });

  it("bumps updatedAt on the modified chat", () => {
    const state = mkState({ chats: [chat1] });
    const before = chat1.updatedAt;
    const next = chatReducer(state, {
      type: "SET_SYSTEM_INSTRUCTION",
      chatId: chat1.id,
      value: "new",
    });
    expect(next.chats[0].updatedAt).not.toBe(before);
  });
});

describe("chatReducer — SET_CHAT_TITLE", () => {
  it("updates only the matching chat's title", () => {
    const state = mkState({ chats: [chat1, chat2] });
    const next = chatReducer(state, {
      type: "SET_CHAT_TITLE",
      chatId: chat1.id,
      title: "Renamed",
    });
    expect(next.chats.find((c) => c.id === chat1.id)?.title).toBe("Renamed");
    expect(next.chats.find((c) => c.id === chat2.id)?.title).toBe(chat2.title);
  });

  it("bumps updatedAt on the renamed chat", () => {
    const state = mkState({ chats: [chat1] });
    const before = chat1.updatedAt;
    const next = chatReducer(state, {
      type: "SET_CHAT_TITLE",
      chatId: chat1.id,
      title: "New name",
    });
    expect(next.chats[0].updatedAt).not.toBe(before);
  });
});

describe("chatReducer — unknown actions", () => {
  it("returns the same state reference for unrecognised action types", () => {
    const state = mkState();
    const next = chatReducer(state, { type: "UNKNOWN" } as unknown as ChatAction);
    expect(next).toBe(state);
  });
});

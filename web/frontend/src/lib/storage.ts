import type { Chat, Message, Role, VertexPromptExport } from "./types";

const CHATS_KEY = "gemini-lite.chats";
const ACTIVE_CHAT_KEY = "gemini-lite.activeChat";

const toIsoString = () => new Date().toISOString();

export const loadChats = (): Chat[] => {
  try {
    const raw = localStorage.getItem(CHATS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as Chat[];
  } catch {
    return [];
  }
};

export const saveChats = (chats: Chat[]) => {
  try {
    localStorage.setItem(CHATS_KEY, JSON.stringify(chats));
  } catch {
    // ignore storage errors
  }
};

export const loadActiveChatId = (): string | null => {
  try {
    return localStorage.getItem(ACTIVE_CHAT_KEY);
  } catch {
    return null;
  }
};

export const saveActiveChatId = (chatId: string | null) => {
  try {
    if (chatId) {
      localStorage.setItem(ACTIVE_CHAT_KEY, chatId);
    } else {
      localStorage.removeItem(ACTIVE_CHAT_KEY);
    }
  } catch {
    // ignore storage errors
  }
};

const extractSystemInstruction = (
  data: VertexPromptExport,
): string | undefined => {
  const parts = data.systemInstruction?.parts ?? [];
  const text = parts
    .map((part) => (typeof part.text === "string" ? part.text : ""))
    .filter((value) => value.trim().length > 0)
    .join("\n")
    .trim();

  return text.length > 0 ? text : undefined;
};

const extractMessages = (data: VertexPromptExport): Message[] => {
  const now = toIsoString();
  const messages = data.messages ?? [];

  return messages.reduce<Message[]>((acc, message) => {
    const author: Role = message.author === "user" ? "user" : "assistant";
    const parts = message.content?.parts ?? [];
    const text = parts
      .filter((part) => !part.thought)
      .map((part) => (typeof part.text === "string" ? part.text : ""))
      .filter((value) => value.trim().length > 0)
      .join("\n")
      .trim();

    if (!text) return acc;

    acc.push({
      id: crypto.randomUUID(),
      role: author,
      content: text,
      createdAt: now,
    });

    return acc;
  }, []);
};

export const hydrateChatFromExport = (data: VertexPromptExport): Chat => {
  const now = toIsoString();
  const title = data.title?.trim() || "Imported Chat";

  return {
    id: crypto.randomUUID(),
    title,
    createdAt: now,
    updatedAt: now,
    systemInstruction: extractSystemInstruction(data),
    parameters: data.parameters ?? undefined,
    model: data.model ?? undefined,
    messages: extractMessages(data),
  };
};

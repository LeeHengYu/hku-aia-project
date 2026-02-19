import type { Chat, Message, Role, VertexPromptExport } from "./types";

const CHATS_KEY = "gemini-lite.chats";
const ACTIVE_CHAT_KEY = "gemini-lite.activeChat";
const AUTH_KEY = "gemini-lite.authKey";

const toIsoString = () => new Date().toISOString();

const normalizeRole = (value: unknown): Role => {
  if (value === "user") return "user";
  return "model";
};

const normalizeChats = (value: unknown): Chat[] => {
  if (!Array.isArray(value)) return [];

  return value.reduce<Chat[]>((acc, rawChat) => {
    if (!rawChat || typeof rawChat !== "object") return acc;
    const chat = rawChat as Partial<Chat> & { messages?: unknown };

    if (
      typeof chat.id !== "string" ||
      typeof chat.title !== "string" ||
      typeof chat.createdAt !== "string" ||
      typeof chat.updatedAt !== "string"
    ) {
      return acc;
    }

    acc.push({
      id: chat.id,
      title: chat.title,
      createdAt: chat.createdAt,
      updatedAt: chat.updatedAt,
      systemInstruction:
        typeof chat.systemInstruction === "string"
          ? chat.systemInstruction
          : undefined,
    });

    return acc;
  }, []);
};

export const loadChats = (): Chat[] => {
  try {
    const raw = localStorage.getItem(CHATS_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    return normalizeChats(parsed);
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

export const loadUserKey = (): string => {
  try {
    return localStorage.getItem(AUTH_KEY) ?? "";
  } catch {
    return "";
  }
};

export const saveUserKey = (key: string) => {
  try {
    localStorage.setItem(AUTH_KEY, key);
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

export const extractMessages = (data: VertexPromptExport): Message[] => {
  const now = toIsoString();
  const messages = data.messages ?? [];

  return messages.reduce<Message[]>((acc, message) => {
    const roleSource =
      typeof message.content?.role === "string"
        ? message.content.role
        : message.author;
    const role = normalizeRole(roleSource);
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
      role,
      content: text,
      createdAt: now,
    });

    return acc;
  }, []);
};

export const hydrateChatFromExport = (
  data: VertexPromptExport,
): { chat: Chat; messages: Message[] } => {
  const now = toIsoString();
  const title = data.title?.trim() || "Imported Chat";

  const chat: Chat = {
    id: crypto.randomUUID(),
    title,
    createdAt: now,
    updatedAt: now,
    systemInstruction: extractSystemInstruction(data),
  };

  return { chat, messages: extractMessages(data) };
};

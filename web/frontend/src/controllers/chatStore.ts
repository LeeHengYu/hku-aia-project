// Chat domain model: reducer, action types, and pure state helpers.

import type { Chat } from "../lib/types";
import { loadChats, loadActiveChatId, loadUserKey } from "../lib/storage";

export type GroupSelection = "market" | "product" | "both";

export interface ChatState {
  chats: Chat[];
  activeChatId: string | null;
  input: string;
  isLoading: boolean;
  userKeyInput: string;
  selectedGroup: GroupSelection;
}

export type ChatAction =
  | { type: "SET_INPUT"; value: string }
  | { type: "SET_LOADING"; value: boolean }
  | { type: "SET_ACTIVE_CHAT"; chatId: string | null }
  | { type: "SET_CHATS"; chats: Chat[] }
  | { type: "SET_USER_KEY_INPUT"; value: string }
  | { type: "SET_SELECTED_GROUP"; value: GroupSelection }
  | { type: "SET_SYSTEM_INSTRUCTION"; chatId: string; value: string | undefined }
  | { type: "SET_CHAT_TITLE"; chatId: string; title: string };

export const createInitialState = (): ChatState => {
  const chats = loadChats();
  const userKeyInput = loadUserKey();

  let activeChatId = loadActiveChatId();
  if (chats.length === 0) {
    activeChatId = null;
  } else if (!activeChatId || !chats.some((c) => c.id === activeChatId)) {
    activeChatId = chats[0].id;
  }

  return {
    chats,
    activeChatId,
    input: "",
    isLoading: false,
    userKeyInput,
    selectedGroup: "market",
  };
};

export const createChat = (title = "New chat"): Chat => {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    title,
    createdAt: now,
    updatedAt: now,
  };
};

export const titleFromMessage = (value: string) => {
  const trimmed = value.trim();
  if (!trimmed) return "New chat";
  return trimmed.slice(0, Math.min(44, trimmed.length));
};

export const chatReducer = (
  state: ChatState,
  action: ChatAction,
): ChatState => {
  switch (action.type) {
    case "SET_INPUT":
      return { ...state, input: action.value };
    case "SET_LOADING":
      return { ...state, isLoading: action.value };
    case "SET_ACTIVE_CHAT":
      return { ...state, activeChatId: action.chatId };
    case "SET_CHATS":
      return { ...state, chats: action.chats };
    case "SET_USER_KEY_INPUT":
      return { ...state, userKeyInput: action.value };
    case "SET_SELECTED_GROUP":
      return { ...state, selectedGroup: action.value };
    case "SET_SYSTEM_INSTRUCTION":
      return {
        ...state,
        chats: state.chats.map((chat) =>
          chat.id === action.chatId
            ? { ...chat, systemInstruction: action.value, updatedAt: new Date().toISOString() }
            : chat,
        ),
      };
    case "SET_CHAT_TITLE":
      return {
        ...state,
        chats: state.chats.map((chat) =>
          chat.id === action.chatId
            ? { ...chat, title: action.title, updatedAt: new Date().toISOString() }
            : chat,
        ),
      };
    default:
      return state;
  }
};

// Chat domain model: reducer, action types, and pure state helpers.

import type { Chat } from "../lib/types";

export interface ChatState {
  chats: Chat[];
  activeChatId: string | null;
  input: string;
  isLoading: boolean;
  userKeyInput: string;
  userKey: string;
}

export type ChatAction =
  | { type: "INIT"; state: ChatState }
  | { type: "SET_INPUT"; value: string }
  | { type: "SET_LOADING"; value: boolean }
  | { type: "SET_ACTIVE_CHAT"; chatId: string | null }
  | { type: "SET_CHATS"; chats: Chat[] }
  | { type: "SET_USER_KEY_INPUT"; value: string }
  | { type: "SET_USER_KEY"; value: string };

export const createChat = (title = "New chat"): Chat => {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    title,
    createdAt: now,
    updatedAt: now,
    messages: [],
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
    case "INIT":
      return action.state;
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
    case "SET_USER_KEY":
      return { ...state, userKey: action.value };
    default:
      return state;
  }
};

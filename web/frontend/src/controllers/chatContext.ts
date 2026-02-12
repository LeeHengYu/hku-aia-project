// Defines shared context contracts: state shape and action interface.

import { createContext } from "react";
import type { Chat, VertexPromptExport } from "../lib/types";
import type { ChatState } from "./chatStore";

export interface ChatActions {
  setInput: (value: string) => void;
  setUserKeyInput: (value: string) => void;
  handleNewChat: () => void;
  handleSelectChat: (chatId: string) => void;
  handleImport: (data: VertexPromptExport) => void;
  handleRenameChat: (chatId: string, nextTitle: string) => void;
  handleDeleteChat: (chatId: string) => void;
  handleSend: () => Promise<void>;
}

export interface ChatContextState extends ChatState {
  activeChat: Chat | null;
}

export const ChatStateContext = createContext<ChatContextState | null>(null);
export const ChatActionsContext = createContext<ChatActions | null>(null);

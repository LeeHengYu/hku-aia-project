// Defines shared context contracts: state shape and action interface.

import { createContext, type Dispatch } from "react";
import type { Chat, VertexPromptExport } from "../lib/types";
import type { ChatAction, ChatState } from "./chatStore";

interface ChatContextActions {
  setInput: (value: string) => void;
  setUserKeyInput: (value: string) => void;
  handleNewChat: () => void;
  handleSelectChat: (chatId: string) => void;
  handleImport: (data: VertexPromptExport) => void;
  handleRenameChat: (chatId: string, nextTitle: string) => void;
  handleDeleteChat: (chatId: string) => void;
  handleSend: () => Promise<void>;
}

interface ChatContextValue extends ChatState, ChatContextActions {
  activeChat: Chat | null;
  dispatch: Dispatch<ChatAction>;
}

export const ChatContext = createContext<ChatContextValue | null>(null);

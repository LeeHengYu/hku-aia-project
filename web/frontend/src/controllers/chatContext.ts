// Defines shared context contracts: state shape and action interface.

import { createContext, type Dispatch } from "react";
import type { Chat, VertexPromptExport } from "../lib/types";
import type { ChatAction, ChatState, GroupSelection } from "./chatStore";

interface ChatContextActions {
  setInput: (value: string) => void;
  setUserKeyInput: (value: string) => void;
  setSelectedGroup: (group: GroupSelection) => void;
  handleNewChat: () => void;
  handleSelectChat: (chatId: string) => void;
  handleImport: (data: VertexPromptExport) => void;
  handleDeleteChat: (chatId: string) => void;
  handleSend: () => Promise<void>;
  handleSetSystemInstruction: (chatId: string, value: string | undefined) => void;
  handleRenameChat: (chatId: string, title: string) => void;
}

interface ChatContextValue extends ChatState, ChatContextActions {
  activeChat: Chat | null;
  dispatch: Dispatch<ChatAction>;
}

export const ChatContext = createContext<ChatContextValue | null>(null);

// Defines shared context contracts: state shape and action interface.

import { createContext, type Dispatch } from "react";
import type { Chat, VertexPromptExport } from "../lib/types";
import type { ChatAction, ChatState, GroupSelection } from "./chatStore";

export interface ChatStateContextValue extends ChatState {
  activeChat: Chat | null;
}

export interface ChatActionsContextValue {
  dispatch: Dispatch<ChatAction>;
  setInput: (value: string) => void;
  setUserKeyInput: (value: string) => void;
  setSelectedGroup: (group: GroupSelection) => void;
  handleNewChat: () => void;
  handleSelectChat: (chatId: string) => void;
  handleImport: (data: VertexPromptExport) => Promise<void>;
  handleDeleteChat: (chatId: string) => void;
  handleSend: () => Promise<void>;
  handleSetSystemInstruction: (chatId: string, value: string | undefined) => void;
  handleRenameChat: (chatId: string, title: string) => void;
}

export const ChatStateContext = createContext<ChatStateContextValue | null>(null);
export const ChatActionsContext = createContext<ChatActionsContextValue | null>(null);

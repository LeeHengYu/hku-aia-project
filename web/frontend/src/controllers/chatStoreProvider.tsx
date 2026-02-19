// Wires reducer-backed state and actions, then provides a unified chat context.

import { useCallback, useMemo, useReducer, type ReactNode } from "react";
import type { Chat, Message, VertexPromptExport } from "../lib/types";
import { hydrateChatFromExport } from "../lib/storage";
import {
  chatReducer,
  createInitialState,
  createChat,
  titleFromMessage,
} from "./chatStore";
import { ChatContext } from "./chatContext";
import { ChatController } from "./chatController";

const DATASTORE_PATH_GP2 = (import.meta.env.VITE_DATASTORE_PATH_GP2 ?? "").trim();
const DATASTORE_PATH_GP3 = (import.meta.env.VITE_DATASTORE_PATH_GP3 ?? "").trim();
const API_BASE_URL = (import.meta.env.VITE_BACKEND_URL ?? "").trim();

const buildApiUrl = (path: string): string => {
  if (!API_BASE_URL) return path;
  return `${API_BASE_URL}${path}`;
};

export const ChatStoreProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(
    chatReducer,
    undefined,
    createInitialState,
  );

  const activeChat = useMemo(
    () => state.chats.find((chat) => chat.id === state.activeChatId) ?? null,
    [state.chats, state.activeChatId],
  );

  const setInput = useCallback((value: string) => {
    dispatch({ type: "SET_INPUT", value });
  }, []);

  const setUserKeyInput = useCallback((value: string) => {
    dispatch({ type: "SET_USER_KEY_INPUT", value });
  }, []);

  const setSelectedGroup = useCallback((value: import("./chatStore").GroupSelection) => {
    dispatch({ type: "SET_SELECTED_GROUP", value });
  }, []);

  const handleNewChat = useCallback(() => {
    const nextChat = createChat();
    dispatch({ type: "SET_CHATS", chats: [nextChat, ...state.chats] });
    dispatch({ type: "SET_ACTIVE_CHAT", chatId: nextChat.id });
  }, [state.chats]);

  const handleSelectChat = useCallback((chatId: string) => {
    dispatch({ type: "SET_ACTIVE_CHAT", chatId });
  }, []);

  const handleImport = useCallback(
    (data: VertexPromptExport) => {
      const imported = hydrateChatFromExport(data);
      dispatch({ type: "SET_CHATS", chats: [imported, ...state.chats] });
      dispatch({ type: "SET_ACTIVE_CHAT", chatId: imported.id });
    },
    [state.chats],
  );

  const handleDeleteChat = useCallback(
    (chatId: string) => {
      const remaining = state.chats.filter((chat) => chat.id !== chatId);
      dispatch({ type: "SET_CHATS", chats: remaining });
      if (state.activeChatId === chatId) {
        dispatch({
          type: "SET_ACTIVE_CHAT",
          chatId: remaining.length > 0 ? remaining[0].id : null,
        });
      }
    },
    [state.chats, state.activeChatId],
  );

  const handleSend = useCallback(async () => {
    if (!activeChat) return;
    const trimmed = state.input.trim();
    if (!trimmed || state.isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      createdAt: new Date().toISOString(),
    };

    const updatedChat: Chat = {
      ...activeChat,
      title:
        activeChat.title === "New chat"
          ? titleFromMessage(trimmed)
          : activeChat.title,
      updatedAt: new Date().toISOString(),
      messages: [...activeChat.messages, userMessage],
    };

    const updatedChats = state.chats.map((chat) =>
      chat.id === activeChat.id ? updatedChat : chat,
    );

    dispatch({ type: "SET_CHATS", chats: updatedChats });
    dispatch({ type: "SET_INPUT", value: "" });
    dispatch({ type: "SET_LOADING", value: true });

    try {
      const authKey = state.userKeyInput.trim();
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (authKey) {
        headers.Authorization = `Bearer ${authKey}`;
      }

      const response = await fetch(buildApiUrl("/api/chat"), {
        method: "POST",
        headers,
        body: JSON.stringify({
          messages: updatedChat.messages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
          systemInstruction: activeChat.systemInstruction ?? null,
          datastorePath:
            state.selectedGroup === "gp3"
              ? DATASTORE_PATH_GP3
              : DATASTORE_PATH_GP2,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = (await response.json()) as { text?: string };
      const assistantText = data.text?.trim() || "No response generated.";

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "model",
        content: assistantText,
        createdAt: new Date().toISOString(),
      };

      const finalChat: Chat = {
        ...updatedChat,
        updatedAt: new Date().toISOString(),
        messages: [...updatedChat.messages, assistantMessage],
      };

      const finalChats = state.chats.map((chat) =>
        chat.id === finalChat.id ? finalChat : chat,
      );

      dispatch({ type: "SET_CHATS", chats: finalChats });
    } catch (error) {
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "model",
        content:
          error instanceof Error
            ? `Error: ${error.message}`
            : "Error: Unable to reach the backend.",
        createdAt: new Date().toISOString(),
      };

      const finalChat: Chat = {
        ...updatedChat,
        updatedAt: new Date().toISOString(),
        messages: [...updatedChat.messages, assistantMessage],
      };

      const finalChats = state.chats.map((chat) =>
        chat.id === finalChat.id ? finalChat : chat,
      );

      dispatch({ type: "SET_CHATS", chats: finalChats });
    } finally {
      dispatch({ type: "SET_LOADING", value: false });
    }
  }, [activeChat, state]);

  const value = {
    ...state,
    activeChat,
    dispatch,
    setInput,
    setUserKeyInput,
    setSelectedGroup,
    handleNewChat,
    handleSelectChat,
    handleImport,
    handleDeleteChat,
    handleSend,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
      <ChatController />
    </ChatContext.Provider>
  );
};

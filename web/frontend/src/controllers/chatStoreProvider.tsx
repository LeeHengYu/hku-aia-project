// Wires reducer-backed state and actions, then provides a unified chat context.

import { useCallback, useMemo, useReducer, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { Message, VertexPromptExport } from "../lib/types";
import { hydrateChatFromExport } from "../lib/storage";
import { sendMessage, saveMessages, deleteMessages } from "../lib/api";
import {
  chatReducer,
  createInitialState,
  createChat,
  titleFromMessage,
} from "./chatStore";
import { ChatContext } from "./chatContext";
import { ChatController } from "./chatController";

const DATASTORE_PATH_GP2 = (
  import.meta.env.VITE_DATASTORE_PATH_GP2 ?? ""
).trim();
const DATASTORE_PATH_GP3 = (
  import.meta.env.VITE_DATASTORE_PATH_GP3 ?? ""
).trim();

export const ChatStoreProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(
    chatReducer,
    undefined,
    createInitialState,
  );
  const queryClient = useQueryClient();

  const activeChat = useMemo(
    () => state.chats.find((chat) => chat.id === state.activeChatId) ?? null,
    [state.chats, state.activeChatId],
  );

  const authKey = state.userKeyInput.trim();

  const setInput = useCallback((value: string) => {
    dispatch({ type: "SET_INPUT", value });
  }, []);

  const setUserKeyInput = useCallback((value: string) => {
    dispatch({ type: "SET_USER_KEY_INPUT", value });
  }, []);

  const setSelectedGroup = useCallback(
    (value: import("./chatStore").GroupSelection) => {
      dispatch({ type: "SET_SELECTED_GROUP", value });
    },
    [],
  );

  const handleNewChat = useCallback(() => {
    const nextChat = createChat();
    dispatch({ type: "SET_CHATS", chats: [nextChat, ...state.chats] });
    dispatch({ type: "SET_ACTIVE_CHAT", chatId: nextChat.id });
  }, [state.chats]);

  const handleSelectChat = useCallback((chatId: string) => {
    dispatch({ type: "SET_ACTIVE_CHAT", chatId });
  }, []);

  const handleImport = useCallback(
    async (data: VertexPromptExport) => {
      const { chat: imported, messages: importedMessages } =
        hydrateChatFromExport(data);
      dispatch({ type: "SET_CHATS", chats: [imported, ...state.chats] });
      dispatch({ type: "SET_ACTIVE_CHAT", chatId: imported.id });

      if (importedMessages.length > 0) {
        queryClient.setQueryData(["messages", imported.id], importedMessages);

        if (authKey) {
          await saveMessages(imported.id, importedMessages, authKey);
        }
      }
    },
    [state.chats, authKey, queryClient],
  );

  const handleDeleteChat = useCallback(
    async (chatId: string) => {
      const remaining = state.chats.filter((chat) => chat.id !== chatId);
      dispatch({ type: "SET_CHATS", chats: remaining });
      if (state.activeChatId === chatId) {
        dispatch({
          type: "SET_ACTIVE_CHAT",
          chatId: remaining.length > 0 ? remaining[0].id : null,
        });
      }

      queryClient.removeQueries({ queryKey: ["messages", chatId] });

      if (authKey) {
        try {
          await deleteMessages(chatId, authKey);
        } catch {
          // Best-effort cleanup
        }
      }
    },
    [state.chats, state.activeChatId, authKey, queryClient],
  );

  const handleSetSystemInstruction = useCallback(
    (chatId: string, value: string | undefined) => {
      dispatch({ type: "SET_SYSTEM_INSTRUCTION", chatId, value });
    },
    [],
  );

  const handleRenameChat = useCallback((chatId: string, title: string) => {
    const trimmed = title.trim();
    if (!trimmed) return;
    dispatch({ type: "SET_CHAT_TITLE", chatId, title: trimmed });
  }, []);

  const handleSend = useCallback(async () => {
    if (!activeChat) return;
    const trimmed = state.input.trim();
    if (!trimmed || state.isLoading) return;

    // Optimistically add user message to cache
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      createdAt: new Date().toISOString(),
    };

    const currentMessages =
      queryClient.getQueryData<Message[]>(["messages", activeChat.id]) ?? [];
    const withUserMsg = [...currentMessages, userMessage];
    queryClient.setQueryData(["messages", activeChat.id], withUserMsg);

    // Update chat title if needed
    if (activeChat.title === "New chat") {
      const updatedChats = state.chats.map((chat) =>
        chat.id === activeChat.id
          ? {
              ...chat,
              title: titleFromMessage(trimmed),
              updatedAt: new Date().toISOString(),
            }
          : chat,
      );
      dispatch({ type: "SET_CHATS", chats: updatedChats });
    }

    dispatch({ type: "SET_INPUT", value: "" });
    dispatch({ type: "SET_LOADING", value: true });

    try {
      const datastorePaths =
        state.selectedGroup === "both"
          ? [DATASTORE_PATH_GP2, DATASTORE_PATH_GP3]
          : state.selectedGroup === "product"
            ? [DATASTORE_PATH_GP3]
            : [DATASTORE_PATH_GP2];

      const data = await sendMessage(
        activeChat.id,
        trimmed,
        {
          systemInstruction: activeChat.systemInstruction ?? null,
          datastorePaths,
        },
        authKey,
      );

      const assistantText = data.text?.trim() || "No response generated.";

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "model",
        content: assistantText,
        createdAt: new Date().toISOString(),
      };

      queryClient.setQueryData(
        ["messages", activeChat.id],
        [...withUserMsg, assistantMessage],
      );
    } catch (error) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "model",
        content:
          error instanceof Error
            ? `Error: ${error.message}`
            : "Error: Unable to reach the backend.",
        createdAt: new Date().toISOString(),
      };

      queryClient.setQueryData(
        ["messages", activeChat.id],
        [...withUserMsg, errorMessage],
      );
    } finally {
      dispatch({ type: "SET_LOADING", value: false });
    }
  }, [activeChat, state, authKey, queryClient]);

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
    handleSetSystemInstruction,
    handleRenameChat,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
      <ChatController />
    </ChatContext.Provider>
  );
};

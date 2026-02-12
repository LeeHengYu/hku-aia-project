// Wires reducer and side effects, then provides chat state/actions contexts.
// dispatch modifies state via reducer, while handlers run side effects and dispatch updates.

import {
  useCallback,
  useEffect,
  useMemo,
  useReducer,
  type ReactNode,
} from "react";
import type { Chat, Message, VertexPromptExport } from "../lib/types";
import {
  hydrateChatFromExport,
  loadActiveChatId,
  loadChats,
  loadUserKey,
  saveActiveChatId,
  saveChats,
  saveUserKey,
} from "../lib/storage";
import {
  chatReducer,
  createChat,
  titleFromMessage,
  type ChatState,
} from "./chatStore";
import {
  ChatActionsContext,
  ChatStateContext,
} from "./chatContext";

const initState = (): ChatState => {
  return {
    chats: loadChats(),
    activeChatId: loadActiveChatId(),
    input: "",
    isLoading: false,
    userKeyInput: loadUserKey(),
    userKey: loadUserKey(),
  };
};

export const ChatStoreProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(chatReducer, undefined, initState);

  const activeChat = useMemo(
    () => state.chats.find((chat) => chat.id === state.activeChatId) ?? null,
    [state.chats, state.activeChatId],
  );

  useEffect(() => {
    if (!state.activeChatId && state.chats.length > 0) {
      dispatch({ type: "SET_ACTIVE_CHAT", chatId: state.chats[0].id });
    }
  }, [state.activeChatId, state.chats]);

  useEffect(() => {
    saveChats(state.chats);
  }, [state.chats]);

  useEffect(() => {
    saveActiveChatId(state.activeChatId);
  }, [state.activeChatId]);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      const trimmed = state.userKeyInput.trim();
      dispatch({ type: "SET_USER_KEY", value: trimmed });
      saveUserKey(trimmed);
    }, 300);

    return () => {
      window.clearTimeout(handle);
    };
  }, [state.userKeyInput]);

  const setInput = useCallback((value: string) => {
    dispatch({ type: "SET_INPUT", value });
  }, []);

  const setUserKeyInput = useCallback((value: string) => {
    dispatch({ type: "SET_USER_KEY_INPUT", value });
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

  const handleRenameChat = useCallback(
    (chatId: string, nextTitle: string) => {
      const title = nextTitle.trim() || "New chat";
      const nextChats = state.chats.map((chat) =>
        chat.id === chatId
          ? { ...chat, title, updatedAt: new Date().toISOString() }
          : chat,
      );
      dispatch({ type: "SET_CHATS", chats: nextChats });
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
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: updatedChat.messages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
          systemInstruction: activeChat.systemInstruction ?? null,
          parameters: activeChat.parameters ?? null,
          model: activeChat.model ?? null,
          authKey: state.userKey,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = (await response.json()) as { text?: string };
      const assistantText = data.text?.trim() || "No response generated.";

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
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
        role: "assistant",
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

  const valueState = useMemo(
    () => ({
      ...state,
      activeChat,
    }),
    [state, activeChat],
  );

  const valueActions = useMemo(
    () => ({
      setInput,
      setUserKeyInput,
      handleNewChat,
      handleSelectChat,
      handleImport,
      handleRenameChat,
      handleDeleteChat,
      handleSend,
    }),
    [
      setInput,
      setUserKeyInput,
      handleNewChat,
      handleSelectChat,
      handleImport,
      handleRenameChat,
      handleDeleteChat,
      handleSend,
    ],
  );

  return (
    <ChatStateContext.Provider value={valueState}>
      <ChatActionsContext.Provider value={valueActions}>
        {children}
      </ChatActionsContext.Provider>
    </ChatStateContext.Provider>
  );
};

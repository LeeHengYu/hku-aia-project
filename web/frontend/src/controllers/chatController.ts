import { useEffect, useMemo, useState } from "react";
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

const createChat = (title = "New chat"): Chat => {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    title,
    createdAt: now,
    updatedAt: now,
    messages: [],
  };
};

const titleFromMessage = (value: string) => {
  const trimmed = value.trim();
  if (!trimmed) return "New chat";
  return trimmed.length > 44 ? `${trimmed.slice(0, 44)}…` : trimmed;
};

export const useChatController = () => {
  const [chats, setChats] = useState<Chat[]>(() => loadChats());
  const [activeChatId, setActiveChatId] = useState<string | null>(() =>
    loadActiveChatId(),
  );
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [userKeyInput, setUserKeyInput] = useState(() => loadUserKey());
  const [userKey, setUserKey] = useState(() => loadUserKey());

  useEffect(() => {
    if (!activeChatId && chats.length > 0) {
      setActiveChatId(chats[0].id);
    }
  }, [activeChatId, chats]);

  useEffect(() => {
    saveChats(chats);
  }, [chats]);

  useEffect(() => {
    saveActiveChatId(activeChatId);
  }, [activeChatId]);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      setUserKey(userKeyInput.trim());
      saveUserKey(userKeyInput.trim());
    }, 300);

    return () => {
      window.clearTimeout(handle);
    };
  }, [userKeyInput]);

  const activeChat = useMemo(
    () => chats.find((chat) => chat.id === activeChatId) ?? null,
    [chats, activeChatId],
  );

  const updateChat = (chatId: string, updater: (chat: Chat) => Chat) => {
    setChats((prev) =>
      prev.map((chat) => (chat.id === chatId ? updater(chat) : chat)),
    );
  };

  const handleNewChat = () => {
    const nextChat = createChat();
    setChats((prev) => [nextChat, ...prev]);
    setActiveChatId(nextChat.id);
  };

  const handleSelectChat = (chatId: string) => {
    setActiveChatId(chatId);
  };

  const handleImport = (data: VertexPromptExport) => {
    const imported = hydrateChatFromExport(data);
    setChats((prev) => [imported, ...prev]);
    setActiveChatId(imported.id);
  };

  const handleDeleteChat = (chatId: string) => {
    setChats((prev) => {
      const remaining = prev.filter((chat) => chat.id !== chatId);
      if (activeChatId === chatId) {
        setActiveChatId(remaining.length > 0 ? remaining[0].id : null);
      }
      return remaining;
    });
  };

  const handleRenameChat = (chatId: string, nextTitle: string) => {
    const title = nextTitle.trim() || "New chat";
    updateChat(chatId, (chat) => ({
      ...chat,
      title,
      updatedAt: new Date().toISOString(),
    }));
  };

  const handleSend = async () => {
    if (!activeChat) return;
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const chatId = activeChat.id;
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      createdAt: new Date().toISOString(),
    };

    updateChat(chatId, (chat) => {
      const title =
        chat.title === "New chat" ? titleFromMessage(trimmed) : chat.title;
      return {
        ...chat,
        title,
        updatedAt: new Date().toISOString(),
        messages: [...chat.messages, userMessage],
      };
    });

    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [...activeChat.messages, userMessage].map((message) => ({
            role: message.role,
            content: message.content,
          })),
          systemInstruction: activeChat.systemInstruction ?? null,
          parameters: activeChat.parameters ?? null,
          model: activeChat.model ?? null,
          authKey: userKey,
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

      updateChat(chatId, (chat) => ({
        ...chat,
        updatedAt: new Date().toISOString(),
        messages: [...chat.messages, assistantMessage],
      }));
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

      updateChat(chatId, (chat) => ({
        ...chat,
        updatedAt: new Date().toISOString(),
        messages: [...chat.messages, assistantMessage],
      }));
    } finally {
      setIsLoading(false);
    }
  };

  return {
    chats,
    activeChatId,
    activeChat,
    input,
    isLoading,
    setInput,
    userKeyInput,
    setUserKeyInput,
    handleNewChat,
    handleSelectChat,
    handleImport,
    handleRenameChat,
    handleDeleteChat,
    handleSend,
  };
};

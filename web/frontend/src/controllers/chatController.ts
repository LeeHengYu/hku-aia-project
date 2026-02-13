// Renderless controller for side effects and local storage subscriptions.

import { useEffect } from "react";
import {
  loadActiveChatId,
  loadChats,
  loadUserKey,
  saveActiveChatId,
  saveChats,
  saveUserKey,
} from "../lib/storage";
import { useChatContext } from "./useChatStore";

export const ChatController = () => {
  const {
    isHydrated,
    chats,
    activeChatId,
    userKeyInput,
    userKey,
    dispatch,
  } = useChatContext();

  useEffect(() => {
    if (isHydrated) return;

    const storedChats = loadChats();
    const storedActiveChatId = loadActiveChatId();
    const storedUserKey = loadUserKey();

    dispatch({
      type: "HYDRATE",
      payload: {
        chats: storedChats,
        activeChatId: storedActiveChatId,
        userKeyInput: storedUserKey,
        userKey: storedUserKey,
      },
    });
  }, [isHydrated, dispatch]);

  useEffect(() => {
    if (!isHydrated) return;

    if (!activeChatId && chats.length > 0) {
      dispatch({ type: "SET_ACTIVE_CHAT", chatId: chats[0].id });
      return;
    }

    if (!activeChatId) return;
    if (chats.some((chat) => chat.id === activeChatId)) return;

    const storedChats = loadChats();
    if (storedChats.length === 0) {
      dispatch({ type: "SET_ACTIVE_CHAT", chatId: null });
      return;
    }

    dispatch({ type: "SET_CHATS", chats: storedChats });

    if (!storedChats.some((chat) => chat.id === activeChatId)) {
      dispatch({ type: "SET_ACTIVE_CHAT", chatId: storedChats[0].id });
    }
  }, [isHydrated, activeChatId, chats, dispatch]);

  useEffect(() => {
    if (!isHydrated) return;
    saveChats(chats);
  }, [isHydrated, chats]);

  useEffect(() => {
    if (!isHydrated) return;
    saveActiveChatId(activeChatId);
  }, [isHydrated, activeChatId]);

  useEffect(() => {
    if (!isHydrated) return;

    const handle = window.setTimeout(() => {
      const trimmed = userKeyInput.trim();
      if (trimmed !== userKey) {
        dispatch({ type: "SET_USER_KEY", value: trimmed });
      }
      saveUserKey(trimmed);
    }, 300);

    return () => {
      window.clearTimeout(handle);
    };
  }, [isHydrated, userKeyInput, userKey, dispatch]);

  return null;
};

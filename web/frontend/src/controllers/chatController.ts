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

    if (chats.length === 0) {
      if (activeChatId !== null) {
        dispatch({ type: "SET_ACTIVE_CHAT", chatId: null });
      }
      return;
    }

    if (!activeChatId || !chats.some((chat) => chat.id === activeChatId)) {
      dispatch({ type: "SET_ACTIVE_CHAT", chatId: chats[0].id });
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
    const trimmed = userKeyInput.trim();
    if (trimmed !== userKey) {
      dispatch({ type: "SET_USER_KEY", value: trimmed });
    }
    saveUserKey(trimmed);
  }, [isHydrated, userKeyInput, userKey, dispatch]);

  return null;
};

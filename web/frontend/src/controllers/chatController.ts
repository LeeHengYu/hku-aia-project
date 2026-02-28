// Renderless controller for persisting state to localStorage.

import { useEffect } from "react";
import { saveActiveChatId, saveChats, saveUserKey } from "../lib/storage";
import { useChatState } from "./useChatStore";

export const ChatController = () => {
  const { chats, activeChatId, userKeyInput } = useChatState();

  useEffect(() => {
    saveChats(chats);
  }, [chats]);

  useEffect(() => {
    saveActiveChatId(activeChatId);
  }, [activeChatId]);

  useEffect(() => {
    saveUserKey(userKeyInput.trim());
  }, [userKeyInput]);

  return null;
};

// Renderless controller for persisting state to localStorage.

import { useEffect } from "react";
import { saveActiveChatId, saveChats, saveUserKey } from "../lib/storage";
import { useChatContext } from "./useChatStore";

export const ChatController = () => {
  const { chats, activeChatId, userKeyInput } = useChatContext();

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

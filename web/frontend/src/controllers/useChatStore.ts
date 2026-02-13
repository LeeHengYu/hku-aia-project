// Typed hook for reading the unified chat context.
import { useContext } from "react";
import { ChatContext } from "./chatContext";

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatContext must be used within ChatStoreProvider");
  }
  return context;
};

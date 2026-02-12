// Typed hooks for reading chat state/actions from React contexts.
import { useContext } from "react";
import { ChatActionsContext, ChatStateContext } from "./chatContext";

export const useChatState = () => {
  const context = useContext(ChatStateContext);
  if (!context) {
    throw new Error("useChatState must be used within ChatStoreProvider");
  }
  return context;
};

export const useChatActions = () => {
  const context = useContext(ChatActionsContext);
  if (!context) {
    throw new Error("useChatActions must be used within ChatStoreProvider");
  }
  return context;
};

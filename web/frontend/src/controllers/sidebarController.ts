// Sidebar controller: maps sidebar-specific state/actions from chat contexts.

import { useChatActions, useChatState } from "./useChatStore";

export const useSidebarController = () => {
  const { chats, activeChatId } = useChatState();
  const {
    handleSelectChat,
    handleNewChat,
    handleImport,
    handleRenameChat,
    handleDeleteChat,
  } = useChatActions();

  return {
    chats,
    activeChatId,
    handleSelectChat,
    handleNewChat,
    handleImport,
    handleRenameChat,
    handleDeleteChat,
  };
};

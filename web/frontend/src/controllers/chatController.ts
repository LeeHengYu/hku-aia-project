// Chat view controller: selects chat-panel state and actions for the UI.
import { useChatActions, useChatState } from "./useChatStore";

export const useChatController = () => {
  const { activeChat, input, isLoading, userKeyInput } = useChatState();
  const { setInput, setUserKeyInput, handleSend } = useChatActions();

  return {
    activeChat,
    input,
    isLoading,
    userKeyInput,
    setInput,
    setUserKeyInput,
    handleSend,
  };
};

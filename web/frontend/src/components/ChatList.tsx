import { useChatContext } from "../controllers/useChatStore";
import type { Chat } from "../lib/types";

interface ChatListItemProps {
  chat: Chat;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

const ChatListItem = ({ chat, isActive, onSelect, onDelete }: ChatListItemProps) => (
  <div
    className={`chat-item border ${
      isActive ? "border-teal-400/50 bg-teal-400/[0.08]" : "border-transparent"
    }`}
  >
    <button className="chat-select" onClick={onSelect} type="button">
      <div className="chat-title">{chat.title}</div>
    </button>
    <button
      className="chat-delete text-slate-400 dark:text-slate-500 hover:text-red-400 dark:hover:text-red-400"
      type="button"
      onClick={onDelete}
      aria-label={`Delete ${chat.title}`}
    >
      ×
    </button>
  </div>
);

const ChatList = () => {
  const { chats, activeChatId, handleSelectChat, handleDeleteChat } =
    useChatContext();

  return (
    <div className="sidebar-section">
      <div className="sidebar-title text-slate-500 dark:text-slate-400">Chats</div>
      <div className="chat-list">
        {chats.map((chat) => (
          <ChatListItem
            key={chat.id}
            chat={chat}
            isActive={chat.id === activeChatId}
            onSelect={() => handleSelectChat(chat.id)}
            onDelete={() => handleDeleteChat(chat.id)}
          />
        ))}
      </div>
    </div>
  );
};

export default ChatList;

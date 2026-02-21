import { useState, useRef, useEffect } from "react";
import { useChatContext } from "../controllers/useChatStore";
import type { Chat } from "../lib/types";

interface ChatListItemProps {
  chat: Chat;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (title: string) => void;
}

const ChatListItem = ({ chat, isActive, onSelect, onDelete, onRename }: ChatListItemProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(chat.title);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [isEditing]);

  const commitEdit = () => {
    const trimmed = editValue.trim();
    if (trimmed && trimmed !== chat.title) {
      onRename(trimmed);
    } else {
      setEditValue(chat.title);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      commitEdit();
    } else if (e.key === "Escape") {
      setEditValue(chat.title);
      setIsEditing(false);
    }
  };

  return (
    <div
      className={`chat-item border ${
        isActive ? "border-teal-400/50 bg-teal-400/[0.08]" : "border-transparent"
      }`}
    >
      {isEditing ? (
        <input
          ref={inputRef}
          className="chat-title-input text-slate-800 dark:text-slate-100"
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={commitEdit}
          onKeyDown={handleKeyDown}
        />
      ) : (
        <button className="chat-select" onClick={onSelect} type="button">
          <div className="chat-title">{chat.title}</div>
        </button>
      )}
      <button
        className="chat-edit text-slate-400 dark:text-slate-500 hover:text-teal-400 dark:hover:text-teal-400"
        type="button"
        onClick={() => {
          setEditValue(chat.title);
          setIsEditing(true);
        }}
        aria-label={`Edit ${chat.title}`}
      >
        &#9998;
      </button>
      <button
        className="chat-delete text-slate-400 dark:text-slate-500 hover:text-red-400 dark:hover:text-red-400"
        type="button"
        onClick={onDelete}
        aria-label={`Delete ${chat.title}`}
      >
        &times;
      </button>
    </div>
  );
};

const ChatList = () => {
  const { chats, activeChatId, handleSelectChat, handleDeleteChat, handleRenameChat } =
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
            onRename={(title) => handleRenameChat(chat.id, title)}
          />
        ))}
      </div>
    </div>
  );
};

export default ChatList;

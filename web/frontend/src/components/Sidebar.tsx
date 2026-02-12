import { useRef, useState, type ChangeEvent } from "react";
import type { Chat } from "../lib/types";
import { useSidebarController } from "../controllers/sidebarController";

const Sidebar = () => {
  const {
    chats,
    activeChatId,
    handleSelectChat,
    handleNewChat,
    handleImport,
    handleRenameChat,
    handleDeleteChat,
  } = useSidebarController();

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const data = JSON.parse(text);
      handleImport(data);
    } catch (error) {
      console.error(error);
      alert(
        "Unable to parse the JSON file. Please use the prompt exported from Vertex AI.",
      );
    } finally {
      event.target.value = "";
    }
  };

  const startRename = (chat: Chat) => {
    setEditingChatId(chat.id);
    setEditingTitle(chat.title);
  };

  const commitRename = () => {
    if (!editingChatId) return;
    handleRenameChat(editingChatId, editingTitle);
    setEditingChatId(null);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <button
          className="sidebar-action"
          onClick={handleNewChat}
          type="button"
        >
          New chat
        </button>
        <button
          className="sidebar-secondary"
          onClick={handleImportClick}
          type="button"
        >
          Import prompt
        </button>
        <input
          ref={fileInputRef}
          className="file-input"
          type="file"
          accept="application/json"
          onChange={handleFileChange}
        />
      </div>

      <div className="sidebar-section">
        <div className="sidebar-title">Chats</div>
        <div className="chat-list">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${
                chat.id === activeChatId ? "active" : ""
              }`}
            >
              {editingChatId === chat.id ? (
                <input
                  className="chat-input"
                  value={editingTitle}
                  onChange={(event) => setEditingTitle(event.target.value)}
                  onBlur={() => setEditingChatId(null)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") commitRename();
                    if (event.key === "Escape") setEditingChatId(null);
                  }}
                />
              ) : (
                <>
                  <button
                    className="chat-select"
                    onClick={() => handleSelectChat(chat.id)}
                    type="button"
                  >
                    <div className="chat-title">{chat.title}</div>
                  </button>
                  <button
                    className="chat-rename"
                    type="button"
                    onClick={() => startRename(chat)}
                    aria-label={`Rename ${chat.title}`}
                  >
                    ✎
                  </button>
                  <button
                    className="chat-delete"
                    type="button"
                    onClick={() => handleDeleteChat(chat.id)}
                    aria-label={`Delete ${chat.title}`}
                  >
                    ×
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

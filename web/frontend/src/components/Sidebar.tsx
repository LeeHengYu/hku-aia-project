import { useRef, type ChangeEvent } from "react";
import type { Chat, VertexPromptExport } from "../lib/types";

interface SidebarProps {
  chats: Chat[];
  activeChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onImport: (data: VertexPromptExport) => void;
  onLoadSample: () => void;
  onDeleteChat: (chatId: string) => void;
}

const Sidebar = ({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onImport,
  onLoadSample,
  onDeleteChat,
}: SidebarProps) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const data = JSON.parse(text);
      onImport(data);
    } catch (error) {
      console.error(error);
      alert(
        "Unable to parse the JSON file. Please use the prompt exported from Vertex AI.",
      );
    } finally {
      event.target.value = "";
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <button className="sidebar-action" onClick={onNewChat} type="button">
          New chat
        </button>
        <button
          className="sidebar-secondary"
          onClick={handleImportClick}
          type="button"
        >
          Import prompt
        </button>
        {import.meta.env.DEV ? (
          <button
            className="sidebar-secondary"
            onClick={onLoadSample}
            type="button"
          >
            Load sample
          </button>
        ) : null}
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
              <button
                className="chat-select"
                onClick={() => onSelectChat(chat.id)}
                type="button"
              >
                <div className="chat-title">{chat.title}</div>
                <div className="chat-meta">
                  {new Date(chat.updatedAt).toLocaleDateString()}
                </div>
              </button>
              <button
                className="chat-delete"
                type="button"
                onClick={() => onDeleteChat(chat.id)}
                aria-label={`Delete ${chat.title}`}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

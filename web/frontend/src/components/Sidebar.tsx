import { useRef, type ChangeEvent } from "react";
import { useChatContext } from "../controllers/useChatStore";

const Sidebar = () => {
  const {
    chats,
    activeChatId,
    handleSelectChat,
    handleNewChat,
    handleImport,
    handleDeleteChat,
  } = useChatContext();

  const fileInputRef = useRef<HTMLInputElement | null>(null);

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
        "Unable to parse the JSON file. Please use the prompt exported from Vertex AI Studio.",
      );
    } finally {
      event.target.value = "";
    }
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
          onClick={() => {
            fileInputRef.current?.click();
          }}
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
              <button
                className="chat-select"
                onClick={() => handleSelectChat(chat.id)}
                type="button"
              >
                <div className="chat-title">{chat.title}</div>
              </button>
              <button
                className="chat-delete"
                type="button"
                onClick={() => handleDeleteChat(chat.id)}
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

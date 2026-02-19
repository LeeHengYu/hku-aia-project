import { useChatContext } from "../controllers/useChatStore";

const ChatList = () => {
  const { chats, activeChatId, handleSelectChat, handleDeleteChat } =
    useChatContext();

  return (
    <div className="sidebar-section">
      <div className="sidebar-title">Chats</div>
      <div className="chat-list">
        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`chat-item ${chat.id === activeChatId ? "active" : ""}`}
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
  );
};

export default ChatList;

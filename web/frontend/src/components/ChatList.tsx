import { useChatContext } from "../controllers/useChatStore";

const ChatList = () => {
  const { chats, activeChatId, handleSelectChat, handleDeleteChat } =
    useChatContext();

  return (
    <div className="sidebar-section">
      <div className="sidebar-title text-slate-500 dark:text-slate-400">Chats</div>
      <div className="chat-list">
        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`chat-item border ${
              chat.id === activeChatId
                ? "border-teal-400/50 bg-teal-400/[0.08]"
                : "border-transparent"
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
              className="chat-delete text-slate-400 dark:text-slate-500 hover:text-red-400 dark:hover:text-red-400"
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

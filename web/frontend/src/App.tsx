import Sidebar from "./components/Sidebar";
import ChatView from "./components/ChatView";
import Composer from "./components/Composer";
import { useChatController } from "./controllers/chatController";

function App() {
  const {
    chats,
    activeChatId,
    activeChat,
    input,
    isLoading,
    setInput,
    userKeyInput,
    setUserKeyInput,
    handleNewChat,
    handleSelectChat,
    handleImport,
    handleRenameChat,
    handleDeleteChat,
    handleSend,
  } = useChatController();

  return (
    <div className="app">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onImport={handleImport}
        onRenameChat={handleRenameChat}
        onDeleteChat={handleDeleteChat}
      />
      <main className="main">
        <div className="main-header">
          <div>
            <div className="main-title">Gemini</div>
            <div className="main-subtitle">
              Grounded responses with clean markdown rendering.
            </div>
          </div>
          {activeChat?.systemInstruction ? (
            <div className="system-indicator">Prompt loaded</div>
          ) : null}
        </div>
        <div className="auth-row">
          <input
            id="auth-key"
            className="auth-input"
            type="text"
            placeholder="Enter access key"
            value={userKeyInput}
            onChange={(event) => setUserKeyInput(event.target.value)}
          />
        </div>
        <ChatView messages={activeChat?.messages ?? []} isLoading={isLoading} />
        <Composer
          value={input}
          onChange={setInput}
          onSend={handleSend}
          disabled={!activeChat || isLoading}
        />
      </main>
    </div>
  );
}

export default App;

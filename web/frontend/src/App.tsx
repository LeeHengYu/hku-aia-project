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
    handleNewChat,
    handleSelectChat,
    handleImport,
    handleLoadSample,
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
        onLoadSample={handleLoadSample}
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

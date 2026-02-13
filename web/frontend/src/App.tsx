import Sidebar from "./components/Sidebar";
import ChatView from "./components/ChatView";
import Composer from "./components/Composer";
import { ChatStoreProvider } from "./controllers/chatStoreProvider";
import { useChatContext } from "./controllers/useChatStore";

const AppLayout = () => {
  const {
    activeChat,
    input,
    isLoading,
    userKeyInput,
    setInput,
    setUserKeyInput,
    handleSend,
  } = useChatContext();

  return (
    <div className="app">
      <Sidebar />
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
          <label className="auth-label" htmlFor="auth-key">
            Access key
          </label>
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
};

function App() {
  return (
    <ChatStoreProvider>
      <AppLayout />
    </ChatStoreProvider>
  );
}

export default App;

import Sidebar from "./components/Sidebar";
import ChatView from "./components/ChatView";
import Composer from "./components/Composer";
import MainHeader from "./components/MainHeader";
import AuthKeyInput from "./components/AuthKeyInput";
import { ChatStoreProvider } from "./controllers/chatStoreProvider";
import { useChatContext } from "./controllers/useChatStore";
import { APP_TITLE } from "./constants/uiText";

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
        <MainHeader
          title={APP_TITLE}
          showPromptLoaded={Boolean(activeChat?.systemInstruction)}
        />
        <AuthKeyInput value={userKeyInput} onChange={setUserKeyInput} />
        <ChatView messages={activeChat?.messages ?? []} isLoading={isLoading} />
        <Composer
          value={input}
          onChange={setInput}
          onSend={handleSend}
          disabled={!activeChat || isLoading}
          visible={Boolean(activeChat)}
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

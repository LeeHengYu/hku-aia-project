import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Sidebar from "./components/Sidebar";
import ChatView from "./components/ChatView";
import Composer from "./components/Composer";
import MainHeader from "./components/MainHeader";
import AuthKeyInput from "./components/AuthKeyInput";
import { ChatStoreProvider } from "./controllers/chatStoreProvider";
import { useChatContext } from "./controllers/useChatStore";
import { APP_TITLE } from "./constants/uiText";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      retry: false,
    },
  },
});

const AppLayout = () => {
  const {
    activeChat,
    messages,
    input,
    isLoading,
    userKeyInput,
    setInput,
    setUserKeyInput,
    handleSend,
  } = useChatContext();

  return (
    <div className="app bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <Sidebar />
      <main className="main">
        <MainHeader title={APP_TITLE} />
        <AuthKeyInput value={userKeyInput} onChange={setUserKeyInput} />
        <ChatView messages={messages} isLoading={isLoading} />
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
    <QueryClientProvider client={queryClient}>
      <ChatStoreProvider>
        <AppLayout />
      </ChatStoreProvider>
    </QueryClientProvider>
  );
}

export default App;

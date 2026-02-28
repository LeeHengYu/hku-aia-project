import { Component, Suspense, type ReactNode } from "react";
import { QueryClient, QueryClientProvider, QueryErrorResetBoundary, useSuspenseQuery } from "@tanstack/react-query";
import Sidebar from "./components/Sidebar";
import ChatView from "./components/ChatView";
import Composer from "./components/Composer";
import MainHeader from "./components/MainHeader";
import AuthKeyInput from "./components/AuthKeyInput";
import { ChatStoreProvider } from "./controllers/chatStoreProvider";
import { useChatState, useChatActions } from "./controllers/useChatStore";
import { fetchMessages } from "./lib/api";
import type { Message } from "./lib/types";
import { APP_TITLE } from "./constants/uiText";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      retry: false,
    },
  },
});

const ChatSkeleton = () => (
  <div className="chat-view chat-skeleton" aria-busy="true" aria-label="Loading messages">
    {(["model", "user", "model"] as const).map((role, i) => (
      <div key={i} className={`skeleton-bubble skeleton-bubble--${role}`} />
    ))}
  </div>
);

class ChatLoadErrorBoundary extends Component<
  { children: ReactNode; onReset: () => void },
  { error: Error | null }
> {
  state = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  handleRetry = () => {
    this.props.onReset();
    this.setState({ error: null });
  };

  render() {
    if (this.state.error) {
      return (
        <div className="chat-empty">
          <p className="text-slate-500 dark:text-slate-400">
            Could not load messages.{" "}
            <span className="text-slate-400 dark:text-slate-500 text-sm">
              {(this.state.error as Error).message}
            </span>
          </p>
          <button
            className="text-sm text-teal-600 dark:text-teal-400 underline underline-offset-2 mt-1"
            onClick={this.handleRetry}
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

const ConversationView = ({ chatId, isLoading }: { chatId: string; isLoading: boolean }) => {
  const { userKeyInput } = useChatState();
  const { data: messages } = useSuspenseQuery<Message[]>({
    queryKey: ["messages", chatId],
    queryFn: () => fetchMessages(chatId, userKeyInput.trim()),
    staleTime: Infinity,
  });

  return <ChatView messages={messages} isLoading={isLoading} />;
};

const AppLayout = () => {
  const { activeChat, input, isLoading, userKeyInput } = useChatState();
  const { setInput, setUserKeyInput, handleSend } = useChatActions();

  const authKey = userKeyInput.trim();

  return (
    <div className="app bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <Sidebar />
      <main className="main">
        <MainHeader title={APP_TITLE} />
        <AuthKeyInput value={userKeyInput} onChange={setUserKeyInput} />
        {activeChat && authKey ? (
          <QueryErrorResetBoundary key={activeChat.id}>
            {({ reset }) => (
              <ChatLoadErrorBoundary onReset={reset}>
                <Suspense fallback={<ChatSkeleton />}>
                  <ConversationView chatId={activeChat.id} isLoading={isLoading} />
                </Suspense>
              </ChatLoadErrorBoundary>
            )}
          </QueryErrorResetBoundary>
        ) : (
          <ChatView messages={[]} isLoading={false} />
        )}
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

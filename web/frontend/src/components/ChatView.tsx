import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import type { Message } from "../lib/types";

interface ChatViewProps {
  messages: Message[];
  isLoading?: boolean;
}

const ChatView = ({ messages, isLoading = false }: ChatViewProps) => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    container.scrollTop = container.scrollHeight;
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="chat-empty">
        <div className="chat-empty-subtitle">
          Import a prompt or send a message to begin.
        </div>
        {import.meta.env.DEV ? (
          <div className="chat-empty-subtitle">
            Or load the sample chat from the sidebar.
          </div>
        ) : null}
      </div>
    );
  }

  return (
    <div className="chat-view" ref={containerRef}>
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isLoading ? (
        <MessageBubble
          message={{
            id: "loading",
            role: "assistant",
            content: "Thinking…",
            createdAt: new Date().toISOString(),
          }}
        />
      ) : null}
    </div>
  );
};

export default ChatView;

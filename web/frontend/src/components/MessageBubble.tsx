import Markdown from "../lib/markdown";
import type { Message } from "../lib/types";

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === "user";

  return (
    <div
      className={
        isUser
          ? "message user bg-blue-50 dark:bg-slate-700 border border-teal-200 dark:border-teal-700"
          : "message assistant bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
      }
    >
      <div className="message-body">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <Markdown content={message.content} />
        )}
      </div>
    </div>
  );
};

export default MessageBubble;

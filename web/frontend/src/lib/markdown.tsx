import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState, type ComponentPropsWithoutRef, type ReactNode } from "react";

interface MarkdownProps {
  content: string;
}

const MarkdownTable = ({ children, ...props }: ComponentPropsWithoutRef<"table">) => (
  <div className="table-wrap">
    <table {...props}>{children}</table>
  </div>
);

const MarkdownTh = ({ children, ...props }: ComponentPropsWithoutRef<"th">) => (
  <th
    {...props}
    className="table-head border border-slate-200 dark:border-slate-700 bg-teal-500/[0.12] dark:bg-teal-500/[0.10]"
  >
    {children}
  </th>
);

const MarkdownTd = ({ children, ...props }: ComponentPropsWithoutRef<"td">) => (
  <td
    {...props}
    className="table-cell border border-slate-200 dark:border-slate-700"
  >
    {children}
  </td>
);

const extractText = (node: ReactNode): string => {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(extractText).join("");
  if (node && typeof node === "object" && "props" in node) {
    return extractText((node as { props: { children?: ReactNode } }).props.children);
  }
  return "";
};

const CodeBlockCopyButton = ({ text }: { text: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1000);
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      className="code-block-copy"
      aria-label="Copy code"
    >
      {copied ? (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ) : (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
        </svg>
      )}
    </button>
  );
};

const MarkdownCodeBlock = ({ children }: ComponentPropsWithoutRef<"pre">) => {
  const text = extractText(children);
  return (
    <div className="code-block-wrap">
      <CodeBlockCopyButton text={text} />
      <pre className="code-block bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-700">
        {children}
      </pre>
    </div>
  );
};

const MarkdownInlineCode = ({
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<"code">) => {
  if (className) {
    return (
      <code {...props} className={className}>
        {children}
      </code>
    );
  }
  return (
    <code
      {...props}
      className="inline-code bg-blue-500/[0.15] dark:bg-blue-500/[0.20] text-blue-700 dark:text-blue-300"
    >
      {children}
    </code>
  );
};

const Markdown = ({ content }: MarkdownProps) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    components={{
      table: MarkdownTable,
      th: MarkdownTh,
      td: MarkdownTd,
      pre: MarkdownCodeBlock,
      code: MarkdownInlineCode,
    }}
  >
    {content}
  </ReactMarkdown>
);

export default Markdown;

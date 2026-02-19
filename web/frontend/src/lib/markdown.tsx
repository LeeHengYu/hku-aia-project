import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ComponentPropsWithoutRef } from "react";

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

const MarkdownCodeBlock = ({ children }: ComponentPropsWithoutRef<"pre">) => (
  <pre className="code-block bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-700">
    {children}
  </pre>
);

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

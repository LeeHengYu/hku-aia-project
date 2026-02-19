import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownProps {
  content: string;
}

const Markdown = ({ content }: MarkdownProps) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    components={{
      table: ({ children, ...props }) => (
        <div className="table-wrap">
          <table {...props}>{children}</table>
        </div>
      ),
      th: ({ children, ...props }) => (
        <th
          {...props}
          className="table-head border border-slate-200 dark:border-slate-700 bg-teal-500/[0.12] dark:bg-teal-500/[0.10]"
        >
          {children}
        </th>
      ),
      td: ({ children, ...props }) => (
        <td
          {...props}
          className="table-cell border border-slate-200 dark:border-slate-700"
        >
          {children}
        </td>
      ),
      pre: ({ children }) => (
        <pre className="code-block bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-700">
          {children}
        </pre>
      ),
      code: ({ className, children, ...props }) => {
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
      },
    }}
  >
    {content}
  </ReactMarkdown>
);

export default Markdown;

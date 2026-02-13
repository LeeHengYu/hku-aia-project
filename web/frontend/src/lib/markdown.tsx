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
        <th {...props} className="table-head">
          {children}
        </th>
      ),
      td: ({ children, ...props }) => (
        <td {...props} className="table-cell">
          {children}
        </td>
      ),
      pre: ({ children }) => <pre className="code-block">{children}</pre>,
      code: ({ className, children, ...props }) => {
        if (className) {
          return (
            <code {...props} className={className}>
              {children}
            </code>
          );
        }
        return (
          <code {...props} className="inline-code">
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

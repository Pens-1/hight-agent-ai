/**
 * Markdownレンダラー（数式対応）
 */
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer = ({ content }: MarkdownRendererProps) => {
  return (
    <div className="prose prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // コードブロックのカスタマイズ
          code: ({ node, inline, className, children, ...props }) => {
            if (inline) {
              return (
                <code className="px-1 py-0.5 bg-gray-800 rounded text-sm" {...props}>
                  {children}
                </code>
              );
            }
            return (
              <code className={`block p-4 bg-gray-800 rounded overflow-x-auto ${className || ''}`} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};


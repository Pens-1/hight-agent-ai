import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'

export const MarkdownRenderer = ({ content }: { content: string }) => {
	return (
		<ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
			{content}
		</ReactMarkdown>
	)
}



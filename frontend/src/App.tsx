import { useState } from 'react'
import { useSettings } from './store/useSettings'
import { MarkdownRenderer } from './components/MarkdownRenderer'

export const App = () => {
	const { useRAG, toggleRAG } = useSettings()
	const [answer, setAnswer] = useState<string>('')

	return (
		<div className="min-h-screen flex flex-col">
			<header className="p-4 border-b border-gray-800 flex items-center justify-between">
				<h1 className="text-lg font-semibold">hight-agent-ai</h1>
				<div className="flex items-center gap-4">
					<label className="flex items-center gap-2">
						<span className="text-sm text-gray-300">RAG</span>
						<input type="checkbox" checked={useRAG} onChange={toggleRAG} />
					</label>
				</div>
			</header>
			<main className="flex-1 p-4">
				<div className="mb-4 text-sm text-gray-400">ダークテーマ / Web検索は未実装</div>
				<MarkdownRenderer content={answer || 'ここに解答が表示されます'} />
			</main>
		</div>
	)
}



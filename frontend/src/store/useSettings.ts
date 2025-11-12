import { create } from 'zustand'

type SettingsState = {
	useRAG: boolean
	toggleRAG: () => void
}

export const useSettings = create<SettingsState>((set) => ({
	useRAG: true,
	toggleRAG: () => set((s) => ({ useRAG: !s.useRAG })),
}))



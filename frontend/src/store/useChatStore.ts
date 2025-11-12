/**
 * チャット状態管理（Zustand）
 */
import { create } from 'zustand';
import type { Message } from '../types';

interface ChatStore {
  messages: Message[];
  isLoading: boolean;
  sessionId: string;
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  isLoading: false,
  sessionId: crypto.randomUUID(),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setLoading: (loading) =>
    set(() => ({
      isLoading: loading,
    })),

  clearMessages: () =>
    set(() => ({
      messages: [],
      sessionId: crypto.randomUUID(),
    })),
}));


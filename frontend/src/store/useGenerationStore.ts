import { create } from 'zustand'
import type { GenerationState, HistoryItem } from '@types/index'

interface GenerationStore extends GenerationState {
  history: HistoryItem[]

  // 상태 업데이트 액션
  setLoading: (isLoading: boolean) => void
  setProgress: (progress: number) => void
  setError: (error: string | null) => void

  // 히스토리 관리
  addToHistory: (item: HistoryItem) => void
  clearHistory: () => void
  removeFromHistory: (id: string) => void

  // 리셋
  reset: () => void
}

const initialState: GenerationState = {
  isLoading: false,
  progress: 0,
  error: null,
}

export const useGenerationStore = create<GenerationStore>((set) => ({
  ...initialState,
  history: [],

  setLoading: (isLoading) => set({ isLoading }),

  setProgress: (progress) => set({ progress }),

  setError: (error) => set({ error, isLoading: false }),

  addToHistory: (item) =>
    set((state) => ({
      history: [item, ...state.history],
    })),

  clearHistory: () => set({ history: [] }),

  removeFromHistory: (id) =>
    set((state) => ({
      history: state.history.filter((item) => item.id !== id),
    })),

  reset: () => set({ ...initialState }),
}))

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type ThemePreference = 'light' | 'dark' | 'system'

// 预设主题色
export const PRESET_COLORS = [
  { name: '默认蓝', color: '#1976d2' },
  { name: '深紫', color: '#7b1fa2' },
  { name: '青色', color: '#0097a7' },
  { name: '深绿', color: '#388e3c' },
  { name: '琥珀', color: '#f57c00' },
  { name: '玫红', color: '#c2185b' },
  { name: '靛青', color: '#303f9f' },
  { name: '棕色', color: '#5d4037' },
]

interface ThemeState {
  preference: ThemePreference  // 用户选择的日夜模式
  mode: 'light' | 'dark'       // 实际应用的主题
  primaryColor: string         // 主题色
  setPrimaryColor: (color: string) => void
  setPreference: (preference: ThemePreference) => void
  initSystemListener: () => () => void  // 返回清理函数
}

// 获取系统主题
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return 'dark'
}

// 根据偏好计算实际主题
const resolveMode = (preference: ThemePreference): 'light' | 'dark' => {
  if (preference === 'system') {
    return getSystemTheme()
  }
  return preference
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      preference: 'system',
      mode: getSystemTheme(),
      primaryColor: '#1976d2',  // 默认蓝色
      
      setPrimaryColor: (color) => {
        set({ primaryColor: color })
      },
      
      setPreference: (preference) => {
        set({
          preference,
          mode: resolveMode(preference),
        })
      },
      
      // 初始化系统主题监听
      initSystemListener: () => {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        
        const handler = (e: MediaQueryListEvent) => {
          const { preference } = get()
          if (preference === 'system') {
            set({ mode: e.matches ? 'dark' : 'light' })
          }
        }
        
        mediaQuery.addEventListener('change', handler)
        
        // 返回清理函数
        return () => mediaQuery.removeEventListener('change', handler)
      },
    }),
    {
      name: 'theme-storage',
      partialize: (state) => ({ 
        preference: state.preference,
        primaryColor: state.primaryColor,
      }),
      onRehydrateStorage: () => (state) => {
        // 恢复存储后重新计算 mode
        if (state) {
          state.mode = resolveMode(state.preference)
        }
      },
    }
  )
)

// 便捷 hook
export const useThemePreference = () => useThemeStore((s) => s.preference)
export const useThemeMode = () => useThemeStore((s) => s.mode)
export const usePrimaryColor = () => useThemeStore((s) => s.primaryColor)

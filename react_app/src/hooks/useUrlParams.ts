/**
 * URL 参数同步 Hook
 * 将组件状态与 URL 查询参数同步，支持返回时恢复状态
 */
import { useSearchParams, useLocation } from 'react-router-dom'
import { useCallback, useMemo } from 'react'

// 参数值类型
type ParamValue = string | number | string[] | number[] | null | undefined

// 参数配置
interface ParamConfig {
  type: 'string' | 'number' | 'array' | 'numberArray'
  default?: ParamValue
}

/**
 * 使用 URL 参数
 * 自动同步状态到 URL，支持多种类型
 */
export function useUrlParams<T extends Record<string, ParamConfig>>(
  config: T
): {
  params: { [K in keyof T]: T[K]['type'] extends 'number' ? number | null
    : T[K]['type'] extends 'array' ? string[]
    : T[K]['type'] extends 'numberArray' ? number[]
    : string | null }
  setParam: (key: keyof T, value: ParamValue) => void
  setParams: (updates: Partial<{ [K in keyof T]: ParamValue }>) => void
  clearParams: () => void
} {
  const [searchParams, setSearchParams] = useSearchParams()
  const location = useLocation()

  // 解析当前 URL 参数
  const params = useMemo(() => {
    const result: Record<string, ParamValue> = {}
    
    for (const [key, cfg] of Object.entries(config)) {
      const value = searchParams.get(key)
      
      if (value === null || value === '') {
        result[key] = cfg.default ?? null
        continue
      }
      
      switch (cfg.type) {
        case 'number':
          const num = parseInt(value, 10)
          result[key] = isNaN(num) ? (cfg.default ?? null) : num
          break
        case 'array':
          result[key] = value.split(',').filter(Boolean)
          break
        case 'numberArray':
          result[key] = value.split(',').map(v => parseInt(v, 10)).filter(n => !isNaN(n))
          break
        default:
          result[key] = value
      }
    }
    
    return result as any
  }, [searchParams, config])

  // 设置单个参数
  const setParam = useCallback((key: keyof T, value: ParamValue) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev)
      
      if (value === null || value === undefined || value === '' || 
          (Array.isArray(value) && value.length === 0)) {
        newParams.delete(key as string)
      } else if (Array.isArray(value)) {
        newParams.set(key as string, value.join(','))
      } else {
        newParams.set(key as string, String(value))
      }
      
      return newParams
    }, { replace: true })
  }, [setSearchParams])

  // 批量设置参数
  const setParams = useCallback((updates: Partial<{ [K in keyof T]: ParamValue }>) => {
    setSearchParams(prev => {
      const newParams = new URLSearchParams(prev)
      
      for (const [key, value] of Object.entries(updates)) {
        if (value === null || value === undefined || value === '' ||
            (Array.isArray(value) && value.length === 0)) {
          newParams.delete(key)
        } else if (Array.isArray(value)) {
          newParams.set(key, value.join(','))
        } else {
          newParams.set(key, String(value))
        }
      }
      
      return newParams
    }, { replace: true })
  }, [setSearchParams])

  // 清除所有参数
  const clearParams = useCallback(() => {
    setSearchParams({}, { replace: true })
  }, [setSearchParams])

  return { params, setParam, setParams, clearParams }
}

/**
 * 简化版：用于 LibraryPage 的筛选参数
 */
export function useLibraryUrlParams() {
  return useUrlParams({
    page: { type: 'number', default: 1 },
    tags: { type: 'numberArray', default: [] },
    formats: { type: 'array', default: [] },
    sort: { type: 'string', default: 'added_at' },
    view: { type: 'string', default: 'grid' },
  })
}

/**
 * 简化版：用于 AdminPage 的 tab 参数
 */
export function useAdminTabParams() {
  return useUrlParams({
    tab: { type: 'string', default: 'libraries' },
  })
}

/**
 * 简化版：用于 SearchPage 的参数
 */
export function useSearchUrlParams() {
  return useUrlParams({
    q: { type: 'string', default: '' },
    page: { type: 'number', default: 1 },
    author: { type: 'number', default: null },
    formats: { type: 'array', default: [] },
    library: { type: 'number', default: null },
  })
}

import { useState, useEffect } from 'react'
import {
  Box, Typography, Button, IconButton, Chip, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Alert, CircularProgress,
  Card, CardContent, Grid, LinearProgress, List, ListItem, ListItemText,
  ListItemSecondaryAction, Switch, Divider, Collapse, Stack, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  FormControl, InputLabel, Select, MenuItem
} from '@mui/material'
import {
  Add, Edit, Delete, Refresh, FolderOpen, ExpandMore, ExpandLess,
  PlayArrow, Stop, CheckCircle, Error as ErrorIcon, Schedule,
  Folder, DeleteOutline, AddCircle, LocalOffer, Sync, Warning,
  Psychology, Code, Preview
} from '@mui/icons-material'
import api from '../../services/api'

interface Library {
  id: number
  name: string
  path: string
  last_scan: string | null
  is_public?: boolean
  book_count?: number
}

interface LibraryPath {
  id: number
  path: string
  enabled: boolean
  created_at: string
}

interface ScanTask {
  id: number
  library_id: number
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  total_files: number
  processed_files: number
  added_books: number
  skipped_books: number
  error_count: number
  error_message: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

interface TagInfo {
  id: number
  name: string
  type: string
  description?: string
}

interface ExtractChange {
  book_id: number
  filename: string
  pattern_name?: string
  current: {
    title: string
    author: string | null
    description?: string
  }
  extracted: {
    title: string | null
    author: string | null
    description?: string
    tags?: string[]
  }
}

interface ExtractResult {
  success: boolean
  error?: string
  library_id: number
  library_name: string
  total_books: number
  sampled_count?: number
  matched_count?: number
  patterns_used?: number
  changes: ExtractChange[]
}

export default function LibrariesTab() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [libraries, setLibraries] = useState<Library[]>([])
  
  // 展开状态
  const [expandedLibrary, setExpandedLibrary] = useState<number | null>(null)
  
  // 路径管理
  const [paths, setPaths] = useState<Record<number, LibraryPath[]>>({})
  const [pathDialogOpen, setPathDialogOpen] = useState(false)
  const [selectedLibraryForPath, setSelectedLibraryForPath] = useState<number | null>(null)
  const [newPath, setNewPath] = useState('')
  
  // 扫描任务
  const [activeTasks, setActiveTasks] = useState<Record<number, ScanTask>>({})
  const [taskHistories, setTaskHistories] = useState<Record<number, ScanTask[]>>({})
  
  // 书库标签
  const [libraryTags, setLibraryTags] = useState<Record<number, TagInfo[]>>({})
  const [allTags, setAllTags] = useState<TagInfo[]>([])
  const [tagDialogOpen, setTagDialogOpen] = useState(false)
  const [selectedLibraryForTag, setSelectedLibraryForTag] = useState<number | null>(null)
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([])
  const [applyingTags, setApplyingTags] = useState<number | null>(null)
  
  // 内容分级
  const [contentRatings, setContentRatings] = useState<Record<number, string>>({})
  const [applyingContentRating, setApplyingContentRating] = useState<number | null>(null)
  
  // 对话框状态
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogType, setDialogType] = useState<'create' | 'edit'>('create')
  const [selectedLibrary, setSelectedLibrary] = useState<Library | null>(null)
  
  // AI/规则提取
  const [extractDialogOpen, setExtractDialogOpen] = useState(false)
  const [extractType, setExtractType] = useState<'ai' | 'pattern'>('ai')
  const [extractLoading, setExtractLoading] = useState(false)
  const [extractResult, setExtractResult] = useState<ExtractResult | null>(null)
  const [selectedChanges, setSelectedChanges] = useState<Set<number>>(new Set())
  const [applyingExtract, setApplyingExtract] = useState(false)
  
  // 表单数据
  const [formData, setFormData] = useState({
    name: '',
    paths: [''] // 支持多路径创建
  })

  useEffect(() => {
    loadLibraries()
    loadAllTags()
  }, [])

  const loadAllTags = async () => {
    try {
      const response = await api.get<TagInfo[]>('/api/tags')
      setAllTags(response.data)
    } catch (err) {
      console.error('加载标签列表失败:', err)
    }
  }

  const loadLibraryTags = async (libraryId: number) => {
    try {
      const response = await api.get<{ tags: TagInfo[] }>(`/api/admin/libraries/${libraryId}/tags`)
      setLibraryTags(prev => ({ ...prev, [libraryId]: response.data.tags }))
    } catch (err) {
      console.error('加载书库标签失败:', err)
    }
  }

  const loadContentRating = async (libraryId: number) => {
    try {
      const response = await api.get<{ content_rating: string }>(`/api/admin/libraries/${libraryId}/content-rating`)
      setContentRatings(prev => ({ ...prev, [libraryId]: response.data.content_rating }))
    } catch (err) {
      console.error('加载内容分级失败:', err)
    }
  }

  const handleContentRatingChange = async (libraryId: number, rating: string) => {
    try {
      await api.put(`/api/admin/libraries/${libraryId}/content-rating`, {
        content_rating: rating
      })
      setContentRatings(prev => ({ ...prev, [libraryId]: rating }))
    } catch (err: any) {
      console.error('更新内容分级失败:', err)
      setError(err.response?.data?.detail || '更新内容分级失败')
    }
  }

  // AI提取
  const handleAIExtract = async (libraryId: number) => {
    setExtractType('ai')
    setExtractLoading(true)
    setExtractResult(null)
    setSelectedChanges(new Set())
    setExtractDialogOpen(true)
    
    try {
      const response = await api.post(`/api/admin/ai/libraries/${libraryId}/ai-extract`)
      if (response.data.success) {
        setExtractResult(response.data)
        // 默认全选
        setSelectedChanges(new Set(response.data.changes.map((c: ExtractChange) => c.book_id)))
      } else {
        setError(response.data.error || 'AI提取失败')
        setExtractDialogOpen(false)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'AI提取失败')
      setExtractDialogOpen(false)
    } finally {
      setExtractLoading(false)
    }
  }
  
  // 规则提取
  const handlePatternExtract = async (libraryId: number) => {
    setExtractType('pattern')
    setExtractLoading(true)
    setExtractResult(null)
    setSelectedChanges(new Set())
    setExtractDialogOpen(true)
    
    try {
      const response = await api.post(`/api/admin/ai/libraries/${libraryId}/pattern-extract`)
      if (response.data.success) {
        setExtractResult(response.data)
        // 默认全选
        setSelectedChanges(new Set(response.data.changes.map((c: ExtractChange) => c.book_id)))
      } else {
        setError(response.data.error || '规则提取失败')
        setExtractDialogOpen(false)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '规则提取失败')
      setExtractDialogOpen(false)
    } finally {
      setExtractLoading(false)
    }
  }
  
  // 应用提取结果
  const handleApplyExtract = async () => {
    if (!extractResult) return
    
    const changesToApply = extractResult.changes.filter(c => selectedChanges.has(c.book_id))
    if (changesToApply.length === 0) {
      alert('请至少选择一项变更')
      return
    }
    
    setApplyingExtract(true)
    try {
      const endpoint = extractType === 'ai' 
        ? `/api/admin/ai/libraries/${extractResult.library_id}/ai-extract/apply`
        : `/api/admin/ai/libraries/${extractResult.library_id}/pattern-extract/apply`
      
      const response = await api.post(endpoint, { changes: changesToApply })
      
      alert(`应用成功！\n已更新 ${response.data.applied_count} 本书${response.data.tags_added ? `\n添加标签 ${response.data.tags_added} 个` : ''}`)
      setExtractDialogOpen(false)
      loadLibraries()
    } catch (err: any) {
      setError(err.response?.data?.detail || '应用失败')
    } finally {
      setApplyingExtract(false)
    }
  }
  
  const toggleChangeSelection = (bookId: number) => {
    setSelectedChanges(prev => {
      const newSet = new Set(prev)
      if (newSet.has(bookId)) {
        newSet.delete(bookId)
      } else {
        newSet.add(bookId)
      }
      return newSet
    })
  }
  
  const toggleAllChanges = () => {
    if (!extractResult) return
    if (selectedChanges.size === extractResult.changes.length) {
      setSelectedChanges(new Set())
    } else {
      setSelectedChanges(new Set(extractResult.changes.map(c => c.book_id)))
    }
  }

  const handleApplyContentRating = async (libraryId: number) => {
    if (!confirm('确定要将书库的内容分级应用到该书库所有书籍吗？这将覆盖现有书籍的分级设置。')) return
    
    try {
      setApplyingContentRating(libraryId)
      const response = await api.post(`/api/admin/libraries/${libraryId}/apply-content-rating`)
      alert(`成功应用内容分级！已更新 ${response.data.updated_count} 本书的分级为 "${getContentRatingLabel(response.data.content_rating)}"。`)
    } catch (err: any) {
      console.error('应用内容分级失败:', err)
      setError(err.response?.data?.detail || '应用内容分级失败')
    } finally {
      setApplyingContentRating(null)
    }
  }

  const getContentRatingLabel = (rating: string) => {
    const labels: Record<string, string> = {
      'general': '全年龄',
      'teen': '青少年 (13+)',
      'adult': '成人 (18+)',
      'r18': 'R18'
    }
    return labels[rating] || rating
  }

  const getContentRatingColor = (rating: string) => {
    const colors: Record<string, 'success' | 'info' | 'warning' | 'error'> = {
      'general': 'success',
      'teen': 'info',
      'adult': 'warning',
      'r18': 'error'
    }
    return colors[rating] || 'default'
  }

  // 轮询活动任务
  useEffect(() => {
    const hasActiveTasks = Object.values(activeTasks).some(
      task => task.status === 'running' || task.status === 'pending'
    )
    
    if (hasActiveTasks) {
      const interval = setInterval(() => {
        updateActiveTasks()
      }, 2000) // 每2秒更新一次
      
      return () => clearInterval(interval)
    }
  }, [activeTasks])

  const loadLibraries = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get<Library[]>('/api/libraries')
      
      // 加载每个书库的详细信息
      const detailedLibraries = await Promise.all(
        response.data.map(async (lib) => {
          try {
            const detailRes = await api.get(`/api/libraries/${lib.id}`)
            return { ...lib, book_count: detailRes.data.book_count }
          } catch {
            return lib
          }
        })
      )
      
      setLibraries(detailedLibraries)
    } catch (err) {
      console.error('加载书库列表失败:', err)
      setError('加载失败')
    } finally {
      setLoading(false)
    }
  }

  const loadLibraryPaths = async (libraryId: number) => {
    try {
      const response = await api.get<LibraryPath[]>(`/api/admin/libraries/${libraryId}/paths`)
      setPaths(prev => ({ ...prev, [libraryId]: response.data }))
    } catch (err) {
      console.error('加载路径失败:', err)
    }
  }

  const loadTaskHistory = async (libraryId: number) => {
    try {
      const response = await api.get<ScanTask[]>(`/api/admin/libraries/${libraryId}/scan-tasks?limit=5`)
      setTaskHistories(prev => ({ ...prev, [libraryId]: response.data }))
      
      // 检查是否有活动任务
      const activeTask = response.data.find(t => t.status === 'running' || t.status === 'pending')
      if (activeTask) {
        setActiveTasks(prev => ({ ...prev, [libraryId]: activeTask }))
      }
    } catch (err) {
      console.error('加载任务历史失败:', err)
    }
  }

  const updateActiveTasks = async () => {
    const taskIds = Object.values(activeTasks).map(t => t.id)
    
    for (const taskId of taskIds) {
      try {
        const response = await api.get<ScanTask>(`/api/admin/scan-tasks/${taskId}`)
        const task = response.data
        
        setActiveTasks(prev => {
          const libraryId = task.library_id
          if (task.status === 'completed' || task.status === 'failed' || task.status === 'cancelled') {
            // 任务完成，移除活动任务并刷新
            const newTasks = { ...prev }
            delete newTasks[libraryId]
            loadLibraries()
            loadTaskHistory(libraryId)
            return newTasks
          }
          return { ...prev, [libraryId]: task }
        })
      } catch (err) {
        console.error('更新任务状态失败:', err)
      }
    }
  }

  const handleExpandLibrary = async (libraryId: number) => {
    if (expandedLibrary === libraryId) {
      setExpandedLibrary(null)
    } else {
      setExpandedLibrary(libraryId)
      if (!paths[libraryId]) {
        await loadLibraryPaths(libraryId)
      }
      if (!taskHistories[libraryId]) {
        await loadTaskHistory(libraryId)
      }
      if (!libraryTags[libraryId]) {
        await loadLibraryTags(libraryId)
      }
      if (contentRatings[libraryId] === undefined) {
        await loadContentRating(libraryId)
      }
    }
  }

  const handleCreate = () => {
    setDialogType('create')
    setSelectedLibrary(null)
    setFormData({ name: '', paths: [''] })
    setDialogOpen(true)
  }

  const handleEdit = (library: Library) => {
    setDialogType('edit')
    setSelectedLibrary(library)
    setFormData({ name: library.name, paths: [] })
    setDialogOpen(true)
  }

  const handleSubmit = async () => {
    try {
      if (dialogType === 'create') {
        // 创建书库时只使用第一个路径
        const createData = {
          name: formData.name,
          path: formData.paths[0]
        }
        const response = await api.post<Library>('/api/libraries', createData)
        
        // 如果有多个路径，逐个添加
        if (formData.paths.length > 1 && response.data.id) {
          for (let i = 1; i < formData.paths.length; i++) {
            if (formData.paths[i].trim()) {
              await api.post(`/api/admin/libraries/${response.data.id}/paths`, {
                path: formData.paths[i]
              })
            }
          }
        }
      } else if (dialogType === 'edit' && selectedLibrary) {
        // 编辑时只更新名称，路径在扫描路径区域管理
        await api.put(`/api/libraries/${selectedLibrary.id}`, {
          name: formData.name
        })
      }
      setDialogOpen(false)
      loadLibraries()
    } catch (err) {
      console.error('操作失败:', err)
      setError('操作失败')
    }
  }

  const handleDelete = async (library: Library) => {
    if (!confirm(`确定要删除书库 "${library.name}" 吗？这将删除所有关联的书籍记录。`)) return
    try {
      await api.delete(`/api/libraries/${library.id}`)
      loadLibraries()
    } catch (err) {
      console.error('删除失败:', err)
      setError('删除失败')
    }
  }

  const handleAddPath = (libraryId: number) => {
    setSelectedLibraryForPath(libraryId)
    setNewPath('')
    setPathDialogOpen(true)
  }

  const handleSubmitPath = async () => {
    if (!selectedLibraryForPath || !newPath.trim()) return
    
    try {
      await api.post(`/api/admin/libraries/${selectedLibraryForPath}/paths`, {
        path: newPath
      })
      setPathDialogOpen(false)
      await loadLibraryPaths(selectedLibraryForPath)
    } catch (err) {
      console.error('添加路径失败:', err)
      setError('添加路径失败')
    }
  }

  const handleDeletePath = async (libraryId: number, pathId: number) => {
    if (!confirm('确定要删除此路径吗？')) return
    
    try {
      await api.delete(`/api/admin/libraries/${libraryId}/paths/${pathId}`)
      await loadLibraryPaths(libraryId)
    } catch (err: any) {
      console.error('删除路径失败:', err)
      setError(err.response?.data?.detail || '删除路径失败')
    }
  }

  const handleTogglePath = async (libraryId: number, pathId: number, enabled: boolean) => {
    try {
      await api.put(`/api/admin/libraries/${libraryId}/paths/${pathId}/toggle?enabled=${enabled}`)
      await loadLibraryPaths(libraryId)
    } catch (err: any) {
      console.error('切换路径状态失败:', err)
      setError(err.response?.data?.detail || '操作失败')
    }
  }

  const handleStartScan = async (libraryId: number) => {
    try {
      const response = await api.post(`/api/admin/libraries/${libraryId}/scan`)
      const taskId = response.data.task_id
      
      // 开始轮询任务状态
      const taskResponse = await api.get<ScanTask>(`/api/admin/scan-tasks/${taskId}`)
      setActiveTasks(prev => ({ ...prev, [libraryId]: taskResponse.data }))
      
      // 展开库以显示进度
      setExpandedLibrary(libraryId)
      await loadTaskHistory(libraryId)
    } catch (err: any) {
      console.error('启动扫描失败:', err)
      setError(err.response?.data?.detail || '启动扫描失败')
    }
  }

  const handleOpenTagDialog = (libraryId: number) => {
    const currentTags = libraryTags[libraryId] || []
    setSelectedLibraryForTag(libraryId)
    setSelectedTagIds(currentTags.map(t => t.id))
    setTagDialogOpen(true)
  }

  const handleSaveLibraryTags = async () => {
    if (!selectedLibraryForTag) return
    
    try {
      await api.put(`/api/admin/libraries/${selectedLibraryForTag}/tags`, {
        tag_ids: selectedTagIds
      })
      setTagDialogOpen(false)
      await loadLibraryTags(selectedLibraryForTag)
    } catch (err) {
      console.error('保存书库标签失败:', err)
      setError('保存标签失败')
    }
  }

  const handleApplyTagsToBooks = async (libraryId: number) => {
    if (!confirm('确定要将书库默认标签应用到该书库所有书籍吗？已有相同标签的书籍将跳过。')) return
    
    try {
      setApplyingTags(libraryId)
      const response = await api.post(`/api/admin/libraries/${libraryId}/apply-tags`)
      alert(`成功应用标签！共处理 ${response.data.books_count} 本书，添加 ${response.data.applied_count} 个标签关联。`)
    } catch (err: any) {
      console.error('应用标签失败:', err)
      setError(err.response?.data?.detail || '应用标签失败')
    } finally {
      setApplyingTags(null)
    }
  }

  const handleCancelScan = async (taskId: number, libraryId: number) => {
    if (!confirm('确定要取消正在运行的扫描任务吗？')) return
    
    try {
      await api.post(`/api/admin/scan-tasks/${taskId}/cancel`)
      await loadTaskHistory(libraryId)
      setActiveTasks(prev => {
        const newTasks = { ...prev }
        delete newTasks[libraryId]
        return newTasks
      })
    } catch (err) {
      console.error('取消任务失败:', err)
      setError('取消任务失败')
    }
  }

  const getStatusChip = (status: ScanTask['status']) => {
    const statusConfig: Record<ScanTask['status'], { label: string; color: any; icon: any }> = {
      pending: { label: '等待中', color: 'default', icon: <Schedule fontSize="small" /> },
      running: { label: '扫描中', color: 'primary', icon: <CircularProgress size={16} /> },
      completed: { label: '完成', color: 'success', icon: <CheckCircle fontSize="small" /> },
      failed: { label: '失败', color: 'error', icon: <ErrorIcon fontSize="small" /> },
      cancelled: { label: '已取消', color: 'warning', icon: <Stop fontSize="small" /> }
    }
    
    const config = statusConfig[status]
    return <Chip label={config.label} color={config.color} size="small" icon={config.icon} />
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '从未'
    return new Date(dateStr).toLocaleString('zh-CN')
  }

  const addPathField = () => {
    setFormData(prev => ({ ...prev, paths: [...prev.paths, ''] }))
  }

  const removePathField = (index: number) => {
    setFormData(prev => ({
      ...prev,
      paths: prev.paths.filter((_, i) => i !== index)
    }))
  }

  const updatePathField = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      paths: prev.paths.map((p, i) => i === index ? value : p)
    }))
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">书库管理</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
          添加书库
        </Button>
      </Box>

      <Grid container spacing={2}>
        {libraries.map((library) => {
          const activeTask = activeTasks[library.id]
          const isExpanded = expandedLibrary === library.id
          const libraryPaths = paths[library.id] || []
          const history = taskHistories[library.id] || []
          
          return (
            <Grid item xs={12} key={library.id}>
              <Card>
                <CardContent>
                  {/* 库头部 */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6">{library.name}</Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                        <FolderOpen fontSize="small" />
                        {library.path}
                      </Typography>
                      
                      <Box sx={{ display: 'flex', gap: 1, mt: 1.5, flexWrap: 'wrap' }}>
                        <Chip label={`${library.book_count || 0} 本书`} size="small" color="primary" variant="outlined" />
                        <Chip label={`上次扫描: ${formatDate(library.last_scan)}`} size="small" variant="outlined" />
                        {activeTask && <Chip label="扫描中" size="small" color="primary" />}
                      </Box>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleStartScan(library.id)}
                        disabled={!!activeTask}
                        title="启动扫描"
                        color="primary"
                      >
                        <PlayArrow />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleAIExtract(library.id)}
                        title="AI提取元数据"
                        color="secondary"
                      >
                        <Psychology />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handlePatternExtract(library.id)}
                        title="规则提取元数据"
                        color="info"
                      >
                        <Code />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleEdit(library)} title="编辑">
                        <Edit />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleDelete(library)} color="error" title="删除">
                        <Delete />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleExpandLibrary(library.id)}>
                        {isExpanded ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </Box>
                  </Box>

                  {/* 活动扫描任务进度 */}
                  {activeTask && (
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">
                          扫描进度: {activeTask.processed_files}/{activeTask.total_files} 文件
                        </Typography>
                        <Typography variant="body2">{activeTask.progress}%</Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={activeTask.progress} />
                      <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          已添加: {activeTask.added_books}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          已跳过: {activeTask.skipped_books}
                        </Typography>
                        {activeTask.error_count > 0 && (
                          <Typography variant="caption" color="error">
                            错误: {activeTask.error_count}
                          </Typography>
                        )}
                        <Box sx={{ flex: 1 }} />
                        <Button
                          size="small"
                          color="error"
                          onClick={() => handleCancelScan(activeTask.id, library.id)}
                        >
                          取消
                        </Button>
                      </Box>
                    </Box>
                  )}

                  {/* 展开详情 */}
                  <Collapse in={isExpanded}>
                    <Divider sx={{ my: 2 }} />
                    
                    {/* 路径管理 */}
                    <Box sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>扫描路径</Typography>
                        <Button
                          size="small"
                          startIcon={<AddCircle />}
                          onClick={() => handleAddPath(library.id)}
                        >
                          添加路径
                        </Button>
                      </Box>
                      
                      {libraryPaths.length === 0 ? (
                        <Typography variant="body2" color="text.secondary">暂无路径</Typography>
                      ) : (
                        <List dense>
                          {libraryPaths.map((path) => (
                            <ListItem key={path.id} sx={{ bgcolor: 'action.hover', borderRadius: 1, mb: 0.5 }}>
                              <Folder fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                              <ListItemText
                                primary={path.path}
                                secondary={`添加于 ${formatDate(path.created_at)}`}
                              />
                              <ListItemSecondaryAction>
                                <Switch
                                  edge="end"
                                  checked={path.enabled}
                                  onChange={(e) => handleTogglePath(library.id, path.id, e.target.checked)}
                                  size="small"
                                />
                                <IconButton
                                  edge="end"
                                  size="small"
                                  onClick={() => handleDeletePath(library.id, path.id)}
                                  color="error"
                                  sx={{ ml: 1 }}
                                >
                                  <DeleteOutline fontSize="small" />
                                </IconButton>
                              </ListItemSecondaryAction>
                            </ListItem>
                          ))}
                        </List>
                      )}
                    </Box>

                    {/* 书库默认标签 */}
                    <Box sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <LocalOffer fontSize="small" />
                          默认标签
                        </Typography>
                        <Stack direction="row" spacing={1}>
                          <Button
                            size="small"
                            startIcon={<Sync />}
                            onClick={() => handleApplyTagsToBooks(library.id)}
                            disabled={applyingTags === library.id || (libraryTags[library.id]?.length || 0) === 0}
                          >
                            {applyingTags === library.id ? '应用中...' : '应用到所有书籍'}
                          </Button>
                          <Button
                            size="small"
                            startIcon={<Edit />}
                            onClick={() => handleOpenTagDialog(library.id)}
                          >
                            管理标签
                          </Button>
                        </Stack>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        新扫描入库的书籍将自动添加这些标签
                      </Typography>
                      
                      {(libraryTags[library.id]?.length || 0) === 0 ? (
                        <Typography variant="body2" color="text.secondary">暂无默认标签</Typography>
                      ) : (
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {libraryTags[library.id]?.map((tag) => (
                            <Chip
                              key={tag.id}
                              label={tag.name}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      )}
                    </Box>

                    {/* 内容分级 */}
                    <Box sx={{ mb: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Warning fontSize="small" />
                          内容分级
                        </Typography>
                        <Button
                          size="small"
                          startIcon={<Sync />}
                          onClick={() => handleApplyContentRating(library.id)}
                          disabled={applyingContentRating === library.id || !contentRatings[library.id]}
                        >
                          {applyingContentRating === library.id ? '应用中...' : '应用到所有书籍'}
                        </Button>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                        新扫描入库的书籍将自动设置此分级，也可手动应用到现有书籍
                      </Typography>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <FormControl size="small" sx={{ minWidth: 180 }}>
                          <InputLabel>内容分级</InputLabel>
                          <Select
                            value={contentRatings[library.id] || ''}
                            label="内容分级"
                            onChange={(e) => handleContentRatingChange(library.id, e.target.value)}
                          >
                            <MenuItem value="">
                              <em>未设置</em>
                            </MenuItem>
                            <MenuItem value="general">全年龄</MenuItem>
                            <MenuItem value="teen">青少年 (13+)</MenuItem>
                            <MenuItem value="adult">成人 (18+)</MenuItem>
                            <MenuItem value="r18">R18</MenuItem>
                          </Select>
                        </FormControl>
                        
                        {contentRatings[library.id] && (
                          <Chip
                            label={getContentRatingLabel(contentRatings[library.id])}
                            size="small"
                            color={getContentRatingColor(contentRatings[library.id]) as any}
                          />
                        )}
                      </Box>
                    </Box>

                    {/* 扫描历史 */}
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>扫描历史</Typography>
                      {history.length === 0 ? (
                        <Typography variant="body2" color="text.secondary">暂无扫描记录</Typography>
                      ) : (
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>状态</TableCell>
                                <TableCell>开始时间</TableCell>
                                <TableCell align="right">文件数</TableCell>
                                <TableCell align="right">添加</TableCell>
                                <TableCell align="right">跳过</TableCell>
                                <TableCell align="right">错误</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {history.map((task) => (
                                <TableRow key={task.id}>
                                  <TableCell>{getStatusChip(task.status)}</TableCell>
                                  <TableCell>{formatDate(task.started_at)}</TableCell>
                                  <TableCell align="right">{task.total_files}</TableCell>
                                  <TableCell align="right">{task.added_books}</TableCell>
                                  <TableCell align="right">{task.skipped_books}</TableCell>
                                  <TableCell align="right">
                                    {task.error_count > 0 ? (
                                      <Typography variant="body2" color="error">{task.error_count}</Typography>
                                    ) : (
                                      task.error_count
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      )}
                    </Box>
                  </Collapse>
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      {libraries.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography color="text.secondary">暂无书库，请点击添加书库</Typography>
        </Box>
      )}

      {/* 创建/编辑书库对话框 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogType === 'create' ? '添加书库' : '编辑书库'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="书库名称"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              fullWidth
              required
              autoFocus
            />
            
            {dialogType === 'create' && (
              <>
                {formData.paths.map((path, index) => (
                  <Box key={index} sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                    <TextField
                      label={`扫描路径 ${index + 1}`}
                      value={path}
                      onChange={(e) => updatePathField(index, e.target.value)}
                      fullWidth
                      required
                      helperText={index === 0 ? '书籍文件所在的目录路径' : ''}
                    />
                    {formData.paths.length > 1 && (
                      <IconButton onClick={() => removePathField(index)} color="error" sx={{ mt: 1 }}>
                        <Delete />
                      </IconButton>
                    )}
                  </Box>
                ))}
                
                <Button startIcon={<Add />} onClick={addPathField} variant="outlined" size="small">
                  添加更多路径
                </Button>
                
                <Alert severity="info" sx={{ mt: 1 }}>
                  创建后可在"扫描路径"区域继续添加或管理路径
                </Alert>
              </>
            )}
            
            {dialogType === 'edit' && (
              <Alert severity="info">
                路径管理请展开书库，在"扫描路径"区域进行操作
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>取消</Button>
          <Button variant="contained" onClick={handleSubmit}>确定</Button>
        </DialogActions>
      </Dialog>

      {/* 书库标签管理对话框 */}
      <Dialog open={tagDialogOpen} onClose={() => setTagDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>管理书库默认标签</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            选择的标签将自动应用到新扫描入库的书籍。
          </Typography>
          
          {allTags.length === 0 ? (
            <Alert severity="info">暂无可用标签，请先在"标签管理"中创建标签。</Alert>
          ) : (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {allTags.map((tag) => (
                <Chip
                  key={tag.id}
                  label={tag.name}
                  onClick={() => {
                    if (selectedTagIds.includes(tag.id)) {
                      setSelectedTagIds(prev => prev.filter(id => id !== tag.id))
                    } else {
                      setSelectedTagIds(prev => [...prev, tag.id])
                    }
                  }}
                  color={selectedTagIds.includes(tag.id) ? 'primary' : 'default'}
                  variant={selectedTagIds.includes(tag.id) ? 'filled' : 'outlined'}
                />
              ))}
            </Box>
          )}
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="caption" color="text.secondary">
              已选择 {selectedTagIds.length} 个标签
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTagDialogOpen(false)}>取消</Button>
          <Button variant="contained" onClick={handleSaveLibraryTags}>保存</Button>
        </DialogActions>
      </Dialog>

      {/* 添加路径对话框 */}
      <Dialog open={pathDialogOpen} onClose={() => setPathDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>添加扫描路径</DialogTitle>
        <DialogContent>
          <TextField
            label="路径"
            value={newPath}
            onChange={(e) => setNewPath(e.target.value)}
            fullWidth
            required
            helperText="输入书籍文件所在的目录路径"
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPathDialogOpen(false)}>取消</Button>
          <Button variant="contained" onClick={handleSubmitPath}>添加</Button>
        </DialogActions>
      </Dialog>

      {/* AI/规则提取预览对话框 */}
      <Dialog 
        open={extractDialogOpen} 
        onClose={() => !extractLoading && !applyingExtract && setExtractDialogOpen(false)} 
        maxWidth="lg" 
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {extractType === 'ai' ? <Psychology /> : <Code />}
          {extractType === 'ai' ? 'AI提取预览' : '规则提取预览'}
          {extractResult && (
            <Chip 
              label={`${extractResult.library_name}`} 
              size="small" 
              color="primary" 
              sx={{ ml: 1 }}
            />
          )}
        </DialogTitle>
        <DialogContent>
          {extractLoading ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
              <CircularProgress size={48} />
              <Typography sx={{ mt: 2 }}>
                {extractType === 'ai' ? '正在使用AI分析文件名...' : '正在使用规则匹配文件名...'}
              </Typography>
            </Box>
          ) : extractResult ? (
            <>
              <Box sx={{ mb: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip label={`总书籍: ${extractResult.total_books}`} variant="outlined" />
                {extractType === 'ai' && extractResult.sampled_count && (
                  <Chip label={`采样数: ${extractResult.sampled_count}`} variant="outlined" color="info" />
                )}
                {extractType === 'pattern' && extractResult.matched_count !== undefined && (
                  <Chip label={`匹配: ${extractResult.matched_count}`} variant="outlined" color="success" />
                )}
                <Chip label={`待变更: ${extractResult.changes.length}`} variant="outlined" color="warning" />
                <Chip label={`已选择: ${selectedChanges.size}`} variant="outlined" color="primary" />
              </Box>
              
              {extractResult.changes.length === 0 ? (
                <Alert severity="info">没有需要变更的内容</Alert>
              ) : (
                <>
                  <Box sx={{ mb: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Button size="small" onClick={toggleAllChanges}>
                      {selectedChanges.size === extractResult.changes.length ? '取消全选' : '全选'}
                    </Button>
                  </Box>
                  
                  <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
                    <Table size="small" stickyHeader>
                      <TableHead>
                        <TableRow>
                          <TableCell padding="checkbox">选择</TableCell>
                          <TableCell>文件名</TableCell>
                          {extractType === 'pattern' && <TableCell>匹配规则</TableCell>}
                          <TableCell>当前书名</TableCell>
                          <TableCell>→</TableCell>
                          <TableCell>提取书名</TableCell>
                          <TableCell>当前作者</TableCell>
                          <TableCell>→</TableCell>
                          <TableCell>提取作者</TableCell>
                          {extractType === 'ai' && <TableCell>标签</TableCell>}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {extractResult.changes.map((change) => (
                          <TableRow 
                            key={change.book_id}
                            sx={{ 
                              bgcolor: selectedChanges.has(change.book_id) ? 'action.selected' : 'inherit',
                              cursor: 'pointer'
                            }}
                            onClick={() => toggleChangeSelection(change.book_id)}
                          >
                            <TableCell padding="checkbox">
                              <input
                                type="checkbox"
                                checked={selectedChanges.has(change.book_id)}
                                onChange={() => toggleChangeSelection(change.book_id)}
                                onClick={(e) => e.stopPropagation()}
                              />
                            </TableCell>
                            <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {change.filename}
                            </TableCell>
                            {extractType === 'pattern' && (
                              <TableCell>
                                <Chip label={change.pattern_name} size="small" />
                              </TableCell>
                            )}
                            <TableCell sx={{ color: 'text.secondary' }}>
                              {change.current.title}
                            </TableCell>
                            <TableCell>→</TableCell>
                            <TableCell sx={{ 
                              fontWeight: change.extracted.title !== change.current.title ? 'bold' : 'normal',
                              color: change.extracted.title !== change.current.title ? 'success.main' : 'inherit'
                            }}>
                              {change.extracted.title || '-'}
                            </TableCell>
                            <TableCell sx={{ color: 'text.secondary' }}>
                              {change.current.author || '-'}
                            </TableCell>
                            <TableCell>→</TableCell>
                            <TableCell sx={{ 
                              fontWeight: change.extracted.author !== change.current.author ? 'bold' : 'normal',
                              color: change.extracted.author !== change.current.author ? 'success.main' : 'inherit'
                            }}>
                              {change.extracted.author || '-'}
                            </TableCell>
                            {extractType === 'ai' && (
                              <TableCell>
                                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                  {change.extracted.tags?.slice(0, 3).map((tag, i) => (
                                    <Chip key={i} label={tag} size="small" variant="outlined" />
                                  ))}
                                  {(change.extracted.tags?.length || 0) > 3 && (
                                    <Chip label={`+${change.extracted.tags!.length - 3}`} size="small" />
                                  )}
                                </Box>
                              </TableCell>
                            )}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  
                  {extractType === 'ai' && (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      AI提取还会更新简介并添加标签。只有系统中已存在的标签才会被添加。
                    </Alert>
                  )}
                </>
              )}
            </>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setExtractDialogOpen(false)} 
            disabled={extractLoading || applyingExtract}
          >
            取消
          </Button>
          <Button 
            variant="contained" 
            onClick={handleApplyExtract}
            disabled={extractLoading || applyingExtract || !extractResult || selectedChanges.size === 0}
            startIcon={applyingExtract ? <CircularProgress size={20} /> : <CheckCircle />}
          >
            {applyingExtract ? '应用中...' : `应用选中的 ${selectedChanges.size} 项变更`}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

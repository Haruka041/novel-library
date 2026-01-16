import { useState, useEffect } from 'react'
import {
  Box, Typography, Button, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Alert, CircularProgress,
  Card, CardContent, Grid, LinearProgress
} from '@mui/material'
import { Add, Edit, Delete, Refresh, Public, Lock, FolderOpen } from '@mui/icons-material'
import api from '../../services/api'

interface Library {
  id: number
  name: string
  path: string
  last_scan: string | null
  is_public?: boolean
  book_count?: number
}

interface LibraryStats {
  library_id: number
  library_name: string
  total_books: number
  total_authors: number
  total_file_size: number
  format_distribution: Record<string, number>
  last_scan: string | null
}

export default function LibrariesTab() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [libraries, setLibraries] = useState<Library[]>([])
  const [scanningId, setScanningId] = useState<number | null>(null)
  
  // 对话框状态
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogType, setDialogType] = useState<'create' | 'edit'>('create')
  const [selectedLibrary, setSelectedLibrary] = useState<Library | null>(null)
  
  // 表单数据
  const [formData, setFormData] = useState({
    name: '',
    path: ''
  })

  useEffect(() => {
    loadLibraries()
  }, [])

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

  const handleCreate = () => {
    setDialogType('create')
    setSelectedLibrary(null)
    setFormData({ name: '', path: '' })
    setDialogOpen(true)
  }

  const handleEdit = (library: Library) => {
    setDialogType('edit')
    setSelectedLibrary(library)
    setFormData({ name: library.name, path: library.path })
    setDialogOpen(true)
  }

  const handleSubmit = async () => {
    try {
      if (dialogType === 'create') {
        await api.post('/api/libraries', formData)
      } else if (dialogType === 'edit' && selectedLibrary) {
        await api.put(`/api/libraries/${selectedLibrary.id}`, formData)
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

  const handleScan = async (library: Library) => {
    try {
      setScanningId(library.id)
      await api.post(`/api/libraries/${library.id}/scan`)
      loadLibraries()
    } catch (err) {
      console.error('扫描失败:', err)
      setError('扫描失败')
    } finally {
      setScanningId(null)
    }
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '从未'
    return new Date(dateStr).toLocaleString('zh-CN')
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
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
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">书库列表</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
          添加书库
        </Button>
      </Box>

      <Grid container spacing={2}>
        {libraries.map((library) => (
          <Grid item xs={12} md={6} key={library.id}>
            <Card>
              {scanningId === library.id && <LinearProgress />}
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6">{library.name}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <FolderOpen fontSize="small" />
                      {library.path}
                    </Typography>
                  </Box>
                  <Box>
                    <IconButton size="small" onClick={() => handleScan(library)} disabled={scanningId !== null} title="扫描">
                      <Refresh fontSize="small" />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleEdit(library)} title="编辑">
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleDelete(library)} color="error" title="删除">
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Chip
                    label={`${library.book_count || 0} 本书`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                  <Chip
                    label={`上次扫描: ${formatDate(library.last_scan)}`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {libraries.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography color="text.secondary">暂无书库，请点击添加书库</Typography>
        </Box>
      )}

      {/* 对话框 */}
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
            />
            <TextField
              label="书库路径"
              value={formData.path}
              onChange={(e) => setFormData({ ...formData, path: e.target.value })}
              fullWidth
              required
              helperText="书籍文件所在的目录路径"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>取消</Button>
          <Button variant="contained" onClick={handleSubmit}>确定</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

import { useState, useEffect } from 'react'
import {
  Box, Typography, Button, Alert, CircularProgress,
  Card, CardContent, Grid, LinearProgress
} from '@mui/material'
import { Image, Refresh, Delete, AutoFixHigh } from '@mui/icons-material'
import api from '../../services/api'

interface CoverStats {
  database: {
    total_books: number
    books_with_cover: number
    books_without_cover: number
    coverage_rate: number
  }
  cache: {
    total_files: number
    total_size: number
    thumbnail_count: number
  }
}

export default function CoversTab() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [stats, setStats] = useState<CoverStats | null>(null)
  const [extracting, setExtracting] = useState(false)
  const [cleaning, setCleaning] = useState(false)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get<CoverStats>('/api/admin/covers/stats')
      setStats(response.data)
    } catch (err) {
      console.error('加载封面统计失败:', err)
      setError('加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleBatchExtract = async () => {
    try {
      setExtracting(true)
      setError('')
      const response = await api.post('/api/admin/covers/batch-extract')
      setSuccess(response.data.message)
      loadStats()
    } catch (err) {
      console.error('批量提取失败:', err)
      setError('批量提取失败')
    } finally {
      setExtracting(false)
    }
  }

  const handleCleanup = async () => {
    if (!confirm('确定要清理孤立的封面文件吗？')) return
    try {
      setCleaning(true)
      setError('')
      const response = await api.delete<{ deleted_count: number }>('/api/admin/covers/cleanup')
      setSuccess(`已清理 ${response.data.deleted_count} 个孤立封面文件`)
      loadStats()
    } catch (err) {
      console.error('清理失败:', err)
      setError('清理失败')
    } finally {
      setCleaning(false)
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
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
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

      {/* 统计信息 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Image sx={{ mr: 1, verticalAlign: 'middle' }} />
                封面覆盖率
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    {stats?.database.books_with_cover || 0} / {stats?.database.total_books || 0} 本书有封面
                  </Typography>
                  <Typography variant="body2" color="primary">
                    {stats?.database.coverage_rate?.toFixed(1) || 0}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={stats?.database.coverage_rate || 0}
                  sx={{ height: 10, borderRadius: 1 }}
                />
              </Box>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Box>
                  <Typography variant="h4" color="success.main">
                    {stats?.database.books_with_cover || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">有封面</Typography>
                </Box>
                <Box>
                  <Typography variant="h4" color="warning.main">
                    {stats?.database.books_without_cover || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">无封面</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>缓存统计</Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="h4">{stats?.cache.total_files || 0}</Typography>
                  <Typography variant="body2" color="text.secondary">总文件数</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="h4">{formatSize(stats?.cache.total_size || 0)}</Typography>
                  <Typography variant="body2" color="text.secondary">总大小</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="h4">{stats?.cache.thumbnail_count || 0}</Typography>
                  <Typography variant="body2" color="text.secondary">缩略图</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 操作按钮 */}
      <Typography variant="h6" gutterBottom>封面操作</Typography>
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          startIcon={<AutoFixHigh />}
          onClick={handleBatchExtract}
          disabled={extracting || (stats?.database.books_without_cover === 0)}
        >
          {extracting ? '提取中...' : `批量提取封面 (${stats?.database.books_without_cover || 0} 本)`}
        </Button>
        <Button
          variant="outlined"
          startIcon={<Delete />}
          onClick={handleCleanup}
          disabled={cleaning}
          color="warning"
        >
          {cleaning ? '清理中...' : '清理孤立封面'}
        </Button>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadStats}
        >
          刷新统计
        </Button>
      </Box>

      {/* 说明 */}
      <Card variant="outlined" sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>说明</Typography>
          <Typography variant="body2" color="text.secondary">
            • <strong>批量提取封面</strong>：从 EPUB/MOBI 等格式的电子书中提取封面图片
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • <strong>清理孤立封面</strong>：删除数据库中不存在对应书籍的封面文件
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • 对于 TXT 格式的书籍，系统会自动生成渐变色封面
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

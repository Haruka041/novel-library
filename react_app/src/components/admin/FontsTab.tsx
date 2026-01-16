import { useState, useEffect, useRef } from 'react'
import {
  Box, Typography, Card, CardContent, Button, IconButton, List, ListItem,
  ListItemText, ListItemSecondaryAction, Alert, CircularProgress, Chip
} from '@mui/material'
import { Upload, Delete, TextFields, Refresh } from '@mui/icons-material'
import api from '../../services/api'

interface FontInfo {
  id: string
  name: string
  family: string
  is_builtin: boolean
  file_url?: string
}

export default function FontsTab() {
  const [fonts, setFonts] = useState<FontInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadFonts()
  }, [])

  const loadFonts = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get<{ fonts: FontInfo[] }>('/api/fonts')
      setFonts(response.data.fonts)
    } catch (err) {
      console.error('加载字体失败:', err)
      setError('加载字体列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      setUploading(true)
      setError('')
      setSuccess('')

      const formData = new FormData()
      formData.append('file', file)

      await api.post('/api/fonts/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setSuccess(`字体 "${file.name}" 上传成功`)
      loadFonts()
    } catch (err: any) {
      console.error('上传字体失败:', err)
      setError(err.response?.data?.detail || '上传失败')
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDelete = async (font: FontInfo) => {
    if (!confirm(`确定要删除字体 "${font.name}" 吗？`)) return

    try {
      setError('')
      setSuccess('')
      await api.delete(`/api/fonts/${font.id}`)
      setSuccess(`字体 "${font.name}" 已删除`)
      loadFonts()
    } catch (err: any) {
      console.error('删除字体失败:', err)
      setError(err.response?.data?.detail || '删除失败')
    }
  }

  const builtinFonts = fonts.filter(f => f.is_builtin)
  const customFonts = fonts.filter(f => !f.is_builtin)

  return (
    <Box>
      {/* 操作栏 */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <input
          type="file"
          accept=".ttf,.otf,.woff,.woff2"
          style={{ display: 'none' }}
          ref={fileInputRef}
          onChange={handleUpload}
        />
        <Button
          variant="contained"
          startIcon={uploading ? <CircularProgress size={20} /> : <Upload />}
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          上传字体
        </Button>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadFonts}
          disabled={loading}
        >
          刷新
        </Button>
      </Box>

      {/* 提示信息 */}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* 内置字体 */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <TextFields />
                内置字体
              </Typography>
              <List dense>
                {builtinFonts.map((font) => (
                  <ListItem key={font.id}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {font.name}
                          <Chip label="内置" size="small" color="primary" variant="outlined" />
                        </Box>
                      }
                      secondary={
                        <Typography
                          variant="body2"
                          sx={{ fontFamily: font.family, mt: 0.5 }}
                        >
                          这是预览文字 The quick brown fox
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* 自定义字体 */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Upload />
                自定义字体
                <Chip label={customFonts.length} size="small" />
              </Typography>
              {customFonts.length === 0 ? (
                <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                  暂无自定义字体，点击上方按钮上传
                </Typography>
              ) : (
                <List dense>
                  {customFonts.map((font) => (
                    <ListItem key={font.id}>
                      <ListItemText
                        primary={font.name}
                        secondary={
                          <Typography variant="body2" sx={{ mt: 0.5 }}>
                            {font.file_url}
                          </Typography>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          color="error"
                          onClick={() => handleDelete(font)}
                        >
                          <Delete />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>

          {/* 使用说明 */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                使用说明
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • 支持格式：TTF、OTF、WOFF、WOFF2<br />
                • 上传的字体将在阅读器设置中可选<br />
                • 内置字体无法删除<br />
                • 建议使用常见中文字体以获得最佳阅读体验
              </Typography>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  )
}

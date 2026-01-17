import { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  CircularProgress,
} from '@mui/material'
import { Save } from '@mui/icons-material'
import api from '../../services/api'
import { useSettingsStore } from '../../stores/settingsStore'

interface SystemSettings {
  server_name: string
  server_description: string
  welcome_message: string
  registration_enabled: boolean
}

export default function SettingsTab() {
  const [settings, setSettings] = useState<SystemSettings>({
    server_name: '小说书库',
    server_description: '',
    welcome_message: '',
    registration_enabled: true,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 获取 settingsStore 用于刷新
  const settingsStore = useSettingsStore()

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const response = await api.get<SystemSettings>('/api/settings')
      setSettings(response.data)
    } catch (err: unknown) {
      console.error('加载设置失败:', err)
      setError('加载设置失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      setSuccess(false)
      
      await api.put('/api/settings', settings)
      setSuccess(true)
      
      // 重置 serverSettingsLoaded 以便刷新全局设置
      useSettingsStore.setState({ serverSettingsLoaded: false })
      settingsStore.loadServerSettings()
      
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: unknown) {
      console.error('保存设置失败:', err)
      setError('保存设置失败')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          设置保存成功！
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            基本设置
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            配置服务器的基本信息，这些信息将显示在界面上
          </Typography>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="服务器名称"
              value={settings.server_name}
              onChange={(e) => setSettings({ ...settings, server_name: e.target.value })}
              helperText="显示在顶部导航栏和登录页面"
              fullWidth
            />

            <TextField
              label="服务器描述"
              value={settings.server_description}
              onChange={(e) => setSettings({ ...settings, server_description: e.target.value })}
              helperText="简短描述您的书库（可选）"
              fullWidth
            />

            <TextField
              label="欢迎消息"
              value={settings.welcome_message}
              onChange={(e) => setSettings({ ...settings, welcome_message: e.target.value })}
              helperText="登录后显示的欢迎消息（可选）"
              multiline
              rows={3}
              fullWidth
            />
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            用户注册
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={settings.registration_enabled}
                onChange={(e) => setSettings({ ...settings, registration_enabled: e.target.checked })}
              />
            }
            label="允许新用户注册"
          />
          <Typography variant="body2" color="text.secondary">
            关闭后，只有管理员可以创建新用户
          </Typography>
        </CardContent>
      </Card>

      <Divider sx={{ my: 3 }} />

      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <Save />}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? '保存中...' : '保存设置'}
        </Button>
      </Box>
    </Box>
  )
}

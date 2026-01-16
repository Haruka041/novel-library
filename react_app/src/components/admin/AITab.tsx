import { useState, useEffect } from 'react'
import {
  Box, Typography, Card, CardContent, TextField, Select, MenuItem,
  FormControl, InputLabel, Switch, FormControlLabel, Button, Alert,
  CircularProgress, Divider, Grid, Slider, Chip, Accordion,
  AccordionSummary, AccordionDetails, InputAdornment, IconButton
} from '@mui/material'
import {
  ExpandMore, Visibility, VisibilityOff, Check, Error,
  Psychology, Settings, AutoAwesome
} from '@mui/icons-material'
import api from '../../services/api'

interface AIProviderConfig {
  provider: string
  api_key: string | null
  api_base: string | null
  model: string
  max_tokens: number
  temperature: number
  timeout: number
  enabled: boolean
}

interface AIFeaturesConfig {
  metadata_enhancement: boolean
  auto_extract_title: boolean
  auto_extract_author: boolean
  auto_generate_summary: boolean
  smart_classification: boolean
  auto_tagging: boolean
  content_rating: boolean
  semantic_search: boolean
  batch_limit: number
  daily_limit: number
}

interface AIConfig {
  provider: AIProviderConfig
  features: AIFeaturesConfig
}

interface PresetModel {
  id: string
  name: string
}

export default function AITab() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [error, setError] = useState('')
  
  const [config, setConfig] = useState<AIConfig | null>(null)
  const [presetModels, setPresetModels] = useState<Record<string, PresetModel[]>>({})
  const [showApiKey, setShowApiKey] = useState(false)
  
  // 表单状态
  const [provider, setProvider] = useState('openai')
  const [apiKey, setApiKey] = useState('')
  const [apiBase, setApiBase] = useState('')
  const [model, setModel] = useState('gpt-3.5-turbo')
  const [maxTokens, setMaxTokens] = useState(2000)
  const [temperature, setTemperature] = useState(0.7)
  const [timeout, setTimeout] = useState(30)
  const [enabled, setEnabled] = useState(false)
  
  const [features, setFeatures] = useState<AIFeaturesConfig>({
    metadata_enhancement: true,
    auto_extract_title: true,
    auto_extract_author: true,
    auto_generate_summary: true,
    smart_classification: true,
    auto_tagging: true,
    content_rating: true,
    semantic_search: false,
    batch_limit: 50,
    daily_limit: 1000,
  })

  useEffect(() => {
    loadConfig()
    loadPresetModels()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const response = await api.get<AIConfig>('/api/admin/ai/config')
      setConfig(response.data)
      
      // 初始化表单
      const p = response.data.provider
      setProvider(p.provider)
      // API key可能被遮蔽，不设置
      setApiBase(p.api_base || '')
      setModel(p.model)
      setMaxTokens(p.max_tokens)
      setTemperature(p.temperature)
      setTimeout(p.timeout)
      setEnabled(p.enabled)
      
      setFeatures(response.data.features)
    } catch (err) {
      console.error('加载AI配置失败:', err)
      setError('加载配置失败')
    } finally {
      setLoading(false)
    }
  }

  const loadPresetModels = async () => {
    try {
      const response = await api.get<Record<string, PresetModel[]>>('/api/admin/ai/models')
      setPresetModels(response.data)
    } catch (err) {
      console.error('加载模型列表失败:', err)
    }
  }

  const saveProviderConfig = async () => {
    try {
      setSaving(true)
      setError('')
      
      const data: any = {
        provider,
        model,
        max_tokens: maxTokens,
        temperature,
        timeout,
        enabled,
      }
      
      // 只有实际输入了API key才更新
      if (apiKey && !apiKey.startsWith('***')) {
        data.api_key = apiKey
      }
      
      if (apiBase) {
        data.api_base = apiBase
      }
      
      await api.put('/api/admin/ai/provider', data)
      setTestResult({ success: true, message: '配置已保存' })
    } catch (err: any) {
      setError(err.response?.data?.detail || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const saveFeaturesConfig = async () => {
    try {
      setSaving(true)
      setError('')
      await api.put('/api/admin/ai/features', features)
      setTestResult({ success: true, message: '功能配置已保存' })
    } catch (err: any) {
      setError(err.response?.data?.detail || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const testConnection = async () => {
    try {
      setTesting(true)
      setTestResult(null)
      const response = await api.post('/api/admin/ai/test')
      setTestResult({
        success: response.data.success,
        message: response.data.success ? '连接成功！' : response.data.error
      })
    } catch (err: any) {
      setTestResult({
        success: false,
        message: err.response?.data?.detail || '测试失败'
      })
    } finally {
      setTesting(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  const currentModels = presetModels[provider] || []

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Psychology /> AI 功能配置
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {testResult && (
        <Alert 
          severity={testResult.success ? 'success' : 'error'} 
          sx={{ mb: 2 }}
          onClose={() => setTestResult(null)}
        >
          {testResult.message}
        </Alert>
      )}

      {/* 提供商配置 */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Settings />
            <Typography>AI 服务提供商</Typography>
            {enabled ? (
              <Chip label="已启用" color="success" size="small" />
            ) : (
              <Chip label="未启用" color="default" size="small" />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={enabled} 
                    onChange={(e) => setEnabled(e.target.checked)}
                    color="primary"
                  />
                }
                label="启用 AI 功能"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>服务提供商</InputLabel>
                <Select
                  value={provider}
                  label="服务提供商"
                  onChange={(e) => {
                    setProvider(e.target.value)
                    // 切换提供商时设置默认模型
                    const models = presetModels[e.target.value]
                    if (models && models.length > 0) {
                      setModel(models[0].id)
                    }
                  }}
                >
                  <MenuItem value="openai">OpenAI</MenuItem>
                  <MenuItem value="claude">Claude (Anthropic)</MenuItem>
                  <MenuItem value="ollama">Ollama (本地模型)</MenuItem>
                  <MenuItem value="custom">自定义 (OpenAI兼容)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>模型</InputLabel>
                <Select
                  value={model}
                  label="模型"
                  onChange={(e) => setModel(e.target.value)}
                >
                  {currentModels.map((m) => (
                    <MenuItem key={m.id} value={m.id}>
                      {m.name}
                    </MenuItem>
                  ))}
                  <MenuItem value={model}>
                    <em>{model} (自定义)</em>
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API 密钥"
                type={showApiKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={config?.provider.api_key ? '已配置 (输入新值以更新)' : '输入API密钥'}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowApiKey(!showApiKey)}>
                        {showApiKey ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                helperText={provider === 'ollama' ? 'Ollama本地模型无需API密钥' : ''}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API 地址 (可选)"
                value={apiBase}
                onChange={(e) => setApiBase(e.target.value)}
                placeholder={
                  provider === 'openai' ? 'https://api.openai.com/v1/chat/completions' :
                  provider === 'claude' ? 'https://api.anthropic.com/v1/messages' :
                  provider === 'ollama' ? 'http://localhost:11434' :
                  '输入自定义API地址'
                }
                helperText="留空使用默认地址，或输入自定义地址（如代理服务）"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="最大Token数"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value) || 2000)}
                inputProps={{ min: 100, max: 32000 }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography gutterBottom>Temperature: {temperature}</Typography>
              <Slider
                value={temperature}
                onChange={(_, value) => setTemperature(value as number)}
                min={0}
                max={2}
                step={0.1}
                marks={[
                  { value: 0, label: '精确' },
                  { value: 1, label: '平衡' },
                  { value: 2, label: '创意' },
                ]}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="超时时间 (秒)"
                value={timeout}
                onChange={(e) => setTimeout(parseInt(e.target.value) || 30)}
                inputProps={{ min: 5, max: 120 }}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  onClick={saveProviderConfig}
                  disabled={saving}
                  startIcon={saving ? <CircularProgress size={20} /> : <Check />}
                >
                  保存配置
                </Button>
                <Button
                  variant="outlined"
                  onClick={testConnection}
                  disabled={testing || !enabled}
                  startIcon={testing ? <CircularProgress size={20} /> : null}
                >
                  测试连接
                </Button>
              </Box>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* 功能配置 */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AutoAwesome />
            <Typography>AI 功能开关</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                元数据增强
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={features.metadata_enhancement}
                    onChange={(e) => setFeatures({...features, metadata_enhancement: e.target.checked})}
                  />
                }
                label="启用AI元数据增强"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={features.auto_extract_title}
                    onChange={(e) => setFeatures({...features, auto_extract_title: e.target.checked})}
                  />
                }
                label="自动提取书名"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={features.auto_extract_author}
                    onChange={(e) => setFeatures({...features, auto_extract_author: e.target.checked})}
                  />
                }
                label="自动提取作者"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={features.auto_generate_summary}
                    onChange={(e) => setFeatures({...features, auto_generate_summary: e.target.checked})}
                  />
                }
                label="自动生成简介"
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                智能分类
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={features.smart_classification}
                    onChange={(e) => setFeatures({...features, smart_classification: e.target.checked})}
                  />
                }
                label="智能分类"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={features.auto_tagging}
                    onChange={(e) => setFeatures({...features, auto_tagging: e.target.checked})}
                  />
                }
                label="自动打标签"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={features.content_rating}
                    onChange={(e) => setFeatures({...features, content_rating: e.target.checked})}
                  />
                }
                label="内容分级"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={features.semantic_search}
                    onChange={(e) => setFeatures({...features, semantic_search: e.target.checked})}
                    disabled
                  />
                }
                label="语义搜索 (开发中)"
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                限制设置
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="单次批量处理上限"
                value={features.batch_limit}
                onChange={(e) => setFeatures({...features, batch_limit: parseInt(e.target.value) || 50})}
                inputProps={{ min: 1, max: 500 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="每日调用上限"
                value={features.daily_limit}
                onChange={(e) => setFeatures({...features, daily_limit: parseInt(e.target.value) || 1000})}
                inputProps={{ min: 1, max: 100000 }}
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={saveFeaturesConfig}
                disabled={saving}
                startIcon={saving ? <CircularProgress size={20} /> : <Check />}
              >
                保存功能配置
              </Button>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* 使用说明 */}
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="subtitle1" gutterBottom>
            使用说明
          </Typography>
          <Typography variant="body2" color="text.secondary">
            1. 选择AI服务提供商并配置API密钥<br />
            2. 启用AI功能后，在扫描书籍时会自动使用AI增强元数据<br />
            3. OpenAI和Claude需要有效的API密钥，Ollama需要本地运行<br />
            4. 自定义模式支持任何OpenAI兼容的API（如LM Studio、LocalAI等）
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

import { useState, useEffect } from 'react'
import {
  Box, Typography, Button, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, FormControl, InputLabel,
  Select, MenuItem, FormControlLabel, Switch, Alert, CircularProgress
} from '@mui/material'
import { Add, Edit, Delete, Lock, VpnKey } from '@mui/icons-material'
import api from '../../services/api'

interface User {
  id: number
  username: string
  is_admin: boolean
  age_rating_limit: string
  telegram_id: string | null
  created_at: string
  library_count: number
}

export default function UsersTab() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [users, setUsers] = useState<User[]>([])
  
  // 对话框状态
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogType, setDialogType] = useState<'create' | 'edit' | 'password'>('create')
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  
  // 表单数据
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    is_admin: false,
    age_rating_limit: 'all'
  })

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get<User[]>('/api/admin/users')
      setUsers(response.data)
    } catch (err) {
      console.error('加载用户列表失败:', err)
      setError('加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setDialogType('create')
    setSelectedUser(null)
    setFormData({ username: '', password: '', is_admin: false, age_rating_limit: 'all' })
    setDialogOpen(true)
  }

  const handleEdit = (user: User) => {
    setDialogType('edit')
    setSelectedUser(user)
    setFormData({
      username: user.username,
      password: '',
      is_admin: user.is_admin,
      age_rating_limit: user.age_rating_limit
    })
    setDialogOpen(true)
  }

  const handleResetPassword = (user: User) => {
    setDialogType('password')
    setSelectedUser(user)
    setFormData({ ...formData, password: '' })
    setDialogOpen(true)
  }

  const handleSubmit = async () => {
    try {
      if (dialogType === 'create') {
        await api.post('/api/admin/users', {
          username: formData.username,
          password: formData.password,
          is_admin: formData.is_admin,
          age_rating_limit: formData.age_rating_limit
        })
      } else if (dialogType === 'edit' && selectedUser) {
        await api.put(`/api/admin/users/${selectedUser.id}`, {
          username: formData.username,
          is_admin: formData.is_admin,
          age_rating_limit: formData.age_rating_limit
        })
      } else if (dialogType === 'password' && selectedUser) {
        await api.put(`/api/admin/users/${selectedUser.id}/password`, {
          new_password: formData.password
        })
      }
      setDialogOpen(false)
      loadUsers()
    } catch (err) {
      console.error('操作失败:', err)
      setError('操作失败')
    }
  }

  const handleDelete = async (user: User) => {
    if (!confirm(`确定要删除用户 "${user.username}" 吗？`)) return
    try {
      await api.delete(`/api/admin/users/${user.id}`)
      loadUsers()
    } catch (err) {
      console.error('删除失败:', err)
      setError('删除失败')
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-CN')
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
        <Typography variant="h6">用户列表</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
          新建用户
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>用户名</TableCell>
              <TableCell>角色</TableCell>
              <TableCell>年龄分级</TableCell>
              <TableCell>书库权限</TableCell>
              <TableCell>创建时间</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {user.username}
                    {user.telegram_id && (
                      <Chip label="TG" size="small" color="info" />
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={user.is_admin ? '管理员' : '普通用户'}
                    color={user.is_admin ? 'primary' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{user.age_rating_limit}</TableCell>
                <TableCell>{user.library_count} 个</TableCell>
                <TableCell>{formatDate(user.created_at)}</TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => handleEdit(user)} title="编辑">
                    <Edit fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleResetPassword(user)} title="重置密码">
                    <VpnKey fontSize="small" />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleDelete(user)} title="删除" color="error">
                    <Delete fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 对话框 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogType === 'create' ? '新建用户' : dialogType === 'edit' ? '编辑用户' : '重置密码'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            {dialogType !== 'password' && (
              <>
                <TextField
                  label="用户名"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  fullWidth
                  required
                />
                <FormControl fullWidth>
                  <InputLabel>年龄分级限制</InputLabel>
                  <Select
                    value={formData.age_rating_limit}
                    label="年龄分级限制"
                    onChange={(e) => setFormData({ ...formData, age_rating_limit: e.target.value })}
                  >
                    <MenuItem value="all">全部</MenuItem>
                    <MenuItem value="G">G (全年龄)</MenuItem>
                    <MenuItem value="PG">PG (家长指导)</MenuItem>
                    <MenuItem value="PG-13">PG-13 (13岁以上)</MenuItem>
                    <MenuItem value="R">R (17岁以上)</MenuItem>
                    <MenuItem value="NC-17">NC-17 (成人)</MenuItem>
                  </Select>
                </FormControl>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_admin}
                      onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
                    />
                  }
                  label="管理员权限"
                />
              </>
            )}
            {(dialogType === 'create' || dialogType === 'password') && (
              <TextField
                label={dialogType === 'create' ? '密码' : '新密码'}
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                fullWidth
                required
              />
            )}
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

import { Box, Typography, Card, CardContent, Avatar, Divider, List, ListItem, ListItemIcon, ListItemText, Switch } from '@mui/material'
import { Person, Lock, History, Favorite, DarkMode, Logout } from '@mui/icons-material'
import { useAuthStore } from '../stores/authStore'
import { useThemeStore } from '../stores/themeStore'

export default function ProfilePage() {
  const { user, logout } = useAuthStore()
  const { mode, toggleMode } = useThemeStore()

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>
        个人中心
      </Typography>

      {/* 用户信息卡片 */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ width: 64, height: 64, bgcolor: 'primary.main' }}>
            <Person sx={{ fontSize: 32 }} />
          </Avatar>
          <Box>
            <Typography variant="h6">{user?.username || '用户'}</Typography>
            <Typography variant="body2" color="text.secondary">
              {user?.isAdmin ? '管理员' : '普通用户'}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* 设置列表 */}
      <Card>
        <List>
          <ListItem>
            <ListItemIcon>
              <DarkMode />
            </ListItemIcon>
            <ListItemText primary="深色模式" />
            <Switch checked={mode === 'dark'} onChange={toggleMode} />
          </ListItem>
          <Divider />
          <ListItem button>
            <ListItemIcon>
              <Lock />
            </ListItemIcon>
            <ListItemText primary="修改密码" secondary="更改账户密码" />
          </ListItem>
          <Divider />
          <ListItem button>
            <ListItemIcon>
              <Favorite />
            </ListItemIcon>
            <ListItemText primary="我的收藏" secondary="查看收藏的书籍" />
          </ListItem>
          <Divider />
          <ListItem button>
            <ListItemIcon>
              <History />
            </ListItemIcon>
            <ListItemText primary="阅读历史" secondary="查看阅读记录" />
          </ListItem>
          <Divider />
          <ListItem button onClick={logout}>
            <ListItemIcon>
              <Logout color="error" />
            </ListItemIcon>
            <ListItemText primary="退出登录" primaryTypographyProps={{ color: 'error' }} />
          </ListItem>
        </List>
      </Card>
    </Box>
  )
}

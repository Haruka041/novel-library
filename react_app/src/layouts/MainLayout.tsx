import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Box, AppBar, Toolbar, Typography, IconButton, Avatar, BottomNavigation, BottomNavigationAction, useMediaQuery, useTheme } from '@mui/material'
import { Home, LibraryBooks, Person, Search } from '@mui/icons-material'
import { useAuthStore } from '../stores/authStore'

const MainLayout = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const user = useAuthStore((state) => state.user)

  const getNavValue = () => {
    if (location.pathname.startsWith('/home')) return 0
    if (location.pathname.startsWith('/library')) return 1
    if (location.pathname.startsWith('/profile')) return 2
    return 0
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Top AppBar */}
      <AppBar position="fixed" sx={{ bgcolor: 'background.paper' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={() => navigate('/home')}>
            📚 小说书库
          </Typography>
          
          <IconButton onClick={() => navigate('/search')}>
            <Search />
          </IconButton>
          
          <IconButton onClick={() => navigate('/profile')}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, pt: 8, pb: isMobile ? 7 : 2 }}>
        <Outlet />
      </Box>

      {/* Bottom Navigation (Mobile) */}
      {isMobile && (
        <BottomNavigation
          value={getNavValue()}
          onChange={(_, newValue) => {
            switch (newValue) {
              case 0:
                navigate('/home')
                break
              case 1:
                navigate('/library')
                break
              case 2:
                navigate('/profile')
                break
            }
          }}
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            bgcolor: 'background.paper',
            borderTop: 1,
            borderColor: 'divider',
          }}
        >
          <BottomNavigationAction label="首页" icon={<Home />} />
          <BottomNavigationAction label="书库" icon={<LibraryBooks />} />
          <BottomNavigationAction label="我的" icon={<Person />} />
        </BottomNavigation>
      )}
    </Box>
  )
}

export default MainLayout

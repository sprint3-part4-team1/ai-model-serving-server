import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Divider,
  Container,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  Article as ArticleIcon,
  Image as ImageIcon,
  AutoFixHigh as AutoFixHighIcon,
  PhotoLibrary as PhotoLibraryIcon,
  Restaurant as RestaurantIcon,
  AutoAwesome as SparklesIcon,
  FilterList as FilterListIcon,
  MenuBook as MenuBookIcon,
  AddBox as AddBoxIcon,
  Store as StoreIcon,
} from '@mui/icons-material'

const drawerWidth = 240

interface MenuItem {
  path: string
  label: string
  icon: JSX.Element
}

const menuItems: MenuItem[] = [
  { path: '/', label: '홈', icon: <HomeIcon /> },
  { path: '/store-management', label: '매장 생성', icon: <StoreIcon /> },
  { path: '/menu-generation', label: '메뉴판 생성', icon: <AddBoxIcon /> },
  { path: '/menu-board', label: 'AI 메뉴판', icon: <RestaurantIcon /> },
  { path: '/ad-copy', label: '광고 문구 생성', icon: <ArticleIcon /> },
  { path: '/image-generator', label: '이미지 생성', icon: <ImageIcon /> },
  { path: '/background-editor', label: '배경 편집', icon: <AutoFixHighIcon /> },
  { path: '/gallery', label: '갤러리', icon: <PhotoLibraryIcon /> },
  { path: '/seasonal-story', label: '시즈널 스토리', icon: <SparklesIcon /> },
  { path: '/menu-recommendation', label: 'AI 메뉴 추천', icon: <FilterListIcon /> },
  { path: '/menu-storytelling', label: '메뉴 스토리텔링', icon: <MenuBookIcon /> },
]

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const handleNavigation = (path: string) => {
    navigate(path)
    setMobileOpen(false)
  }

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          광고 콘텐츠 생성
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            소상공인 광고 콘텐츠 생성 서비스
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Drawer - Mobile */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // 모바일 성능 향상
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Drawer - Desktop */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
          },
        }}
        open
      >
        {drawer}
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: '100%',
          marginLeft: { sm: `${drawerWidth}px` },
          maxWidth: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        <Container maxWidth="xl">
          <Outlet />
        </Container>
      </Box>
    </Box>
  )
}

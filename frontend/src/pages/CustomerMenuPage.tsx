import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material'
import { Restaurant, Store } from '@mui/icons-material'
import { menuApi } from '../services/api'

interface MenuItem {
  id: number
  name: string
  category: string
  price: number
  description: string
  image_url?: string
  ingredients: string[]
}

interface StoreInfo {
  id: number
  name: string
  description: string
}

function MenuItemImage({ imageUrl, menuName }: { imageUrl?: string; menuName: string }) {
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageError, setImageError] = useState(false)

  if (!imageUrl) {
    return (
      <Box
        sx={{
          width: '100%',
          height: 250,
          backgroundColor: 'grey.200',
          borderRadius: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Restaurant sx={{ fontSize: 64, color: 'grey.400' }} />
      </Box>
    )
  }

  return (
    <Box sx={{ position: 'relative', width: '100%', height: 250 }}>
      {!imageLoaded && !imageError && (
        <Box
          sx={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            backgroundColor: 'grey.200',
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircularProgress size={40} />
        </Box>
      )}

      {imageError && (
        <Box
          sx={{
            width: '100%',
            height: '100%',
            backgroundColor: 'grey.200',
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Restaurant sx={{ fontSize: 64, color: 'grey.400' }} />
        </Box>
      )}

      <Box
        component="img"
        src={imageUrl}
        alt={menuName}
        onLoad={() => setImageLoaded(true)}
        onError={() => setImageError(true)}
        sx={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          borderRadius: 2,
          display: imageLoaded && !imageError ? 'block' : 'none',
        }}
      />
    </Box>
  )
}

export default function CustomerMenuPage() {
  const { storeId } = useParams<{ storeId: string }>()
  const [storeInfo, setStoreInfo] = useState<StoreInfo | null>(null)
  const [menus, setMenus] = useState<MenuItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (storeId) {
      loadStoreMenu(parseInt(storeId))
    }
  }, [storeId])

  const loadStoreMenu = async (id: number) => {
    try {
      setLoading(true)
      setError(null)

      const response = await menuApi.getStoreWithMenus(id)

      if (response.success && response.data) {
        setStoreInfo({
          id: response.data.id,
          name: response.data.name,
          description: response.data.description || '',
        })

        // 메뉴 데이터 변환
        const menuList: MenuItem[] = []
        response.data.categories?.forEach((category) => {
          category.items?.forEach((item) => {
            menuList.push({
              id: item.id,
              name: item.name,
              category: category.name,
              price: item.price || 0,
              description: item.description || '',
              image_url: item.image_url,
              ingredients: [],
            })
          })
        })
        setMenus(menuList)
      }
    } catch (err: any) {
      console.error('메뉴 로드 실패:', err)
      setError(err.response?.data?.detail || '메뉴를 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  // 카테고리별로 메뉴 그룹화
  const menusByCategory = menus.reduce((acc, menu) => {
    if (!acc[menu.category]) {
      acc[menu.category] = []
    }
    acc[menu.category].push(menu)
    return acc
  }, {} as Record<string, MenuItem[]>)

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress size={60} />
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Container>
    )
  }

  if (!storeInfo) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Alert severity="warning">매장 정보를 찾을 수 없습니다.</Alert>
      </Container>
    )
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50', py: 4 }}>
      <Container maxWidth="lg">
        {/* 매장 헤더 */}
        <Card sx={{ mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <CardContent sx={{ py: 4 }}>
            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <Store sx={{ fontSize: 48, color: 'white' }} />
              <Box>
                <Typography variant="h3" fontWeight="bold" color="white">
                  {storeInfo.name}
                </Typography>
                {storeInfo.description && (
                  <Typography variant="body1" color="rgba(255,255,255,0.9)" sx={{ mt: 1 }}>
                    {storeInfo.description}
                  </Typography>
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* 메뉴 목록 */}
        {Object.keys(menusByCategory).length === 0 ? (
          <Alert severity="info">등록된 메뉴가 없습니다.</Alert>
        ) : (
          Object.entries(menusByCategory).map(([category, items]) => (
            <Box key={category} sx={{ mb: 6 }}>
              <Typography variant="h4" fontWeight="bold" gutterBottom sx={{ mb: 3 }}>
                {category}
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={3}>
                {items.map((menu) => (
                  <Grid item xs={12} sm={6} md={4} key={menu.id}>
                    <Card
                      sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: 6,
                        },
                      }}
                    >
                      <MenuItemImage imageUrl={menu.image_url} menuName={menu.name} />

                      <CardContent sx={{ flexGrow: 1 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="h6" fontWeight="bold">
                            {menu.name}
                          </Typography>
                          <Chip
                            label={`${menu.price.toLocaleString()}원`}
                            color="primary"
                            size="small"
                          />
                        </Box>

                        {menu.description && (
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              display: '-webkit-box',
                              WebkitLineClamp: 3,
                              WebkitBoxOrient: 'vertical',
                            }}
                          >
                            {menu.description}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          ))
        )}
      </Container>
    </Box>
  )
}

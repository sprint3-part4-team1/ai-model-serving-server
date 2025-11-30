import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardActionArea,
  Grid,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material'
import { Store, Restaurant } from '@mui/icons-material'
import { storeApi } from '../services/api'

interface Store {
  id: number
  name: string
  description: string
  menu_count?: number
}

export default function CustomerMenuListPage() {
  const navigate = useNavigate()
  const [stores, setStores] = useState<Store[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStores()
  }, [])

  const loadStores = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await storeApi.getStores()

      if (response.success && response.data) {
        setStores(response.data.stores || [])
      }
    } catch (err: any) {
      console.error('매장 목록 로드 실패:', err)
      setError(err.response?.data?.detail || '매장 목록을 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleStoreClick = (storeId: number) => {
    navigate(`/menu/${storeId}`)
  }

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

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          <Restaurant sx={{ fontSize: 48, mr: 2, verticalAlign: 'middle' }} />
          매장 메뉴판
        </Typography>
        <Typography variant="body1" color="text.secondary">
          메뉴를 확인하실 매장을 선택해주세요
        </Typography>
      </Box>

      {stores.length === 0 ? (
        <Alert severity="info">등록된 매장이 없습니다.</Alert>
      ) : (
        <Grid container spacing={3}>
          {stores.map((store) => (
            <Grid item xs={12} sm={6} md={4} key={store.id}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 6,
                  },
                }}
              >
                <CardActionArea onClick={() => handleStoreClick(store.id)} sx={{ height: '100%' }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={2} mb={2}>
                      <Box
                        sx={{
                          p: 2,
                          borderRadius: 2,
                          bgcolor: 'primary.main',
                          color: 'white',
                        }}
                      >
                        <Store sx={{ fontSize: 40 }} />
                      </Box>
                      <Box flexGrow={1}>
                        <Typography variant="h5" fontWeight="bold" gutterBottom>
                          {store.name}
                        </Typography>
                        {store.menu_count !== undefined && (
                          <Chip
                            label={`${store.menu_count}개 메뉴`}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </Box>

                    {store.description && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                        }}
                      >
                        {store.description}
                      </Typography>
                    )}
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  )
}

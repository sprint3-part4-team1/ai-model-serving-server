import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
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
  Divider,
  Paper,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material'
import { Restaurant, Store, WbSunny, Star, Search, Close } from '@mui/icons-material'
import { menuApi, seasonalStoryApi } from '../services/api'

interface MenuItem {
  id: number
  name: string
  category: string
  price: number
  description: string
  image_url?: string
  ingredients: string[]
  nutrition?: {
    calories?: number
    protein_g?: number
    carbs_g?: number
    fat_g?: number
    sugar_g?: number
    caffeine_mg?: number
  }
  origin?: string
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

interface MenuHighlight {
  menu_id: number
  name: string
  reason: string
}

interface RecommendationContext {
  weather?: {
    description: string
    temperature: number
  }
  season?: string
  time?: string
  trends?: string[]
}

// 헬스 스토리 생성 함수
function generateHealthStory(menu: MenuItem): string {
  if (!menu.nutrition) {
    return `${menu.name}은(는) 신선한 재료로 만들어진 특별한 메뉴입니다.`
  }

  const { calories, protein_g, carbs_g, fat_g, sugar_g, caffeine_mg } = menu.nutrition
  const stories: string[] = []

  // 칼로리 기반 스토리
  if (calories) {
    if (calories < 200) {
      stories.push('가벼운 한 끼로 부담 없이 즐기기 좋습니다.')
    } else if (calories < 400) {
      stories.push('적당한 칼로리로 균형 잡힌 식사를 제공합니다.')
    } else if (calories < 600) {
      stories.push('든든한 한 끼로 에너지를 충전하기에 좋습니다.')
    } else {
      stories.push('풍부한 영양으로 하루의 활력을 채워줍니다.')
    }
  }

  // 단백질 기반 스토리
  if (protein_g && protein_g > 10) {
    stories.push(`${protein_g}g의 단백질이 근육 건강과 체력 향상에 도움을 줍니다.`)
  }

  // 탄수화물 기반 스토리
  if (carbs_g && carbs_g > 30) {
    stories.push('탄수화물이 빠른 에너지 공급원이 되어 활동적인 하루를 지원합니다.')
  }

  // 당류 기반 스토리
  if (sugar_g) {
    if (sugar_g < 10) {
      stories.push('당류가 적어 건강하게 즐길 수 있습니다.')
    } else if (sugar_g > 20) {
      stories.push('달콤한 맛이 기분을 좋게 만들어줍니다.')
    }
  }

  // 카페인 기반 스토리
  if (caffeine_mg && caffeine_mg > 0) {
    if (caffeine_mg < 50) {
      stories.push('소량의 카페인이 부드러운 각성 효과를 제공합니다.')
    } else if (caffeine_mg < 150) {
      stories.push(`${caffeine_mg}mg의 카페인이 집중력 향상에 도움을 줍니다.`)
    } else {
      stories.push('카페인이 풍부하여 피로 회복과 집중력 향상에 효과적입니다.')
    }
  }

  // 스토리가 없으면 기본 메시지
  if (stories.length === 0) {
    return `${menu.name}은(는) 균형 잡힌 영양으로 건강한 식사를 제공합니다.`
  }

  return stories.join(' ')
}

export default function CustomerMenuPage() {
  const { storeId } = useParams<{ storeId: string }>()
  const [storeInfo, setStoreInfo] = useState<StoreInfo | null>(null)
  const [menus, setMenus] = useState<MenuItem[]>([])
  const [displayedMenus, setDisplayedMenus] = useState<MenuItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [welcomeMessage, setWelcomeMessage] = useState<string>('')
  const [highlights, setHighlights] = useState<MenuHighlight[]>([])
  const [recommendationsLoading, setRecommendationsLoading] = useState(false)
  const [recommendationContext, setRecommendationContext] = useState<RecommendationContext | null>(null)
  const [customerQuery, setCustomerQuery] = useState('')
  const [filterExplanation, setFilterExplanation] = useState<string>('')
  const [selectedMenu, setSelectedMenu] = useState<MenuItem | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  useEffect(() => {
    if (storeId) {
      loadStoreMenu(parseInt(storeId))
      loadRecommendations(parseInt(storeId))
    }
  }, [storeId])

  const loadStoreMenu = async (id: number) => {
    try {
      setLoading(true)
      setError(null)

      // 메뉴 불러오기 (store 정보 포함)
      const menuResponse = await menuApi.getStoreMenus(id)

      if (menuResponse.success && menuResponse.data) {
        // Store 정보 설정
        const data = menuResponse.data as any
        setStoreInfo({
          id: data.store_id,
          name: data.store_name || '매장',
          description: data.store_address || '',
        })
        // 메뉴 데이터 변환
        const menuList: MenuItem[] = []
        menuResponse.data.categories?.forEach((category) => {
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
        setDisplayedMenus(menuList)
      }
    } catch (err: any) {
      console.error('메뉴 로드 실패:', err)
      setError(err.response?.data?.detail || '메뉴를 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const loadRecommendations = async (id: number) => {
    try {
      setRecommendationsLoading(true)

      // 환영 문구와 메뉴 하이라이트 동시 로드
      const [welcomeResponse, highlightsResponse] = await Promise.all([
        seasonalStoryApi.getWelcomeMessage(id).catch(() => null),
        seasonalStoryApi.getMenuHighlights(id, 'Seoul', 3).catch(() => null),
      ])

      if (welcomeResponse?.success) {
        setWelcomeMessage(welcomeResponse.data.message)
        // 컨텍스트 정보 저장
        if (welcomeResponse.data.context) {
          setRecommendationContext({
            weather: welcomeResponse.data.context.weather,
            season: welcomeResponse.data.context.season,
            time: welcomeResponse.data.context.time,
            trends: welcomeResponse.data.context.trends || []
          })
        }
      }

      if (highlightsResponse?.success) {
        setHighlights(highlightsResponse.data.highlights || [])
        // 컨텍스트 정보가 아직 없으면 하이라이트 응답에서 가져오기
        if (!recommendationContext && highlightsResponse.data.context) {
          setRecommendationContext({
            weather: highlightsResponse.data.context.weather,
            season: highlightsResponse.data.context.season,
            time: highlightsResponse.data.context.time,
            trends: highlightsResponse.data.context.trends || []
          })
        }
      }
    } catch (err: any) {
      console.error('추천 정보 로드 실패:', err)
      // 추천 정보는 실패해도 메인 메뉴는 보여줌
    } finally {
      setRecommendationsLoading(false)
    }
  }

  const handleCustomerQuery = async () => {
    if (!customerQuery.trim()) return

    try {
      setLoading(true)
      setError(null)

      // 메뉴 필터링 API 호출
      const response = await menuApi.filterMenus({
        query: customerQuery,
        menus: menus,
      })

      if (response.success && response.data) {
        // 필터링된 메뉴의 ID를 기반으로 원본 메뉴 객체 찾기
        const filteredIds = response.data.filtered_menus.map((m: any) => m.id)
        const filteredMenus = menus.filter((menu) => filteredIds.includes(menu.id))

        // 화면에 필터링된 메뉴만 표시
        setDisplayedMenus(filteredMenus)
        setFilterExplanation(response.data.explanation)
      }
    } catch (err: any) {
      setError('메뉴 필터링 중 오류가 발생했습니다.')
      console.error('Filter error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleResetFilter = () => {
    setDisplayedMenus(menus)
    setCustomerQuery('')
    setFilterExplanation('')
  }

  const handleMenuClick = (menu: MenuItem) => {
    setSelectedMenu(menu)
    setDialogOpen(true)
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
    setSelectedMenu(null)
  }

  // 카테고리별로 메뉴 그룹화
  const menusByCategory = displayedMenus.reduce((acc, menu) => {
    if (!acc[menu.category]) {
      acc[menu.category] = []
    }
    acc[menu.category].push(menu)
    return acc
  }, {} as Record<string, MenuItem[]>)

  // 추천 메뉴 ID 목록
  const highlightedMenuIds = new Set(highlights.map(h => h.menu_id))

  // 특정 메뉴가 추천 메뉴인지 확인
  const isHighlighted = (menuId: number) => highlightedMenuIds.has(menuId)

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

        {/* 시즌별 추천 배너 */}
        {!recommendationsLoading && (welcomeMessage || highlights.length > 0) && (
          <Paper
            elevation={3}
            sx={{
              mb: 4,
              p: 3,
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
            }}
          >
            {welcomeMessage && (
              <Box>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <WbSunny sx={{ fontSize: 32 }} />
                  <Typography variant="h5" fontWeight="600">
                    {welcomeMessage}
                  </Typography>
                </Box>
                {recommendationContext && (
                  <Typography
                    variant="caption"
                    sx={{
                      opacity: 0.85,
                      display: 'block',
                      mb: highlights.length > 0 ? 2 : 0,
                      fontSize: '0.75rem'
                    }}
                  >
                    📍 기반 정보: {recommendationContext.weather?.description} {recommendationContext.weather?.temperature}도
                    {recommendationContext.season && `, ${recommendationContext.season}`}
                    {recommendationContext.time && `, ${recommendationContext.time}`}
                    {recommendationContext.trends && recommendationContext.trends.length > 0 &&
                      ` | 트렌드: ${recommendationContext.trends.slice(0, 3).join(', ')}`
                    }
                  </Typography>
                )}
              </Box>
            )}

            {highlights.length > 0 && (
              <Box>
                <Typography variant="h6" fontWeight="bold" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Star /> 오늘의 추천 메뉴
                </Typography>
                <Grid container spacing={2}>
                  {highlights.map((highlight) => (
                    <Grid item xs={12} sm={4} key={highlight.menu_id}>
                      <Paper
                        sx={{
                          p: 2,
                          bgcolor: 'rgba(255,255,255,0.95)',
                          color: 'text.primary',
                          borderRadius: 2,
                        }}
                      >
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          {highlight.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {highlight.reason}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </Paper>
        )}

        {/* 메뉴 검색 섹션 */}
        <Paper elevation={2} sx={{ p: 2, mb: 4 }}>
          <Box display="flex" gap={2} alignItems="center" mb={filterExplanation ? 2 : 0}>
            <TextField
              fullWidth
              placeholder="예: 칼로리 낮은 음료 추천, 달콤한 디저트 찾기..."
              value={customerQuery}
              onChange={(e) => setCustomerQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCustomerQuery()}
              variant="outlined"
              size="small"
            />
            <Button
              variant="contained"
              startIcon={<Search />}
              onClick={handleCustomerQuery}
              disabled={!customerQuery.trim() || loading}
            >
              검색
            </Button>
            {displayedMenus.length < menus.length && (
              <Button
                variant="outlined"
                onClick={handleResetFilter}
              >
                전체보기
              </Button>
            )}
          </Box>
          {filterExplanation && (
            <Alert severity="info" sx={{ mt: 2 }}>
              {filterExplanation}
            </Alert>
          )}
        </Paper>

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
                {items.map((menu) => {
                  const highlighted = isHighlighted(menu.id)
                  return (
                    <Grid item xs={12} sm={6} md={4} key={menu.id}>
                      <Card
                        sx={{
                          height: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                          transition: 'transform 0.2s, box-shadow 0.2s',
                          position: 'relative',
                          border: highlighted ? '3px solid #f5576c' : 'none',
                          boxShadow: highlighted ? 4 : 1,
                          '&:hover': {
                            transform: 'translateY(-4px)',
                            boxShadow: 6,
                          },
                        }}
                      >
                        {highlighted && (
                          <Chip
                            icon={<Star />}
                            label="추천"
                            color="error"
                            size="small"
                            sx={{
                              position: 'absolute',
                              top: 12,
                              right: 12,
                              zIndex: 1,
                              fontWeight: 'bold',
                            }}
                          />
                        )}

                        <CardActionArea onClick={() => handleMenuClick(menu)} sx={{ flexGrow: 1 }}>
                          <MenuItemImage imageUrl={menu.image_url} menuName={menu.name} />

                          <CardContent>
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
                        </CardActionArea>
                      </Card>
                    </Grid>
                  )
                })}
              </Grid>
            </Box>
          ))
        )}

        {/* 메뉴 상세 다이얼로그 */}
        <Dialog
          open={dialogOpen}
          onClose={handleDialogClose}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h5" fontWeight="bold">
                {selectedMenu?.name}
              </Typography>
              <IconButton onClick={handleDialogClose} size="small">
                <Close />
              </IconButton>
            </Box>
          </DialogTitle>

          <DialogContent>
            {selectedMenu && (
              <Box>
                <Box position="relative">
                  <img
                    src={selectedMenu.image_url}
                    alt={selectedMenu.name}
                    style={{ width: '100%', borderRadius: 8, marginBottom: 8 }}
                  />
                </Box>

                <Chip label={selectedMenu.category} size="small" color="primary" sx={{ mb: 2 }} />

                <Typography variant="body1" color="text.secondary" paragraph>
                  {selectedMenu.description}
                </Typography>

                <Divider sx={{ my: 2 }} />

                {/* 성분 분석 + 스토리텔링 */}
                <Box>
                  {selectedMenu.nutrition && (
                    <>
                      <Typography variant="h6" fontWeight="bold" gutterBottom>
                        영양 성분
                      </Typography>
                      <Grid container spacing={1} sx={{ mb: 2 }}>
                        {selectedMenu.nutrition.calories && (
                          <Grid item xs={6} sm={4}>
                            <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', textAlign: 'center' }}>
                              <Typography variant="body2" color="text.secondary">칼로리</Typography>
                              <Typography variant="h6" fontWeight="bold">{selectedMenu.nutrition.calories} kcal</Typography>
                            </Paper>
                          </Grid>
                        )}
                        {selectedMenu.nutrition.protein_g && (
                          <Grid item xs={6} sm={4}>
                            <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', textAlign: 'center' }}>
                              <Typography variant="body2" color="text.secondary">단백질</Typography>
                              <Typography variant="h6" fontWeight="bold">{selectedMenu.nutrition.protein_g}g</Typography>
                            </Paper>
                          </Grid>
                        )}
                        {selectedMenu.nutrition.carbs_g && (
                          <Grid item xs={6} sm={4}>
                            <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', textAlign: 'center' }}>
                              <Typography variant="body2" color="text.secondary">탄수화물</Typography>
                              <Typography variant="h6" fontWeight="bold">{selectedMenu.nutrition.carbs_g}g</Typography>
                            </Paper>
                          </Grid>
                        )}
                        {selectedMenu.nutrition.fat_g && (
                          <Grid item xs={6} sm={4}>
                            <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', textAlign: 'center' }}>
                              <Typography variant="body2" color="text.secondary">지방</Typography>
                              <Typography variant="h6" fontWeight="bold">{selectedMenu.nutrition.fat_g}g</Typography>
                            </Paper>
                          </Grid>
                        )}
                        {selectedMenu.nutrition.sugar_g && (
                          <Grid item xs={6} sm={4}>
                            <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', textAlign: 'center' }}>
                              <Typography variant="body2" color="text.secondary">당류</Typography>
                              <Typography variant="h6" fontWeight="bold">{selectedMenu.nutrition.sugar_g}g</Typography>
                            </Paper>
                          </Grid>
                        )}
                        {selectedMenu.nutrition.caffeine_mg && selectedMenu.nutrition.caffeine_mg > 0 && (
                          <Grid item xs={6} sm={4}>
                            <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'grey.50', textAlign: 'center' }}>
                              <Typography variant="body2" color="text.secondary">카페인</Typography>
                              <Typography variant="h6" fontWeight="bold">{selectedMenu.nutrition.caffeine_mg}mg</Typography>
                            </Paper>
                          </Grid>
                        )}
                      </Grid>
                    </>
                  )}

                  <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ mt: selectedMenu.nutrition ? 2 : 0 }}>
                    스토리텔링
                  </Typography>
                  <Typography variant="body1" paragraph sx={{ fontStyle: 'italic', color: 'text.secondary', lineHeight: 1.7 }}>
                    {generateHealthStory(selectedMenu)}
                  </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  가격
                </Typography>
                <Typography variant="h5" color="primary" fontWeight="bold">
                  {selectedMenu.price.toLocaleString()}원
                </Typography>

                {selectedMenu.ingredients && selectedMenu.ingredients.length > 0 && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      재료
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {selectedMenu.ingredients.map((ingredient, idx) => (
                        <Chip key={idx} label={ingredient} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </>
                )}

                {selectedMenu.origin && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      원산지
                    </Typography>
                    <Typography variant="body1">{selectedMenu.origin}</Typography>
                  </>
                )}
              </Box>
            )}
          </DialogContent>

          <DialogActions>
            <Button onClick={handleDialogClose}>닫기</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  )
}

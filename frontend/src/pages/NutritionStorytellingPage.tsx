import { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  LinearProgress,
} from '@mui/material'
import {
  Restaurant,
  Science,
  AutoAwesome,
  TrendingUp,
  LocalFireDepartment,
  WaterDrop,
} from '@mui/icons-material'
import { nutritionApi, menuApi } from '@/services/api'
import type { MenuItemWithNutrition, NutritionEstimate } from '@/types'

export default function NutritionStorytellingPage() {
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [storeId, setStoreId] = useState('1')
  const [menus, setMenus] = useState<MenuItemWithNutrition[]>([])
  const [selectedMenu, setSelectedMenu] = useState<MenuItemWithNutrition | null>(null)

  // 매장 메뉴 조회
  const loadStoreMenus = async () => {
    if (!storeId.trim()) {
      setError('매장 ID를 입력해주세요')
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await menuApi.getStoreMenus(parseInt(storeId))

      // 카테고리별 메뉴를 평탄화
      const allMenus: MenuItemWithNutrition[] = []
      response.data.categories.forEach(category => {
        category.items.forEach(item => {
          allMenus.push({
            id: item.id,
            name: item.name,
            category: category.name,
            price: item.price || 0,
            description: item.description,
            image_url: item.image_url,
          })
        })
      })

      setMenus(allMenus)

      if (allMenus.length === 0) {
        setError('해당 매장에 등록된 메뉴가 없습니다.')
      }
    } catch (err: any) {
      setError(err.message || '메뉴 조회 중 오류가 발생했습니다.')
      setMenus([])
    } finally {
      setLoading(false)
    }
  }

  // 영양소 분석 실행
  const handleAnalyze = async () => {
    if (!storeId.trim()) {
      setError('매장 ID를 입력해주세요')
      return
    }

    try {
      setAnalyzing(true)
      setError(null)

      const response = await nutritionApi.analyzeStore(parseInt(storeId))

      if (response.success) {
        alert(response.message + '\n분석이 완료되면 메뉴를 다시 조회해주세요.')
      }
    } catch (err: any) {
      setError(err.message || '영양소 분석 중 오류가 발생했습니다.')
    } finally {
      setAnalyzing(false)
    }
  }

  // 메뉴 선택
  const handleMenuSelect = (menu: MenuItemWithNutrition) => {
    setSelectedMenu(menu)
  }

  // 영양소 정보 표시 컴포넌트
  const NutritionCard = ({ nutrition }: { nutrition: NutritionEstimate }) => {
    const nutritionItems = [
      { label: '칼로리', value: nutrition.calories, unit: 'kcal', icon: <LocalFireDepartment />, color: '#ff6b6b' },
      { label: '단백질', value: nutrition.protein_g, unit: 'g', icon: <TrendingUp />, color: '#51cf66' },
      { label: '지방', value: nutrition.fat_g, unit: 'g', icon: <WaterDrop />, color: '#ffd43b' },
      { label: '탄수화물', value: nutrition.carbs_g, unit: 'g', icon: <Science />, color: '#748ffc' },
      { label: '당분', value: nutrition.sugar_g, unit: 'g', icon: <AutoAwesome />, color: '#ff8787' },
      { label: '카페인', value: nutrition.caffeine_mg, unit: 'mg', icon: <Restaurant />, color: '#8e44ad' },
    ]

    return (
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Science color="primary" />
            <Typography variant="h6" fontWeight="bold">
              영양 성분 분석
            </Typography>
            <Chip
              label={`신뢰도: ${(nutrition.confidence * 100).toFixed(0)}%`}
              color={nutrition.confidence >= 0.7 ? 'success' : 'warning'}
              size="small"
              sx={{ ml: 'auto' }}
            />
          </Box>

          <Grid container spacing={2}>
            {nutritionItems.map((item, index) => (
              <Grid item xs={6} sm={4} md={2} key={index}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    bgcolor: 'grey.50',
                    borderRadius: 2,
                  }}
                >
                  <Box sx={{ color: item.color, mb: 1 }}>{item.icon}</Box>
                  <Typography variant="caption" color="text.secondary" display="block">
                    {item.label}
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {item.value ?? '-'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {item.unit}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    )
  }

  // 건강 스토리텔링 생성
  const generateHealthStory = (menu: MenuItemWithNutrition): string => {
    if (!menu.nutrition) return '영양소 정보가 없습니다.'

    const { calories, protein_g, carbs_g, fat_g, sugar_g, caffeine_mg } = menu.nutrition

    let story = `<strong>${menu.name}</strong>는 `

    // 칼로리 기반 스토리
    if (calories !== undefined) {
      if (calories < 100) {
        story += '저칼로리로 가벼운 간식으로 적합합니다. '
      } else if (calories < 300) {
        story += '적당한 칼로리로 건강한 한 끼 식사로 좋습니다. '
      } else {
        story += '든든한 에너지를 제공하는 고칼로리 메뉴입니다. '
      }
    }

    // 단백질 기반 스토리
    if (protein_g !== undefined && protein_g > 10) {
      story += `풍부한 단백질(${protein_g}g)로 근육 형성과 체력 증진에 도움을 줍니다. `
    }

    // 탄수화물 기반 스토리
    if (carbs_g !== undefined && carbs_g > 30) {
      story += `탄수화물(${carbs_g}g)이 빠른 에너지 공급원이 되어 활동적인 하루를 시작하기에 완벽합니다. `
    }

    // 지방 기반 스토리
    if (fat_g !== undefined) {
      if (fat_g < 5) {
        story += '저지방으로 다이어트 중에도 부담 없이 즐길 수 있습니다. '
      }
    }

    // 당분 기반 스토리
    if (sugar_g !== undefined) {
      if (sugar_g === 0) {
        story += '무설탕으로 혈당 관리가 필요한 분들께 추천합니다. '
      } else if (sugar_g > 20) {
        story += '달콤한 맛으로 기분 전환이 필요할 때 좋습니다. '
      }
    }

    // 카페인 기반 스토리
    if (caffeine_mg !== undefined && caffeine_mg > 0) {
      if (caffeine_mg < 50) {
        story += '소량의 카페인으로 부담 없이 즐길 수 있습니다. '
      } else if (caffeine_mg < 150) {
        story += `적당한 카페인(${caffeine_mg}mg)으로 졸음을 깨우고 집중력을 높여줍니다. `
      } else {
        story += `강한 카페인(${caffeine_mg}mg)으로 빠른 각성 효과를 원하는 분께 추천합니다. `
      }
    }

    return story
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* 헤더 */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
            영양소 기반 스토리텔링
          </Typography>
          <Typography variant="body1" color="text.secondary">
            메뉴의 영양소 정보를 분석하고 건강 스토리를 생성합니다
          </Typography>
        </Box>

        {/* 매장 입력 */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            매장 선택
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            매장 ID를 입력하고 영양소 분석을 시작하세요
          </Typography>

          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="매장 ID"
                type="number"
                value={storeId}
                onChange={(e) => setStoreId(e.target.value)}
                placeholder="1"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={loadStoreMenus}
                  disabled={loading || analyzing}
                >
                  메뉴 조회
                </Button>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleAnalyze}
                  disabled={loading || analyzing}
                  startIcon={analyzing ? <CircularProgress size={20} /> : <Science />}
                >
                  {analyzing ? '분석 중...' : '영양소 분석'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* 로딩 */}
        {loading && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress />
          </Box>
        )}

        {/* 에러 */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* 메뉴 목록 */}
        {menus.length > 0 && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              메뉴 선택 ({menus.length}개)
            </Typography>
            <Grid container spacing={2}>
              {menus.map((menu) => (
                <Grid item xs={12} sm={6} md={4} key={menu.id}>
                  <Card
                    variant="outlined"
                    sx={{
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      border: selectedMenu?.id === menu.id ? 2 : 1,
                      borderColor: selectedMenu?.id === menu.id ? 'primary.main' : 'divider',
                      '&:hover': {
                        boxShadow: 3,
                        transform: 'translateY(-2px)',
                      },
                    }}
                    onClick={() => handleMenuSelect(menu)}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {menu.name}
                      </Typography>
                      <Chip label={menu.category} size="small" sx={{ mb: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        ₩{menu.price.toLocaleString()}
                      </Typography>
                      {menu.description && (
                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                          {menu.description}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}

        {/* 선택된 메뉴의 영양소 정보 및 스토리 */}
        {selectedMenu && (
          <Box>
            <Paper sx={{ p: 3, mb: 3, borderLeft: 4, borderColor: 'primary.main' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Restaurant color="primary" />
                <Typography variant="h5" fontWeight="bold">
                  {selectedMenu.name}
                </Typography>
                <Chip label={selectedMenu.category} color="primary" size="small" sx={{ ml: 1 }} />
              </Box>

              {selectedMenu.description && (
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedMenu.description}
                </Typography>
              )}

              <Divider sx={{ my: 3 }} />

              {/* 영양소 정보 */}
              {selectedMenu.nutrition ? (
                <>
                  <NutritionCard nutrition={selectedMenu.nutrition} />

                  {/* 건강 스토리텔링 */}
                  <Card variant="outlined" sx={{ bgcolor: 'primary.50' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <AutoAwesome color="primary" />
                        <Typography variant="h6" fontWeight="bold">
                          건강 스토리
                        </Typography>
                      </Box>
                      <Typography
                        variant="body1"
                        sx={{ lineHeight: 1.8 }}
                        dangerouslySetInnerHTML={{ __html: generateHealthStory(selectedMenu) }}
                      />
                    </CardContent>
                  </Card>
                </>
              ) : (
                <Alert severity="info">
                  이 메뉴의 영양소 정보가 아직 분석되지 않았습니다.
                  <br />
                  '영양소 분석' 버튼을 클릭하여 분석을 시작하세요.
                </Alert>
              )}
            </Paper>
          </Box>
        )}

        {/* 안내 메시지 */}
        {menus.length === 0 && !loading && !error && (
          <Paper sx={{ p: 4, textAlign: 'center', bgcolor: 'grey.50' }}>
            <Science sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              매장 ID를 입력하고 메뉴를 조회하세요
            </Typography>
            <Typography variant="body2" color="text.secondary">
              영양소 분석 후 메뉴별 건강 스토리를 확인할 수 있습니다
            </Typography>
          </Paper>
        )}
      </Box>
    </Container>
  )
}

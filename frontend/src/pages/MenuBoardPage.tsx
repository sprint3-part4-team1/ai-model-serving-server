import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  CardMedia,
  CardActionArea,
  Grid,
  Chip,
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  IconButton,
} from '@mui/material'
import {
  WbSunny,
  Cloud,
  Umbrella,
  Air,
  ThermostatAuto,
  Restaurant,
  LocalCafe,
  Cake,
  Close,
  Search,
  TrendingUp,
  Edit,
  Save,
  CloudUpload,
} from '@mui/icons-material'
import { seasonalStoryApi, menuApi, menuGenerationApi } from '@services/api'
import type {
  MenuItem,
  SeasonalStoryResponse,
  MenuStorytellingResponse,
  ContextInfo,
} from '@types/index'

// Mock 메뉴 데이터
const MOCK_MENUS: MenuItem[] = [
  {
    id: 1,
    name: '아메리카노',
    category: '커피',
    price: 4500,
    description: '깊고 진한 에스프레소의 맛',
    image_url: 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400',
    ingredients: ['에스프레소', '물'],
    origin: '이탈리아',
    history: '제2차 세계대전 중 미군이 에스프레소에 물을 타서 마신 것이 유래',
  },
  {
    id: 2,
    name: '카페라떼',
    category: '커피',
    price: 5000,
    description: '부드러운 우유와 에스프레소의 조화',
    image_url: 'https://images.unsplash.com/photo-1517487881594-2787fef5ebf7?w=400',
    ingredients: ['에스프레소', '우유'],
    origin: '이탈리아',
  },
  {
    id: 3,
    name: '초콜릿 케이크',
    category: '디저트',
    price: 6500,
    description: '진한 초콜릿의 달콤한 유혹',
    image_url: 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400',
    ingredients: ['초콜릿', '밀가루', '설탕', '계란', '버터'],
  },
  {
    id: 4,
    name: '치즈케이크',
    category: '디저트',
    price: 6000,
    description: '부드럽고 고소한 크림치즈',
    image_url: 'https://images.unsplash.com/photo-1524351199678-941a58a3df50?w=400',
    ingredients: ['크림치즈', '밀가루', '설탕', '계란'],
  },
  {
    id: 5,
    name: '크루아상',
    category: '브런치',
    price: 4000,
    description: '바삭한 버터 향',
    image_url: 'https://images.unsplash.com/photo-1530610476181-d83430b64dcd?w=400',
    ingredients: ['밀가루', '버터', '설탕', '소금'],
    origin: '프랑스',
  },
  {
    id: 6,
    name: '샌드위치',
    category: '브런치',
    price: 7500,
    description: '신선한 재료로 만든 건강한 한끼',
    image_url: 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400',
    ingredients: ['빵', '야채', '치즈', '햄'],
  },
]

const getWeatherIcon = (condition: string) => {
  switch (condition.toLowerCase()) {
    case 'clear':
      return <WbSunny />
    case 'clouds':
      return <Cloud />
    case 'rain':
    case 'drizzle':
      return <Umbrella />
    default:
      return <Cloud />
  }
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

export default function MenuBoardPage() {
  const { storeId } = useParams<{ storeId: string }>()
  const navigate = useNavigate()
  const [seasonalStory, setSeasonalStory] = useState<SeasonalStoryResponse | null>(null)
  const [selectedMenu, setSelectedMenu] = useState<MenuItem | null>(null)
  const [menuStorytelling, setMenuStorytelling] = useState<MenuStorytellingResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [storytellingLoading, setStorytellingLoading] = useState(false)
  const [menuLoading, setMenuLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [displayedMenus, setDisplayedMenus] = useState<MenuItem[]>(MOCK_MENUS)
  const [filterExplanation, setFilterExplanation] = useState<string>('')
  const [inputStoreId, setInputStoreId] = useState<string>(storeId || '0')

  // 편집 모드 상태
  const [editMode, setEditMode] = useState(false)
  const [editedName, setEditedName] = useState('')
  const [editedDescription, setEditedDescription] = useState('')
  const [editedPrice, setEditedPrice] = useState<number>(0)
  const [editedIngredients, setEditedIngredients] = useState<string[]>([])
  const [newIngredient, setNewIngredient] = useState('')
  const [uploadingImage, setUploadingImage] = useState(false)
  const [savingChanges, setSavingChanges] = useState(false)

  // URL의 storeId가 변경될 때마다 데이터 로드
  useEffect(() => {
    if (storeId) {
      setInputStoreId(storeId)
      loadStoreData()
    }
  }, [storeId])

  // 매장 데이터 로드 (시즈널 스토리 + 메뉴)
  const loadStoreData = async () => {
    const id = parseInt(storeId || '0')

    // 매장 ID 0: 디폴트 샘플 메뉴 + 기본 스토리
    if (id === 0) {
      setDisplayedMenus(MOCK_MENUS)
      setFilterExplanation('')
      setError(null)
      // 기본 시즈널 스토리 로드 (샘플 메뉴 카테고리 사용)
      const sampleCategories = ['커피', '디저트', '샌드위치']
      await loadSeasonalStory(0, '샘플 카페', sampleCategories)
      return
    }

    // 매장 ID 1 이상: DB에서 조회
    setLoading(true)
    setMenuLoading(true)
    setError(null)

    try {
      // 메뉴 조회
      const response = await menuApi.getStoreMenus(id)

      if (response.data.categories.length === 0) {
        setError(`매장 ID ${id}번의 메뉴가 없습니다.`)
        setDisplayedMenus([])
        setFilterExplanation('')
      } else {
        // DB 메뉴를 MenuItem 형식으로 변환
        const menus: MenuItem[] = []
        const categories: string[] = []
        const data = response.data as any
        const storeName = data.store_name || `매장 ${id}`

        response.data.categories.forEach((category: any) => {
          categories.push(category.name)
          category.items.forEach((item: any) => {
            menus.push({
              id: item.id,
              name: item.name,
              category: category.name,
              price: item.price || 0,
              description: item.description || '',
              image_url: item.image_url,
              ingredients: item.ingredients || [],
              nutrition: item.nutrition,
            })
          })
        })
        setDisplayedMenus(menus)
        setFilterExplanation(`${storeName}의 메뉴 ${menus.length}개`)

        // 해당 매장의 시즈널 스토리 로드 (실제 매장 정보로)
        await loadSeasonalStory(id, storeName, categories)
      }
    } catch (err: any) {
      setError(err.message || '메뉴 조회 중 오류가 발생했습니다.')
      setDisplayedMenus([])
      setFilterExplanation('')
    } finally {
      setLoading(false)
      setMenuLoading(false)
    }
  }

  // 매장 타입 추론 기능 제거 - 실제 메뉴 데이터로 스토리 생성
  // const inferStoreType = (categories: string[]): string => {
  //   const categoryStr = categories.join(',').toLowerCase()
  //   ...
  // }

  const loadSeasonalStory = async (
    id: number,
    storeName: string,
    categories: string[] = ['커피', '디저트', '브런치']
  ) => {
    try {
      // 매장타입 제거 - 실제 메뉴 데이터로 스토리 생성
      const response = await seasonalStoryApi.generate({
        store_id: id,
        store_name: storeName,
        location: 'Seoul',
        menu_categories: categories,
      })

      setSeasonalStory(response)
    } catch (err: any) {
      console.error('시즈널 스토리 로드 실패:', err)
      // 스토리 로드 실패해도 메뉴는 보여주기
    }
  }

  const handleMenuClick = async (menu: MenuItem) => {
    setSelectedMenu(menu)
    setDialogOpen(true)
    setStorytellingLoading(true)
    setMenuStorytelling(null)

    // 편집 모드 초기화
    setEditMode(false)
    setEditedName(menu.name)
    setEditedDescription(menu.description || '')
    setEditedPrice(menu.price)
    setEditedIngredients(menu.ingredients || [])
    setNewIngredient('')

    try {
      const response = await seasonalStoryApi.generateMenuStorytelling({
        menu_id: menu.id,
        menu_name: menu.name,
        ingredients: menu.ingredients || [],
        origin: menu.origin,
        history: menu.history,
      })

      setMenuStorytelling(response)
    } catch (err: any) {
      console.error('Failed to load menu storytelling:', err)
    } finally {
      setStorytellingLoading(false)
    }
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
    setSelectedMenu(null)
    setMenuStorytelling(null)
    setEditMode(false)
  }

  const handleEditToggle = () => {
    if (editMode) {
      // 편집 취소 - 원래 값으로 되돌리기
      if (selectedMenu) {
        setEditedName(selectedMenu.name)
        setEditedDescription(selectedMenu.description || '')
        setEditedPrice(selectedMenu.price)
        setEditedIngredients(selectedMenu.ingredients || [])
        setNewIngredient('')
      }
    }
    setEditMode(!editMode)
  }

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files || !event.target.files[0] || !selectedMenu) return

    const file = event.target.files[0]
    setUploadingImage(true)

    try {
      const response = await menuGenerationApi.uploadMenuImage(selectedMenu.id, file)

      if (response.success && response.data.image_url) {
        // 메뉴 목록 업데이트
        setDisplayedMenus((prevMenus) =>
          prevMenus.map((m) =>
            m.id === selectedMenu.id
              ? { ...m, image_url: response.data.image_url }
              : m
          )
        )

        // 선택된 메뉴 업데이트
        setSelectedMenu({
          ...selectedMenu,
          image_url: response.data.image_url,
        })

        alert('이미지가 성공적으로 업로드되었습니다!')
      }
    } catch (err: any) {
      console.error('Failed to upload image:', err)
      alert('이미지 업로드에 실패했습니다.')
    } finally {
      setUploadingImage(false)
    }
  }

  const handleSaveChanges = async () => {
    if (!selectedMenu) return

    setSavingChanges(true)

    try {
      const updates: any = {}
      if (editedName !== selectedMenu.name) updates.name = editedName
      if (editedDescription !== selectedMenu.description) updates.description = editedDescription
      if (editedPrice !== selectedMenu.price) updates.price = editedPrice

      // 재료 변경 확인
      const ingredientsChanged = JSON.stringify(editedIngredients.sort()) !== JSON.stringify((selectedMenu.ingredients || []).sort())
      if (ingredientsChanged) {
        updates.ingredients = editedIngredients
      }

      if (Object.keys(updates).length > 0) {
        await menuGenerationApi.updateMenuItem(selectedMenu.id, updates)

        // 메뉴 목록 업데이트
        setDisplayedMenus((prevMenus) =>
          prevMenus.map((m) =>
            m.id === selectedMenu.id
              ? { ...m, name: editedName, description: editedDescription, price: editedPrice, ingredients: editedIngredients }
              : m
          )
        )

        // 선택된 메뉴 업데이트
        setSelectedMenu({
          ...selectedMenu,
          name: editedName,
          description: editedDescription,
          price: editedPrice,
          ingredients: editedIngredients,
        })

        alert('변경사항이 저장되었습니다!')
        setEditMode(false)
      } else {
        alert('변경된 내용이 없습니다.')
      }
    } catch (err: any) {
      console.error('Failed to save changes:', err)
      alert('저장에 실패했습니다.')
    } finally {
      setSavingChanges(false)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 매장 선택 섹션 - 기본 URL에서만 표시 */}
      {!storeId && (
        <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" mb={2}>
            매장 선택
          </Typography>
          <Box display="flex" gap={2} alignItems="center">
            <TextField
              label="매장 ID"
              placeholder="0: 샘플, 1~: DB 메뉴"
              value={inputStoreId}
              onChange={(e) => setInputStoreId(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && navigate(`/menu-board/${inputStoreId}`)}
              variant="outlined"
              size="small"
              sx={{ width: 200 }}
              type="number"
            />
            <Button
              variant="contained"
              onClick={() => navigate(`/menu-board/${inputStoreId}`)}
              disabled={loading || menuLoading}
            >
              {loading || menuLoading ? <CircularProgress size={24} /> : '매장 정보 불러오기'}
            </Button>
          </Box>
        </Paper>
      )}

      {/* 시즈널 스토리 섹션 */}
      <Paper elevation={3} sx={{ p: 3, mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        {!storeId ? (
          <Box textAlign="center" py={4}>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              AI 메뉴판 관리
            </Typography>
            <Typography variant="body1" sx={{ mt: 2, opacity: 0.9 }}>
              위에서 매장 ID를 입력하여 메뉴를 확인하세요
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, opacity: 0.7 }}>
              매장 ID 0: 샘플 메뉴 | 1번 이상: 실제 생성된 메뉴
            </Typography>
          </Box>
        ) : loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="100px">
            <CircularProgress color="inherit" />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : seasonalStory ? (
          <Box>
            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <Box sx={{ fontSize: 40 }}>
                {getWeatherIcon(seasonalStory.data.context.weather.condition)}
              </Box>
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  {seasonalStory.data.store_info.store_name}
                </Typography>
                <Box display="flex" gap={1} alignItems="center" mt={0.5}>
                  <Chip
                    size="small"
                    label={seasonalStory.data.context.weather.description}
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                  />
                  <Chip
                    size="small"
                    label={`${seasonalStory.data.context.weather.temperature}°C`}
                    icon={<ThermostatAuto sx={{ color: 'white !important' }} />}
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                  />
                  <Chip
                    size="small"
                    label={seasonalStory.data.context.time_info.period_kr}
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                  />
                </Box>
              </Box>
            </Box>

            <Typography variant="h6" sx={{ fontStyle: 'italic', my: 2 }}>
              {seasonalStory.data.story}
            </Typography>

            {seasonalStory.data.context.trends.length > 0 && (
              <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
                <TrendingUp fontSize="small" />
                <Typography variant="body2">트렌드:</Typography>
                {seasonalStory.data.context.trends.map((trend, idx) => (
                  <Chip
                    key={idx}
                    size="small"
                    label={trend}
                    sx={{ bgcolor: 'rgba(255,255,255,0.3)', color: 'white' }}
                  />
                ))}
              </Box>
            )}
          </Box>
        ) : null}
      </Paper>

      {/* 메뉴 그리드 - 매장이 선택된 경우에만 표시 */}
      {storeId && (
        <>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              메뉴
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {displayedMenus.length}개의 메뉴
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {displayedMenus.map((menu) => (
          <Grid item xs={12} sm={6} md={4} key={menu.id}>
            <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardActionArea onClick={() => handleMenuClick(menu)} sx={{ flexGrow: 1 }}>
                <CardMedia
                  component="img"
                  height="200"
                  image={menu.image_url}
                  alt={menu.name}
                  sx={{ objectFit: 'cover' }}
                />
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                    <Typography variant="h6" component="div">
                      {menu.name}
                    </Typography>
                    <Chip label={menu.category} size="small" color="primary" />
                  </Box>

                  <Typography variant="body2" color="text.secondary" mb={2}>
                    {menu.description}
                  </Typography>

                  <Typography variant="h6" color="primary" fontWeight="bold">
                    {menu.price.toLocaleString()}원
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
            ))}
          </Grid>
        </>
      )}

      {/* 메뉴 스토리텔링 다이얼로그 */}
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
            <Box display="flex" gap={1}>
              <IconButton
                onClick={handleEditToggle}
                size="small"
                color={editMode ? 'default' : 'primary'}
                title={editMode ? '편집 취소' : '편집'}
              >
                {editMode ? <Close /> : <Edit />}
              </IconButton>
              <IconButton onClick={handleDialogClose} size="small">
                <Close />
              </IconButton>
            </Box>
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
                {editMode && (
                  <Box display="flex" gap={1} mb={2}>
                    <Button
                      variant="outlined"
                      size="small"
                      component="label"
                      startIcon={<CloudUpload />}
                      disabled={uploadingImage}
                    >
                      {uploadingImage ? '업로드 중...' : '이미지 업로드'}
                      <input
                        type="file"
                        hidden
                        accept="image/*"
                        onChange={handleImageUpload}
                      />
                    </Button>
                  </Box>
                )}
              </Box>

              <Chip label={selectedMenu.category} size="small" color="primary" sx={{ mb: 2 }} />

              {editMode ? (
                <Box mb={2}>
                  <TextField
                    fullWidth
                    label="메뉴 이름"
                    value={editedName}
                    onChange={(e) => setEditedName(e.target.value)}
                    variant="outlined"
                    size="small"
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="메뉴 설명"
                    value={editedDescription}
                    onChange={(e) => setEditedDescription(e.target.value)}
                    variant="outlined"
                    size="small"
                  />
                </Box>
              ) : (
                <Typography variant="body1" color="text.secondary" paragraph>
                  {selectedMenu.description}
                </Typography>
              )}

              <Divider sx={{ my: 2 }} />

              {/* 🆕 성분 분석 + 스토리텔링 */}
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
              {editMode ? (
                <TextField
                  label="가격"
                  type="number"
                  value={editedPrice}
                  onChange={(e) => setEditedPrice(Number(e.target.value))}
                  variant="outlined"
                  size="small"
                  sx={{ mb: 2 }}
                  InputProps={{
                    endAdornment: <Typography>원</Typography>
                  }}
                />
              ) : (
                <Typography variant="h5" color="primary" fontWeight="bold">
                  {selectedMenu.price.toLocaleString()}원
                </Typography>
              )}

              {/* 재료 섹션 */}
              {(editMode || (selectedMenu.ingredients && selectedMenu.ingredients.length > 0)) && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    재료
                  </Typography>
                  {editMode ? (
                    <Box>
                      <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                        {editedIngredients.map((ingredient, idx) => (
                          <Chip
                            key={idx}
                            label={ingredient}
                            size="small"
                            onDelete={() => {
                              setEditedIngredients(editedIngredients.filter((_, i) => i !== idx))
                            }}
                          />
                        ))}
                      </Box>
                      <Box display="flex" gap={1}>
                        <TextField
                          size="small"
                          placeholder="재료 입력"
                          value={newIngredient}
                          onChange={(e) => setNewIngredient(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter' && newIngredient.trim()) {
                              setEditedIngredients([...editedIngredients, newIngredient.trim()])
                              setNewIngredient('')
                            }
                          }}
                          sx={{ flexGrow: 1 }}
                        />
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => {
                            if (newIngredient.trim()) {
                              setEditedIngredients([...editedIngredients, newIngredient.trim()])
                              setNewIngredient('')
                            }
                          }}
                        >
                          추가
                        </Button>
                      </Box>
                    </Box>
                  ) : (
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {selectedMenu.ingredients?.map((ingredient, idx) => (
                        <Chip key={idx} label={ingredient} size="small" variant="outlined" />
                      ))}
                    </Box>
                  )}
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
          {editMode && (
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSaveChanges}
              disabled={savingChanges}
            >
              {savingChanges ? '저장 중...' : '저장'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  )
}

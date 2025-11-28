import { useState } from 'react'
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
} from '@mui/material'
import { Search, LocalCafe, Restaurant } from '@mui/icons-material'
import { menuApi } from '@/services/api'

export default function MenuRecommendationPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<any>(null)

  // 샘플 메뉴 데이터
  const sampleMenus = [
    {
      id: 1,
      name: '아메리카노',
      category: 'drink',
      price: 4500,
      calories: 10,
      protein_g: 0.5,
      fat_g: 0.1,
      carbs_g: 2,
      sugar_g: 0,
      caffeine_mg: 150
    },
    {
      id: 2,
      name: '카페라떼',
      category: 'drink',
      price: 5000,
      calories: 150,
      protein_g: 7,
      fat_g: 6,
      carbs_g: 13,
      sugar_g: 11,
      caffeine_mg: 75
    },
    {
      id: 3,
      name: '치즈케이크',
      category: 'dessert',
      price: 6500,
      calories: 450,
      protein_g: 9,
      fat_g: 26,
      carbs_g: 42,
      sugar_g: 28,
      caffeine_mg: 0
    },
    {
      id: 4,
      name: '초코 머핀',
      category: 'dessert',
      price: 4000,
      calories: 380,
      protein_g: 6,
      fat_g: 18,
      carbs_g: 48,
      sugar_g: 30,
      caffeine_mg: 20
    },
    {
      id: 5,
      name: '그린티 라떼',
      category: 'drink',
      price: 5500,
      calories: 200,
      protein_g: 6,
      fat_g: 7,
      carbs_g: 28,
      sugar_g: 24,
      caffeine_mg: 50
    }
  ]

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('추천받고 싶은 메뉴를 입력해주세요')
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await menuApi.filterMenus({
        query: query,
        menus: sampleMenus
      })

      // 백엔드 응답을 프론트엔드 형식으로 변환
      const transformed = {
        recommendations: response.data.data.filtered_menus.map((item: any) => ({
          menu: {
            id: item.id,
            name: item.name,
            category: item.category,
            price: item.price,
            description: item.description,
            calories: item.calories,
            protein_g: item.protein_g,
            fat_g: item.fat_g,
            carbs_g: item.carbs_g,
            sugar_g: item.sugar_g,
            caffeine_mg: item.caffeine_mg
          },
          reason: item.reason
        })),
        total_found: response.data.data.total_count,
        parsed_intent: {
          explanation: response.data.data.explanation
        }
      }

      setResult(transformed)
    } catch (err: any) {
      setError(err.message || '메뉴 추천 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* 헤더 */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
            AI 메뉴 추천
          </Typography>
          <Typography variant="body1" color="text.secondary">
            원하는 메뉴를 자연어로 말해주세요. AI가 최적의 메뉴를 추천해드립니다
          </Typography>
        </Box>

        {/* 검색 폼 */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            메뉴 요청하기
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            예시: "칼로리 낮은 음료 추천", "단백질 많은 메뉴", "저렴한 커피"
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={3}
            label="무엇을 찾으시나요?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="칼로리 낮은 음료 추천해줘"
            sx={{ mb: 2 }}
          />

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleSearch}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <Search />}
          >
            {loading ? '분석 중...' : '메뉴 찾기'}
          </Button>
        </Paper>

        {/* 에러 */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* 결과 */}
        {result && (
          <Box>
            {/* 추천 메뉴 */}
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                추천 메뉴 ({result.total_found}개 발견)
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {result.parsed_intent?.explanation || 'AI가 분석한 결과입니다'}
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {result.recommendations?.map((rec: any, index: number) => (
                  <Card key={index} variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box sx={{ flex: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            {rec.menu.category === 'drink' ? (
                              <LocalCafe color="primary" />
                            ) : (
                              <Restaurant color="primary" />
                            )}
                            <Typography variant="h6">{rec.menu.name}</Typography>
                            <Chip
                              label={rec.menu.category === 'drink' ? '음료' : '디저트'}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          </Box>

                          {rec.menu.description && (
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              {rec.menu.description}
                            </Typography>
                          )}

                          <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', mb: 2 }}>
                            💡 {rec.reason}
                          </Typography>

                          {/* 영양 정보 */}
                          <Grid container spacing={2}>
                            <Grid item xs={3}>
                              <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary" display="block">
                                  칼로리
                                </Typography>
                                <Typography variant="body2" fontWeight="bold">
                                  {rec.menu.calories}kcal
                                </Typography>
                              </Box>
                            </Grid>
                            <Grid item xs={3}>
                              <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary" display="block">
                                  단백질
                                </Typography>
                                <Typography variant="body2" fontWeight="bold">
                                  {rec.menu.protein_g}g
                                </Typography>
                              </Box>
                            </Grid>
                            <Grid item xs={3}>
                              <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary" display="block">
                                  당분
                                </Typography>
                                <Typography variant="body2" fontWeight="bold">
                                  {rec.menu.sugar_g}g
                                </Typography>
                              </Box>
                            </Grid>
                            <Grid item xs={3}>
                              <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary" display="block">
                                  카페인
                                </Typography>
                                <Typography variant="body2" fontWeight="bold">
                                  {rec.menu.caffeine_mg}mg
                                </Typography>
                              </Box>
                            </Grid>
                          </Grid>
                        </Box>

                        <Box sx={{ pl: 2, textAlign: 'right' }}>
                          <Typography variant="h5" color="primary" fontWeight="bold">
                            {rec.menu.price.toLocaleString()}원
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}

                {result.recommendations?.length === 0 && (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      조건에 맞는 메뉴를 찾지 못했습니다.
                    </Typography>
                  </Box>
                )}
              </Box>
            </Paper>

            {/* AI 분석 정보 */}
            {result.parsed_intent && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  AI 분석 결과
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {result.parsed_intent.filter_conditions && (
                    <Typography variant="body2">
                      <strong>필터:</strong> {JSON.stringify(result.parsed_intent.filter_conditions)}
                    </Typography>
                  )}
                  {result.parsed_intent.sort_by && (
                    <Typography variant="body2">
                      <strong>정렬:</strong> {result.parsed_intent.sort_by}
                    </Typography>
                  )}
                </Box>
              </Paper>
            )}
          </Box>
        )}
      </Box>
    </Container>
  )
}

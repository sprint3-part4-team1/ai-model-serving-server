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
  Divider,
  Chip,
} from '@mui/material'
import { AutoAwesome, Cloud, Schedule, TrendingUp } from '@mui/icons-material'
import { seasonalStoryApi } from '@/services/api'

export default function SeasonalStoryPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [storeId, setStoreId] = useState('1')
  const [storeName, setStoreName] = useState('우리 카페')
  const [storeType, setStoreType] = useState('카페')
  const [location, setLocation] = useState('Seoul')
  const [result, setResult] = useState<any>(null)
  const [selectedGoogleTrends, setSelectedGoogleTrends] = useState<string[]>([])
  const [selectedInstagramTrends, setSelectedInstagramTrends] = useState<string[]>([])

  // 트렌드 선택/해제 토글
  const toggleGoogleTrend = (trend: string) => {
    setSelectedGoogleTrends(prev =>
      prev.includes(trend)
        ? prev.filter(t => t !== trend)
        : [...prev, trend]
    )
  }

  const toggleInstagramTrend = (trend: string) => {
    setSelectedInstagramTrends(prev =>
      prev.includes(trend)
        ? prev.filter(t => t !== trend)
        : [...prev, trend]
    )
  }

  // 매장 타입에 따른 메뉴 카테고리 추출
  const getMenuCategoriesByStoreType = (storeType: string): string[] => {
    const type = storeType.toLowerCase()

    if (type.includes('중국')) {
      return ['짜장면', '짬뽕', '탕수육', '볶음밥']
    } else if (type.includes('일식') || type.includes('초밥')) {
      return ['초밥', '우동', '돈까스', '회']
    } else if (type.includes('한식')) {
      return ['김치찌개', '된장찌개', '불고기', '비빔밥']
    } else if (type.includes('양식') || type.includes('이탈리') || type.includes('파스타')) {
      return ['파스타', '스테이크', '피자', '리조또']
    } else if (type.includes('분식')) {
      return ['떡볶이', '김밥', '순대', '라면']
    } else if (type.includes('치킨')) {
      return ['후라이드', '양념치킨', '간장치킨']
    } else if (type.includes('카페') || type.includes('커피')) {
      return ['커피', '음료', '디저트']
    } else if (type.includes('디저트') || type.includes('베이커리') || type.includes('빵')) {
      return ['케이크', '빵', '마카롱', '쿠키']
    } else {
      // 기타 레스토랑
      return ['식사', '음료']
    }
  }

  const handleGenerate = async () => {
    try {
      setLoading(true)
      setError(null)

      // 선택된 Google과 Instagram 트렌드를 합침
      const allSelectedTrends = [...selectedGoogleTrends, ...selectedInstagramTrends]

      const response = await seasonalStoryApi.generate({
        store_id: parseInt(storeId),
        store_name: storeName,
        store_type: storeType,
        location: location,
        menu_categories: getMenuCategoriesByStoreType(storeType),
        selected_trends: allSelectedTrends.length > 0 ? allSelectedTrends : undefined
      })

      setResult(response.data)
    } catch (err: any) {
      setError(err.message || '스토리 생성 중 오류가 발생했습니다.')
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
            시즈널 스토리 생성
          </Typography>
          <Typography variant="body1" color="text.secondary">
            날씨, 계절, 시간대, 트렌드를 반영한 감성 추천 문구를 자동 생성합니다
          </Typography>
        </Box>

        {/* 입력 폼 */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            매장 정보 입력
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            매장 정보를 입력하면 현재 상황에 맞는 추천 문구를 생성합니다
          </Typography>

          <Grid container spacing={2}>
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
              <TextField
                fullWidth
                label="지역"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Seoul"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="매장 이름"
                value={storeName}
                onChange={(e) => setStoreName(e.target.value)}
                placeholder="우리 카페"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="매장 타입"
                value={storeType}
                onChange={(e) => setStoreType(e.target.value)}
                placeholder="카페"
              />
            </Grid>
          </Grid>

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleGenerate}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}
            sx={{ mt: 3 }}
          >
            {loading ? '생성 중...' : '스토리 생성하기'}
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
            {/* 생성된 스토리 */}
            <Paper sx={{ p: 3, mb: 3, borderLeft: 4, borderColor: 'primary.main' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AutoAwesome color="primary" />
                <Typography variant="h6">생성된 추천 문구</Typography>
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 'medium', lineHeight: 1.6 }}>
                {result.story}
              </Typography>
            </Paper>

            {/* 컨텍스트 정보 */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              {/* 날씨 */}
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <Cloud fontSize="small" />
                      <Typography variant="subtitle2" fontWeight="bold">
                        날씨 정보
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">날씨</Typography>
                        <Typography variant="body2">{result.context.weather.description}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">온도</Typography>
                        <Typography variant="body2">{result.context.weather.temperature}°C</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">체감</Typography>
                        <Typography variant="body2">{result.context.weather.feels_like}°C</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">습도</Typography>
                        <Typography variant="body2">{result.context.weather.humidity}%</Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* 시간대 */}
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <Schedule fontSize="small" />
                      <Typography variant="subtitle2" fontWeight="bold">
                        시간 정보
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">시간대</Typography>
                        <Typography variant="body2">{result.context.time_info.period_kr}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">시각</Typography>
                        <Typography variant="body2">{result.context.time_info.time_str}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">요일</Typography>
                        <Typography variant="body2">{result.context.time_info.weekday_kr}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2" color="text.secondary">계절</Typography>
                        <Typography variant="body2">
                          {result.context.season === 'spring' && '봄'}
                          {result.context.season === 'summer' && '여름'}
                          {result.context.season === 'autumn' && '가을'}
                          {result.context.season === 'winter' && '겨울'}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* 구글 트렌드 */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TrendingUp fontSize="small" sx={{ color: '#4285F4' }} />
                        <Typography variant="subtitle2" fontWeight="bold">
                          Google 트렌드
                        </Typography>
                      </Box>
                      {selectedGoogleTrends.length > 0 && (
                        <Typography variant="caption" color="primary">
                          {selectedGoogleTrends.length}개 선택됨
                        </Typography>
                      )}
                    </Box>
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                      클릭하여 강조할 트렌드를 선택하세요
                    </Typography>
                    <Box sx={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: 1,
                      maxHeight: '200px',
                      overflowY: 'auto',
                      pr: 1
                    }}>
                      {result.context.google_trends && result.context.google_trends.length > 0 ? (
                        result.context.google_trends.map((trend: string, index: number) => {
                          const isSelected = selectedGoogleTrends.includes(trend)
                          return (
                            <Chip
                              key={index}
                              label={`#${trend}`}
                              size="small"
                              onClick={() => toggleGoogleTrend(trend)}
                              sx={{
                                backgroundColor: isSelected ? '#1967D2' : '#E8F0FE',
                                color: isSelected ? '#FFF' : '#1967D2',
                                fontWeight: isSelected ? 600 : 500,
                                cursor: 'pointer',
                                '&:hover': {
                                  backgroundColor: isSelected ? '#1557B0' : '#D2E3FC',
                                  transform: 'scale(1.05)',
                                  transition: 'all 0.2s'
                                }
                              }}
                            />
                          )
                        })
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          {result.context.google_trends_status?.message || '데이터 없음'}
                        </Typography>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* 인스타그램 트렌드 */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TrendingUp fontSize="small" sx={{ color: '#E4405F' }} />
                        <Typography variant="subtitle2" fontWeight="bold">
                          Instagram 트렌드
                        </Typography>
                      </Box>
                      {selectedInstagramTrends.length > 0 && (
                        <Typography variant="caption" sx={{ color: '#C2185B' }}>
                          {selectedInstagramTrends.length}개 선택됨
                        </Typography>
                      )}
                    </Box>
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                      클릭하여 강조할 트렌드를 선택하세요
                    </Typography>
                    <Box sx={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: 1,
                      maxHeight: '200px',
                      overflowY: 'auto',
                      pr: 1
                    }}>
                      {result.context.instagram_trends && result.context.instagram_trends.length > 0 ? (
                        result.context.instagram_trends.map((trend: string, index: number) => {
                          const isSelected = selectedInstagramTrends.includes(trend)
                          return (
                            <Chip
                              key={index}
                              label={`#${trend}`}
                              size="small"
                              onClick={() => toggleInstagramTrend(trend)}
                              sx={{
                                backgroundColor: isSelected ? '#C2185B' : '#FCE4EC',
                                color: isSelected ? '#FFF' : '#C2185B',
                                fontWeight: isSelected ? 600 : 500,
                                cursor: 'pointer',
                                '&:hover': {
                                  backgroundColor: isSelected ? '#A91649' : '#F8BBD0',
                                  transform: 'scale(1.05)',
                                  transition: 'all 0.2s'
                                }
                              }}
                            />
                          )
                        })
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          {result.context.instagram_trends_status?.message || '데이터 없음'}
                        </Typography>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* 생성 시간 */}
            <Typography variant="body2" color="text.secondary" align="center">
              생성 시간: {result.generation_time?.toFixed(2)}초
            </Typography>

            {/* 선택한 트렌드로 재생성 버튼 */}
            {(selectedGoogleTrends.length > 0 || selectedInstagramTrends.length > 0) && (
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleGenerate}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}
                  sx={{
                    borderWidth: 2,
                    '&:hover': {
                      borderWidth: 2
                    }
                  }}
                >
                  선택한 트렌드로 재생성하기 ({selectedGoogleTrends.length + selectedInstagramTrends.length}개)
                </Button>
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Container>
  )
}

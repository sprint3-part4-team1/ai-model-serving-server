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
import { MenuBook, Spa, LocationOn, Info, LocalFlorist, History } from '@mui/icons-material'
import { seasonalStoryApi } from '@/services/api'

export default function MenuStorytellingPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [menuId, setMenuId] = useState('1')
  const [menuName, setMenuName] = useState('아메리카노')
  const [ingredients, setIngredients] = useState('에티오피아 원두, 정제수')
  const [origin, setOrigin] = useState('에티오피아')
  const [history, setHistory] = useState('')
  const [result, setResult] = useState<any>(null)

  // 샘플 영양 정보
  const nutrition = {
    calories: 10,
    protein_g: 0.5,
    fat_g: 0.1,
    carbs_g: 2,
    sugar_g: 0,
    caffeine_mg: 150
  }

  const handleGenerate = async () => {
    if (!menuName.trim()) {
      setError('메뉴 이름을 입력해주세요')
      return
    }

    try {
      setLoading(true)
      setError(null)

      const ingredientList = ingredients
        .split(',')
        .map((i) => i.trim())
        .filter((i) => i)

      const response = await seasonalStoryApi.generateMenuStorytelling({
        menu_id: parseInt(menuId),
        menu_name: menuName,
        ingredients: ingredientList,
        origin: origin || undefined,
        history: history || undefined
      })

      setResult(response.data)
    } catch (err: any) {
      setError(err.message || '스토리텔링 생성 중 오류가 발생했습니다.')
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
            메뉴 스토리텔링
          </Typography>
          <Typography variant="body1" color="text.secondary">
            메뉴의 재료, 원산지, 역사를 바탕으로 감성적인 스토리를 생성합니다
          </Typography>
        </Box>

        {/* 입력 폼 */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            메뉴 정보 입력
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            메뉴 정보를 입력하면 AI가 감성적인 스토리를 생성합니다
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="메뉴 ID"
                type="number"
                value={menuId}
                onChange={(e) => setMenuId(e.target.value)}
                placeholder="1"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="메뉴 이름"
                value={menuName}
                onChange={(e) => setMenuName(e.target.value)}
                placeholder="아메리카노"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="재료 (쉼표로 구분)"
                value={ingredients}
                onChange={(e) => setIngredients(e.target.value)}
                placeholder="에티오피아 원두, 정제수"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="원산지"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="에티오피아"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="역사/배경"
                value={history}
                onChange={(e) => setHistory(e.target.value)}
                placeholder="9세기 에티오피아에서 시작..."
              />
            </Grid>
          </Grid>

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleGenerate}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <MenuBook />}
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
            {/* 메뉴 정보 */}
            <Paper sx={{ p: 3, mb: 3, borderLeft: 4, borderColor: 'primary.main' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <MenuBook color="primary" />
                <Typography variant="h5">{result.menu_name}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                메뉴 ID: {result.menu_id}
              </Typography>

              {/* 스토리 */}
              <Paper sx={{ p: 3, mb: 3, bgcolor: 'grey.50' }}>
                <Typography variant="h6" sx={{ fontStyle: 'italic', lineHeight: 1.8 }}>
                  {result.storytelling}
                </Typography>
              </Paper>

              {/* 상세 정보 그리드 */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {/* 재료 */}
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                        <LocalFlorist fontSize="small" />
                        <Typography variant="subtitle2" fontWeight="bold">
                          재료
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {ingredients.split(',').map((ingredient, index) => (
                          <Chip
                            key={index}
                            label={ingredient.trim()}
                            size="small"
                            color="success"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* 원산지 */}
                {origin && (
                  <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                          <LocationOn fontSize="small" />
                          <Typography variant="subtitle2" fontWeight="bold">
                            원산지
                          </Typography>
                        </Box>
                        <Typography variant="body2">{origin}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {/* 역사 */}
                {history && (
                  <Grid item xs={12} md={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                          <History fontSize="small" />
                          <Typography variant="subtitle2" fontWeight="bold">
                            역사/배경
                          </Typography>
                        </Box>
                        <Typography variant="body2">{history}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>

              {/* 영양 정보 */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                    영양 성분 (추정치)
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={4} sm={2}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          칼로리
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {nutrition.calories}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          kcal
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4} sm={2}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          단백질
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {nutrition.protein_g}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          g
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4} sm={2}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          지방
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {nutrition.fat_g}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          g
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4} sm={2}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          탄수화물
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {nutrition.carbs_g}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          g
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4} sm={2}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          당분
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {nutrition.sugar_g}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          g
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4} sm={2}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          카페인
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {nutrition.caffeine_mg}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          mg
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Paper>

            {/* 생성 시간 */}
            <Typography variant="body2" color="text.secondary" align="center">
              생성 시각: {new Date(result.generated_at).toLocaleString('ko-KR')}
            </Typography>
          </Box>
        )}
      </Box>
    </Container>
  )
}

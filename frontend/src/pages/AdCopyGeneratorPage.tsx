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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
} from '@mui/material'
import {
  WbSunny,
  Cloud,
  Umbrella,
  ThermostatAuto,
  ContentCopy,
  Refresh,
  TrendingUp,
} from '@mui/icons-material'
import { seasonalStoryApi, adCopyApi } from '@services/api'
import type {
  SeasonalStoryResponse,
  AdCopyRequest,
  AdCopyResponse,
  AdCopyTone,
  AdCopyLength,
} from '@types/index'

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

export default function AdCopyGeneratorPage() {
  const [seasonalStory, setSeasonalStory] = useState<SeasonalStoryResponse | null>(null)
  const [adCopyResult, setAdCopyResult] = useState<AdCopyResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 폼 상태
  const [formData, setFormData] = useState<AdCopyRequest>({
    product_name: '',
    product_description: '',
    tone: 'friendly',
    length: 'short',
    target_audience: '',
    key_message: '',
    platform: 'Instagram',
    num_variations: 3,
  })

  // 시즈널 스토리 로드
  useEffect(() => {
    loadSeasonalStory()
  }, [])

  const loadSeasonalStory = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await seasonalStoryApi.generate({
        store_id: 1,
        store_name: '우리 가게',
        store_type: '소상공인',
        location: 'Seoul',
      })

      setSeasonalStory(response)
    } catch (err: any) {
      setError(err.message || '스토리를 불러올 수 없습니다')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateAdCopy = async () => {
    if (!formData.product_name.trim()) {
      setError('제품/서비스 이름을 입력해주세요')
      return
    }

    try {
      setGenerating(true)
      setError(null)

      // 시즌 정보를 추가 요청사항에 포함
      const contextInfo = seasonalStory
        ? `현재 컨텍스트: ${seasonalStory.data.context.season} 계절, ${seasonalStory.data.context.weather.description}, ${seasonalStory.data.context.weather.temperature}°C, ${seasonalStory.data.context.time_info.period_kr}. 트렌드: ${seasonalStory.data.context.trends.join(', ')}.`
        : ''

      const requestData: AdCopyRequest = {
        ...formData,
        additional_requirements: contextInfo + (formData.additional_requirements || ''),
      }

      const response = await adCopyApi.generate(requestData)
      setAdCopyResult(response)
    } catch (err: any) {
      setError('광고 문구 생성 중 오류가 발생했습니다: ' + err.message)
    } finally {
      setGenerating(false)
    }
  }

  const handleCopyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('클립보드에 복사되었습니다!')
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" mb={3}>
        AI 광고 문구 생성
      </Typography>

      {/* 시즈널 컨텍스트 */}
      <Paper elevation={3} sx={{ p: 3, mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="100px">
            <CircularProgress color="inherit" />
          </Box>
        ) : seasonalStory ? (
          <Box>
            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <Box sx={{ fontSize: 40 }}>
                {getWeatherIcon(seasonalStory.data.context.weather.condition)}
              </Box>
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  현재 상황 분석
                </Typography>
                <Box display="flex" gap={1} alignItems="center" mt={0.5} flexWrap="wrap">
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
                  <Chip
                    size="small"
                    label={seasonalStory.data.context.season}
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                  />
                </Box>
              </Box>
            </Box>

            <Typography variant="body1" sx={{ fontStyle: 'italic', my: 2 }}>
              {seasonalStory.data.story}
            </Typography>

            {seasonalStory.data.context.trends.length > 0 && (
              <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
                <TrendingUp fontSize="small" />
                <Typography variant="body2">현재 트렌드:</Typography>
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

      {/* 입력 폼 */}
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" fontWeight="bold" mb={3}>
          제품/서비스 정보 입력
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              required
              label="제품/서비스 이름"
              placeholder="예: 수제 초콜릿 케이크"
              value={formData.product_name}
              onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="타겟 고객"
              placeholder="예: 20-30대 여성"
              value={formData.target_audience}
              onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="제품/서비스 설명"
              placeholder="제품이나 서비스에 대한 상세 설명을 입력하세요"
              value={formData.product_description}
              onChange={(e) => setFormData({ ...formData, product_description: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>톤/분위기</InputLabel>
              <Select
                value={formData.tone}
                label="톤/분위기"
                onChange={(e) => setFormData({ ...formData, tone: e.target.value as AdCopyTone })}
              >
                <MenuItem value="professional">전문적</MenuItem>
                <MenuItem value="friendly">친근한</MenuItem>
                <MenuItem value="emotional">감성적</MenuItem>
                <MenuItem value="energetic">활기찬</MenuItem>
                <MenuItem value="luxury">고급스러운</MenuItem>
                <MenuItem value="casual">캐주얼한</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>길이</InputLabel>
              <Select
                value={formData.length}
                label="길이"
                onChange={(e) => setFormData({ ...formData, length: e.target.value as AdCopyLength })}
              >
                <MenuItem value="short">짧게 (1-2문장)</MenuItem>
                <MenuItem value="medium">중간 (3-5문장)</MenuItem>
                <MenuItem value="long">길게 (6문장 이상)</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="플랫폼"
              placeholder="예: Instagram, Facebook"
              value={formData.platform}
              onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="핵심 메시지"
              placeholder="강조하고 싶은 핵심 메시지를 입력하세요"
              value={formData.key_message}
              onChange={(e) => setFormData({ ...formData, key_message: e.target.value })}
            />
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => setFormData({
                  product_name: '',
                  product_description: '',
                  tone: 'friendly',
                  length: 'short',
                  target_audience: '',
                  key_message: '',
                  platform: 'Instagram',
                  num_variations: 3,
                })}
              >
                초기화
              </Button>
              <Button
                variant="contained"
                size="large"
                onClick={handleGenerateAdCopy}
                disabled={!formData.product_name.trim() || generating}
              >
                {generating ? <CircularProgress size={24} color="inherit" /> : '광고 문구 생성'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* 에러 표시 */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 생성 결과 */}
      {adCopyResult && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              생성된 광고 문구
            </Typography>
            <Typography variant="body2" color="text.secondary">
              생성 시간: {adCopyResult.generation_time.toFixed(2)}초 | 모델: {adCopyResult.model_used}
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {adCopyResult.variations.map((variation, index) => (
              <Grid item xs={12} key={index}>
                <Card elevation={2}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                      <Typography variant="h6" color="primary">
                        버전 {index + 1}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => handleCopyToClipboard(variation.text)}
                        title="클립보드에 복사"
                      >
                        <ContentCopy fontSize="small" />
                      </IconButton>
                    </Box>

                    {variation.headline && (
                      <>
                        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                          {variation.headline}
                        </Typography>
                        <Divider sx={{ my: 1 }} />
                      </>
                    )}

                    <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-line' }}>
                      {variation.text}
                    </Typography>

                    {variation.hashtags && variation.hashtags.length > 0 && (
                      <Box display="flex" gap={1} flexWrap="wrap" mt={2}>
                        {variation.hashtags.map((tag, idx) => (
                          <Chip key={idx} label={tag} size="small" color="primary" variant="outlined" />
                        ))}
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  )
}

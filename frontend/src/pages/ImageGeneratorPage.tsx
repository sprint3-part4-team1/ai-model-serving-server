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
  CardMedia,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Divider,
} from '@mui/material'
import {
  Download,
  Refresh,
  Image as ImageIcon,
} from '@mui/icons-material'
import { textToImageApi } from '@services/api'
import type { TextToImageRequest, TextToImageResponse, ImageStyle, AspectRatio } from '@types/index'

const IMAGE_STYLES: { value: ImageStyle; label: string; description: string }[] = [
  { value: 'realistic', label: '사실적', description: '실제 사진처럼 자연스러운 이미지' },
  { value: 'artistic', label: '예술적', description: '회화 스타일의 예술적 이미지' },
  { value: 'minimalist', label: '미니멀', description: '깔끔하고 단순한 디자인' },
  { value: 'vintage', label: '빈티지', description: '복고풍의 따뜻한 느낌' },
  { value: 'modern', label: '모던', description: '현대적이고 세련된 스타일' },
  { value: 'colorful', label: '화려한', description: '다채롭고 생동감 있는 색상' },
]

const ASPECT_RATIOS: { value: AspectRatio; label: string }[] = [
  { value: '1:1', label: '정사각형 (1:1)' },
  { value: '4:5', label: '세로 (4:5)' },
  { value: '16:9', label: '가로 (16:9)' },
  { value: '21:9', label: '와이드 (21:9)' },
]

export default function ImageGeneratorPage() {
  const [formData, setFormData] = useState<TextToImageRequest>({
    prompt: '',
    negative_prompt: '',
    style: 'realistic',
    aspect_ratio: '1:1',
    num_inference_steps: 30,
    guidance_scale: 7.5,
    num_images: 1,
  })

  const [result, setResult] = useState<TextToImageResponse | null>(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!formData.prompt.trim()) {
      setError('이미지 설명을 입력해주세요')
      return
    }

    try {
      setGenerating(true)
      setError(null)

      const response = await textToImageApi.generate(formData)
      setResult(response)
    } catch (err: any) {
      setError('이미지 생성 중 오류가 발생했습니다: ' + err.message)
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = (imageUrl: string, index: number) => {
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = `generated-image-${index + 1}.png`
    link.click()
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" mb={3}>
        AI 이미지 생성
      </Typography>

      {/* 입력 폼 */}
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" fontWeight="bold" mb={3}>
          이미지 설정
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              multiline
              rows={3}
              label="이미지 설명 (Prompt)"
              placeholder="예: 나무 테이블 위에 놓인 맛있는 초콜릿 케이크, 따뜻한 조명, 고품질 사진"
              value={formData.prompt}
              onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="제외할 요소 (Negative Prompt)"
              placeholder="예: 저화질, 흐릿한, 왜곡된"
              value={formData.negative_prompt}
              onChange={(e) => setFormData({ ...formData, negative_prompt: e.target.value })}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>스타일</InputLabel>
              <Select
                value={formData.style}
                label="스타일"
                onChange={(e) => setFormData({ ...formData, style: e.target.value as ImageStyle })}
              >
                {IMAGE_STYLES.map((style) => (
                  <MenuItem key={style.value} value={style.value}>
                    {style.label} - {style.description}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>비율</InputLabel>
              <Select
                value={formData.aspect_ratio}
                label="비율"
                onChange={(e) => setFormData({ ...formData, aspect_ratio: e.target.value as AspectRatio })}
              >
                {ASPECT_RATIOS.map((ratio) => (
                  <MenuItem key={ratio.value} value={ratio.value}>
                    {ratio.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography gutterBottom>생성 스텝: {formData.num_inference_steps}</Typography>
            <Slider
              value={formData.num_inference_steps}
              onChange={(_, value) => setFormData({ ...formData, num_inference_steps: value as number })}
              min={20}
              max={50}
              step={5}
              marks
              valueLabelDisplay="auto"
            />
            <Typography variant="caption" color="text.secondary">
              스텝이 많을수록 품질이 높아지지만 시간이 오래 걸립니다
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography gutterBottom>가이던스 스케일: {formData.guidance_scale}</Typography>
            <Slider
              value={formData.guidance_scale}
              onChange={(_, value) => setFormData({ ...formData, guidance_scale: value as number })}
              min={1}
              max={20}
              step={0.5}
              marks
              valueLabelDisplay="auto"
            />
            <Typography variant="caption" color="text.secondary">
              높을수록 프롬프트를 더 정확히 따르지만, 너무 높으면 부자연스러울 수 있습니다
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => setFormData({
                  prompt: '',
                  negative_prompt: '',
                  style: 'realistic',
                  aspect_ratio: '1:1',
                  num_inference_steps: 30,
                  guidance_scale: 7.5,
                  num_images: 1,
                })}
              >
                초기화
              </Button>
              <Button
                variant="contained"
                size="large"
                startIcon={generating ? <CircularProgress size={20} color="inherit" /> : <ImageIcon />}
                onClick={handleGenerate}
                disabled={!formData.prompt.trim() || generating}
              >
                {generating ? '생성 중...' : '이미지 생성'}
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
      {result && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              생성된 이미지
            </Typography>
            <Box display="flex" gap={1} alignItems="center">
              <Chip label={`모델: ${result.model_used}`} size="small" />
              <Chip label={`생성 시간: ${result.generation_time.toFixed(1)}초`} size="small" color="primary" />
            </Box>
          </Box>

          <Grid container spacing={3}>
            {result.images.map((imageUrl, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card elevation={3}>
                  <CardMedia
                    component="img"
                    image={imageUrl}
                    alt={`Generated image ${index + 1}`}
                    sx={{ aspectRatio: result.parameters.width / result.parameters.height }}
                  />
                  <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" color="text.secondary">
                      이미지 #{index + 1}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={() => handleDownload(imageUrl, index)}
                      title="다운로드"
                    >
                      <Download fontSize="small" />
                    </IconButton>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* 생성 정보 */}
          <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              생성 정보
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="text.secondary">
                  <strong>프롬프트:</strong> {result.parameters.prompt}
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" color="text.secondary">
                  <strong>네거티브 프롬프트:</strong> {result.parameters.negative_prompt || '없음'}
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  <strong>스타일:</strong> {result.parameters.style}
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  <strong>해상도:</strong> {result.parameters.width}×{result.parameters.height}
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  <strong>스텝:</strong> {result.parameters.num_inference_steps}
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  <strong>가이던스:</strong> {result.parameters.guidance_scale}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Box>
      )}
    </Container>
  )
}

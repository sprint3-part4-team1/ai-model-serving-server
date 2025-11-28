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
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
} from '@mui/material'
import {
  Upload,
  Download,
  AutoFixHigh,
  DeleteOutline,
} from '@mui/icons-material'
import { backgroundApi } from '@services/api'
import type {
  BackgroundRemoveRequest,
  BackgroundRemoveResponse,
  BackgroundReplaceRequest,
  BackgroundReplaceResponse,
  ImageStyle,
} from '@types/index'

const IMAGE_STYLES: { value: ImageStyle; label: string }[] = [
  { value: 'realistic', label: '사실적' },
  { value: 'artistic', label: '예술적' },
  { value: 'minimalist', label: '미니멀' },
  { value: 'vintage', label: '빈티지' },
  { value: 'modern', label: '모던' },
  { value: 'colorful', label: '화려한' },
]

type TabValue = 'remove' | 'replace'

export default function BackgroundEditorPage() {
  const [tabValue, setTabValue] = useState<TabValue>('remove')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 배경 제거 상태
  const [removeResult, setRemoveResult] = useState<BackgroundRemoveResponse | null>(null)
  const [returnMask, setReturnMask] = useState(false)

  // 배경 교체 상태
  const [replaceFormData, setReplaceFormData] = useState({
    backgroundPrompt: '',
    backgroundStyle: 'realistic' as ImageStyle,
    preserveLighting: true,
  })
  const [replaceResult, setReplaceResult] = useState<BackgroundReplaceResponse | null>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setRemoveResult(null)
      setReplaceResult(null)
      setError(null)
    }
  }

  const handleRemoveBackground = async () => {
    if (!selectedFile) {
      setError('이미지를 먼저 선택해주세요')
      return
    }

    try {
      setProcessing(true)
      setError(null)

      const request: BackgroundRemoveRequest = {
        image_file: selectedFile,
        return_mask: returnMask,
      }

      const response = await backgroundApi.remove(request)
      setRemoveResult(response)
    } catch (err: any) {
      setError('배경 제거 중 오류가 발생했습니다: ' + err.message)
    } finally {
      setProcessing(false)
    }
  }

  const handleReplaceBackground = async () => {
    if (!selectedFile) {
      setError('이미지를 먼저 선택해주세요')
      return
    }

    if (!replaceFormData.backgroundPrompt.trim()) {
      setError('배경 설명을 입력해주세요')
      return
    }

    try {
      setProcessing(true)
      setError(null)

      const request: BackgroundReplaceRequest = {
        image_file: selectedFile,
        background_prompt: replaceFormData.backgroundPrompt,
        background_style: replaceFormData.backgroundStyle,
        preserve_lighting: replaceFormData.preserveLighting,
      }

      const response = await backgroundApi.replace(request)
      setReplaceResult(response)
    } catch (err: any) {
      setError('배경 교체 중 오류가 발생했습니다: ' + err.message)
    } finally {
      setProcessing(false)
    }
  }

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setRemoveResult(null)
    setReplaceResult(null)
    setError(null)
    setReplaceFormData({
      backgroundPrompt: '',
      backgroundStyle: 'realistic',
      preserveLighting: true,
    })
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" mb={3}>
        AI 배경 편집
      </Typography>

      {/* 탭 */}
      <Paper elevation={2} sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, value) => setTabValue(value)}>
          <Tab
            label="배경 제거"
            value="remove"
            icon={<DeleteOutline />}
            iconPosition="start"
          />
          <Tab
            label="배경 교체"
            value="replace"
            icon={<AutoFixHigh />}
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {/* 이미지 업로드 */}
      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" fontWeight="bold" mb={3}>
          이미지 업로드
        </Typography>

        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
          <Button
            variant="contained"
            component="label"
            startIcon={<Upload />}
            size="large"
          >
            이미지 선택
            <input
              type="file"
              hidden
              accept="image/*"
              onChange={handleFileSelect}
            />
          </Button>

          {previewUrl && (
            <Box mt={2} maxWidth="400px" width="100%">
              <Card>
                <CardMedia
                  component="img"
                  image={previewUrl}
                  alt="Preview"
                  sx={{ maxHeight: 400, objectFit: 'contain' }}
                />
              </Card>
              <Typography variant="body2" color="text.secondary" mt={1} textAlign="center">
                {selectedFile?.name}
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {/* 배경 제거 설정 */}
      {tabValue === 'remove' && (
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" fontWeight="bold" mb={3}>
            배경 제거 설정
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={returnMask}
                    onChange={(e) => setReturnMask(e.target.checked)}
                  />
                }
                label="마스크 이미지도 함께 반환"
              />
              <Typography variant="caption" color="text.secondary" display="block" ml={4}>
                배경 제거 영역을 확인할 수 있는 마스크 이미지를 추가로 생성합니다
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Box display="flex" gap={2} justifyContent="flex-end">
                <Button
                  variant="outlined"
                  onClick={handleReset}
                >
                  초기화
                </Button>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={processing ? <CircularProgress size={20} color="inherit" /> : <DeleteOutline />}
                  onClick={handleRemoveBackground}
                  disabled={!selectedFile || processing}
                >
                  {processing ? '처리 중...' : '배경 제거'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* 배경 교체 설정 */}
      {tabValue === 'replace' && (
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" fontWeight="bold" mb={3}>
            배경 교체 설정
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                multiline
                rows={3}
                label="배경 설명"
                placeholder="예: 햇살 가득한 카페 테라스, 따뜻한 자연광, 나무 테이블"
                value={replaceFormData.backgroundPrompt}
                onChange={(e) => setReplaceFormData({ ...replaceFormData, backgroundPrompt: e.target.value })}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>배경 스타일</InputLabel>
                <Select
                  value={replaceFormData.backgroundStyle}
                  label="배경 스타일"
                  onChange={(e) => setReplaceFormData({ ...replaceFormData, backgroundStyle: e.target.value as ImageStyle })}
                >
                  {IMAGE_STYLES.map((style) => (
                    <MenuItem key={style.value} value={style.value}>
                      {style.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={replaceFormData.preserveLighting}
                    onChange={(e) => setReplaceFormData({ ...replaceFormData, preserveLighting: e.target.checked })}
                  />
                }
                label="조명 보존"
              />
              <Typography variant="caption" color="text.secondary" display="block" ml={4}>
                원본 이미지의 조명과 그림자를 최대한 유지합니다
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Box display="flex" gap={2} justifyContent="flex-end">
                <Button
                  variant="outlined"
                  onClick={handleReset}
                >
                  초기화
                </Button>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={processing ? <CircularProgress size={20} color="inherit" /> : <AutoFixHigh />}
                  onClick={handleReplaceBackground}
                  disabled={!selectedFile || !replaceFormData.backgroundPrompt.trim() || processing}
                >
                  {processing ? '처리 중...' : '배경 교체'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* 에러 표시 */}
      {error && (
        <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* 배경 제거 결과 */}
      {removeResult && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              처리 결과
            </Typography>
            <Chip label={`처리 시간: ${removeResult.processing_time.toFixed(2)}초`} color="primary" />
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={returnMask && removeResult.mask_url ? 6 : 12}>
              <Card elevation={3}>
                <CardMedia
                  component="img"
                  image={removeResult.result_url}
                  alt="Background removed"
                />
                <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    배경 제거 결과
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => handleDownload(removeResult.result_url, 'background-removed.png')}
                    title="다운로드"
                  >
                    <Download fontSize="small" />
                  </IconButton>
                </Box>
              </Card>
            </Grid>

            {removeResult.mask_url && (
              <Grid item xs={12} md={6}>
                <Card elevation={3}>
                  <CardMedia
                    component="img"
                    image={removeResult.mask_url}
                    alt="Mask"
                  />
                  <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" color="text.secondary">
                      마스크 이미지
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={() => handleDownload(removeResult.mask_url!, 'mask.png')}
                      title="다운로드"
                    >
                      <Download fontSize="small" />
                    </IconButton>
                  </Box>
                </Card>
              </Grid>
            )}
          </Grid>
        </Box>
      )}

      {/* 배경 교체 결과 */}
      {replaceResult && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              처리 결과
            </Typography>
            <Chip label={`처리 시간: ${replaceResult.processing_time.toFixed(2)}초`} color="primary" />
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card elevation={3}>
                <CardMedia
                  component="img"
                  image={previewUrl || ''}
                  alt="Original"
                />
                <Box p={2}>
                  <Typography variant="body2" color="text.secondary">
                    원본 이미지
                  </Typography>
                </Box>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card elevation={3}>
                <CardMedia
                  component="img"
                  image={replaceResult.result_url}
                  alt="Background replaced"
                />
                <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body2" color="text.secondary">
                    배경 교체 결과
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => handleDownload(replaceResult.result_url, 'background-replaced.png')}
                    title="다운로드"
                  >
                    <Download fontSize="small" />
                  </IconButton>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}
    </Container>
  )
}

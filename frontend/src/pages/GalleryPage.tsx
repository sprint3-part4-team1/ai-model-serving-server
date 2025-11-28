import { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Alert,
  Paper,
} from '@mui/material'
import {
  Delete,
  Download,
  Visibility,
  Article,
  Image as ImageIcon,
  AutoFixHigh,
} from '@mui/icons-material'
import type { HistoryItem } from '@types/index'

type FilterType = 'all' | 'ad-copy' | 'text-to-image' | 'background-remove' | 'background-replace'

const TYPE_LABELS: Record<string, string> = {
  'ad-copy': '광고 문구',
  'text-to-image': '이미지 생성',
  'background-remove': '배경 제거',
  'background-replace': '배경 교체',
}

const TYPE_ICONS: Record<string, JSX.Element> = {
  'ad-copy': <Article />,
  'text-to-image': <ImageIcon />,
  'background-remove': <AutoFixHigh />,
  'background-replace': <AutoFixHigh />,
}

export default function GalleryPage() {
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([])
  const [filterType, setFilterType] = useState<FilterType>('all')
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = () => {
    try {
      const storedHistory = localStorage.getItem('content_history')
      if (storedHistory) {
        const items: HistoryItem[] = JSON.parse(storedHistory)
        setHistoryItems(items.sort((a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        ))
      }
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const filteredItems = filterType === 'all'
    ? historyItems
    : historyItems.filter(item => item.type === filterType)

  const handleDelete = (id: string) => {
    const updatedItems = historyItems.filter(item => item.id !== id)
    setHistoryItems(updatedItems)
    localStorage.setItem('content_history', JSON.stringify(updatedItems))
  }

  const handleClearAll = () => {
    if (window.confirm('모든 히스토리를 삭제하시겠습니까?')) {
      setHistoryItems([])
      localStorage.removeItem('content_history')
    }
  }

  const handleViewDetail = (item: HistoryItem) => {
    setSelectedItem(item)
    setDetailDialogOpen(true)
  }

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
  }

  const renderCard = (item: HistoryItem) => {
    if (item.type === 'ad-copy') {
      const data = item.data as any
      return (
        <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ flexGrow: 1 }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              {TYPE_ICONS[item.type]}
              <Typography variant="h6" component="div">
                {TYPE_LABELS[item.type]}
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {data.variations?.[0]?.text?.substring(0, 100) || '내용 없음'}...
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              <Chip size="small" label={`${data.variations?.length || 0}개 생성`} />
              <Chip size="small" label={data.model_used} color="primary" />
            </Box>
          </CardContent>
          <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              {new Date(item.created_at).toLocaleString('ko-KR')}
            </Typography>
            <Box>
              <IconButton size="small" onClick={() => handleViewDetail(item)}>
                <Visibility fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={() => handleDelete(item.id)} color="error">
                <Delete fontSize="small" />
              </IconButton>
            </Box>
          </CardActions>
        </Card>
      )
    }

    if (item.type === 'text-to-image') {
      const data = item.data as any
      const firstImage = data.images?.[0]
      return (
        <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {firstImage && (
            <CardMedia
              component="img"
              height="200"
              image={firstImage}
              alt="Generated image"
              sx={{ objectFit: 'cover' }}
            />
          )}
          <CardContent sx={{ flexGrow: 1 }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              {TYPE_ICONS[item.type]}
              <Typography variant="h6" component="div">
                {TYPE_LABELS[item.type]}
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" noWrap sx={{ mb: 2 }}>
              {data.parameters?.prompt || '프롬프트 없음'}
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              <Chip size="small" label={`${data.images?.length || 0}개 이미지`} />
              <Chip size="small" label={data.parameters?.style} color="primary" />
            </Box>
          </CardContent>
          <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              {new Date(item.created_at).toLocaleString('ko-KR')}
            </Typography>
            <Box>
              <IconButton size="small" onClick={() => handleViewDetail(item)}>
                <Visibility fontSize="small" />
              </IconButton>
              {firstImage && (
                <IconButton
                  size="small"
                  onClick={() => handleDownload(firstImage, `image-${item.id}.png`)}
                >
                  <Download fontSize="small" />
                </IconButton>
              )}
              <IconButton size="small" onClick={() => handleDelete(item.id)} color="error">
                <Delete fontSize="small" />
              </IconButton>
            </Box>
          </CardActions>
        </Card>
      )
    }

    if (item.type === 'background-remove' || item.type === 'background-replace') {
      const data = item.data as any
      return (
        <Card elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {data.result_url && (
            <CardMedia
              component="img"
              height="200"
              image={data.result_url}
              alt="Processed image"
              sx={{ objectFit: 'cover' }}
            />
          )}
          <CardContent sx={{ flexGrow: 1 }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              {TYPE_ICONS[item.type]}
              <Typography variant="h6" component="div">
                {TYPE_LABELS[item.type]}
              </Typography>
            </Box>
            <Box display="flex" gap={1} flexWrap="wrap">
              <Chip size="small" label={`${data.processing_time?.toFixed(1)}초`} color="primary" />
            </Box>
          </CardContent>
          <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              {new Date(item.created_at).toLocaleString('ko-KR')}
            </Typography>
            <Box>
              <IconButton size="small" onClick={() => handleViewDetail(item)}>
                <Visibility fontSize="small" />
              </IconButton>
              {data.result_url && (
                <IconButton
                  size="small"
                  onClick={() => handleDownload(data.result_url, `processed-${item.id}.png`)}
                >
                  <Download fontSize="small" />
                </IconButton>
              )}
              <IconButton size="small" onClick={() => handleDelete(item.id)} color="error">
                <Delete fontSize="small" />
              </IconButton>
            </Box>
          </CardActions>
        </Card>
      )
    }

    return null
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          갤러리
        </Typography>
        <Button
          variant="outlined"
          color="error"
          onClick={handleClearAll}
          disabled={historyItems.length === 0}
        >
          모두 삭제
        </Button>
      </Box>

      {/* 필터 탭 */}
      <Paper elevation={2} sx={{ mb: 4 }}>
        <Tabs
          value={filterType}
          onChange={(_, value) => setFilterType(value)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label={`전체 (${historyItems.length})`} value="all" />
          <Tab
            label={`광고 문구 (${historyItems.filter(i => i.type === 'ad-copy').length})`}
            value="ad-copy"
          />
          <Tab
            label={`이미지 생성 (${historyItems.filter(i => i.type === 'text-to-image').length})`}
            value="text-to-image"
          />
          <Tab
            label={`배경 제거 (${historyItems.filter(i => i.type === 'background-remove').length})`}
            value="background-remove"
          />
          <Tab
            label={`배경 교체 (${historyItems.filter(i => i.type === 'background-replace').length})`}
            value="background-replace"
          />
        </Tabs>
      </Paper>

      {/* 히스토리 항목 */}
      {filteredItems.length === 0 ? (
        <Alert severity="info">
          {filterType === 'all'
            ? '생성된 콘텐츠가 없습니다. 콘텐츠를 생성하면 여기에 표시됩니다.'
            : '해당 유형의 콘텐츠가 없습니다.'}
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {filteredItems.map((item) => (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
              {renderCard(item)}
            </Grid>
          ))}
        </Grid>
      )}

      {/* 상세 정보 다이얼로그 */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedItem && (
            <Box display="flex" alignItems="center" gap={1}>
              {TYPE_ICONS[selectedItem.type]}
              {TYPE_LABELS[selectedItem.type]} 상세 정보
            </Box>
          )}
        </DialogTitle>
        <DialogContent dividers>
          {selectedItem && (
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                생성 일시: {new Date(selectedItem.created_at).toLocaleString('ko-KR')}
              </Typography>
              <Box mt={2}>
                <pre style={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  backgroundColor: '#f5f5f5',
                  padding: '16px',
                  borderRadius: '4px',
                  maxHeight: '400px',
                  overflow: 'auto',
                }}>
                  {JSON.stringify(selectedItem.data, null, 2)}
                </pre>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>
            닫기
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

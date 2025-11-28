import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  CardMedia,
  Container,
} from '@mui/material'
import {
  Article as ArticleIcon,
  Image as ImageIcon,
  AutoFixHigh as AutoFixHighIcon,
} from '@mui/icons-material'

interface FeatureCard {
  title: string
  description: string
  path: string
  icon: JSX.Element
  color: string
}

const features: FeatureCard[] = [
  {
    title: '광고 문구 생성',
    description: 'GPT-4를 활용한 전문적인 광고 문구 자동 생성. 6가지 톤과 3가지 길이 선택 가능.',
    path: '/ad-copy',
    icon: <ArticleIcon sx={{ fontSize: 60 }} />,
    color: '#1976d2',
  },
  {
    title: '이미지 생성',
    description: 'Stable Diffusion XL로 고품질 제품 이미지 생성. 6가지 스타일 프리셋 제공.',
    path: '/image-generator',
    icon: <ImageIcon sx={{ fontSize: 60 }} />,
    color: '#9c27b0',
  },
  {
    title: '배경 편집',
    description: 'AI 기반 배경 제거 및 교체. 제품 이미지를 다양한 배경에 합성.',
    path: '/background-editor',
    icon: <AutoFixHighIcon sx={{ fontSize: 60 }} />,
    color: '#2e7d32',
  },
]

export default function HomePage() {
  const navigate = useNavigate()

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* 헤더 */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h3" component="h1" gutterBottom fontWeight={700}>
            소상공인 광고 콘텐츠 생성 서비스
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
            AI를 활용하여 전문적인 광고 콘텐츠를 쉽고 빠르게 제작하세요
          </Typography>
        </Box>

        {/* 기능 카드 */}
        <Grid container spacing={4}>
          {features.map((feature) => (
            <Grid item xs={12} md={4} key={feature.path}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: 6,
                  },
                }}
              >
                <CardActionArea
                  onClick={() => navigate(feature.path)}
                  sx={{ flexGrow: 1 }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      height: 180,
                      bgcolor: feature.color,
                      color: 'white',
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <CardContent>
                    <Typography gutterBottom variant="h5" component="h2" fontWeight={600}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* 안내 섹션 */}
        <Box sx={{ mt: 8, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom fontWeight={600}>
            주요 특징
          </Typography>
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" color="primary" fontWeight={600}>
                고성능 AI 모델
              </Typography>
              <Typography color="text.secondary">
                GPT-4와 Stable Diffusion XL을 활용한 최고 품질의 콘텐츠 생성
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" color="primary" fontWeight={600}>
                빠른 처리 속도
              </Typography>
              <Typography color="text.secondary">
                최적화된 시스템으로 2-30초 내 결과 제공
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" color="primary" fontWeight={600}>
                쉬운 사용
              </Typography>
              <Typography color="text.secondary">
                전문 지식 없이도 직관적인 인터페이스로 쉽게 제작
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  )
}

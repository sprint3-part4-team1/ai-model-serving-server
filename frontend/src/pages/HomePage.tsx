import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Container,
} from '@mui/material'
import {
  Store as StoreIcon,
  AddBox as AddBoxIcon,
  Restaurant as RestaurantIcon,
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
    title: '매장 생성',
    description: '매장 정보를 등록하고 관리합니다. 매장 이름, 주소, 영업 시간 등을 설정할 수 있습니다.',
    path: '/store-management',
    icon: <StoreIcon sx={{ fontSize: 60 }} />,
    color: '#1976d2',
  },
  {
    title: '메뉴판 생성',
    description: 'AI가 자동으로 메뉴 설명과 이미지를 생성합니다. 메뉴 카테고리와 아이템을 입력하면 전문적인 메뉴판이 완성됩니다.',
    path: '/menu-generation',
    icon: <AddBoxIcon sx={{ fontSize: 60 }} />,
    color: '#9c27b0',
  },
  {
    title: 'AI 메뉴판',
    description: '생성된 메뉴판을 확인하고 관리합니다. OCR 기능으로 기존 메뉴판을 업데이트할 수도 있습니다.',
    path: '/menu-board',
    icon: <RestaurantIcon sx={{ fontSize: 60 }} />,
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
            AI 메뉴판 생성 서비스
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
            매장을 등록하고 AI가 자동으로 메뉴판을 생성해드립니다
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
                간편한 매장 관리
              </Typography>
              <Typography color="text.secondary">
                매장 정보를 한 번만 등록하면 언제든지 메뉴판을 생성하고 관리할 수 있습니다
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" color="primary" fontWeight={600}>
                AI 자동 생성
              </Typography>
              <Typography color="text.secondary">
                메뉴 이름만 입력하면 AI가 자동으로 설명과 이미지를 생성해드립니다
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" color="primary" fontWeight={600}>
                전문적인 결과
              </Typography>
              <Typography color="text.secondary">
                GPT-4와 Stable Diffusion을 활용한 고품질 메뉴 설명과 이미지
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  )
}

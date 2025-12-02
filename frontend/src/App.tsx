import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from '@components/layout/Layout'
import HomePage from '@pages/HomePage'
import AdCopyGeneratorPage from '@pages/AdCopyGeneratorPage'
import ImageGeneratorPage from '@pages/ImageGeneratorPage'
import BackgroundEditorPage from '@pages/BackgroundEditorPage'
import GalleryPage from '@pages/GalleryPage'
import MenuBoardPage from '@pages/MenuBoardPage'
import SeasonalStoryPage from '@pages/SeasonalStoryPage'
import MenuRecommendationPage from '@pages/MenuRecommendationPage'
import MenuStorytellingPage from '@pages/MenuStorytellingPage'
import MenuGenerationPage from '@pages/MenuGenerationPage'
import StoreManagementPage from '@pages/StoreManagementPage'
import CustomerMenuPage from '@pages/CustomerMenuPage'
import CustomerMenuListPage from '@pages/CustomerMenuListPage'
import NutritionStorytellingPage from '@pages/NutritionStorytellingPage'

function App() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Routes>
        {/* 고객용 메뉴판 (Layout 없음) */}
        <Route path="/menu/:storeId" element={<CustomerMenuPage />} />

        {/* 관리자 페이지 (Layout 포함) */}
        <Route path="/" element={<Layout />}>
          <Route path="customer-menu" element={<CustomerMenuListPage />} />
          <Route index element={<HomePage />} />
          <Route path="store-management" element={<StoreManagementPage />} />
          <Route path="menu-generation" element={<MenuGenerationPage />} />
          <Route path="menu-board/:storeId" element={<MenuBoardPage />} />
          <Route path="nutrition-storytelling" element={<NutritionStorytellingPage />} />
          <Route path="ad-copy" element={<AdCopyGeneratorPage />} />
          <Route path="image-generator" element={<ImageGeneratorPage />} />
          <Route path="background-editor" element={<BackgroundEditorPage />} />
          <Route path="gallery" element={<GalleryPage />} />
          <Route path="seasonal-story" element={<SeasonalStoryPage />} />
          <Route path="menu-recommendation" element={<MenuRecommendationPage />} />
          <Route path="menu-storytelling" element={<MenuStorytellingPage />} />
        </Route>
      </Routes>
    </Box>
  )
}

export default App

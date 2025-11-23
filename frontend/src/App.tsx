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

function App() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="ad-copy" element={<AdCopyGeneratorPage />} />
          <Route path="image-generator" element={<ImageGeneratorPage />} />
          <Route path="background-editor" element={<BackgroundEditorPage />} />
          <Route path="gallery" element={<GalleryPage />} />
          <Route path="menu-board" element={<MenuBoardPage />} />
          <Route path="seasonal-story" element={<SeasonalStoryPage />} />
          <Route path="menu-recommendation" element={<MenuRecommendationPage />} />
          <Route path="menu-storytelling" element={<MenuStorytellingPage />} />
        </Route>
      </Routes>
    </Box>
  )
}

export default App

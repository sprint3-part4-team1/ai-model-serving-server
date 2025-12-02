// API 요청/응답 타입 정의

// ============ 광고 문구 생성 ============
export type AdCopyTone =
  | 'professional'
  | 'friendly'
  | 'emotional'
  | 'energetic'
  | 'luxury'
  | 'casual'

export type AdCopyLength = 'short' | 'medium' | 'long'

export interface AdCopyRequest {
  product_name: string
  product_description?: string
  tone: AdCopyTone
  length: AdCopyLength
  target_audience?: string
  platform?: string
  keywords?: string[]
  num_variations?: number
  image_url?: string
}

export interface AdCopyVariation {
  text: string
  headline?: string
  hashtags?: string[]
}

export interface AdCopyResponse {
  success: boolean
  generation_id: string
  variations: AdCopyVariation[]
  model_used: string
  generation_time: number
}

// ============ 텍스트→이미지 생성 ============
export type ImageStyle =
  | 'realistic'
  | 'artistic'
  | 'minimalist'
  | 'vintage'
  | 'modern'
  | 'colorful'

export type AspectRatio = '1:1' | '4:5' | '16:9' | '21:9'

export interface TextToImageRequest {
  prompt: string
  negative_prompt?: string
  style?: ImageStyle
  aspect_ratio?: AspectRatio
  num_inference_steps?: number
  guidance_scale?: number
  num_images?: number
  seed?: number
}

export interface TextToImageResponse {
  generation_id: string
  images: string[]
  model_used: string
  parameters: {
    prompt: string
    negative_prompt: string
    style: ImageStyle
    width: number
    height: number
    num_inference_steps: number
    guidance_scale: number
    seed: number
  }
  generation_time: number
  created_at: string
}

// ============ 배경 처리 ============
export interface BackgroundRemoveRequest {
  image_url?: string
  image_file?: File
  return_mask?: boolean
}

export interface BackgroundRemoveResponse {
  result_url: string
  mask_url?: string
  processing_time: number
  created_at: string
}

export interface BackgroundReplaceRequest {
  image_url?: string
  image_file?: File
  background_prompt: string
  background_style?: ImageStyle
  preserve_lighting?: boolean
}

export interface BackgroundReplaceResponse {
  result_url: string
  processing_time: number
  created_at: string
}

// ============ 공통 타입 ============
export interface ApiError {
  detail: string
  status_code: number
}

export interface StylePreset {
  name: ImageStyle
  display_name: string
  description: string
  example_prompt: string
}

export interface AspectRatioOption {
  ratio: AspectRatio
  display_name: string
  width: number
  height: number
}

// ============ 시즈널 스토리 ============
export interface SeasonalStoryRequest {
  store_id?: number
  store_name?: string
  store_type: string
  location: string
  latitude?: number
  longitude?: number
  menu_categories?: string[]
}

export interface WeatherInfo {
  condition: string
  description: string
  temperature: number
  feels_like: number
  humidity: number
  wind_speed: number
}

export interface TimeInfo {
  period: string
  period_kr: string
  hour: number
  minute: number
  time_str: string
  date: string
  weekday: string
  weekday_kr: string
}

export interface ContextInfo {
  weather: WeatherInfo
  season: string
  time_info: TimeInfo
  trends: string[]
  location: string
  timestamp: string
}

export interface SeasonalStoryResponse {
  success: boolean
  data: {
    story: string
    context: {
      weather: WeatherInfo
      season: string
      time_info: TimeInfo
      trends: string[]
    }
    store_info: {
      store_id?: number
      store_name?: string
      store_type: string
      location: string
    }
    generated_at: string
  }
}

export interface MenuStorytellingRequest {
  menu_id?: number
  menu_name: string
  ingredients: string[]
  origin?: string
  history?: string
}

export interface MenuStorytellingResponse {
  success: boolean
  data: {
    storytelling: string
    menu_id?: number
    menu_name: string
    generated_at: string
  }
}

export interface MenuFilterRequest {
  query: string
  menus: MenuItem[]
}

export interface MenuFilterResponse {
  success: boolean
  data: {
    filtered_menus: MenuItem[]
    explanation: string
  }
}

export interface MenuItem {
  id: number
  name: string
  category: string
  price: number
  description?: string
  image_url?: string
  ingredients?: string[]
  origin?: string
  history?: string
}

// ============ 메뉴판 생성 ============
export interface MenuItemCreate {
  name: string
  price?: number
  image_url?: string
  description?: string
  ingredients?: string[]
}

export interface MenuCategoryCreate {
  category_name: string
  category_description?: string
  items: MenuItemCreate[]
}

export interface MenuGenerationRequest {
  store_id: number
  categories: MenuCategoryCreate[]
  auto_generate_images?: boolean
  auto_generate_descriptions?: boolean
  image_style?: string
}

export interface GeneratedMenuItem {
  id: number
  name: string
  description?: string
  price?: number
  image_url?: string
  is_ai_generated_image: boolean
  is_ai_generated_description: boolean
}

export interface GeneratedMenuCategory {
  id: number
  name: string
  description?: string
  items: GeneratedMenuItem[]
}

export interface MenuGenerationResponse {
  success: boolean
  data: {
    categories: GeneratedMenuCategory[]
    total_categories: number
    total_items: number
    generation_time: number
  }
}

// ============ 영양소 분석 & 스토리텔링 ============
export interface NutritionAnalyzeRequest {
  store_id: number
  batch_size?: number
}

export interface NutritionAnalyzeResponse {
  success: boolean
  store_id: number
  message: string
  total_items?: number
}

export interface NutritionEstimate {
  calories?: number
  sugar_g?: number
  caffeine_mg?: number
  protein_g?: number
  fat_g?: number
  carbs_g?: number
  confidence: number
}

export interface MenuItemWithNutrition extends MenuItem {
  nutrition?: NutritionEstimate
}

export interface NutritionStorytellingRequest {
  menu_id: number
  include_health_benefits?: boolean
}

export interface NutritionStorytellingResponse {
  success: boolean
  data: {
    menu_id: number
    menu_name: string
    nutrition: NutritionEstimate
    storytelling: string
    health_benefits?: string[]
    generated_at: string
  }
}

// ============ UI 상태 관리 ============
export interface GenerationState {
  isLoading: boolean
  progress: number
  error: string | null
}

export interface HistoryItem {
  id: string
  type: 'ad-copy' | 'text-to-image' | 'background-remove' | 'background-replace'
  created_at: string
  data: AdCopyResponse | TextToImageResponse | BackgroundRemoveResponse | BackgroundReplaceResponse
}

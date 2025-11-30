import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  AdCopyRequest,
  AdCopyResponse,
  TextToImageRequest,
  TextToImageResponse,
  BackgroundRemoveRequest,
  BackgroundRemoveResponse,
  BackgroundReplaceRequest,
  BackgroundReplaceResponse,
  StylePreset,
  AspectRatioOption,
  ApiError,
  SeasonalStoryRequest,
  SeasonalStoryResponse,
  MenuStorytellingRequest,
  MenuStorytellingResponse,
  ContextInfo,
  MenuFilterRequest,
  MenuFilterResponse,
  MenuGenerationRequest,
  MenuGenerationResponse,
} from '@types/index'

// Axios 인스턴스 생성
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://34.28.223.101:9091',
  timeout: 300000, // 5분 (이미지 생성은 시간이 오래 걸릴 수 있음)
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터: 로깅
api.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터: 에러 처리
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.url} - ${response.status}`)
    return response
  },
  (error: AxiosError<ApiError>) => {
    console.error('[API Response Error]', error)

    if (error.response) {
      // 서버가 에러 응답을 반환한 경우
      const errorMessage = error.response.data?.detail || 'An error occurred'
      return Promise.reject(new Error(errorMessage))
    } else if (error.request) {
      // 요청은 보냈지만 응답을 받지 못한 경우
      return Promise.reject(new Error('No response from server'))
    } else {
      // 요청 설정 중 에러가 발생한 경우
      return Promise.reject(new Error(error.message))
    }
  }
)

// ============ 광고 문구 생성 API ============
export const adCopyApi = {
  /**
   * 광고 문구 생성
   */
  async generate(request: AdCopyRequest): Promise<AdCopyResponse> {
    const { data } = await api.post<AdCopyResponse>('/api/v1/ad-copy/generate', request)
    return data
  },

  /**
   * 광고 문구 예시 조회
   */
  async getExamples(): Promise<AdCopyResponse[]> {
    const { data } = await api.get<AdCopyResponse[]>('/api/v1/ad-copy/examples')
    return data
  },

  /**
   * 헬스 체크
   */
  async health(): Promise<{ status: string }> {
    const { data } = await api.get('/api/v1/ad-copy/health')
    return data
  },
}

// ============ 텍스트→이미지 생성 API ============
export const textToImageApi = {
  /**
   * 텍스트→이미지 생성
   */
  async generate(request: TextToImageRequest): Promise<TextToImageResponse> {
    const { data } = await api.post<TextToImageResponse>(
      '/api/v1/text-to-image/generate',
      request
    )

    // 상대 경로 이미지 URL을 절대 경로로 변환
    const baseURL = import.meta.env.VITE_API_URL || 'http://34.28.223.101:9091'
    if (data.images) {
      data.images = data.images.map(url => {
        if (url.startsWith('/')) {
          return `${baseURL}${url}`
        }
        return url
      })
    }

    return data
  },

  /**
   * 스타일 프리셋 목록 조회
   */
  async getStyles(): Promise<StylePreset[]> {
    const { data } = await api.get<StylePreset[]>('/api/v1/text-to-image/styles')
    return data
  },

  /**
   * 종횡비 목록 조회
   */
  async getAspectRatios(): Promise<AspectRatioOption[]> {
    const { data } = await api.get<AspectRatioOption[]>('/api/v1/text-to-image/aspect-ratios')
    return data
  },

  /**
   * 예시 조회
   */
  async getExamples(): Promise<TextToImageResponse[]> {
    const { data } = await api.get<TextToImageResponse[]>('/api/v1/text-to-image/examples')
    return data
  },

  /**
   * 헬스 체크
   */
  async health(): Promise<{ status: string }> {
    const { data } = await api.get('/api/v1/text-to-image/health')
    return data
  },
}

// ============ 배경 처리 API ============
export const backgroundApi = {
  /**
   * 배경 제거
   */
  async remove(request: BackgroundRemoveRequest): Promise<BackgroundRemoveResponse> {
    const formData = new FormData()

    if (request.image_file) {
      formData.append('image_file', request.image_file)
    }
    if (request.image_url) {
      formData.append('image_url', request.image_url)
    }
    if (request.return_mask !== undefined) {
      formData.append('return_mask', String(request.return_mask))
    }

    const { data } = await api.post<BackgroundRemoveResponse>(
      '/api/v1/background/remove',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return data
  },

  /**
   * 배경 교체
   */
  async replace(request: BackgroundReplaceRequest): Promise<BackgroundReplaceResponse> {
    const formData = new FormData()

    if (request.image_file) {
      formData.append('image_file', request.image_file)
    }
    if (request.image_url) {
      formData.append('image_url', request.image_url)
    }
    formData.append('background_prompt', request.background_prompt)
    if (request.background_style) {
      formData.append('background_style', request.background_style)
    }
    if (request.preserve_lighting !== undefined) {
      formData.append('preserve_lighting', String(request.preserve_lighting))
    }

    const { data } = await api.post<BackgroundReplaceResponse>(
      '/api/v1/background/replace',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return data
  },

  /**
   * 예시 조회
   */
  async getExamples(): Promise<any[]> {
    const { data } = await api.get('/api/v1/background/examples')
    return data
  },

  /**
   * 헬스 체크
   */
  async health(): Promise<{ status: string }> {
    const { data } = await api.get('/api/v1/background/health')
    return data
  },
}

// ============ 시스템 API ============
export const systemApi = {
  /**
   * 전체 헬스 체크
   */
  async health(): Promise<{ status: string; timestamp: string }> {
    const { data } = await api.get('/health')
    return data
  },
}

// ============ 시즈널 스토리 API ============
export const seasonalStoryApi = {
  /**
   * 시즈널 스토리 생성
   */
  async generate(request: SeasonalStoryRequest): Promise<SeasonalStoryResponse> {
    const { data } = await api.post<SeasonalStoryResponse>(
      '/api/v1/seasonal-story/generate',
      request
    )
    return data
  },

  /**
   * 현재 컨텍스트 정보 조회
   */
  async getContext(location: string = 'Seoul', lat?: number, lon?: number): Promise<{ success: boolean; data: ContextInfo }> {
    const params: any = { location }
    if (lat !== undefined) params.lat = lat
    if (lon !== undefined) params.lon = lon

    const { data } = await api.get('/api/v1/seasonal-story/context', { params })
    return data
  },

  /**
   * 메뉴 스토리텔링 생성
   */
  async generateMenuStorytelling(request: MenuStorytellingRequest): Promise<MenuStorytellingResponse> {
    const { data } = await api.post<MenuStorytellingResponse>(
      '/api/v1/seasonal-story/menu-storytelling',
      request
    )
    return data
  },

  /**
   * 헬스 체크
   */
  async health(): Promise<{ success: boolean; data: { status: string } }> {
    const { data } = await api.get('/api/v1/seasonal-story/health')
    return data
  },
}

// ============ 메뉴 필터링 API ============
export const menuApi = {
  /**
   * AI 기반 메뉴 필터링/정렬
   */
  async filterMenus(request: MenuFilterRequest): Promise<MenuFilterResponse> {
    const { data } = await api.post<MenuFilterResponse>(
      '/api/v1/menu/filter',
      request
    )
    return data
  },

  /**
   * 매장별 메뉴 조회
   */
  async getStoreMenus(storeId: number): Promise<{
    success: boolean
    data: {
      store_id: number
      categories: Array<{
        id: number
        name: string
        description?: string
        items: Array<{
          id: number
          name: string
          description?: string
          price?: number
          image_url?: string
          is_available: boolean
        }>
      }>
    }
  }> {
    const { data } = await api.get(`/api/v1/menu/store/${storeId}`)

    // 상대 경로 이미지 URL을 절대 경로로 변환
    const baseURL = import.meta.env.VITE_API_URL || 'http://34.28.223.101:9091'
    if (data.data?.categories) {
      data.data.categories.forEach(category => {
        category.items?.forEach(item => {
          if (item.image_url && item.image_url.startsWith('/')) {
            item.image_url = `${baseURL}${item.image_url}`
          }
        })
      })
    }

    return data
  },
}

// ============ 매장 관리 API ============
export const storeApi = {
  /**
   * 매장 생성
   */
  async createStore(request: {
    name: string
    address?: string
    phone?: string
    open_time?: string
    close_time?: string
  }): Promise<{
    success: boolean
    data: {
      id: number
      name: string
      address?: string
      phone?: string
      open_time?: string
      close_time?: string
      created_at: string
      updated_at: string
    }
  }> {
    const { data } = await api.post('/api/v1/menu/store', request)
    return data
  },

  /**
   * 전체 매장 목록 조회
   */
  async getStores(): Promise<{
    success: boolean
    data: {
      stores: Array<{
        id: number
        name: string
        address?: string
        phone?: string
        open_time?: string
        close_time?: string
        created_at: string
        updated_at: string
      }>
      total: number
    }
  }> {
    const { data } = await api.get('/api/v1/menu/stores')
    return data
  },

  /**
   * 특정 매장 조회
   */
  async getStore(storeId: number): Promise<{
    success: boolean
    data: {
      id: number
      name: string
      address?: string
      phone?: string
      open_time?: string
      close_time?: string
      created_at: string
      updated_at: string
    }
  }> {
    const { data } = await api.get(`/api/v1/menu/store/${storeId}`)
    return data
  },

  /**
   * 매장 정보 수정
   */
  async updateStore(storeId: number, request: {
    name?: string
    address?: string
    phone?: string
    open_time?: string
    close_time?: string
  }): Promise<{
    success: boolean
    data: {
      id: number
      name: string
      address?: string
      phone?: string
      open_time?: string
      close_time?: string
      created_at: string
      updated_at: string
    }
  }> {
    const { data } = await api.put(`/api/v1/menu/store/${storeId}`, request)
    return data
  },

  /**
   * 매장 삭제
   */
  async deleteStore(storeId: number): Promise<{
    success: boolean
    data: {
      message: string
    }
  }> {
    const { data } = await api.delete(`/api/v1/menu/store/${storeId}`)
    return data
  },
}

// ============ 메뉴판 생성 API ============
export const menuGenerationApi = {
  /**
   * AI 기반 메뉴판 생성
   */
  async generate(request: MenuGenerationRequest): Promise<MenuGenerationResponse> {
    const { data } = await api.post<MenuGenerationResponse>(
      '/api/v1/menu-generation/generate',
      request
    )

    // 상대 경로 이미지 URL을 절대 경로로 변환
    const baseURL = import.meta.env.VITE_API_URL || 'http://34.28.223.101:9091'
    if (data.data?.categories) {
      data.data.categories.forEach(category => {
        category.items?.forEach(item => {
          if (item.image_url && item.image_url.startsWith('/')) {
            item.image_url = `${baseURL}${item.image_url}`
          }
        })
      })
    }

    return data
  },

  /**
   * 헬스 체크
   */
  async health(): Promise<{ success: boolean; data: { status: string } }> {
    const { data } = await api.get('/api/v1/menu-generation/health')
    return data
  },

  /**
   * 메뉴 아이템 업데이트
   */
  async updateMenuItem(itemId: number, updates: {
    name?: string
    description?: string
    price?: number
    image_url?: string
  }): Promise<{ success: boolean; data: any }> {
    const { data } = await api.put(`/api/v1/menu/item/${itemId}`, updates)
    return data
  },

  /**
   * 메뉴 이미지 직접 업로드
   */
  async uploadMenuImage(itemId: number, file: File): Promise<{ success: boolean; data: any }> {
    const formData = new FormData()
    formData.append('file', file)

    const { data } = await api.post(`/api/v1/menu/item/${itemId}/upload-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },
}

export default api

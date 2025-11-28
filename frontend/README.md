# 프론트엔드 - React + TypeScript + Material-UI

소상공인 광고 콘텐츠 생성 서비스의 프론트엔드 애플리케이션입니다.

## 🚀 기술 스택

### 핵심 프레임워크
- **React 18** - 최신 React 성능 최적화
- **TypeScript** - 타입 안정성
- **Vite** - 초고속 빌드 도구 (Webpack 대비 10-100배 빠름)

### UI 라이브러리
- **Material-UI (MUI) v5** - 전문적인 디자인 시스템
- **@mui/icons-material** - 아이콘 세트
- **Emotion** - CSS-in-JS 스타일링

### 상태 관리 & API
- **Zustand** - 가볍고 빠른 상태 관리 (Redux보다 간단)
- **Axios** - HTTP 클라이언트
- **React Router v6** - 라우팅

### 개발 도구
- **ESLint** - 코드 품질
- **TypeScript Compiler** - 타입 체크

## 📁 프로젝트 구조

```
frontend/
├── public/                 # 정적 파일
│   └── vite.svg
├── src/
│   ├── components/         # 재사용 컴포넌트
│   │   └── layout/
│   │       └── Layout.tsx  # 메인 레이아웃
│   ├── pages/              # 페이지 컴포넌트
│   │   ├── HomePage.tsx
│   │   ├── AdCopyGeneratorPage.tsx
│   │   ├── ImageGeneratorPage.tsx
│   │   ├── BackgroundEditorPage.tsx
│   │   └── GalleryPage.tsx
│   ├── services/           # API 서비스
│   │   └── api.ts          # Axios 설정 & API 함수
│   ├── store/              # 상태 관리
│   │   └── useGenerationStore.ts
│   ├── types/              # TypeScript 타입 정의
│   │   └── index.ts
│   ├── utils/              # 유틸리티 함수
│   ├── App.tsx             # 메인 앱 컴포넌트
│   ├── main.tsx            # 진입점
│   ├── theme.ts            # MUI 테마 설정
│   └── index.css           # 글로벌 스타일
├── index.html              # HTML 템플릿
├── package.json            # 의존성
├── tsconfig.json           # TypeScript 설정
├── vite.config.ts          # Vite 설정
└── .eslintrc.cjs           # ESLint 설정
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 환경 변수 설정

`.env` 파일이 이미 생성되어 있습니다:

```env
VITE_API_URL=http://localhost:8000
```

### 3. 개발 서버 실행

```bash
npm run dev
```

서버가 실행되면:
- 프론트엔드: http://localhost:3000
- API 프록시: http://localhost:3000/api → http://localhost:8000/api

### 4. 빌드

```bash
# TypeScript 타입 체크
npm run type-check

# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

## 📖 주요 기능

### 1. 라우팅 (React Router v6)

- `/` - 홈페이지
- `/ad-copy` - 광고 문구 생성
- `/image-generator` - 이미지 생성
- `/background-editor` - 배경 편집
- `/gallery` - 갤러리

### 2. API 통합 (Axios)

**서비스 파일**: `src/services/api.ts`

```typescript
import { adCopyApi, textToImageApi, backgroundApi } from '@services/api'

// 광고 문구 생성
const result = await adCopyApi.generate({
  product_name: '초콜릿 케이크',
  tone: 'emotional',
  length: 'short',
})

// 이미지 생성
const images = await textToImageApi.generate({
  prompt: 'chocolate cake on table',
  style: 'realistic',
})

// 배경 제거
const result = await backgroundApi.remove({
  image_file: file,
})
```

### 3. 상태 관리 (Zustand)

**스토어**: `src/store/useGenerationStore.ts`

```typescript
import { useGenerationStore } from '@store/useGenerationStore'

function MyComponent() {
  const { isLoading, setLoading, addToHistory } = useGenerationStore()

  const handleGenerate = async () => {
    setLoading(true)
    // API 호출...
    setLoading(false)
  }
}
```

### 4. 타입 시스템 (TypeScript)

**타입 정의**: `src/types/index.ts`

```typescript
import type {
  AdCopyRequest,
  AdCopyResponse,
  TextToImageRequest,
  TextToImageResponse,
} from '@types/index'
```

### 5. Material-UI 테마

**테마 설정**: `src/theme.ts`

- 커스텀 컬러 팔레트
- 타이포그래피 설정
- 컴포넌트 스타일 오버라이드
- 반응형 디자인

## 🎨 컴포넌트 개발 가이드

### 페이지 컴포넌트 생성

```typescript
// src/pages/NewPage.tsx
import { Box, Typography } from '@mui/material'

export default function NewPage() {
  return (
    <Box>
      <Typography variant="h4">새 페이지</Typography>
    </Box>
  )
}
```

### API 호출 패턴

```typescript
import { useState } from 'react'
import { adCopyApi } from '@services/api'
import { useGenerationStore } from '@store/useGenerationStore'

export default function AdCopyGenerator() {
  const [result, setResult] = useState(null)
  const { setLoading, setError } = useGenerationStore()

  const handleGenerate = async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await adCopyApi.generate({
        product_name: 'Product',
        tone: 'professional',
        length: 'short',
      })

      setResult(data)
    } catch (error) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    // JSX...
  )
}
```

## 🔧 개발 도구

### TypeScript 타입 체크

```bash
npm run type-check
```

### ESLint

```bash
npm run lint
```

### Vite 설정

**파일**: `vite.config.ts`

- **Path Alias**: `@/`, `@components/`, `@pages/`, etc.
- **API Proxy**: `/api` → `http://localhost:8000`
- **포트**: 3000
- **소스맵**: 활성화

## 📊 성능 최적화

### Vite 최적화

- ⚡ **HMR (Hot Module Replacement)**: 즉각적인 업데이트
- 🚀 **ESBuild**: 초고속 번들링
- 📦 **Code Splitting**: 자동 청크 분할
- 🗜️ **Tree Shaking**: 사용하지 않는 코드 제거

### React 최적화

- React 18의 Concurrent Features
- Lazy Loading (향후 구현)
- Memo/useCallback (필요시)

### Material-UI 최적화

- Tree Shaking 지원
- CSS-in-JS 최적화
- Icon Tree Shaking

## 🚧 다음 단계 (Stage 10)

**사용자 인터페이스 컴포넌트 개발**:

1. **AdCopyGenerator** - 광고 문구 생성 폼
2. **ImageGenerator** - 이미지 생성 폼
3. **BackgroundEditor** - 배경 편집 폼
4. **ResultDisplay** - 결과 표시 컴포넌트
5. **GalleryGrid** - 갤러리 그리드
6. **LoadingState** - 로딩 인디케이터
7. **ErrorState** - 에러 표시

## 📚 참고 문서

- [React 공식 문서](https://react.dev/)
- [TypeScript 핸드북](https://www.typescriptlang.org/docs/)
- [Material-UI 문서](https://mui.com/)
- [Vite 문서](https://vitejs.dev/)
- [Zustand 문서](https://zustand-demo.pmnd.rs/)

## 🐛 트러블슈팅

### 포트 충돌

```bash
# 포트 변경 (vite.config.ts)
server: {
  port: 3001
}
```

### API 연결 실패

1. 백엔드 서버 실행 확인
2. `.env` 파일의 `VITE_API_URL` 확인
3. CORS 설정 확인 (백엔드)

### 타입 에러

```bash
# node_modules/@types 재설치
rm -rf node_modules
npm install
```

---

**Made with ❤️ for Small Business Owners**

# AI Image Generator Web Monitor

AI 이미지 생성 및 벡터 검색을 위한 웹 인터페이스

## 🛠️ 설치 및 실행

### 1. 환경 설정

```bash
# Python 3.8+ 필요
conda activate eyewear
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
python src/web_server.py
```

### 3. 웹 접속

```
http://localhost:51003
```

## ⚙️ 설정 관리

### API 엔드포인트 설정 (`src/common/settings.py`)

#### 기본 API URL(DEV3)

```python
EXTERNAL_API_URL = "http://192.168.200.233:52000/api/services/vactorImageSearch/vit/imageGenerate/imagen/data"
```

#### 사전 정의된 엔드포인트

```python
PREDEFINED_ENDPOINTS = [
    {
        "name": "벡터이미지 검색(Dev3/Data)",
        "url": "http://192.168.200.233:52000/api/services/vactorImageSearch/vit/imageGenerate/imagen/data",
        "description": "Imagen 모델을 사용한 이미지 생성후 Vector 검색 그후 결과 이미지 데이터 return"
    },
    {
        "name": "벡터이미지 검색(Dev2/Data)",
        "url": "http://192.168.200.232:51000/api/services/vactorImageSearch/vit/imageGenerate/imagen/data",
        "description": "Imagen 모델을 사용한 이미지 생성후 Vector 검색 그후 결과 이미지 데이터 return"
    }
]
```

#### 서버 설정

- `SERVICE_PORT`: 웹 서버 포트 (기본: 51003)
- `HOST`: 서버 바인딩 IP (기본: "0.0.0.0")
- `API_TIMEOUT_SECONDS`: API 타임아웃 (기본: 600초)
- `DEBUG_MODE`: 디버그 모드 (기본: False)

### 동적 API 변경 사용법

1. **웹페이지 상단의 "API 설정" 클릭**
2. **사전 정의된 버튼 선택** 또는 **커스텀 URL 입력**
3. **실시간으로 API 연결 변경됨**
4. **현재 사용 중인 API가 표시됨**

## 🔧 API 엔드포인트

### 메인 엔드포인트

- `GET /` - 메인 웹 페이지
- `POST /create` - 이미지 생성 요청
- `GET /health` - 서버 상태 확인
- `GET /api-status` - 외부 API 연결 상태

### API 설정 엔드포인트

- `GET /api-endpoints` - 사용 가능한 엔드포인트 목록
- `POST /change-api-url` - API URL 동적 변경
- `GET /config` - 프론트엔드 설정 정보

## 📁 프로젝트 구조

```
src/
├── common/
│   └── settings.py              # 애플리케이션 설정
├── config/
│   ├── __init__.py
│   └── app_config.py           # 통합 설정 관리
├── services/
│   ├── api_manager.py          # API 통합 관리
│   └── image_api_service.py    # 외부 API 호출
├── static/
│   ├── css/
│   │   └── style.css           # CSS 스타일 (CSS 변수 사용)
│   └── js/
│       ├── const.js            # 상수 정의
│       ├── init.js             # 초기화 스크립트
│       └── modules/
│           ├── apiClient.js        # API 통신
│           ├── apiConfigManager.js # API 설정 관리 ⭐ NEW
│           ├── imageGenerator.js   # 이미지 생성 로직
│           ├── stateManager.js     # 상태 관리
│           └── uiManager.js        # UI 관리
├── templates/
│   └── index.html              # HTML 템플릿
└── web_server.py               # FastAPI 웹 서버
```

## 🎨 UI/UX 개선사항

### 반응형 레이아웃

- **데스크톱 (1025px+)**: 이미지 5개/행, 여백 20px
- **태블릿 (769-1024px)**: 이미지 3개/행, 여백 15px
- **모바일 (~768px)**: 이미지 2개/행, 여백 10px

### CSS 최적화

- CSS 변수 도입으로 통일된 디자인 시스템
- 공통 색상, 크기, 그림자 값 중앙 관리

### 사용성 개선

- 접을 수 있는 API 설정 패널
- 실시간 API 상태 표시
- 호버 효과 및 활성 상태 표시

## 🐛 문제 해결

### 포트 충돌

```bash
# 포트 사용 확인
netstat -an | findstr :51003

# settings.py에서 SERVICE_PORT 변경
SERVICE_PORT = 51004  # 다른 포트로 변경
```

### API 연결 문제

```bash
# API 상태 확인
curl http://localhost:51003/api-status

# 또는 브라우저에서
http://localhost:51003/api-status
```

### 개발자 도구 디버깅

- **F12 → 콘솔 탭**: JavaScript 오류 및 API 호출 로그 확인
- **네트워크 탭**: API 요청/응답 상세 분석

## 📝 개발 로그

### v2.0 (2025-08-06)

- ✅ 동적 API 엔드포인트 설정 기능 추가
- ✅ 사전 정의된 서버 버튼들
- ✅ 반응형 이미지 레이아웃 개선 (5/3/2개)
- ✅ CSS 변수 도입 및 최적화
- ✅ Legacy 코드 제거 및 클린업
- ✅ API 설정 패널 UI 추가

### 주요 변경사항

- `apiConfigManager.js` 모듈 추가
- API URL 실시간 변경 기능
- 설정 패널 토글 기능
- CSS 변수 기반 디자인 시스템

## 📞 지원

문제가 발생하면 개발자 도구(F12) 콘솔을 확인하거나 서버 로그를 점검해주세요.

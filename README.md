# AI 헬퍼 코어 (ai-helper-core)

**GPT for Team을 위한 Python 기반 AI 백엔드 서버**

## 1. 프로젝트 개요

AI 헬퍼 코어는 B2B용 OpenAI API 기반 GPT 계정관리 시스템의 핵심 AI 기능을 담당하는 Python 기반 백엔드 서버입니다. 이 컴포넌트는 FastAPI를 활용하여 OpenAI API 연동, 음성 처리, 벡터 검색 등 AI 관련 기능을 제공합니다.

전체 시스템은 다음 3개의 주요 컴포넌트로 구성됩니다:

```
ai-helper/
├── ai-helper-front (프론트엔드 - React/Next.js)
├── ai-helper-back (메인 백엔드 - Java/Spring Boot)
└── ai-helper-core (AI 엔진 백엔드 - Python/FastAPI)
```

## 2. 기술 스택

### 핵심 기술
- **언어**: Python 3.10+
- **웹 프레임워크**: FastAPI
- **비동기 처리**: asyncio, uvicorn
- **컨테이너화**: Docker
- **API 문서화**: Swagger/OpenAPI
- **테스트**: pytest

### 데이터베이스
- **메인 DB 연결**: SQLAlchemy (ai-helper-back과 동일 DB 접근)
- **벡터 데이터베이스**: Chroma DB (임베딩 저장 및 검색용)

### 외부 API 통합
- **LLM API**: OpenAI API (GPT-4, GPT-3.5)
- **임베딩**: OpenAI Ada 002 임베딩 모델
- **음성 처리**: Whisper API (STT), ElevenLabs API (TTS)

## 3. 시스템 아키텍처

### 컴포넌트 구조
![시스템 아키텍처](https://via.placeholder.com/800x500?text=AI+Helper+Core+Architecture)

### 주요 모듈

#### LLM 프록시 모듈
- OpenAI API 호출 추상화 및 최적화
- 토큰 사용량 모니터링 및 제한 기능
- 오류 처리 및 재시도 로직

#### Chroma DB 기반 RAG 모듈
- 문서 처리 및 청크 분할 (Chunking)
- OpenAI 임베딩 생성 및 Chroma DB 저장
- 시맨틱 검색 및 관련 문서 검색
- LLM 응답 생성을 위한 컨텍스트 주입

#### 음성 처리 모듈
- 음성-텍스트 변환 (STT)
- 텍스트-음성 변환 (TTS)
- 실시간 스트리밍 지원

#### 프롬프트 관리 모듈
- 템플릿 기반 프롬프트 관리
- 조직별 커스텀 프롬프트 저장
- 프롬프트 변수 처리

#### 캐싱 및 최적화 모듈
- 반복 쿼리 캐싱
- 비용 최적화 알고리즘
- 배치 처리 지원

## 4. API 엔드포인트 설계

### 채팅/대화 API
```
POST /api/chat/completions - 텍스트 대화 생성
POST /api/chat/stream - 스트리밍 대화 생성
GET /api/models - 사용 가능 모델 목록
```

### 벡터 검색 및 RAG API
```
POST /api/knowledge/documents - 문서 업로드
GET /api/knowledge/documents - 문서 목록 조회
POST /api/knowledge/search - 벡터 검색
POST /api/knowledge/query - RAG 기반 질의응답
```

### 음성 API
```
POST /api/speech/transcribe - 음성-텍스트 변환
POST /api/speech/synthesize - 텍스트-음성 변환
```

### 관리 API
```
GET /api/usage - 사용량 통계
POST /api/prompt-templates - 프롬프트 템플릿 생성
GET /api/prompt-templates - 프롬프트 템플릿 조회
```

## 5. Chroma DB 벡터 스토어 설계

AI 헬퍼 코어는 RAG(Retrieval-Augmented Generation) 기능을 위해 Chroma DB를 벡터 데이터베이스로 활용합니다.

### Chroma DB 선택 이유
- **오픈소스**: 자체 호스팅 가능한 오픈소스 벡터 DB
- **Python 네이티브**: Python 생태계와 완벽하게 통합
- **빠른 쿼리 속도**: 효율적인 벡터 검색 알고리즘
- **메타데이터 필터링**: 다양한 필터링 옵션 제공
- **확장성**: 대규모 데이터셋 처리 가능

### Chroma DB 구현 계획
- 조직별 별도 컬렉션 생성
- 문서 메타데이터 구조화 (파일타입, 날짜, 카테고리 등)
- 청크 사이즈 최적화 (기본 1000자)
- 주기적 임베딩 업데이트 메커니즘

### 인덱싱 및 검색 최적화
- 문서 전처리 파이프라인 구축
- 다양한 거리 측정 방법 지원 (코사인 유사도 기본)
- Top-k 검색 결과 최적화
- 메타데이터 기반 필터링 구현

## 6. 구현 로드맵

### 1단계: 기본 인프라 구축 (2주)
- [x] 프로젝트 기본 구조 설정
- [ ] FastAPI 프레임워크 설정
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인 구축
- [ ] 기본 API 엔드포인트 구현

### 2단계: LLM 프록시 구현 (2주)
- [ ] OpenAI API 클라이언트 구현
- [ ] 모델 파라미터 관리 시스템
- [ ] 토큰 사용량 모니터링
- [ ] 오류 처리 및 재시도 로직
- [ ] 응답 캐싱 구현

### 3단계: Chroma DB & RAG 통합 (3주)
- [ ] Chroma DB 설정 및 연결
- [ ] 문서 처리 및 청킹 파이프라인
- [ ] 임베딩 생성 및 저장 로직
- [ ] 벡터 검색 API 구현
- [ ] RAG 프롬프트 최적화
- [ ] 문서 관리 인터페이스

### 4단계: 음성 처리 구현 (2주)
- [ ] Whisper API 통합 (STT)
- [ ] ElevenLabs API 통합 (TTS)
- [ ] 음성 파일 처리 유틸리티
- [ ] 실시간 음성 스트리밍
- [ ] 다국어 음성 처리 지원

### 5단계: 프롬프트 관리 시스템 (2주)
- [ ] 프롬프트 템플릿 저장소
- [ ] 변수 치환 기능
- [ ] 템플릿 버전 관리
- [ ] 조직별 템플릿 격리
- [ ] 템플릿 평가 및 최적화

### 6단계: 통합 및 최적화 (3주)
- [ ] ai-helper-back과 통합
- [ ] 인증 및 권한 시스템 연동
- [ ] 성능 최적화 및 벤치마킹
- [ ] 부하 테스트 및 스케일링
- [ ] 로깅 및 모니터링 강화

### 7단계: 테스트 및 배포 (2주)
- [ ] 단위 테스트 구현
- [ ] 통합 테스트 구현
- [ ] 문서화 완료
- [ ] 보안 감사
- [ ] 프로덕션 배포

## 7. 기술적 고려사항

### 성능 최적화
- **비동기 처리**: FastAPI의 비동기 기능을 활용한 동시성 최적화
- **배치 처리**: 대량 요청의 배치 처리로 API 호출 최소화
- **캐싱 전략**: 다단계 캐싱으로 응답 속도 향상 및 비용 절감

### 확장성
- **수평적 확장**: 여러 인스턴스로 부하 분산 지원
- **모듈 분리**: 마이크로서비스 아키텍처 지향
- **API 버전 관리**: 하위 호환성 유지

### 보안
- **인증 통합**: ai-helper-back의 JWT 인증 활용
- **API 키 관리**: 안전한 API 키 저장 및 순환
- **데이터 암호화**: 민감 정보 암호화 저장

## 8. 시작하기

### 필수 요구사항
- Python 3.10 이상
- Docker 및 Docker Compose
- OpenAI API 키

### 설치 방법
```bash
# 저장소 복제
git clone https://github.com/your-org/ai-helper.git
cd ai-helper/ai-helper-core

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 필요한 API 키 등을 설정

# 개발 서버 실행
uvicorn app.main:app --reload
```

### Docker로 실행
```bash
docker-compose up -d
```

## 9. 향후 확장 계획

### 추가 예정 기능
- **이미지 생성 및 분석**: DALL-E 및 Vision API 통합
- **파인튜닝 관리**: 조직별 파인튜닝 모델 관리
- **멀티모달 처리**: 이미지, 음성, 텍스트 통합 처리
- **에이전트 프레임워크**: 도구 사용이 가능한 GPT 에이전트

### 통합 가능 서비스
- **Google Workspace/Microsoft 365**: 문서 통합
- **Slack/Teams**: 메시징 플랫폼 연동
- **Jira/Trello**: 작업 관리 도구 연동

## 10. 기여하기

프로젝트에 기여하는 방법에 대한 자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 11. 라이센스

이 프로젝트는 [MIT 라이센스](LICENSE)에 따라 라이센스가 부여됩니다. 
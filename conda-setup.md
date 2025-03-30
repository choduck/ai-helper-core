# Anaconda 환경 설정 가이드

이 문서는 `ai-helper-core` 프로젝트를 위한 Anaconda 환경 설정 방법을 안내합니다.

## 필수 요구사항
- Anaconda 또는 Miniconda가 설치되어 있어야 합니다.
- Git이 설치되어 있어야 합니다.

## 환경 설정 단계

### 1. 저장소 클론
```bash
git clone https://github.com/your-org/ai-helper.git
cd ai-helper/ai-helper-core
```

### 2. Conda 환경 생성
```bash
# Python 3.10 기반 환경 생성
conda create -n ai-helper-core python=3.10
conda activate ai-helper-core
```

### 3. 필요한 패키지 설치
```bash
# 기본 패키지 설치
pip install -r requirements.txt

# 또는 Conda를 사용하여 설치 (권장)
conda install -c conda-forge fastapi uvicorn pydantic python-dotenv python-multipart
conda install -c conda-forge openai tiktoken langchain
conda install -c conda-forge chromadb sentence-transformers
conda install -c conda-forge sqlalchemy pymysql 
conda install -c conda-forge numpy pandas pyyaml jinja2
```

### 4. 환경 변수 설정
```bash
# .env.example 파일을 .env로 복사 (이미 있는 경우 건너뛰기)
cp .env.example .env

# .env 파일 편집
# OpenAI API 키, 데이터베이스 연결 정보 등 필요한 설정 입력
```

### 5. 개발 서버 실행
```bash
# 개발 모드로 실행
uvicorn app.main:app --reload

# 또는 production 모드로 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 환경 내보내기 (다른 시스템으로 이전)
```bash
# 현재 환경의 패키지 리스트 내보내기
conda env export > environment.yml

# 특정 OS에 종속되지 않는 패키지 목록만 내보내기 (권장)
conda env export --from-history > environment.yml
```

## 내보낸 환경 가져오기
```bash
# 내보낸 환경 파일로부터 새 환경 생성
conda env create -f environment.yml
```

## 주의 사항
- 패키지 충돌이 발생할 경우 가상 환경을 새로 만드는 것이 좋습니다.
- OpenAI API 키와 같은 민감한 정보는 .env 파일에 보관하고, 이 파일은 Git에 커밋하지 않도록 주의하세요.
- ChromaDB를 처음 사용할 때 관련 패키지 설치에 시간이 소요될 수 있습니다. 
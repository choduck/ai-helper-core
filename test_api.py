import os
import sys
import openai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

print(f"Python 버전: {sys.version}")
print(f"OpenAI 라이브러리 버전: {openai.__version__}")

# .env 파일의 API 키 출력 (처음 몇 글자만)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"API 키가 .env 파일에 설정되어 있습니다. (처음 몇 글자: {api_key[:10]}...)")
else:
    print("API 키가 .env 파일에 설정되어 있지 않습니다.")

# 환경 변수에서 API 키 확인
env_api_key = os.environ.get("OPENAI_API_KEY")
if env_api_key:
    print(f"API 키가 환경 변수에 설정되어 있습니다. (처음 몇 글자: {env_api_key[:10]}...)")
else:
    print("API 키가 환경 변수에 설정되어 있지 않습니다.")

# API 연결 테스트
try:
    print("\nOpenAI API 연결을 테스트합니다...")
    client = openai.OpenAI()
    models = client.models.list()
    print("API 연결 성공! 사용 가능한 모델:")
    for model in models.data[:5]:  # 처음 5개만 표시
        print(f"- {model.id}")
    print("...")
except Exception as e:
    print(f"API 연결 실패: {str(e)}") 
import os
import sys
import asyncio
from dotenv import load_dotenv
import logging
import traceback

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("api_test_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_test")

# .env 파일에서 환경 변수 로드
load_dotenv()
logger.info(".env 파일에서 환경 변수를 로드했습니다.")

# API 키 확인
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    # 마스킹된 API 키 표시 (앞 8자, 뒤 4자만 표시)
    masked_key = f"{api_key[:8]}{'*' * (len(api_key) - 12)}{api_key[-4:]}"
    logger.info(f"API 키가 설정되어 있습니다: {masked_key}")
    
    # API 키 형식 검증
    if not api_key.startswith(("sk-", "sk-proj-")):
        logger.error(f"API 키 형식이 유효하지 않습니다. 'sk-' 또는 'sk-proj-'로 시작해야 합니다.")
else:
    logger.error("API 키가 설정되어 있지 않습니다.")
    sys.exit(1)

# OpenAI 라이브러리 로드 시도
try:
    import openai
    logger.info(f"OpenAI 라이브러리 버전: {openai.__version__}")
except ImportError:
    logger.error("OpenAI 라이브러리를 로드할 수 없습니다. 설치되어 있는지 확인하세요.")
    logger.info("pip install openai 명령으로 설치하세요.")
    sys.exit(1)

# API 베이스 URL 확인
api_base = os.getenv("OPENAI_API_BASE")
if api_base:
    logger.info(f"OpenAI API Base URL: {api_base}")
else:
    logger.info("기본 OpenAI API URL을 사용합니다.")

# API 연결 테스트
async def test_api():
    logger.info("\n===== 1단계: 동기 API 호출 테스트 =====")
    try:
        # 동기 API 클라이언트
        logger.info("동기 API 클라이언트 초기화...")
        client = openai.OpenAI(api_key=api_key)
        
        # 모델 목록 요청
        logger.info("모델 목록을 요청합니다...")
        models = client.models.list()
        logger.info("API 연결 성공! 사용 가능한 모델:")
        for model in models.data[:5]:  # 처음 5개만 표시
            logger.info(f"- {model.id}")
    except Exception as e:
        logger.error(f"동기 API 호출 실패: {str(e)}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
    
    logger.info("\n===== 2단계: 동기 채팅 API 호출 테스트 =====")
    try:
        # 동기 API 클라이언트로 채팅 요청
        logger.info("간단한 채팅 API 호출 테스트...")
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, what is the capital of South Korea?"}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        # 응답 출력
        logger.info("\n--- 채팅 응답 ---")
        logger.info(f"모델: {response.model}")
        logger.info(f"응답: {response.choices[0].message.content}")
        logger.info(f"Tokens: {response.usage.total_tokens} (프롬프트: {response.usage.prompt_tokens}, 완성: {response.usage.completion_tokens})")
        logger.info("API 호출이 성공적으로 완료되었습니다.")
    except Exception as e:
        logger.error(f"동기 채팅 API 호출 실패: {str(e)}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        
    logger.info("\n===== 3단계: 비동기 API 호출 테스트 =====")
    try:
        # 비동기 API 클라이언트
        logger.info("비동기 API 클라이언트 초기화...")
        async_client = openai.AsyncOpenAI(api_key=api_key)
        
        # 모델 목록 요청
        logger.info("모델 목록을 요청합니다...")
        models = await async_client.models.list()
        logger.info("비동기 API 연결 성공! 사용 가능한 모델:")
        for model in models.data[:5]:  # 처음 5개만 표시
            logger.info(f"- {model.id}")
            
        # 비동기 채팅 요청
        logger.info("\n비동기 채팅 API 호출 테스트...")
        response = await async_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, what is the capital of South Korea?"}
            ],
            temperature=0.7,
            max_tokens=50
        )
        
        # 응답 출력
        logger.info("\n--- 비동기 채팅 응답 ---")
        logger.info(f"모델: {response.model}")
        logger.info(f"응답: {response.choices[0].message.content}")
        logger.info(f"Tokens: {response.usage.total_tokens} (프롬프트: {response.usage.prompt_tokens}, 완성: {response.usage.completion_tokens})")
        logger.info("비동기 API 호출이 성공적으로 완료되었습니다.")
        
    except Exception as e:
        logger.error(f"비동기 API 호출 실패: {str(e)}")
        logger.error(f"상세 오류: {traceback.format_exc()}")

# 비동기 메인 함수
async def main():
    logger.info("OpenAI API 디버깅 테스트 시작...")
    await test_api()
    logger.info("OpenAI API 디버깅 테스트 완료!")

# 스크립트 실행
if __name__ == "__main__":
    asyncio.run(main()) 
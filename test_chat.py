import os
import sys
import openai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

print(f"Python 버전: {sys.version}")
print(f"OpenAI 라이브러리 버전: {openai.__version__}")

# API 키 확인
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("API 키가 설정되어 있지 않습니다.")
    sys.exit(1)

# 간단한 채팅 완성 테스트
try:
    print("\n간단한 채팅 API 호출 테스트...")
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 친절한 AI 어시스턴트야."},
            {"role": "user", "content": "안녕하세요, 대한민국의 수도는 어디인가요?"}
        ],
        temperature=0.7,
        max_tokens=50
    )
    
    # 응답 출력
    print("\n--- 채팅 응답 ---")
    print(f"모델: {response.model}")
    print(f"응답: {response.choices[0].message.content}")
    print(f"Tokens: {response.usage.total_tokens} (프롬프트: {response.usage.prompt_tokens}, 완성: {response.usage.completion_tokens})")
    print("API 호출이 성공적으로 완료되었습니다.")
    
except Exception as e:
    print(f"API 호출 오류: {str(e)}") 
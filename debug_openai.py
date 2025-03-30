import os
import sys
import json
import socket
import requests
import subprocess
import traceback
from datetime import datetime
from dotenv import load_dotenv
import platform

# 타임스탬프 형식의 로그 함수
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

log("OpenAI API 디버깅 스크립트 시작...")

# 시스템 정보 확인
log(f"운영 체제: {platform.system()} {platform.release()}")
log(f"Python 버전: {sys.version}")

# .env 파일에서 환경 변수 로드
load_dotenv()
log(".env 파일에서 환경 변수를 로드했습니다.")

# API 키 검증
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    # 마스킹된 API 키 표시 (앞 8자만 표시)
    masked_key = f"{api_key[:8]}{'*' * (len(api_key) - 8)}"
    log(f"API 키가 설정되어 있습니다: {masked_key}")
    
    # API 키 형식 검증
    if not api_key.startswith(("sk-", "sk-proj-")):
        log(f"API 키 형식이 유효하지 않습니다. 'sk-' 또는 'sk-proj-'로 시작해야 합니다.", "ERROR")
else:
    log("API 키가 설정되어 있지 않습니다.", "ERROR")
    sys.exit(1)

# 환경 변수 확인
for env_var in ["OPENAI_API_KEY", "OPENAI_API_BASE", "OPENAI_ORGANIZATION"]:
    value = os.getenv(env_var)
    if value:
        masked_value = value[:4] + "****" if env_var == "OPENAI_API_KEY" else value
        log(f"환경 변수 {env_var}={masked_value}")

# 네트워크 연결 테스트
def check_network_connection():
    hosts = ["api.openai.com", "8.8.8.8", "google.com"]
    for host in hosts:
        try:
            log(f"{host}에 대한 네트워크 연결 테스트 중...")
            socket.create_connection((host, 80), timeout=5)
            log(f"{host}에 연결 성공!")
            return True
        except Exception as e:
            log(f"{host}에 연결 실패: {str(e)}", "ERROR")
    return False

# 프록시 설정 확인
def check_proxy_settings():
    proxies = {
        "http": os.getenv("HTTP_PROXY"),
        "https": os.getenv("HTTPS_PROXY")
    }
    log(f"프록시 설정: {proxies}")
    return proxies

# OpenAI 라이브러리 로드 시도
try:
    import openai
    log(f"OpenAI 라이브러리 버전: {openai.__version__}")
except ImportError:
    log("OpenAI 라이브러리를 로드할 수 없습니다. 설치되어 있는지 확인하세요.", "ERROR")
    log("pip install openai 명령으로 설치하세요.")
    sys.exit(1)

# API 연결 테스트
try:
    log("\nOpenAI API 연결을 테스트합니다...")
    
    # 네트워크 연결 확인
    if not check_network_connection():
        log("네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인하세요.", "ERROR")
    
    # 프록시 설정 확인
    proxies = check_proxy_settings()
    
    # OpenAI 클라이언트 초기화
    client = openai.OpenAI()
    
    # 모델 목록 요청
    log("모델 목록을 요청합니다...")
    try:
        models = client.models.list()
        log("API 연결 성공! 사용 가능한 모델:")
        for model in models.data[:5]:  # 처음 5개만 표시
            log(f"- {model.id}")
        log("...")
    except Exception as e:
        log(f"모델 목록 요청 실패: {str(e)}", "ERROR")
        log(f"상세 오류: {traceback.format_exc()}", "DEBUG")
    
    # 간단한 채팅 완성 테스트
    log("\n간단한 채팅 API 호출 테스트...")
    try:
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
        log("\n--- 채팅 응답 ---")
        log(f"모델: {response.model}")
        log(f"응답: {response.choices[0].message.content}")
        log(f"Tokens: {response.usage.total_tokens} (프롬프트: {response.usage.prompt_tokens}, 완성: {response.usage.completion_tokens})")
        log("API 호출이 성공적으로 완료되었습니다.")
    except Exception as e:
        log(f"채팅 API 호출 실패: {str(e)}", "ERROR")
        log(f"상세 오류: {traceback.format_exc()}", "DEBUG")
        
        # 오류 심층 분석
        error_message = str(e)
        if "Unauthorized" in error_message:
            log("API 키가 유효하지 않거나 만료되었습니다.", "ERROR")
        elif "rate limit" in error_message.lower():
            log("API 요청 한도에 도달했습니다.", "ERROR")
        elif "timeout" in error_message.lower():
            log("API 요청 시간이 초과되었습니다. 네트워크 상태를 확인하세요.", "ERROR")
        elif "proxy" in error_message.lower():
            log("프록시 설정에 문제가 있습니다.", "ERROR")

    # 직접 API 호출 테스트
    log("\n직접 HTTP 요청으로 API 테스트...")
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, what is the capital of South Korea?"}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            proxies=proxies,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            log("직접 API 호출 성공!")
            log(f"응답: {response_data['choices'][0]['message']['content']}")
        else:
            log(f"직접 API 호출 실패: 상태 코드 {response.status_code}", "ERROR")
            log(f"응답: {response.text}", "ERROR")
    except Exception as e:
        log(f"직접 API 호출 중 오류 발생: {str(e)}", "ERROR")
        log(f"상세 오류: {traceback.format_exc()}", "DEBUG")

except Exception as e:
    log(f"API 연결 테스트 중 일반 오류 발생: {str(e)}", "ERROR")
    log(f"상세 오류: {traceback.format_exc()}", "DEBUG")

log("디버깅 스크립트 완료.") 
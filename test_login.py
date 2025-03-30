import requests
import json

# 로그인 API 테스트
print("로그인 API 테스트를 시작합니다...")

# 백엔드 API 직접 호출
backend_url = "http://localhost:8080/api/auth/login"
print(f"백엔드 API 직접 호출 ({backend_url}):")

try:
    response = requests.post(
        backend_url,
        json={
            "username": "user",
            "password": "user"
        },
        headers={
            "Content-Type": "application/json"
        }
    )
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        print("응답 내용:")
        response_data = response.json()
        print(json.dumps(response_data, indent=2))
        print("백엔드 로그인 API 호출 성공!")
    else:
        print(f"오류: {response.text}")
except Exception as e:
    print(f"백엔드 API 호출 오류: {str(e)}")

# 프론트엔드 API 호출
frontend_url = "http://localhost:3000/api/auth/login"
print(f"\n프론트엔드 API 호출 ({frontend_url}):")

try:
    response = requests.post(
        frontend_url,
        json={
            "username": "user",
            "password": "user"
        },
        headers={
            "Content-Type": "application/json"
        }
    )
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        print("응답 내용:")
        response_data = response.json()
        print(json.dumps(response_data, indent=2))
        print("프론트엔드 로그인 API 호출 성공!")
    else:
        print(f"오류: {response.text}")
except Exception as e:
    print(f"프론트엔드 API 호출 오류: {str(e)}") 
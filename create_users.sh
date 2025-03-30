#!/bin/bash

# 먼저 관리자로 로그인하여 토큰 얻기 (이미 계정이 있는 경우)
# TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' | jq -r '.token')

# 일반 사용자 생성
echo "일반 사용자 생성..."
curl -X POST http://localhost:8080/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{
    "orgId": 1,
    "username": "user",
    "password": "user",
    "fullname": "일반 사용자",
    "email": "user@example.com",
    "role": "USER",
    "status": "ACTIVE",
    "apiUsageLimit": null
  }'

echo -e "\n"

# 관리자 생성
echo "관리자 생성..."
curl -X POST http://localhost:8080/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{
    "orgId": 1,
    "username": "admin",
    "password": "admin",
    "fullname": "관리자",
    "email": "admin@example.com",
    "role": "ADMIN",
    "status": "ACTIVE",
    "apiUsageLimit": null
  }'

echo -e "\n"

# 매니저 생성
echo "매니저 생성..."
curl -X POST http://localhost:8080/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{
    "orgId": 1,
    "username": "manager",
    "password": "manager",
    "fullname": "매니저",
    "email": "manager@example.com",
    "role": "MANAGER",
    "status": "ACTIVE",
    "apiUsageLimit": 1000
  }'

echo -e "\n"
echo "사용자 생성 요청이 완료되었습니다." 
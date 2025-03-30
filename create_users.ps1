# PowerShell 스크립트로 사용자 생성하기

# 일반 사용자 생성
Write-Host "일반 사용자 생성..." -ForegroundColor Green
$userBody = @{
    orgId = 1
    username = "user"
    password = "user"
    fullname = "일반 사용자"
    email = "user@example.com"
    role = "USER"
    status = "ACTIVE"
    apiUsageLimit = $null
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/admin/users" -Method Post -ContentType "application/json" -Body $userBody

# 관리자 생성
Write-Host "`n관리자 생성..." -ForegroundColor Green
$adminBody = @{
    orgId = 1
    username = "admin"
    password = "admin"
    fullname = "관리자"
    email = "admin@example.com"
    role = "ADMIN"
    status = "ACTIVE"
    apiUsageLimit = $null
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/admin/users" -Method Post -ContentType "application/json" -Body $adminBody

# 매니저 생성
Write-Host "`n매니저 생성..." -ForegroundColor Green
$managerBody = @{
    orgId = 1
    username = "manager"
    password = "manager"
    fullname = "매니저"
    email = "manager@example.com"
    role = "MANAGER"
    status = "ACTIVE"
    apiUsageLimit = 1000
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/api/admin/users" -Method Post -ContentType "application/json" -Body $managerBody

Write-Host "`n사용자 생성 요청이 완료되었습니다." -ForegroundColor Cyan

<# 
# 토큰 기반 인증이 필요한 경우 아래 방법 사용
$loginBody = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

$authResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
$token = $authResponse.token

# 토큰을 사용한 요청
Invoke-RestMethod -Uri "http://localhost:8080/api/admin/users" -Method Post -ContentType "application/json" -Headers @{Authorization = "Bearer $token"} -Body $userBody
#> 
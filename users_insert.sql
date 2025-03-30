-- users 테이블에 기본 사용자 추가 스크립트

-- 먼저 organizations 테이블에 기본 조직이 있는지 확인하세요
-- 없는 경우 먼저 organizations 테이블에 INSERT가 필요합니다
-- 아래 예시에서는 org_id가 1인 조직이 있다고 가정합니다

-- user 사용자 추가 (비밀번호: user)
INSERT INTO users (org_id, username, password, fullname, email, role, status, api_usage_limit) 
VALUES (1, 'user', '$2a$10$8BLLiEJXbyKJlvHK0Aql9.Y/WWSfL6tXVdJmK9C5Y5EyILWs.HGIq', '일반 사용자', 'user@example.com', 'USER', 'ACTIVE', NULL);

-- admin 사용자 추가 (비밀번호: admin)
INSERT INTO users (org_id, username, password, fullname, email, role, status, api_usage_limit) 
VALUES (1, 'admin', '$2a$10$0Ub6KDrLl7KbvXJSdELBvO7hcCFQBSnFaIcNJKnbmYhXV4xZHPnFy', '관리자', 'admin@example.com', 'ADMIN', 'ACTIVE', NULL);

-- 매니저 사용자 추가 (비밀번호: manager)
INSERT INTO users (org_id, username, password, fullname, email, role, status, api_usage_limit) 
VALUES (1, 'manager', '$2a$10$XFHv5PZBt.xdUWNqgQpTEeZ4WDp0iQ.HJx0CLqjNpMfQY/IpvSOb.', '매니저', 'manager@example.com', 'MANAGER', 'ACTIVE', 1000);

-- 사용자 테이블 구조 참고:
/*
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    org_id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role ENUM('ADMIN', 'MANAGER', 'USER') NOT NULL DEFAULT 'USER',
    status ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    api_usage_limit INT NULL COMMENT 'Max API calls per month, NULL for unlimited',
    FOREIGN KEY (org_id) REFERENCES organizations(org_id),
    UNIQUE KEY unique_org_username (org_id, username),
    UNIQUE KEY unique_org_email (org_id, email)
);
*/

-- 비밀번호 해시값:
-- user: BCrypt로 해시된 'user'
-- admin: BCrypt로 해시된 'admin'
-- manager: BCrypt로 해시된 'manager' 
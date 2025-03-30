-- organizations 테이블이 없는 경우 생성
CREATE TABLE IF NOT EXISTS organizations (
    org_id INT AUTO_INCREMENT PRIMARY KEY,
    org_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    subscription_plan ENUM('TEAM_BASIC', 'TEAM_PRO', 'ENTERPRISE') NOT NULL DEFAULT 'TEAM_BASIC',
    subscription_start_date DATE NOT NULL,
    subscription_end_date DATE NOT NULL,
    max_users INT NOT NULL DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    contact_email VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20)
);

-- 기본 조직 추가
INSERT INTO organizations (
    org_id, 
    org_name, 
    industry, 
    subscription_plan, 
    subscription_start_date, 
    subscription_end_date, 
    max_users, 
    is_active, 
    contact_email, 
    contact_phone
) VALUES (
    1, 
    '기본 조직', 
    'Technology', 
    'TEAM_BASIC', 
    CURDATE(), 
    DATE_ADD(CURDATE(), INTERVAL 1 YEAR), 
    10, 
    TRUE, 
    'admin@example.com', 
    '010-1234-5678'
);

-- 테스트용 추가 조직
INSERT INTO organizations (
    org_name, 
    industry, 
    subscription_plan, 
    subscription_start_date, 
    subscription_end_date, 
    max_users, 
    is_active, 
    contact_email, 
    contact_phone
) VALUES (
    '테스트 조직', 
    'Education', 
    'TEAM_PRO', 
    CURDATE(), 
    DATE_ADD(CURDATE(), INTERVAL 1 YEAR), 
    25, 
    TRUE, 
    'test@example.com', 
    '010-9876-5432'
);

-- 참고: users 테이블의 org_id는 위 organizations 테이블의 org_id를 참조합니다.
-- users_insert.sql 스크립트를 실행하기 전에 이 스크립트를 먼저 실행하세요. 
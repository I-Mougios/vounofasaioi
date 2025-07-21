-- 1. Create the database
CREATE DATABASE IF NOT EXISTS vounofasaioi;

-- 2. Create the user (only if it doesn’t exist)
CREATE USER IF NOT EXISTS 'imougios'@'%' IDENTIFIED WITH mysql_native_password BY 'user_password';

-- 3. Grant access to the user on that database
GRANT ALL PRIVILEGES ON vounofasaioi.* TO 'imougios'@'%';

-- 4. Apply the privileges
FLUSH PRIVILEGES;
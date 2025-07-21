CREATE USER IF NOT EXISTS 'imougios'@'%' IDENTIFIED WITH mysql_native_password BY 'user_password';
GRANT ALL PRIVILEGES ON vounofasaioi.* TO 'imougios'@'%';
FLUSH PRIVILEGES;
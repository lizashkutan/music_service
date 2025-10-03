--1. Общее количество пользователей и прослушиваний
SELECT 
    COUNT(DISTINCT user_id) AS total_users,
    COUNT(*) AS total_listens
FROM listens;

-- 2. Количество пользователей по странам
SELECT country, COUNT(*) AS users_count
FROM users
GROUP BY country
ORDER BY users_count DESC;
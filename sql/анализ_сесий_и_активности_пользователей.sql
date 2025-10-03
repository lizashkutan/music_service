-- 6. Средняя длина сессии (в минутах)
SELECT AVG(session_duration) AS avg_session_minutes
FROM (
    SELECT session_id, EXTRACT(EPOCH FROM (MAX(listened_at) - MIN(listened_at)))/60 AS session_duration
    FROM listens
    GROUP BY session_id
) t;

-- 7. Пользователи, которые слушают больше всех треков
SELECT user_id, COUNT(*) AS total_listens
FROM listens
GROUP BY user_id
ORDER BY total_listens DESC
LIMIT 10;
-- 8. Популярные треки у новых пользователей (зарегистрированных < 6 месяцев)
SELECT t.title, COUNT(*) AS listens_count
FROM listens l
JOIN tracks t ON l.track_id = t.track_id
JOIN users u ON l.user_id = u.user_id
WHERE u.registration_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY t.track_id
ORDER BY listens_count DESC
LIMIT 10;

-- 9. Наиболее активные устройства
SELECT device, COUNT(*) AS listens_count
FROM listens
GROUP BY device
ORDER BY listens_count DESC;


-- 10. Артисты с наибольшим средним временем прослушивания трека
SELECT a.name, ROUND(AVG(l.duration_played),0) AS avg_played_seconds
FROM listens l
JOIN track_artists ta ON l.track_id = ta.track_id
JOIN artists a ON ta.artist_id = a.artist_id
GROUP BY a.artist_id
ORDER BY avg_played_seconds DESC
LIMIT 10;

-- 11. Среднее количество треков в сессии
SELECT AVG(tracks_count) AS avg_tracks_per_session
FROM (
    SELECT session_id, COUNT(*) AS tracks_count
    FROM listens
    GROUP BY session_id
) t;

-- 12. Сессии с наибольшей суммарной продолжительностью
SELECT session_id, SUM(duration_played) AS total_session_seconds
FROM listens
GROUP BY session_id
ORDER BY total_session_seconds DESC
LIMIT 10;

-- 13. Последовательность треков: какие треки чаще слушают подряд
SELECT track_id, next_track_id, COUNT(*) AS pair_count
FROM (
    SELECT 
        track_id,
        LEAD(track_id) OVER (PARTITION BY session_id ORDER BY listened_at) AS next_track_id
    FROM listens
) t
WHERE next_track_id IS NOT NULL
GROUP BY track_id, next_track_id
ORDER BY pair_count DESC
LIMIT 10;
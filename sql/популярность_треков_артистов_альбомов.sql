-- 3. Топ-10 самых прослушиваемых треков
SELECT t.title, a.name AS artist_name, COUNT(l.listen_id) AS listens_count
FROM listens l
JOIN tracks t ON l.track_id = t.track_id
JOIN track_artists ta ON t.track_id = ta.track_id
JOIN artists a ON ta.artist_id = a.artist_id
GROUP BY t.track_id, a.name
ORDER BY listens_count DESC
LIMIT 10;


-- 4. Топ-5 артистов по количеству прослушиваний
SELECT a.name AS artist_name, COUNT(l.listen_id) AS listens_count
FROM listens l
JOIN track_artists ta ON l.track_id = ta.track_id
JOIN artists a ON ta.artist_id = a.artist_id
GROUP BY a.artist_id
ORDER BY listens_count DESC
LIMIT 5;


-- 5. Топ-5 альбомов по прослушиваниям
SELECT al.title AS album_title, ar.name AS artist_name, COUNT(l.listen_id) AS listens_count
FROM listens l
JOIN tracks t ON l.track_id = t.track_id
JOIN albums al ON t.album_id = al.album_id
JOIN artists ar ON al.artist_id = ar.artist_id
GROUP BY al.album_id, ar.name
ORDER BY listens_count DESC
LIMIT 5;
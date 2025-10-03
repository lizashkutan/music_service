import psycopg2
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

CLIENT_ID = "4fafd0fc9e1448b98023bb53cb6fcc79"
CLIENT_SECRET = "9e70042a7184497ebfd76196b5515d77"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

sp = Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private playlist-read-collaborative"
))

# Подключение к PostgreSQL
conn = psycopg2.connect(
    dbname="music_service",
    user="postgres",
    password="5583liSH_J77",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Вставка данных в таблицы
def insert_artist(artist):
    cur.execute("""
        INSERT INTO artists (spotify_id, name)
        VALUES (%s, %s)
        ON CONFLICT (spotify_id) DO UPDATE SET name = EXCLUDED.name
        RETURNING artist_id;
    """, (artist["id"], artist["name"]))
    conn.commit()
    return cur.fetchone()[0]

def normalize_date(date_str):
    # Приводим release_date из Spotify к формату YYYY-MM-DD
    if len(date_str) == 4:      # только год
        return f"{date_str}-01-01"
    elif len(date_str) == 7:    # год-месяц
        return f"{date_str}-01"
    return date_str             # уже в формате YYYY-MM-DD

def insert_album(album, main_artist_id):
    release_date = normalize_date(album["release_date"])

    cur.execute("""
        INSERT INTO albums (spotify_id, title, release_date, artist_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (spotify_id) DO UPDATE SET title = EXCLUDED.title
        RETURNING album_id;
    """, (album["id"], album["name"], release_date, main_artist_id))
    conn.commit()
    return cur.fetchone()[0]


def insert_track(track, album_id):
    duration_seconds = track["duration_ms"] // 1000
    cur.execute("""
        INSERT INTO tracks (spotify_id, title, duration_seconds, album_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (spotify_id) DO NOTHING
        RETURNING track_id;
    """, (track["id"], track["name"], duration_seconds, album_id))
    res = cur.fetchone()
    if res:
        return res[0]
    else:
        cur.execute("SELECT track_id FROM tracks WHERE spotify_id = %s", (track["id"],))
        return cur.fetchone()[0]

def insert_track_artist(track_id, artist_id):
    cur.execute("""
        INSERT INTO track_artists (track_id, artist_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """, (track_id, artist_id))

# Обработка плейлистов
playlists = [
    "3sXmXMdnG7Jw0oLZpqRAfF",
    "28Qyhv057LsPXAGPRm3J8S",
    "48IvzHbLovDHoKqLuVr6dx",
    "4XOAfKUXxSLpaBmou3m4z2",
    "6wN555g8GN0SjS4F6fUICj",
    "3I3DPU6i9cQ3RSwMpVW91J",
]

for playlist_id in playlists:
    print(f"Загружаем треки из плейлиста {playlist_id} ...")

    results = sp.playlist_tracks(playlist_id, limit=50)
    while results:
        for item in results["items"]:
            track = item["track"]
            if track is None:
                continue

            album = track["album"]
            artists = track["artists"]

            # сохраняем основного артиста
            main_artist_id = insert_artist(sp.artist(artists[0]["id"]))

            # сохраняем альбом
            album_id = insert_album(album, main_artist_id)

            # сохраняем трек
            track_id = insert_track(track, album_id)

            # сохраняем всех артистов для трека
            for artist in artists:
                artist_id = insert_artist(sp.artist(artist["id"]))
                insert_track_artist(track_id, artist_id)

        # если есть следующая страница — загружаем
        if results["next"]:
            results = sp.next(results)
        else:
            results = None

conn.commit()
cur.close()
conn.close()

print("Треки из всех плейлистов загружены в PostgreSQL")

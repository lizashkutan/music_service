import psycopg2
import pandas as pd

#Делаем sample из большого CSV
def create_sample(input_csv, output_csv, sample_size=5000):
    df = pd.read_csv(input_csv)
    df_sample = df.sample(sample_size, random_state=42)
    df_sample.to_csv(output_csv, index=False)
    print(f"Создан файл {output_csv} с {len(df_sample)} строками")


conn = psycopg2.connect(
    dbname="music_service",
    user="postgres",
    password="5583liSH_J77",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

#Вставка данных
def insert_artist(name):
    cur.execute("SELECT artist_id FROM artists WHERE name = %s", (name,))
    res = cur.fetchone()
    if res:
        return res[0]

    cur.execute("INSERT INTO artists (name) VALUES (%s) RETURNING artist_id;", (name,))
    return cur.fetchone()[0]

def insert_album(title, main_artist_id, spotify_id=None, release_date=None):
    cur.execute("""
        INSERT INTO albums (title, artist_id, spotify_id, release_date)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (spotify_id) DO UPDATE SET title = EXCLUDED.title
        RETURNING album_id;
    """, (title, main_artist_id, spotify_id, release_date))
    return cur.fetchone()[0]

def insert_track(title, duration_seconds, album_id, spotify_id):
    cur.execute("""
        INSERT INTO tracks (title, duration_seconds, album_id, spotify_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (spotify_id) DO UPDATE SET title = EXCLUDED.title
        RETURNING track_id;
    """, (title, duration_seconds, album_id, spotify_id))
    return cur.fetchone()[0]

def insert_track_artist(track_id, artist_id):
    cur.execute("""
        INSERT INTO track_artists (track_id, artist_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """, (track_id, artist_id))

# Загрузка sample-CSV в базу
def load_from_kaggle(csv_path):
    df = pd.read_csv(csv_path)

    for i, row in df.iterrows():
        spotify_id = row["track_id"]
        title = row["track_name"]
        album_title = row["album_name"]
        duration_seconds = int(row["duration_ms"] // 1000)

        artists = [a.strip() for a in str(row["artists"]).split(";")]

        if not artists:
            continue

        # основной артист
        main_artist_id = insert_artist(artists[0])

        # альбом
        album_id = insert_album(album_title, main_artist_id)

        # трек
        track_id = insert_track(title, duration_seconds, album_id, spotify_id)

        # все артисты
        for artist_name in artists:
            artist_id = insert_artist(artist_name)
            insert_track_artist(track_id, artist_id)

        # фиксация каждые 1000 строк
        if i % 1000 == 0 and i > 0:
            conn.commit()
            print(f"Зафиксировано {i} строк")

    conn.commit()
    print("Kaggle данные успешно загружены")

# Запуск
if __name__ == "__main__":
    create_sample("dataset.csv", "dataset_sample.csv", sample_size=5000)
    load_from_kaggle("dataset_sample.csv")
    cur.close()
    conn.close()

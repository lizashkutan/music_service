import psycopg2
import random
import uuid
from datetime import timedelta
from faker import Faker

fake = Faker()

conn = psycopg2.connect(
    dbname="music_service",
    user="postgres",
    password="5583liSH_J77",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

#Настройки генерации
NUM_USERS = 1000
NUM_SESSIONS = 5000
MIN_TRACKS_PER_SESSION = 10
MAX_TRACKS_PER_SESSION = 30
COUNTRIES = ["US", "GB", "RU", "DE", "FR", "IT", "ES", "BR", "JP", "IN"]
DEVICES = ["mobile", "desktop", "web", "smart_speaker"]

#Генерация пользователей
users_data = []
for _ in range(NUM_USERS):
    username = fake.user_name()
    country = random.choice(COUNTRIES)
    registration_date = fake.date_between(start_date="-5y", end_date="today")
    users_data.append((username, country, registration_date))

# Вставляем всех пользователей за один execute
args_str = ','.join(cur.mogrify("(%s,%s,%s)", x).decode('utf-8') for x in users_data)
cur.execute("INSERT INTO users (username, country, registration_date) VALUES " + args_str)
conn.commit()
print(f"Сгенерировано {NUM_USERS} пользователей")

#Загрузка пользователей и треков из базы
cur.execute("SELECT user_id FROM users")
user_ids = [u[0] for u in cur.fetchall()]

cur.execute("SELECT track_id, duration_seconds FROM tracks")
tracks = cur.fetchall()

#Генерация прослушиваний
listens_data = []
for _ in range(NUM_SESSIONS):
    user_id = random.choice(user_ids)
    device = random.choice(DEVICES)
    session_id = str(uuid.uuid4())
    start_time = fake.date_time_between(start_date="-2y", end_date="now")

    n_tracks = random.randint(MIN_TRACKS_PER_SESSION, MAX_TRACKS_PER_SESSION)
    current_time = start_time

    for _ in range(n_tracks):
        track_id, track_duration = random.choice(tracks)

        #генерация duration_played
        min_play = max(1, int(track_duration * 0.5))
        max_play = max(min_play, track_duration)
        duration_played = random.randint(min_play, max_play)

        listens_data.append((
            user_id,
            track_id,
            current_time,
            device,
            duration_played,
            session_id
        ))

        current_time += timedelta(seconds=int(duration_played * random.uniform(0.8, 1.2)))

# Вставляем все прослушивания
BATCH_SIZE = 5000
for i in range(0, len(listens_data), BATCH_SIZE):
    batch = listens_data[i:i + BATCH_SIZE]
    args_str = ','.join(cur.mogrify("(%s,%s,%s,%s,%s,%s)", x).decode('utf-8') for x in batch)
    cur.execute(
        "INSERT INTO listens (user_id, track_id, listened_at, device, duration_played, session_id) VALUES " + args_str)
    conn.commit()
    print(f"Вставлено {i + len(batch)} прослушиваний")

cur.close()
conn.close()
print(f"Сгенерировано {len(listens_data)} прослушиваний в {NUM_SESSIONS} сессиях")

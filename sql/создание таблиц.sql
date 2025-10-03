CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    country VARCHAR(2),
    registration_date DATE NOT NULL
);

CREATE TABLE artists (
    artist_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
	spotify_id VARCHAR(50) UNIQUE
);


CREATE TABLE albums (
    album_id BIGSERIAL PRIMARY KEY,
    artist_id BIGINT REFERENCES artists(artist_id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    release_date DATE,
	spotify_id VARCHAR(50) UNIQUE
);

CREATE TABLE tracks (
    track_id BIGSERIAL PRIMARY KEY,
    album_id BIGINT REFERENCES albums(album_id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    duration_seconds INT NOT NULL,
	spotify_id VARCHAR(50) UNIQUE
);

CREATE TABLE track_artists (
    track_id BIGINT REFERENCES tracks(track_id) ON DELETE CASCADE,
    artist_id BIGINT REFERENCES artists(artist_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, artist_id)
);


CREATE TABLE listens (
    listen_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    track_id BIGINT REFERENCES tracks(track_id) ON DELETE CASCADE,
    listened_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    device VARCHAR(50),
    duration_played INT NOT NULL,
    session_id UUID
);

CREATE INDEX idx_listens_user_time ON listens (user_id, listened_at);
CREATE INDEX idx_listens_track_time ON listens (track_id, listened_at);

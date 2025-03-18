from db.connection import connect_db

def insert_artist(name, url):
    db = connect_db()
    cursor = db.cursor()
    query = "INSERT INTO artists (name, url) VALUES (%s, %s)"
    cursor.execute(query, (name, url))
    db.commit()
    cursor.close()
    db.close()

def insert_albums(name, cover_url, buy_url):
    db = connect_db()
    cursor = db.cursor()
    query = "INSERT INTO albums (name, cover_url, buy_url) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, cover_url, buy_url))
    db.commit()
    cursor.close()
    db.close()

def insert_track(name, youtube_url):
    db = connect_db()
    cursor = db.cursor()
    query = "INSERT INTO tracks (name, youtube_url) VALUES (%s, %s)"
    cursor.execute(query, (name, youtube_url))
    db.commit()
    cursor.close()
    db.close()

def insert_user(name, email):
    db = connect_db()
    cursor = db.cursor()
    query = "INSERT INTO users (name, email) VALUES (%s, %s)"
    cursor.execute(query, (name, email))
    db.commit()
    cursor.close()
    db.close()

def insert_playlist(name, user_id, mood1_id, mood2_id):
    db = connect_db()
    cursor = db.cursor()
    query = "INSERT INTO playlists (name, user_id, mood1_id, mood2_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, user_id, mood1_id, mood2_id))
    db.commit()
    cursor.close()
    db.close()

def insert_mood(name):
    db = connect_db()
    cursor = db.cursor()
    query = "INSERT INTO moods (name) VALUES (%s)"
    cursor.execute(query, (name))
    db.commit()
    cursor.close()
    db.close()
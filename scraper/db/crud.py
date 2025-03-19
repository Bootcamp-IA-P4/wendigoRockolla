from scraper.db.connection import connect_db

def insert_artist(name, url):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO artists (name, url) VALUES (%s, %s)"
        cursor.execute(query, (name, url))
        db.commit()
    except Exception as e:
        print(f"Error inserting artist: {e}")
    finally:
        cursor.close()
        db.close()

def insert_albums(name, cover_url, buy_url):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO albums (name, cover_url, buy_url) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, cover_url, buy_url))
        db.commit()
    except Exception as e:
        print(f"Error inserting album: {e}")
    finally:
        cursor.close()
        db.close()

def insert_song(name, youtube_url):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO songs (name, youtube_url) VALUES (%s, %s)"
        cursor.execute(query, (name, youtube_url))
        db.commit()
    except Exception as e:
        print(f"Error inserting song: {e}")
    finally:
        cursor.close()
        db.close()

def insert_user(name, email):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        cursor.execute(query, (name, email))
        db.commit()
    except Exception as e:
        print(f"Error inserting user: {e}")
    finally:
        cursor.close()
        db.close()

def insert_playlist(name, user_id, mood1_id, mood2_id):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO playlists (name, user_id, mood1_id, mood2_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, user_id, mood1_id, mood2_id))
        db.commit()
    except Exception as e:
        print(f"Error inserting playlist: {e}")
    finally:
        cursor.close()
        db.close()

def insert_mood(name):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO moods (name) VALUES (%s)"
        cursor.execute(query, (name,))
        db.commit()
    except Exception as e:
        print(f"Error inserting mood: {e}")
    finally:
        cursor.close()
        db.close()

def get_data(query, search_type):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    
    if search_type == 'mood':
        cursor.execute("SELECT * FROM moods WHERE name LIKE %s", ('%' + query + '%',))
    elif search_type == 'artist':
        cursor.execute("SELECT * FROM artists WHERE name LIKE %s", ('%' + query + '%',))
    elif search_type == 'song':
        cursor.execute("SELECT * FROM songs WHERE name LIKE %s", ('%' + query + '%',))
    
    results = cursor.fetchall()
    cursor.close()
    db.close()
    
    return results
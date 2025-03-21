import os
import sys
# Usar try/except para manejar las importaciones de forma más robusta
try:
    # Primero intenta importar como si estuviera en el scraper
    from db.connection import connect_db
except ImportError:
    # Si falla, intenta importar como si estuviera desde app.py
    from scraper.db.connection import connect_db

def get_all_moods():
    try:
        db = connect_db()
        cursor = db.cursor(dictionary=True)
        
        # Primero verificamos si la columna url existe
        cursor.execute("SHOW COLUMNS FROM moods LIKE 'url'")
        column_exists = cursor.fetchone()
        
        if column_exists:
            query = "SELECT id, name, url FROM moods"
        else:
            query = "SELECT id, name FROM moods"
            
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db.close()
        return results
    except Exception as e:
        print(f"Error retrieving moods: {e}")
        return []

def insert_artist(name, url):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO artists (name, url) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=name"
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
        query = "INSERT INTO albums (name, cover_url, buy_url) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE name=name"
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
        query = "INSERT INTO songs (name, youtube_url) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=name"
        cursor.execute(query, (name, youtube_url))
        db.commit()
    except Exception as e:
        print(f"Error inserting song: {e}")
    finally:
        cursor.close()
        db.close()

def insert_mood(name):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO moods (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=name"
        cursor.execute(query, (name,))
        db.commit()
    except Exception as e:
        print(f"Error inserting mood: {e}")
    finally:
        cursor.close()
        db.close()

def get_mood_id(name):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT id FROM moods WHERE name = %s"
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error retrieving mood ID: {e}")
    finally:
        cursor.close()
        db.close()

def update_mood_url(mood_name, url):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "UPDATE moods SET url = %s WHERE name = %s"
        cursor.execute(query, (url, mood_name))
        db.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        db.close()
        return affected_rows > 0
    except Exception as e:
        print(f"Error updating mood URL for '{mood_name}': {e}")
        return False

def insert_mood_song(mood_id, song_id):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO mood_songs (mood_id, song_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE mood_id=mood_id"
        cursor.execute(query, (mood_id, song_id))
        db.commit()
    except Exception as e:
        print(f"Error inserting mood_song: {e}")
    finally:
        cursor.close()
        db.close()

def insert_mood_album(mood_id, album_id):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "INSERT INTO mood_albums (mood_id, album_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE mood_id=mood_id"
        cursor.execute(query, (mood_id, album_id))
        db.commit()
    except Exception as e:
        print(f"Error inserting mood_album: {e}")
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

def get_album_id(name):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT id FROM albums WHERE name = %s"
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error retrieving album ID: {e}")
    finally:
        cursor.close()
        db.close()

def get_song_id(name):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT id FROM songs WHERE name = %s"
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error retrieving song ID: {e}")
    finally:
        cursor.close()
        db.close()
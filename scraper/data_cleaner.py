import pandas as pd
from db.connection import connect_db

# python data_cleaner.py

def fetch_data():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    
    cursor.execute("SELECT * FROM albums")
    albums = cursor.fetchall()
    
    cursor.execute("SELECT * FROM artists")
    artists = cursor.fetchall()
    
    cursor.execute("SELECT * FROM moods")
    moods = cursor.fetchall()
    
    cursor.execute("SELECT * FROM mood_songs")
    mood_songs = cursor.fetchall()
    
    cursor.execute("SELECT * FROM mood_albums")
    mood_albums = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return songs, albums, artists, moods, mood_songs, mood_albums

def remove_duplicates_in_db():
    """
    Esta función elimina filas duplicadas directamente en la base de datos,
    manteniendo solo la entrada con el ID más bajo para cada nombre.
    """
    db = connect_db()
    cursor = db.cursor()
    
    # Eliminar duplicados de songs basados en name
    print("Eliminando duplicados de songs...")
    cursor.execute("""
        CREATE TEMPORARY TABLE temp_songs AS
        SELECT MIN(id) as id
        FROM songs
        GROUP BY name
    """)
    cursor.execute("""
        DELETE FROM mood_songs 
        WHERE song_id NOT IN (SELECT id FROM temp_songs)
    """)
    cursor.execute("""
        DELETE FROM songs 
        WHERE id NOT IN (SELECT id FROM temp_songs)
    """)
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_songs")
    
    # Eliminar duplicados de albums basados en name
    print("Eliminando duplicados de albums...")
    cursor.execute("""
        CREATE TEMPORARY TABLE temp_albums AS
        SELECT MIN(id) as id
        FROM albums
        GROUP BY name
    """)
    cursor.execute("""
        DELETE FROM mood_albums 
        WHERE album_id NOT IN (SELECT id FROM temp_albums)
    """)
    cursor.execute("""
        DELETE FROM albums 
        WHERE id NOT IN (SELECT id FROM temp_albums)
    """)
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_albums")
    
    # Eliminar duplicados de artists basados en name
    print("Eliminando duplicados de artists...")
    cursor.execute("""
        CREATE TEMPORARY TABLE temp_artists AS
        SELECT MIN(id) as id
        FROM artists
        GROUP BY name
    """)
    cursor.execute("""
        DELETE FROM artists 
        WHERE id NOT IN (SELECT id FROM temp_artists)
    """)
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_artists")
    
    # Eliminar duplicados de moods basados en name
    print("Eliminando duplicados de moods...")
    cursor.execute("""
        CREATE TEMPORARY TABLE temp_moods AS
        SELECT MIN(id) as id
        FROM moods
        GROUP BY name
    """)
    cursor.execute("""
        DELETE FROM mood_songs 
        WHERE mood_id NOT IN (SELECT id FROM temp_moods)
    """)
    cursor.execute("""
        DELETE FROM mood_albums 
        WHERE mood_id NOT IN (SELECT id FROM temp_moods)
    """)
    cursor.execute("""
        DELETE FROM moods 
        WHERE id NOT IN (SELECT id FROM temp_moods)
    """)
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_moods")
    
    # Eliminar duplicados en tablas de relaciones
    print("Eliminando duplicados en relaciones mood_songs...")
    cursor.execute("""
        CREATE TEMPORARY TABLE temp_mood_songs AS
        SELECT MIN(id) as id
        FROM mood_songs
        GROUP BY mood_id, song_id
    """)
    cursor.execute("""
        DELETE FROM mood_songs 
        WHERE id NOT IN (SELECT id FROM temp_mood_songs)
    """)
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_mood_songs")
    
    print("Eliminando duplicados en relaciones mood_albums...")
    cursor.execute("""
        CREATE TEMPORARY TABLE temp_mood_albums AS
        SELECT MIN(id) as id
        FROM mood_albums
        GROUP BY mood_id, album_id
    """)
    cursor.execute("""
        DELETE FROM mood_albums 
        WHERE id NOT IN (SELECT id FROM temp_mood_albums)
    """)
    cursor.execute("DROP TEMPORARY TABLE IF EXISTS temp_mood_albums")
    
    db.commit()
    cursor.close()
    db.close()
    print("Duplicados eliminados de la base de datos.")

def clean_and_organize_data():
    songs, albums, artists, moods, mood_songs, mood_albums = fetch_data()
    
    # Convertir a DataFrames de pandas
    df_songs = pd.DataFrame(songs)
    df_albums = pd.DataFrame(albums)
    df_artists = pd.DataFrame(artists)
    df_moods = pd.DataFrame(moods)
    df_mood_songs = pd.DataFrame(mood_songs)
    df_mood_albums = pd.DataFrame(mood_albums)
    
    # Imprimir información antes de la limpieza
    print("Antes de la limpieza (en pandas):")
    print(f"Songs: {df_songs.shape}")
    print(f"Albums: {df_albums.shape}")
    print(f"Artists: {df_artists.shape}")
    print(f"Moods: {df_moods.shape}")
    print(f"Mood-Songs relationships: {df_mood_songs.shape}")
    print(f"Mood-Albums relationships: {df_mood_albums.shape}")
    
    # Limpiar y organizar los datos
    df_songs.drop_duplicates(subset=['name'], inplace=True)
    df_albums.drop_duplicates(subset=['name'], inplace=True)
    df_artists.drop_duplicates(subset=['name'], inplace=True)
    df_moods.drop_duplicates(subset=['name'], inplace=True)
    df_mood_songs.drop_duplicates(subset=['mood_id', 'song_id'], inplace=True)
    df_mood_albums.drop_duplicates(subset=['mood_id', 'album_id'], inplace=True)
    
    # Imprimir información después de la limpieza
    print("\nDespués de la limpieza (en pandas):")
    print(f"Songs: {df_songs.shape}")
    print(f"Albums: {df_albums.shape}")
    print(f"Artists: {df_artists.shape}")
    print(f"Moods: {df_moods.shape}")
    print(f"Mood-Songs relationships: {df_mood_songs.shape}")
    print(f"Mood-Albums relationships: {df_mood_albums.shape}")
    
    # Guardar los DataFrames limpios en archivos CSV
    df_songs.to_csv('clean_songs.csv', index=False)
    df_albums.to_csv('clean_albums.csv', index=False)
    df_artists.to_csv('clean_artists.csv', index=False)
    df_moods.to_csv('clean_moods.csv', index=False)
    df_mood_songs.to_csv('clean_mood_songs.csv', index=False)
    df_mood_albums.to_csv('clean_mood_albums.csv', index=False)
    
    print("\nArchivos CSV generados correctamente.")

if __name__ == "__main__":
    print("=== LIMPIEZA DE DUPLICADOS EN PANDAS (para CSV) ===")
    clean_and_organize_data()
    
    print("\n=== ELIMINACIÓN DE DUPLICADOS EN LA BASE DE DATOS ===")
    remove_duplicates_in_db()
    
    # Verificar cambios después de limpiar la BD
    songs, albums, artists, moods, mood_songs, mood_albums = fetch_data()
    print("\nResultados después de limpiar la base de datos:")
    print(f"Songs: {len(songs)}")
    print(f"Albums: {len(albums)}")
    print(f"Artists: {len(artists)}")
    print(f"Moods: {len(moods)}")
    print(f"Mood-Songs relationships: {len(mood_songs)}")
    print(f"Mood-Albums relationships: {len(mood_albums)}")
    print("\n¡Limpieza completada!🐼")
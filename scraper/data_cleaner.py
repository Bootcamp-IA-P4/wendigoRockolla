import pandas as pd
from db.connection import connect_db

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
    print("Antes de la limpieza:")
    print(f"Songs: {df_songs.shape}")
    print(f"Albums: {df_albums.shape}")
    print(f"Artists: {df_artists.shape}")
    print(f"Moods: {df_moods.shape}")
    
    # Limpiar y organizar los datos
    # Aquí puedes agregar cualquier lógica de limpieza que necesites
    # Por ejemplo, eliminar duplicados:
    df_songs.drop_duplicates(subset=['name'], inplace=True)
    df_albums.drop_duplicates(subset=['name'], inplace=True)
    df_artists.drop_duplicates(subset=['name'], inplace=True)
    df_moods.drop_duplicates(subset=['name'], inplace=True)
    
    # Imprimir información después de la limpieza
    print("Después de la limpieza:")
    print(f"Songs: {df_songs.shape}")
    print(f"Albums: {df_albums.shape}")
    print(f"Artists: {df_artists.shape}")
    print(f"Moods: {df_moods.shape}")
    
    # Guardar los DataFrames limpios en archivos CSV
    df_songs.to_csv('clean_songs.csv', index=False)
    df_albums.to_csv('clean_albums.csv', index=False)
    df_artists.to_csv('clean_artists.csv', index=False)
    df_moods.to_csv('clean_moods.csv', index=False)
    df_mood_songs.to_csv('clean_mood_songs.csv', index=False)
    df_mood_albums.to_csv('clean_mood_albums.csv', index=False)

if __name__ == "__main__":
    clean_and_organize_data()
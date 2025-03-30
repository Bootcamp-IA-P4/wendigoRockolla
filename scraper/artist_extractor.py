import re
from db.connection import connect_db

def extract_artist_name_from_url(url):
    """
    Extrae el nombre del artista desde una URL de AllMusic
    Por ejemplo: https://www.allmusic.com/artist/lady-gaga-mn0000994823 -> lady gaga
    """
    if not url or "artist" not in url:
        return None
        
    # Obtener el segmento del artista de la URL
    try:
        # Buscar el patrón /artist/nombre-artista-mnnumeros
        pattern = r'/artist/([^/]+)-mn\d+'
        match = re.search(pattern, url)
        
        if match:
            artist_slug = match.group(1)
            # Reemplazar guiones por espacios y mejorar formato
            artist_name = artist_slug.replace('-', ' ')
            # Capitalizar palabras
            artist_name = ' '.join(word.capitalize() for word in artist_name.split())
            return artist_name
    except:
        pass
    
    return None

def clean_complex_artist_names(artist_name):
    """
    Limpia nombres complejos de artistas, quedándose solo con el primero
    Por ejemplo: "Marc Ribot / Marc Ribot's Ceramic Dog" -> "Marc Ribot"
    """
    if not artist_name:
        return artist_name
        
    # Buscar separadores comunes y quedarse con la primera parte
    separators = [' / ', '/', ' & ', ' and ', ' with ', ' feat. ', ' ft. ', ' featuring ']
    
    for separator in separators:
        if separator in artist_name:
            return artist_name.split(separator)[0].strip()
            
    return artist_name

def update_unknown_artists():
    """
    Actualiza artistas desconocidos basándose en la información de las URLs
    """
    db = connect_db()
    cursor = db.cursor()
    
    # Obtener todas las canciones con "Artista Desconocido" pero que tienen youtube_url
    cursor.execute("""
        SELECT id, name, artist, youtube_url
        FROM songs
        WHERE (artist = 'Artista Desconocido' OR artist = 'Artista desconocido' OR artist IS NULL OR artist = '')
        AND youtube_url IS NOT NULL
        AND youtube_url != ''
    """)
    
    unknown_songs = cursor.fetchall()
    print(f"Encontradas {len(unknown_songs)} canciones con artista desconocido pero con URL.")
    
    updated_count = 0
    
    for song in unknown_songs:
        song_id = song[0]
        song_name = song[1]
        current_artist = song[2] or "Ninguno"
        youtube_url = song[3]
        
        # Intentar extraer el nombre del artista de la URL
        artist_name = extract_artist_name_from_url(youtube_url)
        
        if artist_name:
            # Limpiar nombre en caso de ser compuesto
            artist_name = clean_complex_artist_names(artist_name)
            
            # Actualizar el registro en la base de datos
            cursor.execute(
                "UPDATE songs SET artist = %s WHERE id = %s",
                (artist_name, song_id)
            )
            db.commit()
            
            print(f"✅ Actualizada canción ID {song_id} - '{song_name}': '{current_artist}' → '{artist_name}'")
            updated_count += 1
    
    # Ahora limpiamos los nombres complejos de artistas (que tengan separadores)
    # Modificar esta consulta para solo incluir canciones que tienen URL
    cursor.execute("""
        SELECT id, name, artist, youtube_url
        FROM songs
        WHERE (artist LIKE '%/%' 
           OR artist LIKE '%&%'
           OR artist LIKE '% and %'
           OR artist LIKE '% with %'
           OR artist LIKE '% feat.%'
           OR artist LIKE '% ft.%'
           OR artist LIKE '% featuring %')
        AND youtube_url IS NOT NULL
        AND youtube_url != ''
    """)
    
    complex_artists = cursor.fetchall()
    print(f"\nEncontradas {len(complex_artists)} canciones con nombres de artistas complejos.")
    
    for song in complex_artists:
        song_id = song[0]
        song_name = song[1]
        current_artist = song[2]
        youtube_url = song[3]  # Añadir esta línea
        
        # Limpiar el nombre del artista
        simplified_artist = clean_complex_artist_names(current_artist)
        
        if simplified_artist != current_artist:
            # Actualizar el registro en la base de datos
            cursor.execute(
                "UPDATE songs SET artist = %s WHERE id = %s",
                (simplified_artist, song_id)
            )
            db.commit()
            
            print(f"🔄 Simplificado artista para canción ID {song_id} - '{song_name}': '{current_artist}' → '{simplified_artist}'")
            updated_count += 1
    
    cursor.close()
    db.close()
    
    print(f"\n✨ Proceso completado. Se actualizaron {updated_count} registros en total.")
    
if __name__ == "__main__":
    print("=== EXTRACCIÓN Y ACTUALIZACIÓN DE NOMBRES DE ARTISTAS ===")
    update_unknown_artists()

# python artist_extractor.py
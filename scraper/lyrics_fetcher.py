import sys
import time
import random
from pathlib import Path

# Añadir el directorio principal al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.connection import connect_db
from services.genius_service import search_song, get_song_lyrics

def get_songs_without_lyrics(limit=None):
    """Obtiene canciones que no tienen letras en la base de datos"""
    try:
        db = connect_db()
        cursor = db.cursor(dictionary=True)
        
        # Modificada para buscar en la tabla songs donde lyrics es NULL o vacío
        query = """
            SELECT id, name, artist FROM songs
            WHERE (lyrics IS NULL OR lyrics = '')
            AND artist IS NOT NULL
            AND artist != 'Artista Desconocido'
            AND artist != ''
        """
        
        if limit:
            query += f" LIMIT {limit}"
            
        cursor.execute(query)
        songs = cursor.fetchall()
        
        cursor.close()
        db.close()
        return songs
    except Exception as e:
        print(f"Error obteniendo canciones sin letras: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_lyrics(song_id, lyrics_text):
    """Guarda las letras directamente en la tabla songs"""
    try:
        db = connect_db()
        cursor = db.cursor()
        
        # Actualizar directamente en la tabla songs - SIN updated_at
        cursor.execute(
            "UPDATE songs SET lyrics = %s WHERE id = %s",
            (lyrics_text, song_id)
        )
            
        db.commit()
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"Error guardando letras: {e}")
        import traceback
        traceback.print_exc()
        return False

def fetch_and_save_lyrics(batch_size=50, total_limit=None):
    """Obtiene y guarda letras para canciones que no las tienen"""
    print("=== OBTENIENDO LETRAS DE CANCIONES ===")
    
    # Obtener canciones sin letras
    songs = get_songs_without_lyrics(total_limit)
    total_songs = len(songs)
    
    print(f"Encontradas {total_songs} canciones sin letras")
    
    if total_songs == 0:
        print("No hay canciones para procesar")
        return
    
    # Contadores para estadísticas
    success_count = 0
    failure_count = 0
    
    # Procesar en lotes para evitar sobrecargar la API
    for i, song in enumerate(songs):
        song_id = song['id']
        song_name = song['name']
        artist_name = song['artist']
        
        print(f"\n[{i+1}/{total_songs}] Procesando: '{song_name}' por {artist_name}")
        
        try:
            # Buscar la canción en Genius
            hits = search_song(song_name, artist_name)
            
            if not hits:
                print(f"❌ No se encontraron resultados para '{song_name}' por {artist_name}")
                failure_count += 1
                continue
            
            # Obtener la URL de la primera coincidencia
            genius_url = hits[0]['result']['url']
            print(f"🔎 Encontrada en Genius: {genius_url}")
            
            # Extraer letras
            lyrics = get_song_lyrics(genius_url)
            
            if not lyrics or lyrics.startswith("Error") or lyrics == "No se pudieron extraer las letras.":
                print(f"❌ No se pudieron obtener letras: {lyrics}")
                failure_count += 1
                continue
                
            # Mostrar fragmento de las letras
            preview = lyrics[:100] + "..." if len(lyrics) > 100 else lyrics
            print(f"📝 Letras obtenidas: {preview}")
            
            # Guardar en la base de datos
            if save_lyrics(song_id, lyrics):
                print(f"✅ Letras guardadas para '{song_name}'")
                success_count += 1
            else:
                print(f"❌ Error al guardar letras para '{song_name}'")
                failure_count += 1
                
            # Añadir pausa para evitar limitaciones de la API
            if (i + 1) % batch_size == 0:
                pause_time = random.randint(5, 15)
                print(f"\n⏱️ Pausa de {pause_time} segundos para evitar limitaciones de API...")
                time.sleep(pause_time)
                
        except Exception as e:
            print(f"❌ Error procesando '{song_name}': {e}")
            failure_count += 1
            continue
    
    # Mostrar resumen final
    print("\n=== RESUMEN ===")
    print(f"Total de canciones procesadas: {total_songs}")
    print(f"✅ Letras obtenidas con éxito: {success_count}")
    print(f"❌ Canciones sin letras: {failure_count}")
    print("===============")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Obtener letras de canciones de Genius')
    parser.add_argument('--limit', type=int, help='Número máximo de canciones a procesar')
    parser.add_argument('--batch', type=int, default=25, help='Tamaño del lote para pausas')
    
    args = parser.parse_args()
    
    fetch_and_save_lyrics(batch_size=args.batch, total_limit=args.limit)

#     # Para procesar todas las canciones sin letras
# python scripts/lyrics_fetcher.py

# # Para limitar a cierta cantidad de canciones
# python scripts/lyrics_fetcher.py --limit 100

# # Para ajustar el tamaño del lote (para pausas entre consultas a la API)
# python scripts/lyrics_fetcher.py --batch 10 --limit 50
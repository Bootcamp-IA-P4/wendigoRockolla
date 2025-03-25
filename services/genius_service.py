import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")
BASE_URL = "https://api.genius.com"
HEADERS = {"Authorization": f"Bearer {GENIUS_API_KEY}"}

def search_song(song_name, artist_name=None):
    """
    Busca una canción en Genius por nombre y (opcionalmente) artista
    """
    search_term = f"{song_name} {artist_name}" if artist_name else song_name
    endpoint = f"{BASE_URL}/search"
    params = {"q": search_term}
    
    response = requests.get(endpoint, headers=HEADERS, params=params)
    data = response.json()
    
    if response.status_code == 200:
        hits = data.get("response", {}).get("hits", [])
        if hits:
            return hits
    
    return []

def get_song_lyrics(url):
    """Extrae la letra de una canción de Genius"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Intenta encontrar el contenedor de letras
        lyrics_containers = [
            soup.select_one('div[data-lyrics-container="true"]'),
            soup.select_one('.lyrics'),
            soup.select_one('div.SongPageGrid-sc-1vi6xda-0')
        ]
        
        lyrics_container = next((container for container in lyrics_containers if container), None)
        
        if lyrics_container:
            # Reemplazar <br> por salto de línea y luego eliminar todas las etiquetas HTML
            lyrics = lyrics_container.get_text(separator='\n')
            
            # Eliminar [?] y espacios en blanco/saltos de línea excesivos
            lyrics = re.sub(r'\[.*?\]', '', lyrics)
            lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)
            lyrics = lyrics.strip()
            
            return lyrics
            
        return "No se pudieron extraer las letras."
    except Exception as e:
        print(f"Error al obtener letras: {e}")
        return f"Error al obtener letras: {str(e)}"

def get_song_details(song_id):
    """
    Obtiene detalles de una canción por ID
    """
    endpoint = f"{BASE_URL}/songs/{song_id}"
    response = requests.get(endpoint, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("response", {}).get("song", {})
    
    return {}

def search_and_get_details(song_name, artist_name=None):
    """
    Busca una canción por nombre y artista, y devuelve sus detalles
    """
    hits = search_song(song_name, artist_name)
    if not hits:
        return None
    
    # Tomar el primer resultado (más relevante)
    song_id = hits[0].get('result', {}).get('id')
    if not song_id:
        return None
    
    # Obtener los detalles completos
    return get_song_details(song_id)
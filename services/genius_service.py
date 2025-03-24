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

def get_song_lyrics(song_url):
    """
    Extrae la letra de una canción desde su URL en Genius
    """
    try:
        response = requests.get(song_url)
        if response.status_code != 200:
            return "No se pudo obtener la letra"
            
        # Usar BeautifulSoup para extraer la letra
        soup = BeautifulSoup(response.text, 'html.parser')
        lyrics_div = soup.find("div", class_=re.compile("Lyrics__Container"))
        
        if not lyrics_div:
            return "Letra no disponible"
            
        # Extraer la letra y preservar formato
        lyrics = ""
        for element in lyrics_div:
            if element.name == "br":
                lyrics += "\n"
            elif element.string:
                lyrics += element.string
        
        return lyrics.strip()
    except Exception as e:
        return f"Error al obtener la letra: {str(e)}"

def get_song_details(song_id):
    """
    Obtiene detalles de una canción por ID
    """
    endpoint = f"{BASE_URL}/songs/{song_id}"
    response = requests.get(endpoint, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("response", {}).get("song", {})
    
    return {}
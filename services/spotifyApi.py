import os
import base64
import requests
import re
import urllib.parse
from datetime import datetime, timedelta
from flask import session, redirect, url_for, request
from dotenv import load_dotenv
from scraper.db.connection import connect_db

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1/"

SCOPES = [
    "user-read-private",
    "user-read-email",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-top-read",
    "user-read-recently-played"
]

def get_auth_url():
    """Construye la URL para autorización OAuth de Spotify"""
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "show_dialog": True
    }
    
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return auth_url

def get_token_info(authorization_code=None):
    """Obtiene un token de acceso usando el código de autorización"""
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    if authorization_code:
        # Exchange authorization code for access token
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI
        }
    else:
        # Use refresh token to get new access token
        refresh_token = session.get("refresh_token")
        if not refresh_token:
            return None
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        token_info = response.json()
        
        # Calculate token expiration time
        now = datetime.now()
        token_info["expires_at"] = (now + timedelta(seconds=token_info["expires_in"])).timestamp()
        
        return token_info
    
    return None

def get_access_token():
    """
    Obtiene un token de acceso válido, actualizándolo si es necesario
    """
    token_info = session.get("token_info")
    
    if not token_info:
        # No token info available, redirect to authentication
        return None
    
    # Check if token has expired
    now = datetime.now().timestamp()
    
    if now >= token_info["expires_at"]:
        # Token has expired, refresh it
        new_token_info = get_token_info()
        if not new_token_info:
            # Could not refresh token
            return None
        
        # Update token info in session
        session["token_info"] = new_token_info
        token_info = new_token_info
    
    return token_info["access_token"]

def make_api_request(endpoint, method="GET", data=None):
    """
    Realiza una solicitud a la API de Spotify
    """
    access_token = get_access_token()
    if not access_token:
        return {"error": "No access token available"}
    
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{API_BASE_URL}{endpoint}"
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        headers["Content-Type"] = "application/json"
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        headers["Content-Type"] = "application/json"
        response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201, 204]:
        if response.content:
            return response.json()
        return {"success": True}
    
    return {"error": f"Error {response.status_code}: {response.text}"}

def search_tracks(query, limit=10):
    """
    Busca canciones en Spotify
    """
    endpoint = f"search?q={urllib.parse.quote(query)}&type=track&limit={limit}"
    return make_api_request(endpoint)

def get_user_profile():
    """
    Obtiene el perfil del usuario
    """
    return make_api_request("me")

def get_user_playlists(limit=10, offset=0):
    endpoint = f"me/playlists?limit={limit}&offset={offset}"
    return make_api_request(endpoint)

def create_playlist(name, description="", public=True):
    """
    Crea una nueva playlist
    """
    user_info = get_user_profile()
    if "error" in user_info:
        return user_info
    
    user_id = user_info["id"]
    endpoint = f"users/{user_id}/playlists"
    data = {
        "name": name,
        "description": description,
        "public": public
    }
    
    return make_api_request(endpoint, method="POST", data=data)

def add_tracks_to_playlist(playlist_id, track_uris):
    """
    Añade canciones a una playlist
    """
    endpoint = f"playlists/{playlist_id}/tracks"
    data = {"uris": track_uris}
    
    return make_api_request(endpoint, method="POST", data=data)



def get_recommendations_by_mood(mood, limit=20):
    """
    Obtiene recomendaciones basadas en un mood
    Mapea moods a características de audio de Spotify
    """
    # Mapeo básico de moods a características de audio
    mood_mappings = {
        "Happy": {"min_valence": 0.7, "min_energy": 0.7, "target_tempo": 120},
        "Sad": {"max_valence": 0.4, "max_energy": 0.4, "target_tempo": 80},
        "Energetic": {"min_energy": 0.8, "min_danceability": 0.7, "target_tempo": 140},
        "Relaxing": {"max_energy": 0.4, "max_loudness": -10, "target_acousticness": 0.8},
        "Romantic": {"target_valence": 0.6, "target_acousticness": 0.6, "max_energy": 0.6},
        # Añadir más mapeos según sea necesario
    }
    
    # Valores predeterminados si el mood no se encuentra en el mapeo
    params = {"limit": limit}
    
    # Añadir parámetros basados en el mood si está disponible
    if mood in mood_mappings:
        params.update(mood_mappings[mood])
    
    # Para obtener recomendaciones necesitamos seed tracks, artists o genres
    # Podemos usar géneros populares como semilla
    params["seed_genres"] = "pop,rock,hip-hop,electronic,jazz"
    
    endpoint = f"recommendations?{urllib.parse.urlencode(params)}"
    return make_api_request(endpoint)


def update_song_spotify_id(song_id, spotify_id):
    """Actualiza el spotify_id de una canción en la base de datos"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Primero verificamos si la columna existe
        cursor.execute("SHOW COLUMNS FROM songs LIKE 'spotify_id'")
        column_exists = cursor.fetchone()
        
        # Si la columna no existe, la creamos
        if not column_exists:
            cursor.execute("ALTER TABLE songs ADD COLUMN spotify_id VARCHAR(255)")
            
        # Actualizamos el ID de Spotify
        cursor.execute("UPDATE songs SET spotify_id = %s WHERE id = %s", (spotify_id, song_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al actualizar spotify_id: {e}")
        return False

def get_songs_by_mood_id(mood_id):
    """Obtiene canciones por ID de mood desde la base de datos"""
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT s.id, s.name, s.artist, s.url, s.spotify_id 
            FROM songs s
            INNER JOIN mood_songs ms ON s.id = ms.song_id
            WHERE ms.mood_id = %s
        """, (mood_id,))
        
        songs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return songs
    except Exception as e:
        print(f"Error al obtener canciones por mood_id: {e}")
        return []

def get_mood_id_by_name(mood_name):
    """Obtiene el ID de un mood por su nombre"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM moods WHERE name = %s", (mood_name,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result[0] if result else None
    except Exception as e:
        print(f"Error al obtener mood_id por nombre: {e}")
        return None
    

def advanced_search_track(song_name, max_attempts=3):
    """
    Búsqueda avanzada de canciones en Spotify con múltiples intentos
    """
    
    # Intento 1: Búsqueda exacta
    search_query = song_name
    result = search_tracks(search_query, limit=1)
    
    if "error" not in result and result.get('tracks', {}).get('items'):
        return result['tracks']['items'][0]
    
    # Intento 2: Eliminar caracteres especiales y entre paréntesis
    if max_attempts >= 2:
        # Remover texto entre paréntesis
        cleaned_name = re.sub(r'\([^)]*\)', '', song_name)
        # Remover texto entre corchetes
        cleaned_name = re.sub(r'\[[^]]*\]', '', cleaned_name)
        # Remover caracteres especiales
        cleaned_name = re.sub(r'[^\w\s]', '', cleaned_name)
        # Eliminar espacios múltiples
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
        
        if cleaned_name != song_name:
            search_query = cleaned_name
            result = search_tracks(search_query, limit=1)
            
            if "error" not in result and result.get('tracks', {}).get('items'):
                return result['tracks']['items'][0]
    
    # Intento 3: Usar solo las primeras palabras (más probables de coincidencia)
    if max_attempts >= 3:
        words = song_name.split()
        if len(words) > 2:
            search_query = " ".join(words[:2])  # Primeras dos palabras
            result = search_tracks(search_query, limit=1)
            
            if "error" not in result and result.get('tracks', {}).get('items'):
                return result['tracks']['items'][0]
    
    # No se encontró nada
    return None
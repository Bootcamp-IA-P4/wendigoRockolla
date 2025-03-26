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

def make_api_request(endpoint, params=None, method="GET", data=None):
    """
    Realiza una solicitud a la API de Spotify
    
    Args:
        endpoint (str): Endpoint de la API (sin la base URL)
        params (dict, optional): Parámetros de la consulta
        method (str, optional): Método HTTP (GET, POST, etc)
        data (dict, optional): Datos para enviar en el cuerpo (para POST)
        
    Returns:
        dict: Respuesta de la API
    """
    try:
        # Verificar si tenemos un token y si está vigente
        if 'token_info' not in session:
            print("No hay token en la sesión")
            return {"error": "No autenticado"}
            
        token_info = session['token_info']
        now = datetime.now().timestamp()
        
        # Si el token está a punto de expirar (menos de 60 segundos), renovarlo
        if token_info['expires_at'] - now < 60:
            token_info = get_token_info()
            session['token_info'] = token_info
        
        # Construir la URL completa con los parámetros
        url = f"https://api.spotify.com/v1/{endpoint}"
        
        # Configurar los headers con el token de acceso
        headers = {
            "Authorization": f"Bearer {token_info['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Realizar la solicitud según el método
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, params=params, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, params=params, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, params=params)
        else:
            return {"error": f"Método no soportado: {method}"}
        
        # Verificar si la respuesta fue exitosa
        if response.status_code >= 200 and response.status_code < 300:
            # Algunos endpoints no devuelven JSON
            try:
                return response.json()
            except:
                return {"status": "success", "status_code": response.status_code}
        else:
            # Intentar obtener mensaje de error
            error_msg = "Error desconocido"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', "Error desconocido")
            except:
                error_msg = f"Error HTTP {response.status_code}"
                
            print(f"Error API Spotify: {error_msg}")
            return {"error": error_msg, "status_code": response.status_code}
            
    except Exception as e:
        print(f"Error en la solicitud a Spotify: {e}")
        return {"error": str(e)}
    

def diagnose_api_status():
    """Verifica el estado de la conexión con la API de Spotify"""
    try:
        # 1. Verificar autenticación
        if 'token_info' not in session:
            return {"status": "error", "message": "No hay token en sesión"}
        
        # 2. Verificar token expirado
        token_info = session['token_info']
        now = datetime.now().timestamp()
        if now >= token_info["expires_at"]:
            return {"status": "warning", "message": "Token expirado, intentando renovar"}
        
        # 3. Probar una llamada simple a la API
        user = make_api_request("me")
        if "error" in user:
            return {"status": "error", "message": f"Error al llamar a la API: {user['error']}"}
        
        # 4. Probar específicamente el endpoint de recomendaciones
        test_params = {
            "limit": 1,
            "seed_artists": "4NHQUGzhtTLFvgF5SZesLK"  # Ben E. King
        }
        test_rec = make_api_request("recommendations", params=test_params)
        if "error" in test_rec:
            return {"status": "error", "message": f"Error específico en recomendaciones: {test_rec['error']}"}
        
        return {"status": "ok", "message": "La API de Spotify funciona correctamente"}
    except Exception as e:
        return {"status": "error", "message": f"Error en diagnóstico: {str(e)}"}

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
    Obtiene recomendaciones basadas en un mood usando una combinación de seed tracks y seed genres.
    """
    try:
        # Mapeo de características de audio
        mood_mappings = {
            "Happy": {"min_valence": 0.7, "min_energy": 0.7},
            "Sad": {"max_valence": 0.4, "max_energy": 0.4},
            "Energetic": {"min_energy": 0.8, "min_danceability": 0.7},
            "Relaxing": {"max_energy": 0.4, "target_acousticness": 0.8},
            "Romantic": {"target_valence": 0.6, "target_acousticness": 0.6},
            "Aggressive": {"min_energy": 0.8, "target_valence": 0.3},
            "Foggy": {"max_valence": 0.4, "target_energy": 0.4}
        }
        
        # Géneros VERIFICADOS que existen en Spotify
        verified_genres = {
            "Happy": "pop,disco",
            "Sad": "ambient,blues",
            "Energetic": "electronic,house",
            "Relaxing": "ambient,classical",
            "Romantic": "r-n-b,soul",
            "Aggressive": "metal,punk-rock",
            "Foggy": "alternative,ambient"
        }
        
        # Canciones populares como semillas (URIs verificadas)
        seed_tracks = {
            "Happy": "4iV5W9uYEdYUVa79Axb7Rh,2takcwOaAZWiXQijPHIx7B", # "Uptown Funk", "Blinding Lights"
            "Sad": "4RCWB3V8V0dignt99LZ8vH,4gMgiXfqtPYnI5qPIrFNJm", # "Say Something", "Someone You Loved"
            "Energetic": "2KH16WveTQWT6KOG9Rg6e2,6ocbgoVGwYJhOv1GgI9NsF", # "Titanium", "Light It Up"
            "Relaxing": "7qEKqBCD2vE5vIBsrUitpD,3NRqlXufRMelTwPnGvSfAP", # "River Flows In You", "Weightless"
            "Romantic": "4NHQUGzhtTLFvgF5SZesLK,7qiZfU4dY1lWllzX7mPBI3", # "Stand By Me", "Shape of You"
            "Aggressive": "57bgtoPSgt236HzfBOd8kj,2zYzyRzz6pRmhPzyfMEC8s", # "Master of Puppets", "Break Stuff"
            "Foggy": "5zyI2dYKka9pdaGgLnQFId,5P9X0wOTucQnvkHjj1jdrb" # "A Forest", "How Soon Is Now?"
        }
        
        # Parámetros base
        params = {"limit": limit}
        
        # Añadir características de audio según el mood
        if mood in mood_mappings:
            params.update(mood_mappings[mood])
        
        # Estrategia de semillas:
        # 1. Usar seed_tracks específicos para el mood (esto es crucial)
        if mood in seed_tracks:
            params["seed_tracks"] = seed_tracks[mood]
        else:
            # Usar tracks de respaldo si no hay específicos
            params["seed_tracks"] = "4iV5W9uYEdYUVa79Axb7Rh,2takcwOaAZWiXQijPHIx7B"
            
        # 2. También usar seed_genres si aplica (pero no mezclar muchos)
        if mood in verified_genres:
            # Solo usar géneros si no hemos alcanzado el límite de semillas (máximo 5 en total)
            track_count = len(params.get("seed_tracks", "").split(","))
            genres = verified_genres[mood].split(",")
            
            # Ajustar la cantidad para no exceder 5 semillas en total
            max_genres = min(len(genres), 5 - track_count)
            if max_genres > 0:
                params["seed_genres"] = ",".join(genres[:max_genres])
        
        print(f"PARÁMETROS FINALES para mood '{mood}': {params}")
        
        # Llamada a la API
        response = make_api_request("recommendations", params=params)
        
        # Depuración detallada
        if 'error' in response:
            print(f"ERROR DE API: {response['error']}")
            print(f"Código de estado: {response.get('status_code', 'desconocido')}")
        elif 'tracks' in response:
            print(f"ÉXITO! Recibidas {len(response['tracks'])} canciones para mood '{mood}'")
            
        return response
    except Exception as e:
        import traceback
        print(f"ERROR EN get_recommendations_by_mood: {e}")
        print(traceback.format_exc())  # Esto imprimirá el stack trace completo
        return {"error": str(e), "tracks": []}

def get_available_genres():
    """Obtiene los géneros disponibles en Spotify"""
    return make_api_request("recommendations/available-genre-seeds")


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
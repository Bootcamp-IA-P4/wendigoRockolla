from flask import Flask, render_template, request, url_for, session, redirect, jsonify
import os
import secrets
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper.db.crud import get_data, get_all_moods, get_all_artists, get_all_albums, get_songs_by_mood_id, get_mood_by_name, get_popular_songs 
from static.mood_images import get_mood_image
from services.genius_service import get_song_lyrics, get_song_details
from services.spotifyApi import (
    get_auth_url, get_token_info, get_user_profile, 
    search_tracks, create_playlist, add_tracks_to_playlist,
    get_recommendations_by_mood, update_song_spotify_id, get_songs_by_mood_id, advanced_search_track
)
from scraper.db.connection import connect_db

app = Flask(__name__)


# Configuración para session
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(16)

# Configurar sesión para que dure más tiempo (1 semana)
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

@app.before_request
def make_session_permanent():
    session.permanent = True
    
@app.context_processor
def inject_spotify_user():
    """Inyecta el usuario de Spotify en todas las plantillas"""
    spotify_user = None
    if 'token_info' in session:
        try:
            spotify_user = get_user_profile()
        except:
            pass
    return dict(spotify_user=spotify_user)

# Función auxiliar para obtener iconos según el mood
def get_mood_icon(mood_name):
    # Diccionario de iconos para algunos moods comunes
    mood_icons = {
        'Happy': 'fa-smile',
        'Sad': 'fa-frown',
        'Angry': 'fa-fire',
        'Relaxing': 'fa-spa',
        'Energetic': 'fa-bolt',
        'Romantic': 'fa-heart',
        'Epic': 'fa-mountain',
        'Melancholic': 'fa-cloud-rain',
        'Dreamy': 'fa-moon',
        'Dramatic': 'fa-theater-masks',
        'Gloomy': 'fa-cloud',
        'Uplifting': 'fa-sun',
    }
    
    # Devuelve el icono si existe, o un icono predeterminado si no
    return mood_icons.get(mood_name, 'fa-music')

@app.route('/')
def index():
    
    moods_data = get_all_moods()
    moods = moods_data[:12] if moods_data else []
    artists = get_all_artists()  # Función que debes implementar
    albums = get_all_albums()
    popular_songs = get_popular_songs()
    
    # Obtener información del usuario de Spotify si está autenticado
    spotify_user = None
    if 'token_info' in session:
        try:
            spotify_user = get_user_profile()
        except:
            pass
    
    return render_template('index.html', moods=moods, artists=artists, albums=albums, popular_songs=popular_songs, spotify_user=spotify_user, get_mood_image=get_mood_image, get_mood_icon=get_mood_icon)
    

@app.route('/search')
def search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'mood')
    results = get_data(query, search_type)
    return render_template('results.html', results=results, query=query, type=search_type)

# Página de administración para editar moods
@app.route('/admin/moods')
def admin_moods():
    moods = get_all_moods()
    message = request.args.get('message')
    message_type = request.args.get('type', 'alert-info')
    
    return render_template('admin_moods.html', moods=moods, get_mood_image=get_mood_image, message=message,message_type=message_type)

@app.route('/admin/moods/add', methods=['POST'])
def add_mood():
    name = request.form.get('name')
    url = request.form.get('url')
    
    try:
        from scraper.db.connection import connect_db
        conn = connect_db()
        cursor = conn.cursor()
        
        # Insertar nuevo mood
        cursor.execute("INSERT INTO moods (name, url) VALUES (%s, %s)", (name, url))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_moods', message=f'Mood "{name}" añadido correctamente', type='alert-success'))
    except Exception as e:
        print(f"Error al añadir mood: {e}")
        return redirect(url_for('admin_moods', message=f'Error al añadir mood: {e}', type='alert-error'))

# Ruta para actualizar un mood existente
@app.route('/admin/moods/update/<int:mood_id>', methods=['POST'])
def update_mood(mood_id):
    name = request.form.get('name')
    url = request.form.get('url')
    
    try:
        from scraper.db.connection import connect_db
        conn = connect_db()
        cursor = conn.cursor()
        
        # Actualizar mood
        cursor.execute("UPDATE moods SET name = %s, url = %s WHERE id = %s", (name, url, mood_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_moods', message=f'Mood actualizado correctamente', type='alert-success'))
    except Exception as e:
        print(f"Error al actualizar mood: {e}")
        return redirect(url_for('admin_moods', message=f'Error al actualizar mood: {e}', type='alert-error'))

# Ruta para eliminar un mood
@app.route('/admin/moods/delete/<int:mood_id>')
def delete_mood(mood_id):
    try:
        from scraper.db.connection import connect_db
        conn = connect_db()
        cursor = conn.cursor()
        
        # Primero eliminar referencias en la tabla mood_songs
        cursor.execute("DELETE FROM mood_songs WHERE mood_id = %s", (mood_id,))
        
        # Luego eliminar el mood
        cursor.execute("DELETE FROM moods WHERE id = %s", (mood_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_moods', message='Mood eliminado correctamente', type='alert-success'))
    except Exception as e:
        print(f"Error al eliminar mood: {e}")
        return redirect(url_for('admin_moods', message=f'Error al eliminar mood: {e}', type='alert-error'))



# Gestión de letras de canciones
@app.route('/lyrics')
def lyrics():
    song_name = request.args.get('song')
    artist_name = request.args.get('artist')
    
    # Buscar la canción en Genius
    results = get_song_details(song_name, artist_name)
    
    if not results:
        return jsonify({"error": "Canción no encontrada"}), 404
    
    song_id = results[0]["result"]["id"]  # Obtiene el ID de la primera coincidencia
    song_details = get_song_details(song_id)  # Obtiene los detalles de la canción
    
    if not song_details:
        return jsonify({"error": "No se encontraron detalles de la canción"}), 404

    song_url = song_details.get("url")  # URL de la canción en Genius
    lyrics = get_song_lyrics(song_url)  # Scrapea la letra desde la URL
    
    return jsonify({"song": song_name, "artist": artist_name, "lyrics": lyrics})



# Rutas para autenticación de Spotify
@app.route('/spotify/login')
def spotify_login():
    auth_url = get_auth_url()
    return redirect(auth_url)

@app.route('/callback')
def spotify_callback():
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return render_template('error.html', message=f"Error de autenticación: {error}")
    
    if code:
        token_info = get_token_info(code)
        if token_info:
            session["token_info"] = token_info
            session["refresh_token"] = token_info.get("refresh_token")
            return redirect(url_for('spotify_profile'))
    
    return render_template('error.html', message="Error al obtener el token de acceso")

@app.route('/spotify/logout')
def spotify_logout():
    # Eliminar información de sesión relacionada con Spotify
    session.pop('token_info', None)
    return redirect(url_for('index'))


@app.route('/spotify/profile')
def spotify_profile():
    if "token_info" not in session:
        return redirect(url_for('spotify_login'))
    
    profile = get_user_profile()
    
    if "error" in profile:
        return render_template('error.html', message=f"Error: {profile['error']}")
    
    return render_template('spotify_profile.html', profile=profile)

@app.route('/spotify/create_playlist')
def spotify_create_playlist_page():
    if "token_info" not in session:
        return redirect(url_for('spotify_login'))
    
    mood = request.args.get('mood', '')
    
    # Obtener todos los moods para el selector
    all_moods = get_all_moods()
    
    return render_template('create_playlist.html', mood=mood, all_moods=all_moods)

@app.route('/spotify/create_playlist', methods=['POST'])
def spotify_create_playlist():
    if "token_info" not in session:
        return redirect(url_for('spotify_login'))
    
    playlist_name = request.form.get('name')
    description = request.form.get('description', '')
    mood = request.form.get('mood', '')
    selected_songs_json = request.form.get('selected_songs', '[]')
    
    try:
        selected_songs = json.loads(selected_songs_json)
    except:
        selected_songs = []
    
    if not playlist_name:
        return render_template('create_playlist.html', error="Por favor, introduce un nombre para la playlist",all_moods=get_all_moods(), mood=mood)
    
    # Crear la playlist en Spotify
    from services.spotifyApi import create_playlist, add_tracks_to_playlist, search_tracks
    
    playlist_result = create_playlist(playlist_name, description)
    
    if "error" in playlist_result:
        return render_template('create_playlist.html', error=f"Error: {playlist_result['error']}",all_moods=get_all_moods(), mood=mood)
    
    playlist_id = playlist_result["id"]
    
    # Buscar y añadir las canciones seleccionadas a la playlist
    if selected_songs:
        track_uris = []
        failed_tracks = []
        
        for song in selected_songs:
            # Si ya tienes el spotify_id guardado
            if song.get('spotify_id'):
                track_uris.append(f"spotify:track:{song['spotify_id']}")
            else:
                track = advanced_search_track(song['name'])
                
                if track:
                    track_uris.append(track['uri'])
                    update_song_spotify_id(song['id'], track['id'])
                else:
                    failed_tracks.append(f"{song['name']}")
        # Añadir las canciones encontradas a la playlist
        if track_uris:
            add_result = add_tracks_to_playlist(playlist_id, track_uris)
            
            if "error" in add_result:
                return render_template('playlist_created.html', playlist=playlist_result,error=f"Playlist creada, pero hubo problemas al añadir algunas canciones: {add_result['error']}", failed_tracks=failed_tracks, mood=mood)
    
    # Mostrar resultado exitoso
    return render_template('playlist_created.html', playlist=playlist_result, mood=mood, failed_tracks=failed_tracks if 'failed_tracks' in locals() else [])

@app.route('/api/preview_spotify_search', methods=['POST'])
def api_preview_spotify_search():
    songs = request.json.get('songs', [])
    results = []
    
    for song in songs:
        # Buscar en Spotify
        track = advanced_search_track(song['name'])
        
        if track:
            results.append({
                'db_song': song['name'],
                'found': True,
                'spotify_name': track['name'],
                'spotify_artist': ", ".join([artist['name'] for artist in track['artists']]),
                'spotify_id': track['id'],
                'song_id': song['id'],
                'preview_url': track.get('preview_url', None)
            })
        else:
            results.append({
                'db_song': song['name'],
                'found': False
            })
    
    return jsonify(results)

# Función para obtener álbumes de la base de datos
def get_albums():
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        
        # Adapta esta consulta a tu estructura de base de datos
        cursor.execute("""
            SELECT DISTINCT name, artist FROM albums 
            ORDER BY name LIMIT 8
        """)
        
        albums = cursor.fetchall()
        cursor.close()
        conn.close()
        return albums
    except Exception as e:
        print(f"Error al obtener álbumes: {e}")
        return []

# Función para obtener canciones populares
def get_popular_songs():
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        
        # Adapta esta consulta a tu estructura de base de datos
        cursor.execute("""
            SELECT s.id, s.name, s.spotify_id, 'Artista Desconocido' as artist
            FROM songs s
            WHERE s.spotify_id IS NOT NULL
            ORDER BY RAND()
            LIMIT 10
        """)
        
        songs = cursor.fetchall()
        cursor.close()
        conn.close()
        return songs
    except Exception as e:
        print(f"Error al obtener canciones populares: {e}")
        return []

# Función para crear un enlace de Spotify para una canción
@app.route('/create_spotify_link/<int:song_id>')
def create_spotify_link(song_id):
    try:
        import urllib.parse
        # Obtener información de la canción
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM songs WHERE id = %s", (song_id,))
        song = cursor.fetchone()
        
        if not song:
            return redirect(url_for('index'))
            
        # Buscar en Spotify
        search_result = search_tracks(song['name'], limit=1)
        
        if "error" not in search_result and search_result.get('tracks', {}).get('items'):
            track = search_result['tracks']['items'][0]
            spotify_id = track['id']
            
            # Actualizar la base de datos
            cursor.execute("UPDATE songs SET spotify_id = %s WHERE id = %s", (spotify_id, song_id))
            conn.commit()
            
            # Redirigir a Spotify
            return redirect(f"https://open.spotify.com/track/{spotify_id}")
        else:
            # Si no encuentra la canción, redirigir a la búsqueda en Spotify
            return redirect(f"https://open.spotify.com/search/{urllib.parse.quote(song['name'])}")
            
    except Exception as e:
        print(f"Error al crear enlace de Spotify: {e}")
        return redirect(url_for('index'))
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


@app.route('/spotify/recommendations')
def spotify_recommendations():
    if "token_info" not in session:
        return redirect(url_for('spotify_login'))
    
    mood = request.args.get('mood', '')
    
    if not mood:
        return render_template('recommendations.html')
    
    recommendations = get_recommendations_by_mood(mood)
    
    if "error" in recommendations:
        return render_template('recommendations.html', error=f"Error: {recommendations['error']}")
    
    return render_template('recommendations.html', recommendations=recommendations, mood=mood)

# Ruta para obtener todos los moods para la creación de playlists
@app.route('/api/moods')
def api_get_moods():
    moods_data = get_all_moods()
    return jsonify(moods_data)

# Ruta para obtener canciones por mood
@app.route('/api/songs')
def api_get_songs_by_mood():
    mood = request.args.get('mood', '')
    if not mood:
        return jsonify([])
    
    # Depuración
    print(f"Buscando canciones para mood: {mood}")
    
    # Modificación: Primero intenta obtener el mood por nombre
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Buscar el ID del mood por su nombre
    cursor.execute("SELECT id FROM moods WHERE name = %s", (mood,))
    mood_result = cursor.fetchone()
    print(f"Mood result: {mood_result}")
    
    # Si encontró el mood, buscar canciones asociadas
    if mood_result:
        mood_id = mood_result[0]
        
        # Buscar canciones asociadas al mood en la tabla relacional mood_songs
        cursor.execute("""
            SELECT s.id, s.name, s.youtube_url, s.spotify_id
            FROM songs s
            INNER JOIN mood_songs ms ON s.id = ms.song_id
            WHERE ms.mood_id = %s
        """, (mood_id,))
        
        songs_result = cursor.fetchall()
        print(f"Encontradas {len(songs_result)} canciones para mood_id {mood_id}")
        
        # Formatea los resultados para el frontend
        formatted_songs = []
        for song in songs_result:
            formatted_songs.append({
                'id': song[0],
                'name': song[1],
                'artist': 'Artista Desconocido',  # Valor predeterminado ya que no tenemos este campo
                'url': song[2],  # youtube_url
                'spotify_id': song[3] if len(song) > 3 and song[3] else ''
            })
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        return jsonify(formatted_songs)
    
    # Como respaldo, intenta con la función original
    songs = get_data(mood, 'mood')
    
    formatted_songs = []
    for song in songs:
        formatted_songs.append({
            'id': song.get('id', ''),
            'name': song.get('name', ''),
            'artist': song.get('artist', 'Artista Desconocido'),
            'spotify_id': song.get('spotify_id', ''),
            'url': song.get('url', '') or song.get('youtube_url', '')
        })
    
    return jsonify(formatted_songs)

if __name__ == '__main__':
    app.run(debug=True)
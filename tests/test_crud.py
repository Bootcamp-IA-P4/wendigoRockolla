import pytest
import sys
import os

# Ajustar la ruta para importar desde el directorio principal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funciones CRUD
from scraper.db.crud import (
    get_all_moods, get_mood_by_name, get_all_artists, get_all_albums,
    get_songs_by_mood_id, update_mood_url, add_mood, delete_mood_by_id
)

@pytest.mark.usefixtures("setup_test_db")
class TestCrud:
    
    def test_get_all_moods(self):
        """Prueba que podemos obtener todos los moods de la base de datos"""
        moods = get_all_moods()
        
        # Verificar que devuelve una lista no vacía
        assert isinstance(moods, list)
        assert len(moods) >= 3  # Deberíamos tener al menos 3 moods de prueba
        
        # Verificar que tiene los campos esperados
        assert 'id' in moods[0]
        assert 'name' in moods[0]
        
        # Verificar que contiene los moods de prueba
        mood_names = [mood['name'] for mood in moods]
        assert 'Happy' in mood_names
        assert 'Sad' in mood_names
        assert 'Aggressive' in mood_names
    
    def test_get_mood_by_name(self):
        """Prueba que podemos obtener un mood específico por nombre"""
        mood = get_mood_by_name('Happy')
        
        # Verificar que devuelve el mood correcto
        assert mood is not None
        assert mood['name'] == 'Happy'
        assert mood['url'] == 'https://example.com/happy.jpg'
        
        # Verificar que devuelve None para un mood inexistente
        non_existent = get_mood_by_name('NonExistentMood')
        assert non_existent is None
    
    def test_get_all_artists(self):
        """Prueba que podemos obtener todos los artistas"""
        artists = get_all_artists()
        
        # Verificar que devuelve una lista no vacía
        assert isinstance(artists, list)
        assert len(artists) >= 2
        
        # Verificar que contiene los artistas de prueba
        artist_names = [artist['name'] for artist in artists]
        assert 'Metallica' in artist_names
        assert 'The Beatles' in artist_names
    
    def test_get_all_albums(self):
        """Prueba que podemos obtener todos los álbumes"""
        albums = get_all_albums()
        
        # Verificar que devuelve una lista no vacía
        assert isinstance(albums, list)
        assert len(albums) >= 1
        
        # Verificar que contiene el álbum de prueba
        assert any(album['name'] == 'Master of Puppets' for album in albums)
    
    def test_get_songs_by_mood_id(self):
        """Prueba que podemos obtener canciones por mood_id"""
        # Primero obtenemos el ID del mood Aggressive
        mood = get_mood_by_name('Aggressive')
        assert mood is not None
        
        songs = get_songs_by_mood_id(mood['id'])
        
        # Verificar que devuelve una lista no vacía
        assert isinstance(songs, list)
        assert len(songs) >= 1
        
        # Verificar que contiene la canción esperada
        assert any(song['name'] == 'Master of Puppets' for song in songs)
    
    def test_update_mood_url(self, db_connection):
        """Prueba que podemos actualizar la URL de un mood"""
        new_url = 'https://example.com/new_happy.jpg'
        result = update_mood_url('Happy', new_url)
        
        # Verificar que la actualización fue exitosa
        assert result is True
        
        # Verificar que el cambio se aplicó
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT url FROM moods WHERE name = 'Happy'")
        mood = cursor.fetchone()
        cursor.close()
        
        assert mood['url'] == new_url
    
    def test_add_mood(self, db_connection):
        """Prueba que podemos añadir un nuevo mood"""
        new_mood = {
            'name': 'Romantic',
            'url': 'https://example.com/romantic.jpg'
        }
        
        result = add_mood(new_mood['name'], new_mood['url'])
        
        # Verificar que la inserción fue exitosa
        assert result is True
        
        # Verificar que el mood se añadió correctamente
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM moods WHERE name = 'Romantic'")
        mood = cursor.fetchone()
        cursor.close()
        
        assert mood is not None
        assert mood['name'] == new_mood['name']
        assert mood['url'] == new_mood['url']
    
    def test_delete_mood_by_id(self, db_connection):
        """Prueba que podemos eliminar un mood por ID"""
        # Primero obtenemos el ID del mood a eliminar
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM moods WHERE name = 'Sad'")
        mood = cursor.fetchone()
        cursor.close()
        
        assert mood is not None
        
        # Eliminar el mood pasando la conexión de prueba
        result = delete_mood_by_id(mood['id'], db_connection)
        
        # Verificar que la eliminación fue exitosa
        assert result is True
        
        # Verificar que el mood ya no existe
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM moods WHERE id = %s", (mood['id'],))
        deleted_mood = cursor.fetchone()
        cursor.close()
        
        assert deleted_mood is None
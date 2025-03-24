import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Ajustar la ruta para importar desde el directorio principal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funciones de la API de Spotify
from services.spotifyApi import (
    search_tracks, advanced_search_track, get_auth_url,
    get_token_info, get_user_profile
)

@pytest.mark.usefixtures("setup_test_db")
class TestSpotifyAPI:
    
    @patch('services.spotifyApi.requests.get')
    @patch('services.spotifyApi.get_access_token')
    def test_search_tracks(self, mock_get_token, mock_get):
        """Prueba la búsqueda de canciones en Spotify"""
        # Configurar mock para simular respuesta de Spotify
        mock_get_token.return_value = "fake_access_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tracks': {
                'items': [
                    {
                        'id': '2MZZrDA-I4M',
                        'name': 'Master of Puppets',
                        'uri': 'spotify:track:2MZZrDA-I4M',
                        'artists': [
                            {'name': 'Metallica'}
                        ]
                    },
                    {
                        'id': '1jzDzZWeSDBg5fhNc3tczV',
                        'name': 'Enter Sandman',
                        'uri': 'spotify:track:1jzDzZWeSDBg5fhNc3tczV',
                        'artists': [
                            {'name': 'Metallica'}
                        ]
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Ejecutar búsqueda
        results = search_tracks('Metallica')
        
        # Verificar resultados
        assert 'tracks' in results
        assert len(results['tracks']['items']) == 2
        assert results['tracks']['items'][0]['name'] == 'Master of Puppets'
        assert results['tracks']['items'][0]['artists'][0]['name'] == 'Metallica'
    
    @patch('services.spotifyApi.search_tracks')
    def test_advanced_search_track(self, mock_search):
        """Prueba la búsqueda avanzada de canciones"""
        # Configurar mock para simular respuesta normal
        mock_search.return_value = {
            'tracks': {
                'items': [
                    {
                        'id': '2MZZrDA-I4M',
                        'name': 'Master of Puppets',
                        'uri': 'spotify:track:2MZZrDA-I4M',
                        'artists': [
                            {'name': 'Metallica'}
                        ]
                    }
                ]
            }
        }
        
        # Ejecutar búsqueda avanzada
        track = advanced_search_track('Master of Puppets')
        
        # Verificar resultados
        assert track is not None
        assert track['id'] == '2MZZrDA-I4M'
        assert track['name'] == 'Master of Puppets'
        
        # Probar con una canción que requiere limpieza
        mock_search.side_effect = [
            {'tracks': {'items': []}},  # Primera llamada falla
            {
                'tracks': {
                    'items': [
                        {
                            'id': '2MZZrDA-I4M',
                            'name': 'Master of Puppets',
                            'uri': 'spotify:track:2MZZrDA-I4M',
                            'artists': [
                                {'name': 'Metallica'}
                            ]
                        }
                    ]
                }
            }  # Segunda llamada exitosa
        ]
        
        track = advanced_search_track('Master of Puppets (Live Version) [Remastered]')
        
        # Verificar que se limpió el título y encontró resultados
        assert track is not None
        assert track['name'] == 'Master of Puppets'
    
    def test_get_auth_url(self):
        """Prueba la generación de URL de autenticación"""
        # Ejecutar función
        auth_url = get_auth_url()
        
        # Verificar que la URL contiene los parámetros esperados
        assert 'https://accounts.spotify.com/authorize' in auth_url
        assert 'client_id=' in auth_url
        assert 'redirect_uri=' in auth_url
        assert 'scope=' in auth_url
        assert 'response_type=code' in auth_url
    
    @patch('services.spotifyApi.requests.post')
    def test_get_token_info(self, mock_post, spotify_token):
        """Prueba la obtención del token de acceso"""
        # Configurar mock para simular respuesta
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = spotify_token
        mock_post.return_value = mock_response
        
        # Ejecutar función
        token = get_token_info('test_code')
        
        # Verificar resultados
        assert token is not None
        assert token['access_token'] == 'test_access_token'
        assert token['refresh_token'] == 'test_refresh_token'
    
    @patch('services.spotifyApi.requests.get')
    @patch('services.spotifyApi.get_access_token')
    def test_get_user_profile(self, mock_get_token, mock_get, spotify_token):
        """Prueba la obtención del perfil de usuario"""

        mock_get_token.return_value = "fake_access_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
        'id': 'test_user',
        'display_name': 'Test User',
        'email': 'test@example.com',
        'images': [{'url': 'https://example.com/profile.jpg'}]
    }
        mock_get.return_value = mock_response
        
        # Ejecutar función directamente (no necesitamos el patch de session)
        profile = get_user_profile()
            
         # Verificar resultados
        assert profile is not None
        assert profile['id'] == 'test_user'
        assert profile['display_name'] == 'Test User'
        assert profile['email'] == 'test@example.com'
import os
import sys
import pytest
import mysql.connector
from dotenv import load_dotenv

# Ajustar la ruta para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar .env.test desde la carpeta config
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', '.env.test')
print(f"Cargando variables de entorno desde: {dotenv_path}")
load_dotenv(dotenv_path)

# Verificar que se cargó correctamente
db_name = os.getenv("DB_NAME")
print(f"Base de datos seleccionada: {db_name}")

@pytest.fixture
def app_context():
    """Crea un contexto de aplicación Flask para pruebas"""
    try:
        from app import app
        with app.app_context():
            with app.test_request_context():
                yield
    except ImportError:
        # Si no podemos importar la app, creamos un mock mínimo
        from flask import Flask
        test_app = Flask(__name__)
        with test_app.app_context():
            with test_app.test_request_context():
                yield

@pytest.fixture(scope="session")
def setup_test_db():
    """Configurar base de datos de prueba"""
    # Verificación extra para no usar DB de producción
    db_name = os.getenv("DB_NAME")
    if not db_name:
        raise ValueError("No se ha cargado la variable DB_NAME del archivo .env.test")
    
    if db_name == "wendigo" or db_name == "bcia" or "test" not in db_name.lower():
        raise ValueError("¡STOP! Intentando usar base de datos de producción para tests")
    
    # Conexión a MySQL para crear la base de datos
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306)
    )
    cursor = connection.cursor()
    
    # Crear base de datos de prueba
    cursor.execute(f"DROP DATABASE IF EXISTS {os.getenv('DB_NAME')}")
    cursor.execute(f"CREATE DATABASE {os.getenv('DB_NAME')}")
    cursor.execute(f"USE {os.getenv('DB_NAME')}")
    
    # Crear tablas necesarias
    cursor.execute("""
        CREATE TABLE moods (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            url VARCHAR(255)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE artists (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            url VARCHAR(255)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE songs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            youtube_url VARCHAR(255),
            spotify_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE albums (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            artist VARCHAR(255),
            cover_url VARCHAR(255),
            album_url VARCHAR(255)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE mood_songs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mood_id INT,
            song_id INT,
            FOREIGN KEY (mood_id) REFERENCES moods(id),
            FOREIGN KEY (song_id) REFERENCES songs(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE mood_albums (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mood_id INT,
            album_id INT,
            FOREIGN KEY (mood_id) REFERENCES moods(id),
            FOREIGN KEY (album_id) REFERENCES albums(id)
        )
    """)
    
    # Insertar datos de prueba
    cursor.execute("INSERT INTO moods (name, url) VALUES ('Happy', 'https://example.com/happy.jpg')")
    cursor.execute("INSERT INTO moods (name, url) VALUES ('Sad', 'https://example.com/sad.jpg')")
    cursor.execute("INSERT INTO moods (name, url) VALUES ('Aggressive', 'https://example.com/aggressive.jpg')")
    
    cursor.execute("INSERT INTO artists (name, url) VALUES ('Metallica', 'https://example.com/metallica.jpg')")
    cursor.execute("INSERT INTO artists (name, url) VALUES ('The Beatles', 'https://example.com/beatles.jpg')")
    
    cursor.execute("""
        INSERT INTO songs (name, youtube_url, spotify_id) 
        VALUES ('Master of Puppets', 'https://youtube.com/watch?v=master', '2MZZrDA-I4M')
    """)
    
    cursor.execute("""
        INSERT INTO songs (name, youtube_url, spotify_id) 
        VALUES ('Yesterday', 'https://youtube.com/watch?v=yesterday', '3BQHpFgAZ0o')
    """)
    
    cursor.execute("INSERT INTO albums (name, artist, cover_url) VALUES ('Master of Puppets', 'Metallica', 'https://example.com/master.jpg')")
    
    # Relaciones mood_songs
    cursor.execute("INSERT INTO mood_songs (mood_id, song_id) VALUES (3, 1)")  # Aggressive - Master of Puppets
    cursor.execute("INSERT INTO mood_songs (mood_id, song_id) VALUES (2, 2)")  # Sad - Yesterday
    
    connection.commit()
    
    # Cerrar conexión
    cursor.close()
    connection.close()
    
    yield
    
    # Limpieza después de las pruebas 
    # connection = mysql.connector.connect(
    #     host=os.getenv("DB_HOST"),
    #     user=os.getenv("DB_USER"),
    #     password=os.getenv("DB_PASSWORD")
    # )
    # cursor = connection.cursor()
    # cursor.execute(f"DROP DATABASE IF EXISTS {os.getenv('DB_NAME')}")
    # cursor.close()
    # connection.close()

@pytest.fixture
def db_connection():
    """Conexión a la base de datos de prueba"""
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT", 3306)
    )
    yield connection
    connection.close()

# Sobrescribir la función connect_db para pruebas
@pytest.fixture(autouse=True)
def mock_db_connection(monkeypatch):
    """Reemplaza la conexión a BD real con la de prueba"""
    def mock_connect():
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT", 3306)
        )
    
    # Importar la función original para reemplazarla
    from scraper.db.connection import connect_db
    monkeypatch.setattr('scraper.db.connection.connect_db', mock_connect)

# Mock para spotify API
@pytest.fixture
def spotify_token():
    """Mock de token de Spotify para pruebas"""
    from datetime import datetime
    return {
        "access_token": "test_access_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": datetime.now().timestamp() + 3600,
        "refresh_token": "test_refresh_token",
        "scope": "user-read-private user-read-email playlist-modify-public playlist-modify-private"
    }
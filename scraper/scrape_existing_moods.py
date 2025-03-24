# Descripción: Este script permite al usuario seleccionar un mood de la base de datos y extraer detalles de los álbumes y canciones relacionados con ese mood.
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
try:
    from db.crud import insert_artist, insert_mood, insert_song, insert_albums, insert_mood_song, insert_mood_album, get_mood_id, get_album_id, get_song_id, get_all_moods, update_mood_url
except ImportError:
    from db.crud import insert_artist, insert_mood, insert_song, insert_albums, insert_mood_song, insert_mood_album, get_mood_id, get_album_id, get_song_id, get_all_moods, update_mood_url

# Opciones de Selenium
options = Options()
# options.add_argument('--incognito')

# Configurar Selenium con ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(options=options)
print("Open Google browser")

def handle_cookie_consent():
    try:
        time.sleep(3)
        consent_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.fc-consent-root button.fc-button.fc-cta-consent"))
        )
        consent_button.click()
        print("Cookie consent accepted")
    except Exception as e:
        print(f"Error handling cookie consent: {e}")

# Actualizar las URLs de los moods en la base de datos
def update_mood_urls():
    print("Actualizando URLs de los moods...")
    # Primero, asegurémonos de que la columna URL existe en la tabla moods
    try:
        from db.connection import connect_db
        db = connect_db()
        cursor = db.cursor()
        
        # Verificar si la columna url existe en la tabla moods
        cursor.execute("SHOW COLUMNS FROM moods LIKE 'url'")
        column_exists = cursor.fetchone()
        
        if not column_exists:
            print("Agregando columna 'url' a la tabla 'moods'...")
            cursor.execute("ALTER TABLE moods ADD COLUMN url VARCHAR(255)")
            db.commit()
            print("Columna 'url' agregada correctamente.")
        
        cursor.close()
        db.close()
    except Exception as e:
        print(f"Error al verificar/crear la columna 'url': {e}")

    # Obtener todos los nombres de moods de la base de datos
    moods = get_all_moods()
    mood_names = [mood['name'] for mood in moods]
    
    # Hacer scraping de las URLs de los moods
    moods_url = "https://www.allmusic.com/moods"
    driver.get(moods_url)
    handle_cookie_consent()
    
    try:
        mood_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#allMoodsGridDesktop a"))
        )
        
        # Crear un diccionario con los nombres y URLs de los moods
        moods_dict = {}
        for mood_element in mood_elements:
            mood_name = mood_element.get_attribute("title").strip()
            mood_url = mood_element.get_attribute("href").strip()
            if mood_name:
                moods_dict[mood_name] = mood_url
        
        # Actualizar las URLs de los moods en la base de datos
        updated_count = 0
        not_found_count = 0
        for mood_name in mood_names:
            if mood_name in moods_dict:
                success = update_mood_url(mood_name, moods_dict[mood_name])
                if success:
                    updated_count += 1
                    print(f"URL actualizada para el mood: {mood_name}")
                else:
                    print(f"Error al actualizar URL para el mood: {mood_name}")
            else:
                not_found_count += 1
                print(f"No se encontró URL para el mood: {mood_name}")
        
        print(f"Se actualizaron {updated_count} de {len(mood_names)} moods.")
        print(f"No se encontraron URLs para {not_found_count} moods.")
        
        # Verificar que las URLs realmente se actualizaron
        print("Verificando actualizaciones...")
        moods_after = get_all_moods()
        urls_count = sum(1 for mood in moods_after if mood.get('url'))
        print(f"Moods con URL después de actualizar: {urls_count} de {len(moods_after)}")
        
    except Exception as e:
        print(f"Error al extraer URLs de moods: {e}")

# Obtener todos los moods de la base de datos
def get_all_moods_from_db():
    moods = get_all_moods()
    
    # Crear diccionario con nombre y URL (puede ser None si no existe)
    moods_dict = {}
    for mood in moods:
        name = mood['name']
        url = mood.get('url')  # Usa get para manejar el caso donde 'url' no exista
        if name:
            moods_dict[name] = url
    
    return moods_dict

# Extraer detalles de cada mood
def scrape_mood_details(mood_url, mood_id):
    driver.get(mood_url)
    handle_cookie_consent()
    
    try:
        # Scrape albums related to the mood
        albums = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "singleGenreAlbum"))
        )
        for album in albums:
            try:
                title_element = album.find_element(By.CLASS_NAME, "descriptorTitle")
                artist_element = album.find_element(By.CLASS_NAME, "descriptorArtist")
                cover_element = album.find_element(By.TAG_NAME, "img")

                album_name = title_element.text.strip()
                album_url = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                artist_name = artist_element.text.strip()
                artist_url = artist_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                cover_url = cover_element.get_attribute("data-src") or cover_element.get_attribute("src")

                if album_name and artist_name and cover_url:
                    print(f"Album: {album_name}, Artist: {artist_name}, Cover: {cover_url}")
                    insert_artist(artist_name, artist_url)
                    insert_albums(album_name, cover_url, album_url)
                    album_id = get_album_id(album_name)
                    if album_id:
                        insert_mood_album(mood_id, album_id)
                else:
                    print("Incomplete data for album or artist, skipping...")
            except Exception as e:
                print(f"Error processing album element: {e}")

        # Scrape songs related to the mood
        songs = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "songRow"))
        )
        for song in songs:
            try:
                song_name = song.find_element(By.CLASS_NAME, "songTitle").text.strip()
                artist_element = song.find_element(By.CLASS_NAME, "songRight").find_element(By.TAG_NAME, "a")
                artist_name = artist_element.get_attribute("title").strip()
                artist_url = artist_element.get_attribute("href").strip()
                
                if song_name and artist_name:
                    print(f"Song: {song_name}, Artist: {artist_name}")
                    insert_song(song_name, artist_url)
                    song_id = get_song_id(song_name)
                    if song_id:
                        insert_mood_song(mood_id, song_id)
                else:
                    print("Incomplete data for song or artist, skipping...")
            except Exception as e:
                print(f"Error processing song element: {e}")
    except Exception as e:
        print(f"Error al extraer detalles del mood {mood_id}: {e}")

# Permitir la selección del mood desde la consola
def select_mood():
    moods_dict = get_all_moods_from_db()
    
    # Filtrar los moods que tienen URL
    valid_moods = {name: url for name, url in moods_dict.items() if url}
    
    if not valid_moods:
        print("No hay moods con URLs disponibles. Actualizando URLs primero...")
        update_mood_urls()
        moods_dict = get_all_moods_from_db()
        valid_moods = {name: url for name, url in moods_dict.items() if url}
        
        if not valid_moods:
            print("No se pudieron actualizar las URLs. Por favor, verifica la conexión a la base de datos y a AllMusic.")
            driver.quit()
            exit(1)
    
    # Mostrar los moods disponibles
    print("\nMoods disponibles:")
    mood_names = list(valid_moods.keys())
    for i, mood_name in enumerate(mood_names, 1):
        print(f"{i}. {mood_name}")
    
    try:
        # Permitir al usuario seleccionar un mood
        choice = int(input("\nSelecciona un mood por número (o 0 para salir): "))
        if choice == 0:
            print("Saliendo...")
            driver.quit()
            exit(0)
        
        selected_mood_name = mood_names[choice - 1]
        selected_mood_url = valid_moods[selected_mood_name]
        
        return selected_mood_name, selected_mood_url
    except (ValueError, IndexError):
        print("Selección inválida. Por favor, ingresa un número válido.")
        return select_mood()  # Recursión para pedir de nuevo
    

if __name__ == "__main__":
    try:
        # Actualizar las URLs de los moods en la base de datos si es necesario
        print("Verificando si hay moods sin URL...")
        moods_dict = get_all_moods_from_db()
        missing_urls = sum(1 for url in moods_dict.values() if not url)
        
        if missing_urls > 0:
            print(f"Encontrados {missing_urls} moods sin URL. Actualizando...")
            update_mood_urls()
        else:
            print("Todos los moods tienen URL.")
        
        # Permitir al usuario seleccionar un mood
        selected_mood_name, selected_mood_url = select_mood()
        print(f"\nIniciando scraping del mood: {selected_mood_name}")
        print(f"URL: {selected_mood_url}")
        
        # Obtener el ID del mood y hacer el scraping
        mood_id = get_mood_id(selected_mood_name)
        if mood_id:
            print(f"ID del mood: {mood_id}")
            # Añadir un retraso para asegurarnos de que el navegador esté listo
            time.sleep(2)
            scrape_mood_details(selected_mood_url, mood_id)
            print(f"\nScraping del mood {selected_mood_name} completado exitosamente.")
        else:
            print(f"No se pudo obtener el ID para el mood: {selected_mood_name}")
    
    except Exception as e:
        print(f"Error en la ejecución del script: {e}")
    finally:
        print("\nCerrando el navegador...")
        driver.quit()
        print("Script finalizado.")
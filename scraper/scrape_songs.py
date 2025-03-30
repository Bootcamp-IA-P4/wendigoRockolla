import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db.crud import insert_song, insert_mood_song, get_mood_id, get_mood_details_by_id, get_all_moods

#Selenium options
options = Options()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
print("Opening Google Chrome")

def handle_cookie_consent():
    try:
        
        time.sleep(5)
        consent_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.fc-consent-root button.fc-button.fc-cta-consent"))
        )
        consent_button.click()
        print("Cookie consent accepted")
    except Exception as e:
        print(f"Error handling cookie consent: {e}")

def getting_mood_id(mood_name):
    try:
        from db.crud import get_mood_id
        mood_id = get_mood_id(mood_name)
        print (f"Mood ID for '{mood_name}': {mood_id}")
        return mood_id
    except Exception as e:
        print(f"Error getting mood ID: {e}")
        return None

def get_mood_details_by_id(mood_id):
    """Get mood details including URL from database based on mood ID."""
    try:
        from db.crud import get_mood_details_by_id  # You'll need to create this function
        return get_mood_details_by_id(mood_id)
    except Exception as e:
        print(f"Error getting mood details: {e}")
        return None

def list_available_moods():
    """Muestra todos los moods disponibles en la base de datos."""
    try:
        moods = get_all_moods()
        if not moods:
            print("No hay moods disponibles en la base de datos.")
            return
        
        print("\n===== MOODS DISPONIBLES =====")
        for mood in moods:
            print(f"ID: {mood['id']} - Nombre: {mood['name']} - URL: {mood.get('url', 'Sin URL')}")
        print("=============================\n")
    except Exception as e:
        print(f"Error al listar moods: {e}")

def scrape_songs_for_mood(mood_id, mood_url, is_more_page=False):
    """Scrape songs for a given mood from AllMusic."""
    try:
        # Verificar que la URL sea válida
        if not mood_url or not mood_url.startswith("http"):
            print(f"URL inválida: {mood_url}")
            return False
        
        # Navigate to the mood page
        print(f"Intentando navegar a: {mood_url}")
        driver.get(mood_url)
        
        # Esperar más tiempo en la página de "More Songs"
        wait_time = 30 if is_more_page else 20
        time.sleep(5)  # Espera adicional para asegurar carga completa
        print(f"Navegado a {mood_url}")
        
        # Handle cookie consent if needed
        handle_cookie_consent()
        
        # Wait for the songs container to load - usar un selector diferente según la página
        if is_more_page:
            # Para la página "More Songs" tenemos un selector específico
            container_selector = "section.all-songs"
            print(f"Usando selector para página 'More Songs': {container_selector}")
        else:
            container_selector = "div#descriptorSongHighlights"
            print(f"Usando selector para página principal: {container_selector}")
        
        try:
            # Intentar con el selector específico primero
            song_container = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, container_selector))
            )
        except:
            # Si falla, intentar con un selector más genérico
            print(f"No se encontró el contenedor con selector {container_selector}. Intentando con selector genérico...")
            container_selector = "body"
            song_container = driver.find_element(By.CSS_SELECTOR, container_selector)
        
        # Esperar a que los títulos de canciones estén disponibles
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.songTitle"))
        )
        
        # En la página "More Songs", los selectores son diferentes
        song_titles = song_container.find_elements(By.CSS_SELECTOR, "span.songTitle")
        song_artists = song_container.find_elements(By.CSS_SELECTOR, "div.songRight")
        
        print(f"Encontrados {len(song_titles)} títulos de canciones")
        print(f"Encontrados {len(song_artists)} artistas")
        
        # Procesar cada canción con su artista correspondiente
        for i in range(min(len(song_titles), len(song_artists))):
            try:
                song_name = song_titles[i].text.strip()
                artist_name = song_artists[i].text.strip()
                
                # Excluir información del compositor si está presente
                if "(" in song_name:
                    song_name = song_name.split("(")[0].strip()
                
                print(f"Canción encontrada: '{song_name}' por {artist_name}")
                
                # Insertar en la base de datos
                song_id = insert_song(song_name, artist_name, force_update_artist=True)
                if song_id:
                    insert_mood_song(mood_id, song_id)
                    print(f"Guardada canción '{song_name}' por {artist_name}")
                else:
                    print(f"Error: No se pudo obtener ID para la canción '{song_name}'")
            except Exception as e:
                print(f"Error procesando una canción: {e}")
        
        # Si no estamos ya en la página "More", buscar y seguir el enlace "More X Songs"
        if not is_more_page:
            try:
                print("Buscando enlace a 'More Songs'...")
                # Usar un selector más genérico para encontrar el enlace "More X Songs"
                more_songs_links = driver.find_elements(By.XPATH, "//a[contains(@title, 'More')]")
                
                more_url = None
                for link in more_songs_links:
                    title = link.get_attribute('title')
                    if title and 'Songs' in title:
                        more_url = link.get_attribute('href')
                        break
                
                if more_url:
                    print(f"Encontrado enlace a más canciones: {more_url}")
                    
                    # Llamar recursivamente a esta función con la nueva URL
                    print("Navegando a la página de más canciones...")
                    return scrape_songs_for_mood(mood_id, more_url, is_more_page=True)
                else:
                    print("No se encontró enlace a más canciones.")
            except Exception as e:
                print(f"Error al buscar enlace a más canciones: {e}")
        
        return True
    except Exception as e:
        print(f"Error scraping songs for mood: {e}")
        import traceback
        traceback.print_exc()  # Imprimir stack trace completo
        return False

def main():
    try:
        # Mostrar moods disponibles primero
        list_available_moods()
        
        # Preguntar si desea scrapear todos los moods o seleccionar algunos
        choice = input("¿Deseas scrapear todos los moods? (s/n): ").strip().lower()
        
        mood_ids = []
        if choice == 's' or choice == 'si':
            # Obtener todos los IDs de moods disponibles
            moods = get_all_moods()
            mood_ids = [mood['id'] for mood in moods]
            print(f"Se procesarán todos los {len(mood_ids)} moods disponibles.")
        else:
            # Permitir al usuario ingresar múltiples IDs
            mood_ids_input = input("Ingresa los IDs de los moods que deseas scrapear (separados por coma): ")
            try:
                mood_ids = [int(id.strip()) for id in mood_ids_input.split(',') if id.strip()]
            except ValueError:
                print("Por favor, ingresa números enteros válidos para los IDs de los moods.")
                return
        
        if not mood_ids:
            print("No se seleccionaron moods para procesar.")
            return
            
        # Procesar cada mood seleccionado
        successfully_scraped = 0
        for mood_id in mood_ids:
            try:
                print(f"\n{'='*50}")
                print(f"Procesando mood ID: {mood_id}")
                
                # Get mood details including URL
                mood_details = get_mood_details_by_id(mood_id)
                
                if not mood_details or 'url' not in mood_details:
                    print(f"No se encontraron detalles válidos para el mood con ID {mood_id}, saltando...")
                    continue
                
                mood_name = mood_details.get('name', f"Mood {mood_id}")
                mood_url = mood_details['url']
                
                print(f"Scraping songs for mood: {mood_name}")
                print(f"URL a visitar: {mood_url}")
                
                # Scrape songs for the selected mood
                success = scrape_songs_for_mood(mood_id, mood_url)
                
                if success:
                    print(f"Successfully scraped songs for mood: {mood_name}")
                    successfully_scraped += 1
                else:
                    print(f"Failed to scrape songs for mood: {mood_name}")
                    
                print(f"{'='*50}\n")
            except Exception as e:
                print(f"Error procesando mood ID {mood_id}: {e}")
        
        print(f"\nResumen: Scrapeados correctamente {successfully_scraped} de {len(mood_ids)} moods.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    main()
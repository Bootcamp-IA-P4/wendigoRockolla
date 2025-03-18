import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from db.crud import insert_artist, insert_mood, insert_song, insert_albums, insert_mood  # Importar funciones de la DB

#Optiones de Selenium
options = Options()
# options.add_argument('--incognito')


# Configurar Selenium con ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(options=options)
print("Open Google browser")

def handle_cookie_consent():
    try:
        consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.fc-consent-root button.fc-button.fc-cta-consent"))
        )
        consent_button.click()
        print("Cookie consent accepted")
    except Exception as e:
        print(f"Error handling cookie consent: {e}")

# Extraer moods
def scrape_moods():
    moods_url = "https://www.allmusic.com/moods"
    driver.get(moods_url)
    handle_cookie_consent()
    
    try:
        mood_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#allMoodsGridDesktop a"))
        )
        for mood_element in mood_elements:
            mood_name = mood_element.get_attribute("title").strip()
            if mood_name:
                print(f"Mood: {mood_name}")
                insert_mood(mood_name)
    except Exception as e:
        print(f"Error al extraer moods: {e}")

# Extrae albums y artistas
def scrape_albums():
    driver.get("https://www.allmusic.com/mood/druggy-xa0000000979")
    handle_cookie_consent()
    
    try:
        albums = WebDriverWait(driver, 10).until(
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
                else:
                    print("Incomplete data for album or artist, skipping...")
            except Exception as e:
                print(f"Error processing album element: {e}")
    except Exception as e:
        print(f"Error al extraer álbumes: {e}")

# Extraer canciones
def scrape_songs():
    """Extrae y guarda canciones"""
    driver.get("https://www.allmusic.com/mood/druggy-xa0000000979")
    handle_cookie_consent()

    try:
        song_rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "songRow"))
        )
        for song_row in song_rows:
            try:
                song_name = song_row.find_element(By.CLASS_NAME, "songTitle").text.strip()
                artist_element = song_row.find_element(By.CLASS_NAME, "songRight").find_element(By.TAG_NAME, "a")
                artist_name = artist_element.get_attribute("title").strip()
                artist_url = artist_element.get_attribute("href").strip()
                
                if song_name and artist_name:
                    print(f"Song: {song_name}, Artist: {artist_name}")
                    insert_song(song_name, artist_url)
                else:
                    print("Incomplete data for song or artist, skipping...")
            except Exception as e:
                print(f"Error processing song element: {e}")
    except Exception as e:
        print(f"Error al extraer canciones: {e}")

if __name__ == "__main__":
    scrape_moods()
    scrape_albums()
    scrape_songs()
    driver.quit()

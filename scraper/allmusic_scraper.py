import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from db.crud import insert_artist, insert_mood, insert_track, insert_albums  # Importar funciones de la DB

#Optiones de Selenium
options = Options()
options.add_argument('--incognito')


# Configurar Selenium con ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(options=options)
print ("Open Google browser in incognito mode")

# Extraer moods
def scrape_moods():
    
    moods_url = "https://www.allmusic.com/moods"
    driver.get(moods_url)
    time.sleep(3)
    
    try:
        mood_elements = driver.find_elements(By.CLASS_NAME, "allMoodGridDesktop a")
        for mood_element in mood_elements:
            mood_name = mood_element.text.strip()
            if mood_name:
                print(f"Mood: {mood_name}")
                insert_mood(mood_name)
    except Exception as e:
        print(f"Error al extraer moods: {e}")

# Extrae albums y artistas
def scrape_albums():
    
    driver.get("https://www.allmusic.com/mood/druggy-xa0000000979")
    time.sleep(3)
    
    try:
        albums = driver.find_elements(By.CLASS_NAME, "singleGenreAlbum")
        for album in albums:
            title_element = album.find_element(By.CLASS_NAME, "descriptorTitle")
            artist_element = album.find_element(By.CLASS_NAME, "descriptorArtist")
            cover_element = album.find_element(By.TAG_NAME, "img")

            album_name = title_element.text.strip()
            album_url = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            artist_name = artist_element.text.strip()
            artist_url = artist_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            cover_url = cover_element.get_attribute("data-src") or cover_element.get_attribute("src")

            print(f"Album: {album_name}, Artist: {artist_name}, Cover: {cover_url}")
            
            insert_artist(artist_name, artist_url)
            insert_albums(album_name, cover_url, album_url)
    except Exception as e:
        print(f"Error al extraer álbumes: {e}")

# Extraer canciones
def scrape_songs():
    """Extrae y guarda canciones"""
    try:
        songs = driver.find_elements(By.CLASS_NAME, "song")
        for song in songs:
            song_name = song.find_element(By.CLASS_NAME, "songTitle").text.strip()
            song_url = song.find_element(By.CLASS_NAME, "songTitle").find_element(By.TAG_NAME, "a").get_attribute("href")
            
            print(f"Song: {song_name}, URL: {song_url}")
            insert_track(song_name, song_url)
    except Exception as e:
        print(f"Error al extraer canciones: {e}")

if __name__ == "__main__":
    scrape_moods()
    scrape_albums()
    scrape_songs()
    driver.quit()

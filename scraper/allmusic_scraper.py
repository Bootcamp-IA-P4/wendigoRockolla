import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from db.crud import insert_artist, insert_mood, insert_song, insert_albums, insert_mood_song, insert_mood_album, get_mood_id, get_album_id, get_song_id

#Optiones de Selenium
options = Options()
# options.add_argument('--incognito')

# Configurar Selenium con ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(options=options)
print("Open Google browser")

def handle_cookie_consent():
    try:
        consent_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.fc-consent-root button.fc-button.fc-cta-consent"))
        )
        consent_button.click()
        print("Cookie consent accepted")
    except Exception as e:
        print(f"Error handling cookie consent: {e}")

# Extraer moods y URLs
def get_moods():
    moods_url = "https://www.allmusic.com/moods"
    driver.get(moods_url)
    handle_cookie_consent()
    
    moods_dict = {}
    try:
        mood_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#allMoodsGridDesktop a"))
        )
        for mood_element in mood_elements:
            mood_name = mood_element.get_attribute("title").strip()
            mood_url = mood_element.get_attribute("href").strip()
            if mood_name:
                moods_dict[mood_name] = mood_url
    except Exception as e:
        print(f"Error al extraer moods: {e}")
    
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

# Scrape todos los moods
def scrape_all_moods():
    moods_dict = get_moods()
    for mood_name, mood_url in moods_dict.items():
        print(f"Scraping mood: {mood_name}")
        insert_mood(mood_name)
        mood_id = get_mood_id(mood_name)
        if mood_id:
            scrape_mood_details(mood_url, mood_id)

if __name__ == "__main__":
    scrape_all_moods()
    driver.quit()
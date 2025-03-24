![wendigo](https://github.com/user-attachments/assets/5ae70e39-8c86-422a-be78-dc1efffc34b3)


<p align="center"> <img src="https://img.shields.io/badge/Wendigo_Finder-WIP-yellow?style=for-the-badge&logo=GitHub&logoColor=blue&logoSize=auto&labelColor=black"> </p>
<p align="center"><img src="https://img.shields.io/badge/ATENCIÓN-red?style=for-the-badge&labelColor=yellow"></p>

<p align="center"><em>Este proyecto es exclusivamente educativo y no tiene fines comerciales.  
Los datos obtenidos a través de scraping y APIs pertenecen a sus respectivos dueños.</em></p>

<h1 align="center"> Introducción </h1> 
🔥 Wendigo Music Finder no es solo un buscador de música... es un cazador. Como la mítica criatura del folklore, no eres tú quien lo encuentra; es él quien te encuentra a ti.

Olvídate de perder horas explorando listas interminables. Solo elige tu mood y deja que Wendigo descubra la música perfecta para ti. No busques la música… deja que la música te encuentre. 🎵✨

Por cierto, puedes encontrar todos los géneros en esta app, a wendi le gusta toda la música...

El proyecto cuenta con integración de APIs de **Last.fm, Genius y Spotify** para poder guardar tus playlists y compartirlas con otros usuarios, enriqueciendo tu experiencia musical con información detallada sobre artistas, canciones y letras.  

---

## 📌 Índice  
- [Requisitos](#requisitos)  
- [Instalación](#instalación)  
- [Configuración](#configuración)  
- [Uso](#uso)  
  - [Aplicación Principal](#app-principal)  
  - [Scraper Principal](#scraper-principal)  
  - [Scraper de Moods Existentes](#scraper-de-moods-existentes)  
  - [Data Cleaner](#data-cleaner)  
- [Tecnologías](#tecnologías)  
- [Funcionalidades](#funcionalidades)  
- [APIs](#apis)  
- [Licencia](#licencia)  

---

## REQUISITOS
- **Python 3.9 o superior**  
- **MySQL/MariaDB**  
- **Google Chrome** (para Selenium)  
- **Conexión a internet**  


![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.0+-43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![Genius](https://img.shields.io/badge/API-Genius-FFFF64?style=for-the-badge&logo=genius&logoColor=black)
![Spotify](https://img.shields.io/badge/API-Spotify-1DB954?style=for-the-badge&logo=spotify&logoColor=white)


---

## INSTALACIÓN

1. **Clona el repositorio:**  
   ```bash
   git clone https://github.com/tu-usuario/wendigo-music-finder.git
   cd wendigo-music-finder
   ```

2. **Crea y activa un entorno virtual:**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # En macOS/Linux
   venv\Scripts\activate     # En Windows
   ```

3. **Instala las dependencias:**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura la base de datos:**  
   ```bash
   mysql -u root -p -e "CREATE DATABASE wendigo_db;"
   ```

---

## CONFIGURACIÓN

1. **Crea un archivo .env en la raíz del proyecto con las siguientes variables**

   ```bash
   MYSQL_HOST=localhost
   MYSQL_USER=tu_usuario
   MYSQL_PASSWORD=tu_contraseña
   MYSQL_DB=wendigo_db
   SPOTIFY_CLIENT_ID=tu_spotify_client_id
   SPOTIFY_CLIENT_SECRET=tu_spotify_client_secret
   GENIUS_API_KEY=tu_genius_api_key
   ```
---

## USO

### <em>App principal</em>

   1. **Asegúrate de estar a la altura del archivo "app.py" (en la raíz del proyecto)**

   2. **Para iniciar la aplicación web principal:**

      ```bash
      python app.py
      ```

   3. **Abre tu navegador y ve a http://localhost:5000 para acceder a la aplicación.**

Podrás explorar las diferentes funcionalidades de la aplicación, como buscar música, ver tus playlists, etc.

<em>Scraper Allmusic</em>

1. **Asegúrate de estar a la altura del archivo scraper_allmusic.py**
2. **Para iniciar el scraper:**

   ```bash
   python scraper_allmusic.py
   ```

3.**El scraper comenzará a recopilar datos de Allmusic. (Puede tardar un par de horas, recuerda que es mucha información)**

### <em>Scraper de moods independientes</em>

 Este scraper se encarga de obtener los datos de los moods existentes en la base de datos.

1. **Asegúrate de estar a la altura del archivo scraper_moods.py**
2. **Para iniciar el scraper:**

   ```bash
   python scrape_existing_moods.
   ```

3. **El scraper comenzará a recopilar datos de los moods existentes en la base de datos**

### <em>Limpiador de data</em>

El limpiador de datos se encarga de limpiar los datos obtenidos de las APIs y de los scrapers, evitando que existan datos duplicados.

1. **Asegúrate de estar a la altura del archivo data_cleaner.py**
2. **Para iniciar el limpiador de datos:**
   
   ```bash
   python data_cleaner.py
   ```

3. **El limpiador de datos comenzará a limpiar los datos obtenidos de las APIs y de los scrapers.**

---

## Tecnologías
- **Python:** Lenguaje principal de desarrollo
- **Selenium:** Para web scraping y automatización del navegador
- **MySQL:** Base de datos relacional para almacenamiento de la información
- **Pandas:** Análisis y limpieza de datos
- **Flask:** Framework web para la interfaz de usuario
- **ChromeDriver:** Driver para controlar Chrome desde Selenium

---

## Funcionalidades

- ✔ **Búsqueda por Mood:** Encuentra música basada en tu estado de ánimo actual
- ✔ **Descubrimiento de Música:** Descubre nuevos artistas y canciones relacionadas con tus preferencias
- ✔ **Integración con Spotify:** Guarda y comparte playlists directamente en tu cuenta de Spotify
- ✔ **Letras de Canciones:** Accede a letras e información adicional gracias a la API de Genius
- ✔ **Recomendaciones Personalizadas:** Recibe recomendaciones basadas en tu historial de escucha
- ✔ **Depuración de Datos:** Limpieza automatizada de datos para asegurar información de calidad

![Macbook-Air](https://github.com/user-attachments/assets/269213b2-2cf2-45dd-b6a8-ea1b9ee7bde7)


---

## Tests 🧪

1. **Asegúrate de estar a la altura del archivo test.py, en la rama test**
2. **Instalación de las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Para ejecutar los tests con detalles:**
   ```bash
   python -m unittest test.py -v
   ```

Lista de tests:

 - Tests CRUD de la base de datos
   - test_get_all_moods
   - test_get_mood_by_name
   - test_add_mood
   - test_update_mood_url
   - test_delete_mood_by_id
   - test_get_all_artists
   - test_get_all_albums
   - test_get_songs_by_mood_id
  
    ![crudtestpassed](https://github.com/user-attachments/assets/7542bc88-f065-43a3-9bde-cdf113816595)


- Tests de la API de Spotify **(test_spotify_api.py)**
  - test_search_tracks
  - test_advanced_search_track
  - test_get_auth_url
  - test_get_token_info
  - test_get_user_profile
 
  ![TestsapiSpotifyPassed](https://github.com/user-attachments/assets/1aeb6054-bcff-4aeb-a9de-98848d6e0649)


**Base de datos de prueba:** Utilizan una base de datos separada para evitar modificar datos reales.

**Mocks para APIs externas:** Simulan las respuestas de Spotify sin necesidad de conexiones reales.

**Cobertura completa:** Prueban todos los aspectos críticos de la aplicación: base de datos, scraping y API externa.

**Automatización:** Pueden ejecutarse automáticamente como parte del proceso de desarrollo para detectar problemas temprano.

Estos tests constituyen una base sólida para garantizar que Wendigo Music Finder funcione correctamente en todos sus componentes clave.

![test passed](https://github.com/user-attachments/assets/e2250153-02a2-49e0-9640-227611cafc3a)

---
## Licencia 📜

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para obtener más detalles.

---
## Contacto 📧
Si tienes preguntas o comentarios, no dudes en contactarme:






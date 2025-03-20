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
  - [Aplicación Principal](#aplicación-principal)  
  - [Scraper Principal](#scraper-principal)  
  - [Scraper de Moods Existentes](#scraper-de-moods-existentes)  
  - [Data Cleaner](#data-cleaner)  
- [Tecnologías](#tecnologías)  
- [Funcionalidades](#funcionalidades)  
- [APIs](#apis)  
- [Contribuciones](#contribuciones)  
- [Licencia](#licencia)  

---

## ✅ Requisitos  
- **Python 3.9 o superior**  
- **MySQL/MariaDB**  
- **Google Chrome** (para Selenium)  
- **Conexión a internet**  


![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-yellow.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg)
![Last.fm](https://img.shields.io/badge/API-Last.fm-red.svg)
![Genius](https://img.shields.io/badge/API-Genius-purple.svg)
![Spotify](https://img.shields.io/badge/API-Spotify-brightgreen.svg)

---

## ⚙️ Instalación  

1. **Clona el repositorio:**  
   ```bash
   git clone https://github.com/tu-usuario/wendigo-music-finder.git
   cd wendigo-music-finder

2. **Crea y activa un entorno virtual:**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # En macOS/Linux
   venv\Scripts\activate     # En Windows

3. **Instala las dependencias:**  
   ```bash
   pip install -r requirements.txt

4. **Configura la base de datos:**  
   ```bash
   mysql -u root -p -e "CREATE DATABASE wendigo_db;"

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
   LASTFM_API_KEY=tu_lastfm_api_key

---

## USO

<em>App principal</em>

1. Asegúrate de estar a la altura del archivo app.py

2. Para iniciar la aplicación web principal:
```bash
   python app.py


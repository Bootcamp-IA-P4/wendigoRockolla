from flask import Flask, render_template, request, url_for
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper.db.crud import get_data, get_all_moods
from static.mood_images import get_mood_image

app = Flask(__name__)

# Función auxiliar para obtener iconos según el mood
def get_mood_icon(mood_name):
    # Diccionario de iconos para algunos moods comunes
    mood_icons = {
        'Happy': 'fa-smile',
        'Sad': 'fa-frown',
        'Angry': 'fa-fire',
        'Relaxing': 'fa-spa',
        'Energetic': 'fa-bolt',
        'Romantic': 'fa-heart',
        'Epic': 'fa-mountain',
        'Melancholic': 'fa-cloud-rain',
        'Dreamy': 'fa-moon',
        'Dramatic': 'fa-theater-masks',
        'Gloomy': 'fa-cloud',
        'Uplifting': 'fa-sun',
    }
    
    # Devuelve el icono si existe, o un icono predeterminado si no
    return mood_icons.get(mood_name, 'fa-music')

@app.route('/')
def index():
    # Obtener algunos moods de la base de datos (limita a 8-12 para la página principal)
    moods_data = get_all_moods()
    moods = moods_data[:12] if moods_data else []
    
    return render_template('index.html', moods=moods, get_mood_icon=get_mood_icon, get_mood_image=get_mood_image)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    search_type = request.args.get('type', 'mood')
    results = get_data(query, search_type)
    return render_template('results.html', results=results, query=query, type=search_type)

# Página de administración para editar moods
@app.route('/admin/moods')
def admin_moods():
    moods_data = get_all_moods()
    return render_template('admin_moods.html', moods=moods_data, get_mood_image=get_mood_image)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)
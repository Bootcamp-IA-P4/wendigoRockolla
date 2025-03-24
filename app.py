from flask import Flask, render_template, request
from scraper.db.crud import get_moods, get_recommendations_by_mood

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    moods = get_moods()
    recommendations = {"albums": [], "songs": []}
    
    if request.method == "POST":
        selected_mood_id = request.form["mood"]
        recommendations = get_recommendations_by_mood(selected_mood_id)

    return render_template("index.html", moods=moods, recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)

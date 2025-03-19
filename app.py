from flask import Flask, render_template, request
from scraper.db.crud import get_data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    search_type = request.args.get('type')
    
    results = get_data(query, search_type)
    
    return render_template('results.html', results=results, query=query, search_type=search_type)

if __name__ == '__main__':
    app.run(debug=True)
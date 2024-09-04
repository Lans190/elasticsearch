from flask import Flask, render_template, jsonify, request
from elasticsearch import Elasticsearch, helpers
import requests

app = Flask(__name__)

# Configuration
api_key = 'd477bb2e60fc4ee6aee9ea1421afba7e'
competition_id = '2021'  # Premier League

# Connexion à Elasticsearch
# Connexion à Elasticsearch sur localhost
es = Elasticsearch(
    hosts=["http://localhost:9200"],  # URL du nœud Elasticsearch local
)

# Fonction pour obtenir les matchs d'une compétition
def get_matches(competition_id):
    url = f"https://api.football-data.org/v4/competitions/{competition_id}/matches"
    headers = {'X-Auth-Token': api_key}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()['matches']
    else:
        print(f"Erreur lors de la récupération des données: {response.status_code}")
        return []

# Fonction pour insérer les données dans Elasticsearch
def index_data_to_elasticsearch(matches):
    actions = [
        {
            "_index": "football_matches",
            "_source": match
        }
        for match in matches
    ]
    
    helpers.bulk(es, actions)
    return len(actions)




# Route pour l'interface
@app.route('/')
def index():
    return render_template('index.html')

# Route pour récupérer les données de matchs et les insérer dans Elasticsearch
@app.route('/load-data')
def load_data():
    matches = get_matches(competition_id)
    if matches:
        count = index_data_to_elasticsearch(matches)
        return jsonify({'message': f"{count} données de football insérées avec succès dans Elasticsearch."})
    else:
        return jsonify({'message': "Aucune donnée à insérer."})

# Route pour rechercher des données dans Elasticsearch

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'message': 'Veuillez fournir un mot-clé pour la recherche.'})

    search_body = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"homeTeam.name": query}},
                    {"match": {"awayTeam.name": query}},
                    {"match": {"referees.name": query}},
                ]
            }
        }
    }

    try:
        result = es.search(index="football_matches", body=search_body)
        hits = result['hits']['hits']
        results = [
            {
                "_index": hit["_index"],
                "_id": hit["_id"],
                "_source": hit["_source"]
            }
            for hit in hits
        ]
        return jsonify(results)
    except Exception as e:
        import traceback
        error_message = str(e)
        tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
        return jsonify({'error': error_message, 'traceback': ''.join(tb_str)})


if __name__ == '__main__':
    app.run(debug=True)
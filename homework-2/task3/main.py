from flask import Flask, request, jsonify
from google.cloud import datastore
import logging
import farmhash


app = Flask(__name__)
datastore_client = datastore.Client()

# Configure logging
logging.basicConfig(level=logging.INFO)

RELATED_QUERIES_KIND = "RelatedQueries"

def get_group_id(query):
    hash_value = farmhash.fingerprint64(query)
    group_id = abs(hash_value) % 1000
    return group_id

def get_related_queries_group(group_id):
    try:
        key = datastore_client.key(RELATED_QUERIES_KIND, str(group_id))
        group = datastore_client.get(key)
        return group
    except Exception as e:
        logging.error(f"Error fetching group from Datastore: {e}")
        return None

def get_related_queries(query):
    group_id = get_group_id(query)
    # Fetch from Datastore
    group = get_related_queries_group(group_id)
    if group:
        queries_dict = group.get('queries_dict')
        if queries_dict:
            related_queries = queries_dict.get(query, [])

            return related_queries
    return []

@app.route('/related', methods=['GET'])
def related():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    related_queries = get_related_queries(query)
    return jsonify(related_queries)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
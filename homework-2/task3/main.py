from flask import Flask, request, jsonify
from google.cloud import datastore
import logging
import hashlib
from pymemcache.client.base import Client
import json
import base64

app = Flask(__name__)
datastore_client = datastore.Client()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure Memcache
memcache_client = Client(('10.115.208.3', 11211))

RELATED_QUERIES_KIND = "RelatedQueries"
ttl = 300  # cache ttl (5 minutes)

def get_group_id(query):
    hash_object = hashlib.sha256(query.encode())
    group_id = hash_object.hexdigest()[:2]
    return group_id

def get_related_queries_group(group_id):
    try:
        key = datastore_client.key(RELATED_QUERIES_KIND, str(group_id))
        group = datastore_client.get(key)
        return group
    except Exception as e:
        logging.error(f"Error fetching group from Datastore: {e}")
        return None

def encode_key(key):
    return base64.urlsafe_b64encode(key.encode()).decode()

def get_related_queries(query):
    group_id = get_group_id(query)
    logging.info(f"group_id: {group_id}")

    encoded_query = encode_key(query)
    # Check Memcache first
    cached_result = memcache_client.get(encoded_query)
    if cached_result:
        logging.info(f"Cache hit for query: {query}")
        return json.loads(cached_result)

    # Fetch from Datastore if not in cache
    group = get_related_queries_group(group_id)
    if group:
        queries_dict = group.get('queries_dict')
        if queries_dict:
            related_queries = queries_dict.get(query, [])

            # Store result in Memcache
            memcache_client.set(encoded_query, json.dumps(related_queries), expire=ttl)

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
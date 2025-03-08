from flask import Flask, request, jsonify
from google.cloud import datastore
from google.cloud import memcache
import logging

app = Flask(__name__)
datastore_client = datastore.Client()
memcache_client = memcache.Client()

TTL = 300  # 5 minutes in seconds

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define Datastore kind
RELATED_QUERIES_KIND = "RelatedQueries"

def get_group_id(query):
    return abs(hash(query)) % 1000  # Assuming 1000 groups

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

    # Check Memcache first
    try:
        cached_result = memcache_client.get(query)
        if cached_result:
            logging.info(f"Cache hit for query: {query}")
            return cached_result
    except Exception as e:
        logging.error(f"Error accessing Memcache: {e}")

    # Fetch from Datastore if not in Memcache
    group = get_related_queries_group(group_id)
    if group:
        queries_dict = group.get('queries_dict')
        if queries_dict:
            related_queries = queries_dict.get(query, [])

            # Cache the result in Memcache
            try:
                memcache_client.set(query, related_queries, TTL)
                logging.info(f"Cached result for query: {query}")
            except Exception as e:
                logging.error(f"Error setting Memcache: {e}")

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
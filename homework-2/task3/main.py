from flask import Flask, request, jsonify
from google.cloud import datastore
import logging
import hashlib
from pymemcache.client.base import Client
import json
import base64
import time

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

datastore_client = datastore.Client()
# configure Memcache
memcache_client = Client(('10.115.208.3', 11211))
ttl = 300  # cache ttl (5 minutes)
RELATED_QUERIES_KIND = "RelatedQueries"

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
    # check memcache first
    cached_result = memcache_client.get(encoded_query)
    if cached_result:
        logging.info(f"Cache hit for query: {query}")
        return json.loads(cached_result)

    # fetch from datastore if not in cache
    group = get_related_queries_group(group_id)
    if group:
        queries_dict = group.get('queries_dict')
        if queries_dict:
            related_queries = queries_dict.get(query, [])

            # store result in Memcache
            memcache_client.set(encoded_query, json.dumps(related_queries), expire=ttl)

            return related_queries
    return []

@app.route('/related', methods=['GET'])
def related():
    start_time = time.time()
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    related_queries = get_related_queries(query)
    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000
    logging.info(f"processing_time: {int(processing_time_ms)} ms")
    return jsonify(related_queries)


@app.route('/ping', methods=['GET'])
def ping():
    return "pong"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True)
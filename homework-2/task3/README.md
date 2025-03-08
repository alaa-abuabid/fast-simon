

## Overview

application with an API endpoint to fetch related queries based on an input query. It uses Google Cloud Datastore for persistent storage and Memcache for caching to enhance performance and reduce latency.

## What It Does

The application receives a query and returns a list of related queries. It first checks if the related queries are available in the cache (Memcache). If not it fetches the related queries from Google Cloud Datastore, caches the result and then returns the related queries.

## How It Does It

1. **Group ID Generation**:
   - The application generates a group id for each query using the SHA256 hashing algorithm. By taking a substring of the hash, it ensures a manageable number of unique groups.

2. **Cache Check**:
   - The application checks Memcache to see if the related queries for the given query are already cached. If a cache hit occurs, the related queries are returned immediately.

3. **Datastore Fetch**:
   - If the related queries are not found in the cache, the application fetches the related queries group from Google Cloud Datastore using the generated group id.

4. **Response**:
   - The related queries are returned as a JSON response. If the queries were fetched from Datastore, they are also stored in Memcache for future requests.

5. **Encoding**:
   - The query is encoded using base64 before storing it in Memcache to ensure that the key is safe for caching and does not contain any special characters.

## Why This Approach

1. **Caching**:
   - **Reason**: Caching is used to improve performance by reducing the number of reads from Datastore. This helps in serving frequent queries faster and reduces the load on the Datastore.
   - **Benefit**: Faster response times for frequently requested queries and reduced operational costs.

2. **SHA256 Hashing**:
   - **Reason**: SHA256 is a robust hashing algorithm that ensures consistent and unique group ids. By taking a substring of the hash, the application can control the number of unique groups.
   - **Benefit**: Effective grouping of related queries and consistent group ids generation.

3. **Encoding Before Caching**:
   - **Reason**: Encoding the query using base64 before storing it in Memcache ensures that the key is safe for caching and does not contain any special characters.
   - **Benefit**: Prevents issues with special characters in cache keys and ensures compatibility with Memcache.


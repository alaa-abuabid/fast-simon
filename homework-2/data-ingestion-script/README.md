# Data Ingestion Script

Overview
This script processes user query logs from BigQuery and stores related queries in Google Datastore. 
It is designed to run periodically or be triggered by new data, ensuring that the Datastore is always up-to date with the latest log data.

## What It Does

The script performs the following tasks:

1. Runs an SQL query in BigQuery to find related queries based on user sessions.
2. Processes the results to create a dictionary of related queries.
3. Stores the processed data in Google Datastore.

## How It Does It

1. **SQL Query Execution:** The script runs an SQL query that groups user search queries into 1000 evenly distributed groups using a hash function. For each query, it finds related queries that appear in the same user sessions and removes duplicates.
2. **Processing Results:** The results of the SQL query are processed to create a dictionary (queries_dict) where each key is an original query and the value is an array of related queries.
3. **Storing in Datastore:** The processed data is stored in Google Datastore as entities of kind RelatedQueriesGroup. Each entity contains a group_id and a queries_dict.

## Why This Approach

1. **Hashing for Grouping:**
* Scalability: Hashing distributes queries evenly across groups, ensuring no single group becomes too large. This makes the system scalable and capable of handling large datasets.
* Performance: Grouping queries reduces the number of Datastore entities, improving read/write performance and reducing latency.
* Space Optimization: Using group_id to group related queries helps minimize the number of entities stored in Datastore, optimizing storage space and reducing costs.

2. **Using a Dictionary (queries_dict):**
* Efficient Retrieval: A dictionary allows for fast O(1) lookups, ensuring efficient retrieval of related queries.
* Memory Optimization: Storing related queries in a dictionary reduces the number of entities in Datastore, optimizing memory usage and reducing costs.
Effective Caching:

3. **Fast Access:** 
* Grouping allows for effective caching in Memcache, reducing the need for frequent Datastore lookups and ensuring fast response times for frequently accessed queries.

This approach provides an efficient solution for managing and retrieving related queries, balancing performance, scalability, and cost-efficiency.
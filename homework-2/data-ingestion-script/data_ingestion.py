from google.cloud import bigquery, datastore
import logging


# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Print to console
        logging.FileHandler('data_ingestion.log')  # Print to file
    ]
)

RELATED_QUERIES_KIND = "RelatedQueries"
project_id = 'charged-state-451616-h7'
bigquery_client = bigquery.Client(project=project_id)
datastore_client = datastore.Client(project=project_id)

query = """
SELECT
  group_id,
  ARRAY_AGG(STRUCT(query, related_queries)) AS queries
FROM (
  SELECT
    SUBSTR(TO_HEX(SHA256(query)), 1, 2) AS group_id,
    query,
    ARRAY_AGG(related_query ORDER BY count DESC LIMIT 3) AS related_queries
  FROM (
    SELECT a.query AS query, b.query AS related_query, COUNT(*) AS count
    FROM `charged-state-451616-h7.query_logs_dataset.query_logs` a
    JOIN `charged-state-451616-h7.query_logs_dataset.query_logs` b
    ON a.session = b.session AND a.query != b.query
    WHERE a.query IS NOT NULL AND a.query != ''
      AND b.query IS NOT NULL AND b.query != ''
    GROUP BY a.query, b.query
  )
  GROUP BY query, group_id
)
GROUP BY group_id
"""

def run_query_and_update_datastore():
    try:
        # run the query
        query_job = bigquery_client.query(query)
        results = query_job.result()

        for row in results:
            group_id = row['group_id']
            queries_dict = {entry['query']: entry['related_queries'] for entry in row['queries']}

            # create a datastore entity
            entity_key = datastore_client.key(RELATED_QUERIES_KIND, str(group_id))
            entity = datastore.Entity(key=entity_key, exclude_from_indexes=['queries_dict'])
            entity.update({
                'group_id': group_id,
                'queries_dict': queries_dict
            })

            # store the entity in datastore
            datastore_client.put(entity)

            logging.info(f"Stored entity with group_id={group_id} and dict_length={len(queries_dict)}")

        logging.info("Data ingestion completed successfully.")
    except Exception as e:
        logging.error(f"Error during data ingestion: {e}")

if __name__ == "__main__":
    run_query_and_update_datastore()
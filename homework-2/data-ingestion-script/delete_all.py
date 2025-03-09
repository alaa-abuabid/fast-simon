from google.cloud import datastore
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Print to console
        logging.FileHandler('delete_entities.log')  # Print to file
    ]
)

project_id = 'charged-state-451616-h7'
datastore_client = datastore.Client(project=project_id)
ENTITY_KIND = "RelatedQueries"

def delete_all_entities():
    try:
        query = datastore_client.query(kind=ENTITY_KIND)
        entities = query.fetch()

        # delete each entity
        for entity in entities:
            datastore_client.delete(entity.key)
            logging.info(f"Deleted entity with key: {entity.key}")

        logging.info("All entities deleted successfully.")
    except Exception as e:
        logging.error(f"Error during entity deletion: {e}")

if __name__ == "__main__":
    delete_all_entities()
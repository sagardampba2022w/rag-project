from typing import Dict, List
from elasticsearch import Elasticsearch, exceptions
from mage_ai.data_preparation.variable_manager import get_global_variable

# Sample text query to be used in the search
SAMPLE_QUERY = "When is the next cohort?"

@data_loader
def search(*args, **kwargs) -> List[List[Dict]]:
    """
    query_text: str
    connection_string: str
    search_field: str
    top_k: int
    """
    
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    top_k = kwargs.get('top_k', 5)

    # Debug: Print all kwargs
    # print("Debug: Received kwargs:", kwargs)

    # Retrieve the global index name
    index_name = get_global_variable('stellar_luminos', 'index_name')
    # print(f"Debug: Retrieved index name: {index_name}")
    if not index_name:
        # print("Error: Global variable 'index_name' not found.")
        return []

    query_text = None
    if len(args):
        query_text = args[0]
    if not query_text:
        query_text = SAMPLE_QUERY
    # print(f"Debug: Using query text: {query_text}")

    search_query = {
        "size": top_k,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "data-engineering-zoomcamp"
                    }
                }
            }
        }
    }

    es_client = Elasticsearch(connection_string)
    
    try:
        # Debug: Check if the index exists
        if not es_client.indices.exists(index=index_name):
            # print(f"Debug: Index '{index_name}' does not exist!")
            return []

        # Perform the search
        response = es_client.search(index=index_name, body=search_query)

        # Print the ID of the top retrieved search result
        top_hit_id = response['hits']['hits'][0]['_id']
        print(f"ID of the top retrieved search result: {top_hit_id}")

        # Collect the source of all hits
        result_docs = []
        for hit in response['hits']['hits']:
            result_docs.append(hit['_source'])

        # Iterate and return the top 5 documents in a structured way
        return [result_docs[i] for i in range(min(len(result_docs), 5))]
    
    except exceptions.BadRequestError as e:
        # print(f"BadRequestError: {e.info}")
        return []
    except Exception as e:
        # print(f"Unexpected error: {e}")
        return []

# Debug: Print global variables after function definition
# print("Debug: Global variable 'index_name':", get_global_variable('stellar_luminos', 'index_name'))

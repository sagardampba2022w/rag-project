from typing import Dict, List
from elasticsearch import Elasticsearch, exceptions
from mage_ai.data_preparation.variable_manager import get_global_variable

# Sample text query to be used in the search
SAMPLE_QUERY = "When is the next cohort?"

@data_loader
def search(*args, **kwargs) -> List[Dict]:
    """
    query_text: str
    connection_string: str
    search_field: str
    top_k: int
    """
    
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    search_field = kwargs.get('search_field', 'text')
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

    match_query = {
        "match": {
            search_field: query_text
        }
    }

    # print("Debug: Sending match query:", match_query)

    es_client = Elasticsearch(connection_string)
    
    try:
        # Debug: Check if the index exists
        if not es_client.indices.exists(index=index_name):
            # print(f"Debug: Index '{index_name}' does not exist!")
            return []

        # Debug: Get index mapping
        # index_mapping = es_client.indices.get_mapping(index=index_name)
        # print(f"Debug: Index mapping: {index_mapping}")

        # Perform the search
        response = es_client.search(
            index=index_name,
            body={
                "size": top_k,
                "query": match_query,
                "_source": True,  # Return all fields
            },
        )

        # print("Debug: Raw response from Elasticsearch:", response)

        # Check if there are any hits
        if response['hits']['total']['value'] == 0:
            # print("Debug: No hits found for the query")
            return []

        top_hit_id = response['hits']['hits'][0]['_id']
        print(f"ID of the top retrieved search result: {top_hit_id}")

        # Return all fields for each hit
        return [hit['_source'] for hit in response['hits']['hits'][:1]]
    
    except exceptions.BadRequestError as e:
        # print(f"BadRequestError: {e.info}")
        return []
    except Exception as e:
        # print(f"Unexpected error: {e}")
        return []

# Debug: Print global variables after function definition
# print("Debug: Global variable 'index_name':", get_global_variable('stellar_luminos', 'index_name'))

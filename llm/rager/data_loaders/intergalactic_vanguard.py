from typing import Dict, List, Union
from elasticsearch import Elasticsearch, exceptions
from mage_ai.data_preparation.variable_manager import get_global_variable
import pandas as pd  # Import pandas for DataFrame creation

SAMPLE_QUERY = "When is the next cohort?"

@data_loader
def search(*args, **kwargs) -> List[Dict]:
    """
    Perform a search in Elasticsearch and return matching documents.
    """
    # Check and print the key variables
    print("Checking Elasticsearch export variables:")
    
    # Check connection_string
    connection_string = kwargs.get('connection_string', get_global_variable('stellar_luminos', 'connection_string') or 'http://localhost:9200')
    print(f"  connection_string: {connection_string}")
    
    # Check course
    course = kwargs.get('course', 'llm-zoomcamp')
    print(f"  course: {course}")
    
    # Check top_k
    top_k = kwargs.get('top_k', 5)
    print(f"  top_k: {top_k}")
    
    # Check index_name (this should be set in the export pipeline)
    index_name = get_global_variable('stellar_luminos', 'index_name')
    print(f"  index_name: {index_name}")
    
    print("------------------------")

    if not index_name:
        print("Error: Global variable 'index_name' not found.")
        return []

    query_text = args[0] if args else SAMPLE_QUERY
    print(f"Searching for: '{query_text}' in course '{course}'")

    es_client = Elasticsearch(connection_string)
    
    try:
        # Check if the index exists
        if not es_client.indices.exists(index=index_name):
            print(f"Error: Index '{index_name}' does not exist!")
            return []

        # Construct the search query
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
                            "course": course
                        }
                    }
                }
            }
        }

        # Perform the search
        response = es_client.search(
            index=index_name,
            body=search_query
        )

        hits = response['hits']['hits']
        if not hits:
            print("No results found for the query.")
            return []

        results = []
        for hit in hits:
            doc = hit['_source']
            doc['score'] = hit['_score']
            results.append(doc)

        print(f"Found {len(results)} results.")
        
        # Convert results to a DataFrame and print
        df = pd.DataFrame(results)
        print("\nResults in DataFrame:")
        print(df)

        return df
    
    except exceptions.BadRequestError as e:
        print(f"BadRequestError: {e.info}")
        return []
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return []

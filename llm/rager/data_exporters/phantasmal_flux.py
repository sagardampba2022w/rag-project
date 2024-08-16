import json
from typing import Dict, List, Union
from datetime import datetime
from elasticsearch import Elasticsearch
from mage_ai.data_preparation.variable_manager import set_global_variable

# Set the global variable outside the function
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
index_name = f"documents_{current_time}"
set_global_variable('stellar_luminos', 'index_name', index_name)

@data_exporter
def elasticsearch(documents: List[Dict[str, Union[Dict, str]]], *args, **kwargs):
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    print("Index name:", index_name)

    number_of_shards = kwargs.get('number_of_shards', 1)
    number_of_replicas = kwargs.get('number_of_replicas', 0)

    es_client = Elasticsearch(connection_string)

    print(f'Connecting to Elasticsearch at {connection_string}')

    index_settings = {
        "settings": {
            "number_of_shards": number_of_shards,
            "number_of_replicas": number_of_replicas
        },
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "section": {"type": "text"},
                "question": {"type": "text"},
                "course": {"type": "keyword"},
                #"document_id": {"type": "keyword"}
            }
        }
    }

    # Recreate the index by deleting if it exists and then creating with new settings
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
        print(f'Index {index_name} deleted')

    es_client.indices.create(index=index_name, body=index_settings)
    print('Index created with properties:')
    print(json.dumps(index_settings, indent=2))

    count = len(documents)
    print(f'Indexing {count} documents to Elasticsearch index {index_name}')
    last_document = None
    failed_docs = []
    for idx, document in enumerate(documents):
        if idx % 100 == 0:
            print(f'{idx + 1}/{count}')
        
        try:
            es_client.index(index=index_name, document=document)
        except Exception as e:
            print(f"Error indexing document {idx + 1}: {e}")
            failed_docs.append(document)
        last_document = document

    # Retry failed documents
    if failed_docs:
        print(f"Retrying {len(failed_docs)} failed documents...")
        for doc in failed_docs:
            try:
                es_client.index(index=index_name, document=doc)
            except Exception as e:
                print(f"Retry failed for a document: {e}")

    # Debugging step: Check if all documents are indexed properly
    indexed_document_count = es_client.count(index=index_name)['count']
    if indexed_document_count == count:
        print(f"All {indexed_document_count} documents are indexed properly.")
    else:
        print(f"Indexed {indexed_document_count} documents, but expected {count}. Some documents might be missing.")

    # Print the last document
    if last_document:
        print("Last document indexed:")
        print(json.dumps(last_document, indent=2))

    return [[d for d in documents[:2]]]

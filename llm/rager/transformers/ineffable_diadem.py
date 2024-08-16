
import hashlib
from typing import List, Dict, Union


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def chunk_documents_pipeline(data: Dict[str, Union[str, List[Dict[str, str]]]]) -> List[Dict[str, str]]:
    """
    Transforms the input data by adding course name and generating document IDs for each document.

    Args:
        data (Dict[str, Union[str, List[Dict[str, str]]]]): The input data containing course name and documents.

    Returns:
        List[Dict[str, str]]: The transformed list of documents with added course names and document IDs.
    """
    # Internal function to generate a unique document ID
    def generate_document_id(doc: Dict[str, str]) -> str:
        """
        Generates a unique document ID by hashing a combination of course, question, and text.

        Args:
            doc (Dict[str, str]): The document dictionary containing course, question, and text fields.

        Returns:
            str: A unique document ID.
        """
        combined = f"{doc['course']}-{doc['question']}-{doc['text'][:10]}"
        hash_object = hashlib.md5(combined.encode())
        hash_hex = hash_object.hexdigest()
        document_id = hash_hex[:8]  # Use the first 8 characters of the hash as the document ID
        return document_id

    # List to store the processed documents
    documents = []

    # Process each document in the data['documents'] list
    for doc in data['documents']:
        doc['course'] = data['course']
        # Generate and assign a unique document ID
        doc['document_id'] = generate_document_id(doc)
        documents.append(doc)

    # Print the number of documents processed
    print(f"Number of documents processed: {len(documents)}")

    # Return the transformed list of documents
    return documents





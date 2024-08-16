import io
import requests
import docx
from typing import List, Dict, Union

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def read_faq_and_process_documents() -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
    """
    Reads FAQ documents from Google Docs, processes them, and returns the extracted data.

    Returns:
        List[Dict[str, Union[str, List[Dict[str, str]]]]]: A list of dictionaries containing course names and their associated FAQ documents.
    """
    # Internal function to clean lines of text
    def clean_line(line: str) -> str:
        """
        Cleans a line of text by stripping whitespace and BOM characters.
        """
        return line.strip().strip('\uFEFF')

    # Internal function to read and extract FAQs from a single Google Docs file
    def read_faq(file_id: str) -> List[Dict[str, Union[str, Dict]]]:
        """
        Reads an FAQ document from Google Docs and extracts questions and answers.

        Args:
            file_id (str): The Google Docs file ID.

        Returns:
            List[Dict[str, Union[str, Dict]]]: Extracted FAQ data.
        """
        url = f'https://docs.google.com/document/d/{file_id}/export?format=docx'
        
        response = requests.get(url)
        response.raise_for_status()
        
        with io.BytesIO(response.content) as f_in:
            doc = docx.Document(f_in)

        questions = []

        question_heading_style = 'heading 2'
        section_heading_style = 'heading 1'
        
        section_title = ''
        question_title = ''
        answer_text_so_far = ''
         
        for p in doc.paragraphs:
            style = p.style.name.lower()
            p_text = clean_line(p.text)
        
            if len(p_text) == 0:
                continue
        
            if style == section_heading_style:
                section_title = p_text
                continue
        
            if style == question_heading_style:
                answer_text_so_far = answer_text_so_far.strip()
                if answer_text_so_far != '' and section_title != '' and question_title != '':
                    questions.append({
                        'text': answer_text_so_far,
                        'section': section_title,
                        'question': question_title,
                    })
                    answer_text_so_far = ''
        
                question_title = p_text
                continue
            
            answer_text_so_far += '\n' + p_text
        
        answer_text_so_far = answer_text_so_far.strip()
        if answer_text_so_far != '' and section_title != '' and question_title != '':
            questions.append({
                'text': answer_text_so_far,
                'section': section_title,
                'question': question_title,
            })

        return questions

    # Dictionary of course documents
    faq_documents = {
        'llm-zoomcamp': '1T3MdwUvqCL3jrh3d3VCXQ8xE0UqRzI3bfgpfBq3ZWG0',
    }

    
    # List to store the documents
    documents = []
    document_count = 0  # Initialize a counter for documents

    # Process each document in the faq_documents dictionary
    for course, file_id in faq_documents.items():
        print(f"Processing course: {course}")
        course_documents = read_faq(file_id)
        documents.append({'course': course, 'documents': course_documents})
        document_count += 1  # Increment the counter for each processed document
        print(f"Processed document {document_count}: {course}")

    # Print the total number of documents processed
    print(f"Total number of documents processed: {document_count}")

    # The documents list now contains the extracted FAQs for each course
    #print(documents)
    
    return documents

# Call the function to execute the entire process
#read_faq_and_process_documents()

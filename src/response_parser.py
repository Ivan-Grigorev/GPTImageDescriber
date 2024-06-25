"""This module parses the GPT-4 response to extract the title, description, and keywords."""

import re
import string
import sys

from src.logging_config import setup_logger

# Initialize logger using the setup function
logger = setup_logger(__name__)


def parse_response(gpt_response):
    """
    Parse the GPT-4 response to extract the title, description, and keywords.

    Args:
        gpt_response (dict): The GPT-4 response is to be parsed.

    Returns:
        tuple: A tuple containing the title (str), description (str), and keywords (list) extracted from the GPT-4 response.
    """
    # Check if there is an error in the ChatGPT response
    if 'error' in gpt_response.keys():
        logger.error(f"{gpt_response.get('error')['message']}")
        # Exit the program with a status code 1
        sys.exit(1)

    try:
        content = gpt_response['choices'][0].get('message').get('content')

        # Use lower-case for consistent searches
        content_lower = content.lower()

        # Find the indexes of 'Title', 'Description', and 'Keywords' in a case-insensitive manner
        title_index = content_lower.find('title')
        description_index = content_lower.find('description')
        keywords_index = content_lower.find('keywords')

        # Define a translation table to map non-letter characters to None
        translation_table = str.maketrans('', '', string.punctuation + string.digits)

        # Get the values by slicing
        title = 'No Title'
        description = 'No Description'
        keywords = []

        if title_index != -1:
            # Slice until the next section or end of content
            start_index = title_index + len('Title')
            end_index = (
                description_index
                if description_index > title_index
                else keywords_index if keywords_index > title_index else len(content)
            )
            title = content[start_index:end_index].translate(translation_table).strip()

        if description_index != -1:
            # Slice until the next section or end of content
            start_index = description_index + len('Description')
            end_index = keywords_index if keywords_index > description_index else len(content)
            description = content[start_index:end_index].translate(translation_table).strip()

        if keywords_index != -1:
            # Slice to the end of the content and split by common delimiters
            start_index = keywords_index + len('Keywords')
            keywords_string = content[start_index:]
            keywords = [
                kw.strip()
                for kw in re.split(r'[,\s]+', keywords_string.translate(translation_table).lower())
                if kw
            ]

        return title, description, keywords

    except Exception as e:
        print(f"Error processing response ID {gpt_response.get('id')}: {e}")

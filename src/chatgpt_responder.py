"""This module describes images using OpenAI's GPT model."""

import base64
import sys

import requests

from src.logging_config import setup_logger

# Initialize logger using the setup function
logger = setup_logger(__name__)

# Set your OpenAI API key
try:
    with open('./openai_key.txt', 'r') as f:
        API_KEY = f.read().strip()
except FileNotFoundError as e:
    logger.error(f"Could not find {e.filename}. Please ensure the file exists and is accessible.")
    sys.exit(1)


def process_photo(image_file, prompt):
    """
    Process a given photo to generate a title, description, and keywords with ChatGPT-4.

    Args:
        image_file (file object): The image file to be processed.
        prompt (str): The prompt to be sent to the GPT model for generating descriptions.

    Returns:
         dict: A JSON object containing the generated title, description, and keywords.
    """
    # Convert the image to a based64 string
    image_base64 = base64.b64encode(image_file.read()).decode('ascii')

    # Use GPT-4 by creating a prompt to generate a title, description, and keywords
    payload = {
        'model': 'gpt-4o',
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {
                        'type': 'image_url',
                        'image_url': {'url': f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
        'max_tokens': 300,
    }

    response = requests.post(
        url="https://api.openai.com/v1/chat/completions",
        headers={
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {API_KEY}",
        },
        json=payload,
    ).json()

    return response

import base64
import logging
import os
import requests
import sys
import time

# Set Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
)
logger = logging.getLogger(__name__)

# Set your OpenAI API key
try:
    with open('openai_key.txt', 'r') as f:
        API_KEY = f.read().strip()
except FileNotFoundError as e:
    logger.error(
        f"Could not find {e.filename}. Please ensure the file exists and is accessible."
    )
    sys.exit(1)


def image_to_base64(photo_path):
    """
    Converts an image to a base64 string.

    Args:
        photo_path (str): Path to the image file.

    Returns:
        str: Base64 encoded string of the image.
    """

    with open(photo_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def process_photo(src_path):
    """
    Processes a given photo to generate a title, keywords, and suitable holidays
    with ChatGPT-4.

    Args:
        src_path (str): The path to the photo to be processed.

    Returns:
         dict: A dictionary containing the generated title, keywords, and holidays.
    """

    # Record the function process start time
    time_start = time.perf_counter()

    # Convert the image to a based64 string
    image_base64 = image_to_base64(src_path)
    logger.info("Images processing has started!")

    # Use GPT-4 by creating a prompt to generate a title, keywords, and holidays
    prompt = "Create a title and 30 keywords for this image. \
              The keywords should be SEO optimized and reflect current trends and interests. \
              The keywords are single words not a combination of words."

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
    )

    # Display the function process time
    logger.info(
        f"Images processing time is {time.perf_counter() - time_start:.2f} seconds."
    )

    return response.json()


print(process_photo('/Users/a1/PythonProjects/GPTImageDescriber/Images/IMG_7809.jpeg'))

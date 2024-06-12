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


class GPTImagesDescriber:
    """
    A class to facilitate image description generation using OpenAI's GPT model.
    """

    def __init__(self, prompt, src_path, dst_path=None):
        self.prompt = str(prompt)
        self.src_path = str(src_path)
        self.dst_path = str(dst_path)

    def image_to_base64(self) -> str:
        """
        Converts an image to a base64 string.

        Returns:
            str: Base64 encoded string of the image.
        """

        with open(self.src_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def process_photo(self) -> str:
        """
        Processes a given photo to generate a title, keywords, and suitable holidays
        with ChatGPT-4.

        Returns:
             dict: A dictionary containing the generated title, keywords, and holidays.
        """

        # Record the function process start time
        time_start = time.perf_counter()

        # Convert the image to a based64 string
        image_base64 = self.image_to_base64()
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
                        {'type': 'text', 'text': self.prompt},
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f"data:image/jpeg;base64,{image_base64}"
                            },
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

    def __str__(self):
        return (
            f"GPTImagesDescriber(\n"
            f"\tprompt={self.prompt},\n"
            f"\tsrc_path={self.src_path},\n"
            f"\tdst_path={self.dst_path}\n"
            f")"
        )


if __name__ == '__main__':
    try:
        configuration = {}
        with open('configurations.txt', 'r') as f:
            for line in f:
                line = line.strip()  # remove leading and trailing whitespace
                if line and not line.startswith('#'):  # ignore empty lines and comments
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    configuration[key] = value
        image_describer = GPTImagesDescriber(
            prompt=configuration.get('prompt'),
            src_path=configuration.get('source_folder'),
            dst_path=configuration.get(
                'destination_folder', configuration.get('source_folder')
            ),
        )
        print(image_describer.process_photo())
    except FileNotFoundError as e:
        logger.error(
            f"Could not find {e.filename}. Please ensure the file exists and is accessible."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading the configuration file: {e}")
        sys.exit(1)

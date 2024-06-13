import base64
import logging
import os
import re
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

    def image_to_base64(self):
        """
        Converts an image to a base64 string.

        Returns:
            str: Base64 encoded string of the image.
        """

        with open(self.src_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def process_photo(self):
        """
        Processes a given photo to generate a title, keywords, and suitable holidays
        with ChatGPT-4.

        Returns:
             dict: A dictionary containing the generated title, keywords, and holidays.
        """

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

        return response.json()

    def parse_response(self, image_file):
        """
        Parses the response from GPT-4 to extract the title and keywords.

        Returns:
            tuple: A tuple containing the parsed title and keywords.
        """

        content = self.process_photo().get('choices')[0].get('message').get('content')

        # Use regular expressions to extract the title and keywords
        title_match = re.search(r'\*\*Title:\*\*\n(.+)', content)
        keywords_match = re.search(r'\*\*Keywords:\*\*\n(.+)', content)

        # Extract and process the title
        if title_match:
            title = title_match.group(1).strip()
            title = title.replace(' ', '_').lower()
        else:
            # Leave the file name unchanged
            title = image_file
            logger.warning(
                f"Due to the lack of title data, "
                f"the title of the {image_file} file has not been changed."
            )

        # Extract and process the keywords
        keywords = keywords_match.group(1).strip() if keywords_match else 'No Keywords'
        keywords = ', '.join([kw.strip() for kw in keywords.split(',')])

        return title, keywords

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
        # Extract settings from the configurations file
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
    except FileNotFoundError as e:
        logger.error(
            f"Could not find {e.filename}. Please ensure the file exists and is accessible."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading the configuration file: {e}")
        sys.exit(1)

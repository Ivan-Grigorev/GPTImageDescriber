import base64
import os
import re
import shutil
import sys
import time
from pathlib import Path

import requests
from iptcinfo3 import IPTCInfo
from logging_config import setup_logger
from PIL import Image, JpegImagePlugin

# Initialize logger using the setup function
logger = setup_logger(__name__)

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
    A class to facilitate image description generation using OpenAI's GPT model and add metadata to images.

    Attributes:
        prompt (str): The prompt to be sent to the GPT model for generating descriptions.
        src_path (str): The source directory containing the images to be processed.
        image_files (list): List of image file names to be processed.
        dst_path (str): The destination directory for saving the processed images.
        author_name (str): The author name of images.

    Methods:
        __init__(prompt, src_path, image_files, dst_path):
            Initializes the GPTImagesDescriber with the specified parameters.

        process_photo(image_file):
            Processes a given image file to generate a title and keywords using ChatGPT-4.
            Returns a dictionary containing the generated title and keywords.

        parse_response(image_file):
            Parses the GPT-4 response to extract the title and keywords for a given image.
            Returns a tuple containing the parsed title and keywords.

        add_metadata():
            Adds processed titles and keywords to the metadata of the images in the source directory.
            Saves the processed images in the destination directory.

        __str__():
            Returns a string representation of the GPTImagesDescriber instance.
    """

    def __init__(self, prompt, src_path, image_files, dst_path, author_name):
        """
        Initializes the GPTImagesDescriber with a prompt, source path, list of image files, and destination path.

        Args:
            prompt (str): The prompt to be sent to the GPT model for generating descriptions.
            src_path (str): The path to the directory containing the images to be processed.
            image_files (list): A list of image file names to be processed.
            dst_path (str): The path to the directory where processed images will be saved. Defaults to src_path if not provided.
        """

        self.prompt = prompt
        self.src_path = src_path
        self.image_files = image_files
        self.dst_path = dst_path if dst_path else src_path
        self.author_name = author_name

    def process_photo(self, image_file):
        """
        Processes a given photo to generate a title, keywords, and suitable holidays
        with ChatGPT-4.

        Returns:
             dict: A dictionary containing the generated title, keywords, and holidays.
        """

        # Convert the image to a based64 string
        image_base64 = base64.b64encode(image_file.read()).decode('ascii')

        # Use GPT-4 by creating a prompt to generate a title, keywords
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
        Parses the GPT-4 response to extract the title and keywords for a given image file.

        Args:
            image_file (file object): The image file whose GPT-4 response is to be parsed.

        Returns:
            tuple: A tuple containing the title (str) and keywords (str) extracted from the GPT-4 response.
        """

        response_data = self.process_photo(image_file)

        # Check if there is an error in the ChatGPT response
        if 'error' in response_data.keys():
            logger.error(f"{response_data.get('error')['message']}")
            sys.exit(1)

        content = response_data['choices'][0].get('message').get('content')

        # Extract title
        title_match = re.search(
            r'\*\*Title:\*\*["\n\s]*(.*?)(?=["\n])', content, re.IGNORECASE
        )
        title = (
            title_match.group(1).strip().replace(":", "") if title_match else "No Title"
        )

        # Extract description
        description_match = re.search(
            r'\*\*Description:\*\*["\n\s]*(.*?)(?=["\n])', content, re.IGNORECASE
        )
        description = (
            description_match.group(1).strip().replace(":", "")
            if description_match
            else "No Description"
        )

        # Extract keywords
        keywords_match = re.search(
            r'\*\*Keywords:\*\*[\s\n]*([^\*]*)', content, re.IGNORECASE
        )
        if keywords_match:
            keywords_text = keywords_match.group(1).strip()
            # Clean the keywords by removing numbers and any other unwanted characters
            keywords_list = (
                re.sub(r'\d+\.?', '', keywords_text).replace(",", " ").lower().split()
            )
        else:
            keywords_list = "No Keywords"

        return title, description, keywords_list

    def add_metadata(self):
        """
        Adds processed titles and keywords to the metadata of images in the source directory.
        Saves the processed images in the destination directory.

        Returns:
            None
        """

        # Record the start time of the process of handling the images
        time_start = time.perf_counter()

        # Initialize counters for images
        processed_count = 0
        unprocessed_count = 0

        # Get number of files to process
        files_num = len([
            f
            for f in os.listdir(self.src_path)
            if os.path.isfile(os.path.join(self.src_path, f)) and not f.startswith('.')
        ])
        logger.info(f"Images processing has started! {files_num} to process.")

        # Get title and keywords for each image file
        for image_name in self.image_files:
            image_path = os.path.join(self.src_path, image_name)
            destination_path = os.path.join(self.dst_path, image_name)

            # Check if the file is an image based on its extension
            if image_name.lower().endswith(
                (
                    '.jpg',
                    '.jpeg',
                    '.png',
                    '.gif',
                    '.bmp',
                    '.webp',
                    '.tiff',
                    '.ico',
                    '.svg',
                )
            ) and os.path.isfile(image_path):
                try:
                    with open(image_path, 'rb') as image_file:
                        title, description, keywords = self.parse_response(
                            image_file=image_file
                        )

                        # Open image and modify metadata
                        with Image.open(image_path) as img:
                            # JPEG Metadata
                            if isinstance(img, JpegImagePlugin.JpegImageFile):
                                # Load IPTC metadata or create a new one
                                try:
                                    info = IPTCInfo(image_path)
                                except Exception as e:
                                    logger.error(
                                        f"No IPTC metadata found, create a new one. Error: {e}")
                                    info = IPTCInfo(None)
                                info['object name'] = title
                                info['caption/abstract'] = description
                                info['keywords'] = keywords
                                info['by-line'] = self.author_name
                                # Save the image with new IPTC metadata
                                info.save_as(destination_path)
                                logger.info(f"Metadata added to {image_name} (JPEG)")
                                processed_count += 1

                            # Other image formats - move file without modification
                            else:
                                img.save(destination_path)
                                logger.info(
                                    f"Because the image format is not processed,"
                                    f" {image_name} has been moved to {destination_path}."
                                )

                except Exception as e:
                    logger.error(f"Error adding metadata to {image_name}: {e}")
                    unprocessed_count += 1
            else:
                # Move non-image files to the 'Not_Images' folder
                not_img_fld = os.path.join(self.dst_path, 'Not_Images')
                Path(not_img_fld).mkdir(parents=True, exist_ok=True)
                if not os.path.samefile(image_path, not_img_fld):
                    shutil.move(image_path, os.path.join(not_img_fld, image_name))
                else:
                    logger.error(
                        f"Error: Cannot move '{image_path}' into itself {not_img_fld}."
                    )

        # Display the images processing time
        logger.info(
            f"Processing complete: "
            f"{processed_count} images processed, {unprocessed_count} unprocessed. "
            f"Images processing time is {time.perf_counter() - time_start:.2f} seconds."
        )

    def __str__(self):
        """
        Returns a string representation of the GPTImagesDescriber instance.

        Returns:
            str: A string representation of the class instance, showing key attributes.
        """

        return (
            f"GPTImagesDescriber(\n"
            f"\tprompt={self.prompt},\n"
            f"\tsrc_path={self.src_path},\n"
            f"\timage_files={self.image_files},\n"
            f"\tdst_path={self.dst_path},\n"
            f"\tauthor_name={self.author_name}\n"
            f")"
        )


def main():
    try:
        # Extract settings from the configurations file
        with open('configurations.txt', 'r') as f:
            configurations = {
                key.strip(): value.strip()
                for key, value in (
                    line.split('=', 1)
                    for line in f
                    if line.strip() and not line.startswith('#')
                )
            }

        image_describer = GPTImagesDescriber(
            prompt=configurations.get('prompt'),
            src_path=configurations.get('source_folder'),
            image_files=[
                f
                for f in os.listdir(configurations.get('source_folder'))
                if not f.startswith('.')
            ],
            dst_path=configurations.get('destination_folder'),
            author_name=configurations.get('author_name'),
        )
        image_describer.add_metadata()
    except FileNotFoundError as e:
        logger.error(
            f"Could not find {
                e.filename}. Please ensure the file exists and is accessible.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading the configuration file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

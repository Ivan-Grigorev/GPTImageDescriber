"""Describes images using OpenAI's GPT model and adds metadata."""

import base64
import os
import shutil
import string
import sys
import tempfile
import time

import requests
from iptcinfo3 import IPTCInfo
from PIL import Image

from src.check_access import terminate_processes_using_file
from src.files_filter import filter_files_by_extension
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


class ImagesDescriber:
    """
    A class to facilitate image description generation using OpenAI's GPT model and add metadata to images.

    Attributes:
        prompt (str): The prompt to be sent to the GPT model for generating descriptions.
        src_path (str): The source directory containing the images to be processed.
        image_files (list): List of image file names to be processed.
        dst_path (str): The destination directory for saving the processed images.
        author_name (str): The author name of images.

    Methods:
        __init__.py(prompt, src_path, image_files, dst_path):
            Initializes the ImagesDescriber with the specified parameters.

        process_photo(image_file):
            Processes a given image file to generate a title, description, and keywords using ChatGPT-4.
            Returns a dictionary containing the generated title and keywords.

        parse_response(image_file):
            Parses the GPT-4 response to extract the title, description, and keywords for a given image.
            Returns a tuple containing the parsed title, description, and keywords.

        add_metadata():
            Adds processed titles, descriptions, and keywords to the metadata of the images in the source directory.
            Saves the processed images in the destination directory.

        __str__():
            Returns a string representation of the ImagesDescriber instance.
    """

    def __init__(self, prompt, src_path, image_files, dst_path, author_name):
        """
        Initialize the ImagesDescriber with a prompt, source path, list of image files, and destination path.

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
        Process a given photo to generate a title, description, and keywords with ChatGPT-4.

        Args:
            image_file (file object): The image file to be processed.

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
                        {'type': 'text', 'text': self.prompt},
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

        # Get cleaned data from GPT response
        title, description, keywords = self.parse_response(response)

        return title, description, keywords

    def parse_response(self, gpt_response):
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
            sys.exit(1)

        # Extract the content from the response
        content = gpt_response['choices'][0].get('message').get('content')

        # Find the indexes of 'Title', 'Description', and 'Keywords'
        title_index = content.find('Title')
        description_index = content.find('Description')
        keywords_index = content.find('Keywords')

        # Define a translation table to map non-letter characters to None
        translation_table = str.maketrans('', '', string.punctuation + string.digits)

        # Get the values by slicing
        title_start = title_index + len('Title:')
        title = (
            content[title_start:description_index].translate(translation_table).strip()
            if title_index != -1
            else 'No Title'
        )

        description_start = description_index + len('Description')
        description = (
            content[description_start:keywords_index].translate(translation_table).strip()
            if description_index != -1
            else 'No Description'
        )

        keywords_start = keywords_index + len('Keywords:')
        keywords = (
            content[keywords_start:].translate(translation_table).lower().split()
            if keywords_index != -1
            else []
        )

        return title, description, keywords

    def add_metadata(self):
        """
        Add processed titles and keywords to the metadata of images in the source directory.

        Saves the processed images in the destination directory.
        """
        # Record the start time of the process of handling the images
        time_start = time.perf_counter()

        # Initialize counter for images
        processed_count = 0

        # Get filtered image files to process
        filtered_image_files = filter_files_by_extension(src_path=self.image_files)
        logger.info(
            f"Images processing has started! {len(filtered_image_files)} images to process."
        )

        # Get title and keywords for each image file
        for image_name in filtered_image_files:
            image_path = os.path.join(self.src_path, image_name)
            destination_path = os.path.join(self.dst_path, image_name)

            # Ensure destination directory exists; create if it doesn't
            if not os.path.exists(destination_path):
                os.makedirs(self.dst_path, exist_ok=True)

            # Terminate processes using the image file
            terminate_processes_using_file(image_path)

            try:
                with open(image_path, 'rb') as image_file:
                    # Get data from GPT response
                    title, description, keywords = self.process_photo(image_file=image_file)

                    # Open image and modify metadata
                    with Image.open(image_path) as img:
                        img.verify()  # verify image integrity

                    # Create a temporary copy of the image
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_image_path = temp_file.name
                    shutil.copyfile(image_path, temp_image_path)

                    # Load IPTC metadata or create a new one
                    try:
                        info = IPTCInfo(temp_image_path)
                    except Exception as e:
                        logger.error(f"No IPTC metadata found, create a new one. Error: {e}")
                        info = IPTCInfo(None)

                    # Modify metadata on the temporary file
                    info['object name'] = title
                    info['caption/abstract'] = description
                    info['keywords'] = keywords
                    info['by-line'] = self.author_name

                    # Save the modified metadata back to the temp file
                    info.save_as(temp_image_path)
                    shutil.move(temp_image_path, destination_path)
                    logger.info(
                        f"Metadata added to {image_name} (JPEG) "
                        f"{'and moved to ' + os.path.dirname(destination_path) if destination_path != image_path else ''}"
                    )
                    processed_count += 1

            except Exception as e:
                logger.error(f"Error adding metadata to {image_name}: {e}")
            finally:
                # Remove the original file only if the edited copy
                # has been moved to another folder
                if image_path != destination_path:
                    os.remove(image_path)

                # Ensure backup files are removed regardless of success or failure
                self.remove_backup_file(destination_path)

                # Clean up temp file if it exists and is not needed
                if temp_image_path and os.path.exists(temp_image_path):
                    os.remove(temp_image_path)

        # Calculate the number of unprocessed images
        unprocessed_count = len(filtered_image_files) - processed_count

        # Display the images processing time
        process_time = time.perf_counter() - time_start
        if process_time < 60:
            # Display process time in seconds
            logger.info(
                f"Processing complete: "
                f"{processed_count} images processed, {unprocessed_count} unprocessed. "
                f"Images processing time is {process_time:.2f} seconds."
            )
        elif 60 < process_time < 3600:
            # Display process time in minutes and seconds
            process_minutes = process_time // 60
            process_seconds = process_time % 60
            logger.info(
                f"Processing complete: "
                f"{processed_count} images processed, {unprocessed_count} unprocessed. "
                f"Images processing time is {process_minutes:.0f} minutes {process_seconds:.0f} seconds."
            )
        else:
            # Display process time in hours, minutes, and seconds
            process_hours = process_time // 3600
            process_minutes = (process_time % 3600) // 60
            process_seconds = (process_time % 3600) % 60
            logger.info(
                f"Processing complete: "
                f"{processed_count} images processed, {unprocessed_count} unprocessed. "
                f"Images processing time is {process_hours:.0f} "
                f"{'hour' if process_hours == 1 else 'hours'} "
                f"{process_minutes:.0f} minutes {process_seconds:.0f} seconds."
            )

    @staticmethod
    def remove_backup_file(filename):
        """
        Remove the backup file created by the IPTCInfo library.

        Args:
            filename: path to the backup file has a '~' suffix.
        """
        if filename is None or filename.strip() == '':
            logger.error("No valid filename provided to remove backup file.")
            return

        backup_file_path = filename + '~'
        if os.path.exists(backup_file_path):
            try:
                os.remove(backup_file_path)
                logger.warning(f"Removed backup file: {backup_file_path}")
            except Exception as e:
                logger.error(f"Error removing backup file '{backup_file_path}': {e}")

    def __str__(self):
        """
        Return a string representation of the ImagesDescriber instance.

        Returns:
            str: A string representation of the class instance, showing key attributes.
        """
        return (
            f"ImagesDescriber(\n"
            f"\tprompt={self.prompt},\n"
            f"\tsrc_path={self.src_path},\n"
            f"\timage_files={self.image_files},\n"
            f"\tdst_path={self.dst_path},\n"
            f"\tauthor_name={self.author_name}\n"
            f")"
        )

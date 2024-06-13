from PIL import Image, PngImagePlugin, JpegImagePlugin
import base64
import logging
import os
import re
import requests
import sys
import shutil
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
    A class to facilitate image description generation using OpenAI's GPT model and add metadata to images.

    Attributes:
        prompt (str): The prompt to be sent to the GPT model for generating descriptions.
        src_path (str): The source directory containing the images to be processed.
        image_files (list): List of image file names to be processed.
        dst_path (str): The destination directory for saving the processed images.

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

    def __init__(self, prompt, src_path, image_files, dst_path):
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
        content = response_data.get('choices')[0].get('message').get('content')

        # Use regular expressions to extract the title and keywords
        title_match = re.search(r'\*\*Title:\*\*\n(.+)', content)
        keywords_match = re.search(r'\*\*Keywords:\*\*\n(.+)', content)

        # Extract and process the title
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Leave the file name unchanged
            title = os.path.basename(image_file)
            logger.warning(
                f"Due to the lack of title data, "
                f"the title of the '{title}' file has not been changed."
            )

        # Extract and process the keywords
        keywords = keywords_match.group(1).strip() if keywords_match else 'No Keywords'
        keywords = ', '.join([kw.strip() for kw in keywords.split(',')])

        return title, keywords

    def add_metadata(self):
        """
        Adds processed titles and keywords to the metadata of images in the source directory.
        Saves the processed images in the destination directory.

        Returns:
            None
        """

        # Record the start time of the process of handling the images
        time_start = time.perf_counter()

        # Get number of files to process
        files_num = sum(
            1
            for entry in os.scandir(self.src_path)
            if entry.is_file() and not entry.name.startswith('.')
        )
        logger.info(f"Images processing has started! {files_num} to process.")
        # Get title and keywords for each image file
        try:
            for image in self.image_files:
                image_path = os.path.join(self.src_path, image)
                destination_path = os.path.join(self.dst_path, image)
                # Check if the file is an image based on its extension
                if image.lower().endswith(
                    ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
                ):
                    try:
                        with open(image_path, 'rb') as image_file:
                            title, keywords = self.parse_response(image_file=image_file)
                            # Open image and modify metadata
                            with Image.open(image_path) as img:
                                metadata = img.info
                                if isinstance(img, PngImagePlugin.PngImageFile):
                                    metadata.update(
                                        {'Title': title, 'Keywords': keywords}
                                    )
                                    img.save(destination_path, pnginfo=metadata)
                                elif isinstance(img, JpegImagePlugin.JpegImageFile):
                                    exif_data = img.getexif()
                                    exif_data[270] = (
                                        title  # tag for 'Image Description'
                                    )
                                    exif_data[40094] = keywords  # tag for 'XP Keywords'
                                    img.save(destination_path, exif=exif_data)
                                else:
                                    img.save(destination_path)
                                logger.info(f"Metadata added to {image}.")
                    except Exception as e:
                        logger.error(f"Error adding metadata to {image}: {e}")
                else:
                    # Move non-image files to the 'Not_Images' folder
                    not_img_fld = os.path.join(self.src_path, 'Not_Images')
                    if os.path.exists(not_img_fld):
                        shutil.move(image_path, not_img_fld)
                    os.mkdir(not_img_fld)
                    not_img_fld_path = os.path.join(not_img_fld, image)
                    shutil.move(image_path, not_img_fld_path)
        except Exception as e:
            logger.error(f"Error {e} reading image files from {self.src_path}")

        # Display the images processing time
        logger.info(
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
            f"\tdst_path={self.dst_path}\n"
            f")"
        )


if __name__ == '__main__':
    try:
        # Extract settings from the configurations file
        configurations = {}
        with open('configurations.txt', 'r') as f:
            for line in f:
                line = line.strip()  # remove leading and trailing whitespace
                if line and not line.startswith('#'):  # ignore empty lines and comments
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    configurations[key] = value

            image_describer = GPTImagesDescriber(
                prompt=configurations.get('prompt'),
                src_path=configurations.get('source_folder'),
                image_files=[
                    f
                    for f in os.listdir(configurations.get('source_folder'))
                    if not f.startswith('.')
                ],
                dst_path=configurations.get('destination_folder'),
            )
        print(image_describer.__str__())
        image_describer.add_metadata()
    except FileNotFoundError as e:
        logger.error(
            f"Could not find {e.filename}. Please ensure the file exists and is accessible."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading the configuration file: {e}")
        sys.exit(1)

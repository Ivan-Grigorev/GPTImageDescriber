"""Main script to run the image description project."""

import os
import sys

from src.image_describer import ImagesDescriber
from src.logging_config import setup_logger

# Initialize logger using the setup function
logger = setup_logger(__name__)


def main():
    """
    Read configurations from 'configurations.txt' to describe images located in a specified source folder.

    The extracted configurations are passed to the ImagesDescriber class,
    which processes the images by adding metadata and saving them to a destination folder.

    Dependencies:
        - ImagesDescriber: Class responsible for describing images.

    Configuration File ('configurations.txt'):
        - Expected format: key=value
        - Example:
            prompt=Describe this image.
            source_folder=/path/to/source
            destination_folder=/path/to/destination
            author_name=Firstname Lastname
    """
    try:
        # Extract settings from the configurations file
        with open('configurations.txt', 'r') as f:
            configurations = {
                key.strip(): value.strip()
                for key, value in (
                    line.split('=', 1) for line in f if line.strip() and not line.startswith('#')
                )
            }

        # Initialize ImagesDescriber with extracted configurations
        image_describer = ImagesDescriber(
            prompt=configurations.get('prompt'),
            src_path=configurations.get('source_folder'),
            image_files=[
                f for f in os.listdir(configurations.get('source_folder')) if not f.startswith('.')
            ],
            dst_path=configurations.get('destination_folder'),
            author_name=configurations.get('author_name'),
        )

        # Add metadata to the described images
        image_describer.add_metadata()
    except FileNotFoundError as e:
        logger.error(
            f"Could not find {e.filename}. Please ensure the file exists and is accessible."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading the configuration file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

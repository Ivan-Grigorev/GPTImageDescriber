import os
import sys

from src.image_describer import ImagesDescriber
from src.logging_config import setup_logger


# Initialize logger using the setup function
logger = setup_logger(__name__)


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

        image_describer = ImagesDescriber(
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
        logger.error(f"Could not find {e.filename}. Please ensure the file exists and is accessible.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading the configuration file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

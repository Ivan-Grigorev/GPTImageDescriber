"""Main script to run the image description project."""

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

    Configuration File ('configurations.txt'):
        - Expected format: key=value
        - Example:
            prompt=Describe this image.
            source_folder=/path/to/source
            destination_folder=/path/to/destination
            author_name=Firstname Lastname

    User Confirmation:
        - Before processing begins, the user is prompted to confirm the folder paths.
        - The script provides detailed messages about the source and destination folders.
        - If the source and destination folders are the same, a warning is issued about potential overwriting.
        - The user must confirm (Y) or cancel (N) the process to proceed.

    Dependencies:
        - ImagesDescriber: Class responsible for describing images.
        - setup_logger: A function to configure and obtain a logger instance.
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
            image_files=configurations.get('source_folder'),
            dst_path=configurations.get('destination_folder'),
            author_name=configurations.get('author_name'),
        )

        src_folder = configurations.get('source_folder')
        dst_folder = configurations.get('destination_folder')

        # Request process confirmation from user
        simple_logger = setup_logger('simple_logger', use_simple_formatter=True)
        logger.info(
            "\n\n--- Images Describer with ChatGPT ---\n\n"
            "You are about to begin the process of adding metadata to your images.\n"
            "Please confirm the folder paths specified in 'configurations.txt' file:"
        )

        # Folder paths message based on the folder conditions
        if dst_folder and src_folder != dst_folder:
            simple_logger.info(
                f"Source Folder (from which the application will retrieve images): '{src_folder}'"
            )
            simple_logger.info(
                f"Destination Folder (where images with added metadata will be saved): '{dst_folder}'"
            )

        elif src_folder == dst_folder:
            simple_logger.warning(
                f"The Source Folder (from which the application will retrieve images): '{src_folder}' and the\n"
                f"Destination Folder (where images with added metadata will be saved): '{dst_folder}' are the same.\n"
                f"This means that the images with added metadata will be saved in the Source Folder,"
                f" potentially overwriting the original files."
            )

        else:
            simple_logger.info(
                f"Source Folder (from which the application will retrieve images): '{src_folder}'\n"
                f"Destination Folder (where images with added metadata will be saved):"
            )
            simple_logger.warning(
                "No destination folder specified, "
                "images with added metadata will be saved back to the source folder, "
                "overwriting existing metadata."
            )

        # User confirmation loop
        while True:
            user_confirmation = (
                input('Do you confirm the starting of the process? (Y/N)\n>>> ').strip().lower()
            )

            if user_confirmation == 'y':
                # Proceed with adding metadata
                image_describer.add_metadata()
                break
            elif user_confirmation == 'n':
                logger.info(
                    "You have chosen to cancel the process.\n"
                    f"The operation has been halted.\nAll images in the folder '{src_folder}' remain unchanged."
                )
                sys.exit(1)
            else:
                logger.warning(
                    f"Unrecognized input: '{user_confirmation}'. Please enter 'Y' for Yes or 'N' for No."
                )

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

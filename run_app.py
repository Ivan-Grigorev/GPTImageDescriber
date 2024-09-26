"""Main script to execute the image description and metadata generation project."""

import sys

from src.csv_generator import CSVGenerator
from src.image_describer import ImagesDescriber
from src.logging_config import setup_logger

# Initialize logger using the setup function
logger = setup_logger(__name__)


def main():
    """
    Read configuration settings from 'configurations.txt' and provides two options for processing images.

    1. Add metadata directly to image files and save them to a destination folder.
    2. Generate a CSV file containing image names, titles, descriptions, and keywords without modifying the images.

    Configuration File ('configurations.txt'):
        - Format: key=value
        - Example:
            prompt=Describe this image.
            source_folder=/path/to/source
            destination_folder=/path/to/destination
            author_name=Firstname Lastname

    Process Overview:
        - The script reads the configuration file for the image source folder, destination folder, and a prompt for generating descriptions.
        - The user is asked to confirm the source and destination folders.
        - The user selects between adding metadata to images (Option 1) or generating a CSV (Option 2).
        - Detailed logs are provided throughout the process.

    Dependencies:
        - CSVGenerator: Handles CSV file generation from image descriptions.
        - ImagesDescriber: Processes and embeds metadata in images using GPT.
        - setup_logger: Configures and initializes the logging system.
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

        # User confirmation and option choosing loop
        simple_logger.info(
            'The application provides you the option to handle your images with two choices:\n'
            'Option 1: Fully describe all images in the source folder with ChatGPT,\n'
            'add metadata to the images, and save them into the destination folder.\n'
            'Option 2: Only describe all images in the source folder with ChatGPT,\n'
            'create a CSV file with titles, descriptions, and keywords, then\n'
            'save the CSV file to the destination folder.'
        )
        while True:
            user_confirmation = (
                input(
                    'Confirm the start of the process by choosing option 1 or 2\n'
                    'or cancel the process by entering (N)\n>>> '
                )
                .strip()
                .lower()
            )

            if user_confirmation == '1':
                # Proceed with adding metadata
                # Initialize ImagesDescriber with extracted configurations
                image_describer = ImagesDescriber(
                    prompt=configurations.get('prompt'),
                    src_path=src_folder,
                    dst_path=dst_folder,
                    author_name=configurations.get('author_name'),
                )
                image_describer.add_metadata()
                break
            elif user_confirmation == '2':
                # Proceed with only CSV file creation
                csv_generator = CSVGenerator(
                    prompt=configurations.get('prompt'),
                    src_path=src_folder,
                    dst_path=dst_folder,
                )
                csv_generator.write_data_to_csv()
                break
            elif user_confirmation == 'n':
                logger.info(
                    "You have chosen to cancel the process.\n"
                    f"The operation has been halted.\nAll images in the folder '{src_folder}' remain unchanged."
                )
                sys.exit(1)
            else:
                logger.warning(
                    f"Unrecognized input: '{user_confirmation}'. "
                    f"Please enter '1' for Option 1, '2' for Option 2, or 'N' to cancel."
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

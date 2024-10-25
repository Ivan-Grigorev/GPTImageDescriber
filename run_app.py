"""Main script to execute the image description and metadata generation project."""

import sys

from src.caption_csv_generator import CaptionCSVGenerator
from src.csv_generator import CSVGenerator
from src.image_describer import ImagesDescriber
from src.services.logging_config import setup_logger

# Initialize logger using the setup function
logger = setup_logger(__name__)


def main():
    """
    Main script to execute the GPT-based image description and metadata generation project.

    Configuration File ('configurations.txt'):
        - Format: key=value
        - Example:
            prompt=Create title, description, and 20 keywords for this image.
            source_folder=/path/to/source
            destination_folder=/path/to/destination
            author_name=Firstname Lastname

    Process Overview:
        - Reads configuration file to retrieve source folder, destination folder, and GPT prompt for generating descriptions.
        - Confirms source and destination folders with the user.
        - Prompts the user to select one of three processing options:
            - Option 1: Adds GPT-generated metadata (titles, descriptions, and keywords) to images and saves them to the destination folder.
            - Option 2: Generates a CSV file with GPT-generated titles, descriptions, and keywords without altering the images.
            - Option 3: Generates a CSV file using both GPT-generated titles, descriptions, keywords, and captions from existing image metadata.
        - Provides detailed logging throughout the process.

    Dependencies:
        - CaptionCSVGenerator: Generates CSV files from image descriptions, including existing metadata captions.
        - CSVGenerator: Creates CSV files from GPT-generated descriptions without metadata dependencies.
        - ImagesDescriber: Embeds GPT-generated metadata directly into images.
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
            "\n========== Images Describer with ChatGPT ==========\n"
            "Welcome to the application that describes images using GPT.\n"
            "Please confirm the folder paths specified in 'configurations.txt' file:"
        )

        # Folder paths message based on the folder conditions
        if dst_folder and src_folder != dst_folder:
            simple_logger.warning(
                f"Source Folder (from which the application will retrieve images): '{src_folder}'\n"
                f"Destination Folder (where images with added metadata, or CSV files will be saved): '{dst_folder}'"
            )

        elif src_folder == dst_folder:
            simple_logger.warning(
                f"The Source Folder (from which the application will retrieve images): '{src_folder}' and the "
                f"Destination Folder (where images with added metadata or CSV files will be saved):"
                f" '{dst_folder}' are the same. "
                f"This means that the images with added metadata (potentially overwriting"
                f" the original files) or CSV files will be saved back into the Source Folder."
            )

        else:
            simple_logger.warning(
                f"Source Folder (from which the application will retrieve images): '{src_folder}'\n"
                f"No destination folder specified. "
                "Images with added metadata (potentially overwriting the original files) or CSV files"
                " will be saved back into the Source folder."
            )

        # User confirmation and option choosing loop
        simple_logger.info(
            "The application provides three options for processing your images:\n"
            "** Option 1 **: Describe all images in the source folder using ChatGPT, "
            "add metadata (title, description, and keywords) directly to the image files, "
            "and save them in the destination folder.\n"
            "** Option 2 **: Describe all images in the source folder using ChatGPT, "
            "generate a CSV file with the image filename, titles, descriptions, and keywords, "
            "and save the CSV file to the destination folder.\n"
            "** Option 3 **: Describe all images in the source folder using ChatGPT, utilizing "
            "captions extracted from image metadata, generate a CSV file with the image filename,"
            " titles, descriptions, and keywords, and save the CSV file to the destination folder."
        )
        while True:
            user_confirmation = (
                input(
                    'Confirm the start of the process by choosing option 1, 2, or 3, '
                    'or cancel the process by entering (N):\n>>> '
                )
                .strip()
                .lower()
            )

            if user_confirmation == '1':
                # Proceed with adding metadata
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

            elif user_confirmation == '3':
                # Proceed with CSV file creation with images metadata
                caption_csv_generator = CaptionCSVGenerator(
                    prompt=configurations.get('prompt'),
                    src_path=src_folder,
                    dst_path=dst_folder,
                )
                caption_csv_generator.write_data_to_csv()
                break

            elif user_confirmation == 'n':
                logger.info(
                    "You have chosen to cancel the process. "
                    f"The operation has been halted. All images in the folder '{src_folder}' remain unchanged."
                )
                sys.exit(1)
            else:
                logger.warning(
                    f"Unrecognized input: '{user_confirmation}'. "
                    f"Please enter '1' for Option 1, '2' for Option 2, '3' for Option 3 or 'N' to cancel."
                )

    except FileNotFoundError as e:
        logger.error(
            f"Could not find {e.filename}. Please ensure the file exists and is accessible."
        )
        sys.exit(1)
    except Exception as e:
        logger.error(
            f"An unexpected error occurred: {e}. Please check the configuration file and try again."
        )
        sys.exit(1)


if __name__ == '__main__':
    main()

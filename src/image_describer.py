"""This module processes images by generating descriptive metadata using GPT and adds the metadata to images."""

import os
import shutil
import tempfile
import time

from iptcinfo3 import IPTCInfo

from src.check_access import terminate_processes_using_file
from src.files_filter import filter_files_by_extension
from src.logging_config import setup_logger
from src.response_parser import parse_response

# Initialize logger using the setup function
logger = setup_logger(__name__)


class ImagesDescriber:
    """
    A class to facilitate image description generation using OpenAI's GPT model and add metadata to images.

    Attributes:
        prompt (str): The prompt to be sent to the GPT model for generating descriptions.
        src_path (str): The source directory containing the images to be processed.
        dst_path (str): The destination directory for saving the processed images. If not provided, defaults to src_path.
        author_name (str): The author name of the images.

    Methods:
        __init__(prompt, src_path, dst_path, author_name):
            Initializes the ImagesDescriber with the specified parameters.

        add_metadata():
            Adds processed titles, descriptions, and keywords to the metadata of the images in the source directory.
            Saves the processed images in the destination directory.

        remove_backup_file(filename):
            Static method. Removes the backup file created by the IPTCInfo library, if it exists.
            Typically, backup files have a '~' suffix.

        __str__():
            Returns a string representation of the ImagesDescriber instance.
    """

    def __init__(self, prompt, src_path, dst_path, author_name):
        """
        Initialize the ImagesDescriber with a prompt, source path, destination path, and author name.

        Args:
            prompt (str): The prompt to be sent to the GPT model for generating descriptions.
            src_path (str): The path to the directory containing the images to be processed.
            dst_path (str): The path to the directory where processed images will be saved. Defaults to src_path if not provided.
            author_name (str): The name of the author for the images.
        """
        self.prompt = prompt
        self.src_path = src_path
        self.dst_path = dst_path if dst_path else src_path
        self.author_name = author_name

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
        filtered_image_files = filter_files_by_extension(src_path=self.src_path)
        logger.info(
            f"Images processing has started! {len(filtered_image_files)} images to process."
        )

        # Get title, description, and keywords for each image file
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
                    # Get cleaned data from GPT response
                    title, description, keywords = parse_response(
                        image_file=image_file, prompt=self.prompt
                    )

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
            f"\tdst_path={self.dst_path},\n"
            f"\tauthor_name={self.author_name}\n"
            f")"
        )

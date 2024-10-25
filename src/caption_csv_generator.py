"""This module processes images by generating descriptive metadata using GPT, captions from images meatadata and saves the data to a CSV file."""

import csv
import os
import time
from datetime import datetime

from iptcinfo3 import IPTCInfo

from src.files_filter import filter_files_by_extension
from src.logging_config import setup_logger
from src.response_parser import parse_response

# Initialize logger using the setup function
logger = setup_logger(__name__)


class CaptionCSVGenerator:
    """
    A class to generate image descriptions using OpenAI's GPT model based on extracted captions from image metadata, then save the results to a CSV file.

    Attributes:
        prompt (str): The prompt to be sent to the GPT model for generating descriptions.
        src_path (str): The source directory containing the images to be processed.
        dst_path (str): The destination directory for saving the generated CSV file. If not provided, defaults to src_path.

    Methods:
        __init__(prompt, src_path, dst_path):
            Initializes the CaptionCSVGenerator with the specified parameters.

        write_data_to_csv():
            Generates a CSV file containing the file names, titles, descriptions, and keywords of the processed images.
            Saves the CSV file in the destination directory.

        __str__():
            Returns a string representation of the CaptionCSVGenerator instance.
    """

    def __init__(self, prompt, src_path, dst_path):
        """
        Initialize the CaptionCSVGenerator with a prompt, source path, and destination path.

        Args:
            prompt (str): The prompt to be sent to the GPT model for generating descriptions.
            src_path (str): The path to the directory containing the images to be processed.
            dst_path (str): The path to the directory where the generated CSV file will be saved. Defaults to src_path if not provided.
        """
        self.prompt = prompt
        self.src_path = src_path
        self.dst_path = dst_path if dst_path else src_path

    def write_data_to_csv(self):
        """Write image metadata (image_name, title, description, keywords) to a single CSV file."""
        # Record the start time of the process of handling the images
        time_start = time.perf_counter()

        # Initialize counter for images
        processed_count = 0

        # Get filtered image files to process
        filtered_image_files = filter_files_by_extension(src_path=self.src_path)
        logger.info(
            f"Images processing has started! {len(filtered_image_files)} images to process."
        )

        # Ensure destination directory exists; create if it doesn't
        if not os.path.exists(self.dst_path):
            os.makedirs(self.dst_path, exist_ok=True)

        # Get the current datetime and format for the CSV file name
        current_datetime = datetime.now().strftime('%d-%m-%Y--%H-%M-%S')
        csv_filepath = os.path.join(self.dst_path, f"{current_datetime}.csv")

        try:
            # Open the CSV file for writing
            with open(csv_filepath, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)

                # Write the CSV header
                writer.writerow(['image_name', 'title', 'description', 'keywords'])

                # Process each image file and write its data to CSV file
                for image_name in filtered_image_files:
                    image_path = os.path.join(self.src_path, image_name)

                    try:
                        with open(image_path, 'rb') as image_file:
                            # Load IPTC metadata
                            try:
                                info = IPTCInfo(image_path)
                            except Exception as e:
                                logger.error(
                                    f"No IPTC metadata found, create a new one. Error: {e}"
                                )
                                info = IPTCInfo(None)

                            # Get image caption from image metadata
                            image_caption = info['caption/abstract']
                            if not image_caption:
                                logger.warning(
                                    f"The file '{image_name}' does not contain IPTC metadata. "
                                    "Title, description, and keywords will be generated "
                                    "without using the image caption."
                                )

                            # Get cleaned data from GPT response
                            title, description, keywords = parse_response(
                                image_file=image_file,
                                prompt=self.prompt,
                                image_caption=image_caption,
                            )
                            keywords_str = ','.join(keywords)
                            # Write the data to the CSV file
                            writer.writerow([image_name, title, description, keywords_str])
                            logger.info(
                                f"Image name, title, description, and keywords of {image_name} (JPEG) "
                                f"were successfully added to CSV file."
                            )
                            processed_count += 1
                    except Exception as e:
                        logger.error(f"Error processing {image_name}: {e}")

            logger.info(f"CSV file created successfully at: {csv_filepath}")
        except Exception as e:
            logger.error(f"Failed to create CSV file: {e}")
            return

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


def __str__(self):
    """
    Return a string representation of the CaptionCSVGenerator instance.

    Returns:
        str: A string representation of the class instance, showing key attributes.
    """
    return (
        f"CaptionCSVGenerator(\n"
        f"\tprompt={self.prompt},\n"
        f"\tsrc_path={self.src_path},\n"
        f"\tdst_path={self.dst_path},\n"
        f")"
    )

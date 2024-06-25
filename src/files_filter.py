"""This module filters files by image extensions to be processed."""

import os
import shutil
from pathlib import Path
from typing import List, Union

from PIL import Image, JpegImagePlugin

from src.logging_config import setup_logger

# Initialize logger using the setup function
logger = setup_logger(__name__)


def filter_files_by_extension(src_path: Union[str, List[str]]) -> List[str]:
    """
    Filter files by image extensions. Non-image files are moved to a 'Not_Images' folder.

    Args:
        src_path: Path to source directory or a list of files.

    Returns:
        List of filtered image file names.
    """
    logger.info("Starting to filter files by image types in the source folder.")

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.ico', '.svg'}
    filtered_files = []

    for image_name in (
        f
        for f in os.listdir(src_path)
        if os.path.isfile(os.path.join(src_path, f)) and not f.startswith('.')  # skip hidden files
    ):
        image_path = os.path.join(src_path, image_name)

        # Check if the file is an image based on its extension
        if image_name.lower().endswith(tuple(image_extensions)) and os.path.isfile(image_path):
            with Image.open(image_path) as img:
                # Verify image integrity
                img.verify()

                # Ensure that only JPEG files are processed
                if isinstance(img, JpegImagePlugin.JpegImageFile):
                    filtered_files.append(image_name)

                # Other image formats - leave file without modification
                else:
                    logger.warning(
                        f"Unsupported image format ({str(image_name).upper().split('.')[-1]}), "
                        f"the file '{image_name}' was left in the source folder unprocessed."
                    )
        else:
            move_non_image_format(image_name, image_path, src_path)
        logger.info("Finished filtering files by image types in the source folder.")
        return filtered_files


def move_non_image_format(image_name: str, image_path: str, src_path: str):
    """
    Move a non-image file to the 'Not_Images' folder, handling name conflicts.

    Args:
        image_name (str): Name of the file to move.
        image_path (str): Path of the file to move.
        src_path (str): Source directory path.

    """
    try:
        # Create 'Not_Images' folder
        not_img_fld = os.path.join(src_path, 'Not_Images')
        Path(not_img_fld).mkdir(parents=True, exist_ok=True)

        # Separate the filename and extension
        base_name, ext = os.path.splitext(image_name)
        destination_file_path = os.path.join(not_img_fld, image_name)

        # Initialize counter for same file names
        counter = 1

        # Check if the file already exists in the destination folder
        while os.path.exists(destination_file_path):
            destination_file_path = os.path.join(not_img_fld, f"{base_name}_({counter}){ext}")
            counter += 1

        shutil.move(image_path, destination_file_path)
        logger.warning(
            f"Moved non-image file '{image_name}' to {not_img_fld} as {os.path.basename(destination_file_path)}."
        )
    except shutil.Error as e:
        logger.error(f"Error moving file '{image_path}' to 'Not Images': {e}.")
    except Exception as e:
        logger.error(f"An expected error occurred while moving {image_name}: {e}")

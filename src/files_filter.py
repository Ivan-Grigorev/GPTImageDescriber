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

    filtered_files = []

    for image_name in (
        f
        for f in os.listdir(src_path)
        if os.path.isfile(os.path.join(src_path, f)) and not f.startswith('.')  # skip hidden files
    ):
        image_path = os.path.join(src_path, image_name)

        # Check if the file is an image based on its extension
        if image_name.lower().endswith(
            (
                '.jpg',
                '.jpeg',
                '.png',
                '.gif',
                '.bmp',
                '.webp',
                '.tiff',
                '.ico',
                '.svg',
            )
        ) and os.path.isfile(image_path):

            with Image.open(image_path) as img:
                # Ensure that only JPEG files are processed
                if isinstance(img, JpegImagePlugin.JpegImageFile):
                    filtered_files.append(image_name)

                # Other image formats - leave file without modification
                else:
                    logger.warning(
                        f"Due to the unsupported ({str(image_name).upper().split('.')[-1]}) "
                        f"format, the file '{image_name}' was left in the Source Folder without being processed."
                    )

        else:
            # Move non-image files to the 'Not_Images' folder
            try:
                not_img_fld = os.path.join(src_path, 'Not_Images')
                Path(not_img_fld).mkdir(parents=True, exist_ok=True)

                # Separate the filename and extension
                base_name, ext = os.path.splitext(image_name)
                counter = 1
                file_to_move = image_name
                destination_file_path = os.path.join(not_img_fld, file_to_move)

                # Check if the file already exists in the destination folder
                while os.path.exists(destination_file_path):
                    file_to_move = f"{base_name}_({counter}){ext}"
                    destination_file_path = os.path.join(not_img_fld, file_to_move)
                    counter += 1
                shutil.move(image_path, destination_file_path)
                logger.warning(
                    f"Moved non-image file '{image_name}' to {not_img_fld} as {file_to_move}."
                )
            except shutil.Error as e:
                logger.error(f"Error moving file '{image_path}' to 'Not Images': {e}.")
            except Exception as e:
                logger.error(f"An expected error occurred while moving {image_name}: {e}")

    logger.info("Finished filtering files by image types in the source folder.")

    return filtered_files

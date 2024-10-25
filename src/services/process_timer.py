"""Module to display processing time for image processing operations."""

from src.services.logging_config import setup_logger

# Initialize logger using the setup function
logger = setup_logger(__name__)


def execution_timer(processed_count, unprocessed_count, process_time):
    """
    Log the processing time and count of processed and unprocessed images.

    Attributes:
        processed_count (int): The number of images successfully processed.
        unprocessed_count (int): The number of images that were not processed.
        process_time (float): The total time taken to process the images, in seconds.
    """

    if process_time < 60:
        # Display process time in seconds
        logger.info(
            f"Processing complete: "
            f"{processed_count} images processed, {unprocessed_count} unprocessed. "
            f"Images processing time is {process_time:.2f} seconds."
        )
    elif 60 <= process_time < 3600:
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
        process_seconds = process_time % 60
        logger.info(
            f"Processing complete: "
            f"{processed_count} images processed, {unprocessed_count} unprocessed. "
            f"Images processing time is {process_hours:.0f} "
            f"{'hour' if process_hours == 1 else 'hours'} "
            f"{process_minutes:.0f} minutes {process_seconds:.0f} seconds."
        )

"""Script to check if an image is locked by any process."""

import psutil

from src.logging_config import setup_logger

# Initialize logger using the setup function
logger = setup_logger(__name__)


def terminate_process_using_file(file_path):
    """
    Terminate all process that are using a specific file.

    Args:
        file_path: Path to the file to check and terminate process.
    """
    process = get_process_using_file(file_path)
    if process:
        for proc in process:
            terminate_process(proc.info['pid'])


def get_process_using_file(file_path):
    """
    Get a list of processes that have a specific file open.

    Args:
        file_path: Path to the file to check.

    Returns:
         List of psutil.Process objects.
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            # Iterate through open file of each process
            for file in proc.info['open_files'] or []:
                # Check if the file path matches the given file path
                if file.path == file_path:
                    processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Ignore processes that raise the exceptions
            continue

    return processes


def terminate_process(pid):
    """
    Terminate process by its PID.

    Args:
        pid: Process ID (PID) of the process to terminate.
    """
    try:
        process = psutil.Process(pid)  # get process object by PID
        process.terminate()  # terminate the process
        process.wait()  # wait for the process to terminate
        logger.warning(f"Terminated process {pid} ({process.name()}) that was using the file.")
    except psutil.NoSuchProcess:
        logger.warning(f"Process {pid} does not exist or already terminated.")
    except psutil.AccessDenied:
        logger.error(f"Access denied when trying to terminate process {pid}.")

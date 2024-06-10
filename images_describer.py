from PIL import Image
from PIL.ExifTags import TAGS
import openai
import subprocess
import sys
import os

# Get secret key from a file for security (not shown here)
with open("openai_key.txt", "r") as f:
    openai.api_key = f.read().strip()

# Disable the image size warning to handle large images
Image.MAX_IMAGE_PIXELS = None


class GPTImagesDescriber:
    """
    This class processes images in a directory and uses their existing description
    metadata to generate a title and keywords. It then writes these back to
    the image metadata.
    """

    def __init__(self, src_path):
        """
        Initializes the class with the source directory path.

        Args:
            src_path (str): Path to the directory containing images.
            dst_path (str): Path to the directory to download processed images.
        """
        self.src_path = src_path

        # Optional output directory (defaults to source path)
        self.dst_path = sys.argv[2] if len(sys.argv) > 2 else src_path

    def get_prompt_from_metadata(self, file_path):
        """
        Extracts the "ImageDescription" metadata from the image.

        Args:
            file_path (str): Path to the image file.

        Returns:
            str: The description text from the metadata or None if not found.
        """
        try:
            image = Image.open(file_path)
            info = image._getexif()
            if info is not None:
                for tag, value in info.items():
                    if TAGS.get(tag) == "ImageDescription":
                        return value
            return None
        except Exception as e:
            print(f"Error reading metadata: {e}")

    def generate_title_and_keywords(self, prompt):
        """
        Generates a title and keywords from the provided prompt.

        The title is extracted as the first sentence of the prompt,
        and keywords are the first 49 words.

        Args:
            prompt (str): The description text to use for generation.

        Returns:
            tuple: A tuple containing the generated title (str) and keywords (list).
        """
        title = prompt.split(".")[0]  # First sentence as title
        keywords = prompt.split()[:49]  # First 49 words as keywords
        return title, keywords

    def write_metadata(self, title, keywords):
        """
        Writes the title and keywords back to the image metadata using exiftool.

        Args:
            title (str): The title to write to the metadata.
            keywords (list): The list of keywords to write to the metadata.

        Raises:
            Exception: If there is an error writing the metadata.
        """
        try:
            subprocess.run(
                [
                    "exiftool",
                    f"-ImageDescription={title}",
                    f"-Keywords={','.join(keywords)}",
                    self.dst_path,
                ],
                check=True,
            )
        except Exception as e:
            print(f"Error writing metadata: {e}")

    def process_images(self):
        """
        Processes all images in the source directory.

        Iterates through all files, checks for image formats, and if a description
        is found in the metadata, generates a title and keywords before writing
        them back to the image metadata.
        """
        for filename in os.listdir(self.src_path):
            if any(
                [
                    filename.lower().endswith(".jpg"),
                    filename.lower().endswith(".jpeg"),
                    filename.lower().endswith(".png"),
                ]
            ):
                file_path = os.path.join(self.src_path, filename)
                prompt = self.get_prompt_from_metadata(file_path)
                if prompt:
                    title, keywords = self.generate_title_and_keywords(prompt)
                    self.write_metadata(title, keywords)
                    print(f"Processed {filename}")


if __name__ == "__main__":
    try:
        gpt_describer = GPTImagesDescriber(
            src_path=sys.argv[1],
        )
        gpt_describer.process_images()
    except FileNotFoundError as err:
        print(err.__str__())

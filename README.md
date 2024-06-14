# GPT Image Describer

**Quickly add titles & keywords to your photos using AI!**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [Example](#example)
7. [License](#license)
8. [Credits](#credits)
9. [Additional Notes](#additional-notes)

---

## Introduction

**GPT Image Describer** is a Python-based tool that leverages OpenAI's GPT model to automatically generate SEO-optimized titles and keywords for your photos. This project is designed for quick personal use and is not intended for production environments.

---

## Features

- Generates SEO-friendly titles and keywords for images.
- Supports popular image formats such as JPG, JPEG, and PNG.
- Automatically adds metadata to the images.
- Handles images from a specified source folder and saves the processed images to a destination folder.

---

## Installation

1. **Save the Script**: Save the script as `images_describer.py`.
2. **Install Dependencies**: Run the following command to install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
3. **Get OpenAI API Key**: Obtain your OpenAI API key from [OpenAI's website](https://openai.com/). Save the key in a file named `openai_key.txt` in the same directory as your script. **Keep this key secret and do not share it!**

---

## Usage

Run the script from your command line, specifying the source folder containing your images. Optionally, you can specify a destination folder for the processed images.

```bash
python images_describer.py [source folder] [optional destination]
```

### Example

```bash
python images_describer.py /mypics /modified
```

In this example, images from the `/mypics` folder will be processed, and the resulting images will be saved in the `/modified` folder.

---

## Configuration

Create a `configurations.txt` file in the same directory as `images_describer.py`. This file should contain the necessary settings for handling images. Here’s a template:

```plaintext
prompt=Describe the image and generate a title and keywords.
source_folder=/path/to/your/source/folder
destination_folder=/path/to/your/destination/folder
author=Your Name
```

- **prompt**: A prompt for generating titles, descriptions, and keywords using ChatGPT.
- **source_folder**: The folder where your images are located.
- **destination_folder**: The folder where the processed images will be saved. If not provided, images will be saved back to the source folder.
- **author**: The name of the image's author or creator.

---

## License

**MIT License**

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Credits

This repository and project were created by [Ivan Grigorev](https://github.com/Ivan-Grigorev). This project is not intended for production use and is designed for educational purposes and quick personal use.

---

## Additional Notes

- **Source Folder**: Ensure that the source folder contains only the images you want to process. The script will process all files with supported extensions.
- **Destination Folder**: If no destination folder is specified, the processed images will be saved back in the source folder, overwriting the original files.
- **Image Metadata**: The script uses the "ImageDescription" metadata field to store the generated titles and keywords.
- **Free OpenAI Tier**: Be aware that the free tier of OpenAI may have limitations on the number of requests you can make.

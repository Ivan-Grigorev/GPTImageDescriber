# GPT Image Describer

**Quickly add titles, descriptions & keywords to your photos using AI!**

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Example CSV Output](#example-csv-output)
7. [License](#license)
8. [Credits](#credits)

## Introduction

**GPT Image Describer** is a Python-based tool that leverages OpenAI's GPT model to automatically generate SEO-optimized titles, descriptions, and keywords for your photos. This project is designed for quick personal use and is not intended for production environments.

## Features

- Generates SEO-friendly titles, descriptions, and keywords for images.
- Supports popular image formats such as JPG and JPEG.
- Automatically adds metadata to the images.
- Generates a CSV file containing image names, titles, descriptions, and keywords.
- Handles images from a specified source folder and saves the processed images or CSV file to a destination folder.

## Installation

1. **Clone the Repository**: Start by cloning the repository to your local machine:
    ```bash
    git clone https://github.com/Ivan-Grigorev/GPTImageDescriber
    ```
2. **Navigate to the Project Directory**: Change your working directory to the cloned repository:
    ```bash
    cd GPTImageDescriber
    ```
3. **Install Dependencies**: Run the following command to install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4. **Get OpenAI API Key**: Obtain your OpenAI API key from [OpenAI's website](https://openai.com/). Save the key in a file named `openai_key.txt` in the same directory as your script. **Keep this key secret and do not share it!** Note that the free tier of OpenAI may have limitations on the number of requests you can make.

## Configuration

Edit a `configurations.txt` file in the root directory. This file should contain the necessary settings for handling images. Here’s a template:

```plaintext
prompt=Describe the image and generate a title, description, and keywords.
source_folder=/full/path/to/your/source/folder
destination_folder=/full/path/to/your/destination/folder
author=Your Name
```

- **prompt**: A prompt for generating titles, descriptions, and keywords using ChatGPT.
- **source_folder**: The folder where your images are located.
- **destination_folder**: The folder where the processed images or CSV file will be saved. If not provided, files will be saved back to the source folder.
- **author**: The name of the image's author or creator.

## Usage

To run the image processing script, execute the following command in your terminal:

```bash
python run_app.py
```

### Processing Options

Upon running the script, you will be prompted to choose between three options:

1. **Option 1: Add Metadata to Images**
   This option uses GPT to generate titles, descriptions, and keywords for your images and directly adds them as metadata to the image files. Processed images are saved to the destination folder.

2. **Option 2: Generate CSV File**
   This option uses GPT to generate titles, descriptions, and keywords for your images but does not modify the image files. Instead, it creates a CSV file containing the image names, titles, descriptions, and keywords, and saves it in the destination folder.

3. **Option 3: Generate CSV File with Metadata Captions**
   This option uses GPT to generate titles, descriptions, and keywords for your images without modifying the image files. In addition to the standard prompt, GPT leverages the existing captions found in the image metadata to generate a more tailored description. The output CSV file, containing image names, titles, descriptions, and keywords, is saved in the destination folder.

## Example CSV Output

When you select **Option 2** or **Option 3**, the CSV file will have the following format:

```csv
image_name,title,description,keywords
image1.jpg,Sunset on the Beach,A serene sunset over the ocean,...,sunset,beach,serenity
image2.jpg,Mountain Peaks,High snow-capped mountains under a clear sky,...,mountain,snow,adventure
```

The CSV file is named with the current date and time and saved in the destination folder.

## License

This project is licensed under the terms of the [LICENSE](./LICENSE).

## Credits

This repository and project were created by [Ivan Grigorev](https://github.com/Ivan-Grigorev). This project is not intended for production use and is designed for educational purposes and quick personal use.

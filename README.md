
# Gallery Gather

Discover. Collect. Unveil. Upload an image with a person and a Google Drive link to check if the person is present in any of the images from the link.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Requirements](#requirements)

## Introduction

Gallery Gather is an application that helps users find images containing a specific person from a Google Drive folder. Using advanced face recognition techniques, it processes and analyzes images to detect and match faces.

## Features

- Upload an image of a person.
- Provide a Google Drive link to a folder containing images.
- Automatically download and process images from the provided link.
- Detect and match the person’s face in the images.
- Download matched images in a ZIP file.

## Installation

To install and run this project locally, follow these steps:

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Aiswarya-Menon/Gallery_Gather.git
    cd gallery-gather
    ```

2. **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Place the service account JSON file:**
   - Ensure you have your Google service account JSON file.
   - Place the JSON file in the root directory of the project and name it `image-checker-423607-292291835303.json`.

## Usage

1. **Run the Streamlit app:**
    ```sh
    streamlit run app.py
    ```

2. **Upload an image:**
   - Upload an image of the person you want to search for in the Google Drive folder. Supported formats: JPG, JPEG, PNG, HEIC.

3. **Provide the Google Drive link:**
   - Enter the Google Drive folder link containing the images to be checked.

4. **Find matching images:**
   - Click on "Find Matching Images" to start the process.
   - The app will process the images and display the results.
   - You can download the matching images as a ZIP file.

## File Structure
├── app.py
├── requirements.txt
├── image-checker-423607-292291835303.json # Place your service account JSON file here


## Requirements

- Python 3.x
- Streamlit
- OpenCV
- NumPy
- Pillow
- pillow-heif
- Google API Client
- face_recognition

Install the requirements using:
```sh
pip install -r requirements.txt


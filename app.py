import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import re
import io
import zipfile
import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pillow_heif  # Library to handle HEIC files
import face_recognition

# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = "path/to/json/file"

# Function to authenticate and build Google Drive service


def create_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=credentials)

# Function to get file IDs from Google Drive link


def get_file_ids_from_link(drive_service, folder_id):
    file_ids = []
    query = f"'{folder_id}' in parents and trashed=false"
    results = drive_service.files().list(
        q=query, fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':  # Check if it's a folder
            # Recursively get files from subfolders
            file_ids.extend(get_file_ids_from_link(drive_service, item['id']))
        else:
            file_ids.append(item['id'])

    return file_ids

# Function to download files from Google Drive


def download_files(drive_service, file_ids, download_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    downloaded_files = []
    for file_id in file_ids:
        file = drive_service.files().get(fileId=file_id).execute()
        file_name = file['name']
        file_path = os.path.join(download_dir, file_name)
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        downloaded_files.append(file_path)
    return downloaded_files

# Function to detect person in images


def detect_person_in_image(person_image, check_image):
    # Convert images to RGB
    person_image = person_image.convert("RGB")
    check_image = check_image.convert("RGB")

    # Convert images to numpy arrays
    person_image_np = np.array(person_image)
    check_image_np = np.array(check_image)

    # Encode faces in the images
    person_encodings = face_recognition.face_encodings(person_image_np)
    check_encodings = face_recognition.face_encodings(check_image_np)

    if not person_encodings or not check_encodings:
        return False

    # Compare faces
    for person_encoding in person_encodings:
        results = face_recognition.compare_faces(
            check_encodings, person_encoding, tolerance=0.6)
        if any(results):
            return True

    return False


def create_zip(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))


def main():
    st.title("Gallery Gather")
    st.write("Discover. Collect. Unveil.")
    st.write("Upload an image with a person and a Google Drive link to check if the person is present in any of the images from the link.")

    # Upload person image
    person_image = st.file_uploader(
        "Upload Person Image", type=["jpg", "jpeg", "png", "heic"])
    # Google Drive link input
    google_drive_link = st.text_input("Enter Google Drive folder link")

    if person_image and google_drive_link:
        if st.button("Find Matching Images"):
            with st.spinner('Processing...'):
                # Create Google Drive service
                drive_service = create_drive_service()

                # Extract folder ID from Google Drive link
                match = re.match(
                    r'^https://drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)', google_drive_link)
                if not match:
                    st.error("Invalid Google Drive link.")
                    return
                folder_id = match.group(1)

                # Get file IDs from the Google Drive link
                file_ids = get_file_ids_from_link(drive_service, folder_id)

                # Specify the directory to save the downloaded files
                download_directory = "downloaded_images"

                # Download files from Google Drive
                downloaded_images = download_files(
                    drive_service, file_ids, download_directory)

                # Load person image
                person_image = Image.open(person_image)

                # Find matching images
                matching_images = []
                matching_folder = "matching_images"
                if not os.path.exists(matching_folder):
                    os.makedirs(matching_folder)

                for image_path in downloaded_images:
                    # Open HEIC files using pillow-heif
                    if image_path.lower().endswith('.heic'):
                        heif_file = pillow_heif.read_heif(image_path)
                        check_image = Image.frombytes(
                            heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride)
                    else:
                        check_image = Image.open(image_path)

                    if detect_person_in_image(person_image, check_image):
                        matching_images.append(image_path)
                        shutil.copy(image_path, os.path.join(
                            matching_folder, os.path.basename(image_path)))

                # Display results
                if matching_images:
                    st.success(
                        f"Found {len(matching_images)} matching images:")
                    for image_path in matching_images:
                        st.image(image_path)

                    # Create zip file of matching images
                    zip_path = "matching_images.zip"
                    create_zip(matching_folder, zip_path)

                    # Provide download link for the zip file
                    with open(zip_path, "rb") as f:
                        bytes_data = f.read()
                        st.download_button(
                            label="Download Matching Images",
                            data=bytes_data,
                            file_name="matching_images.zip",
                            mime="application/zip"
                        )
                else:
                    st.warning("No matching images found.")


if __name__ == "__main__":
    main()

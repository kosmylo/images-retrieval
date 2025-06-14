import os
import json
import zipfile
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi
from PIL import Image
from tqdm import tqdm
from datetime import datetime
import logging

# Configuration 
DATASET_NAME = "liushuyuu/irregular-facades-irfs"
DOWNLOAD_PATH = "./irfs_dataset"
EXTRACTED_PATH = "./irfs_dataset_extracted"

def authenticate_kaggle():
    api = KaggleApi()
    api.authenticate()
    logging.info("Authenticated Kaggle API successfully.")
    return api

def download_dataset(api, dataset_name, download_path):
    logging.info("Downloading dataset from Kaggle...")
    os.makedirs(download_path, exist_ok=True)
    api.dataset_download_files(dataset_name, path=download_path, unzip=False)

def extract_dataset(zip_path, extract_to):
    logging.info(f"Extracting dataset from {zip_path}...")
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info("Dataset extracted successfully.")
    else:
        logging.error("Zip file not found. Extraction failed.")

def collect_jpg_images_and_json(extracted_path, max_images_total, output_dir):
    logging.info("Selecting JPEG images and JSON annotations...")
    image_paths = []
    json_paths = {}

    # Collect jpg images and corresponding json files
    for root, dirs, files in os.walk(extracted_path):
        for file in files:
            if file.lower().endswith(".jpg"):
                image_full_path = os.path.join(root, file)
                json_file = os.path.splitext(file)[0] + ".json"
                json_full_path = os.path.join(root, json_file)

                if os.path.exists(json_full_path):
                    image_paths.append(image_full_path)
                    json_paths[image_full_path] = json_full_path

    # Limit to max_images_total
    image_paths = sorted(image_paths)[:max_images_total]

    os.makedirs(output_dir, exist_ok=True)
    for img_path in tqdm(image_paths, desc="Copying images"):
        shutil.copy(img_path, output_dir)

    logging.info(f"Copied {len(image_paths)} images.")
    return image_paths, json_paths

def generate_metadata(image_paths, json_paths, output_dir):
    logging.info("Generating metadata for selected images...")
    for img_path in tqdm(image_paths, desc="Generating metadata"):
        fname = os.path.basename(img_path)
        metadata_filename = os.path.splitext(fname)[0] + ".json"
        metadata_path = os.path.join(output_dir, metadata_filename)

        # Default metadata
        width, height = None, None
        json_annotation_path = json_paths.get(img_path)

        # Extract resolution from the JSON annotation file
        if json_annotation_path:
            with open(json_annotation_path, 'r', encoding='utf-8') as jf:
                annotation = json.load(jf)
                width = annotation.get("imageWidth")
                height = annotation.get("imageHeight")

        # If JSON not available or failed, fall back to PIL
        if width is None or height is None:
            try:
                with Image.open(img_path) as img:
                    width, height = img.size
            except Exception as e:
                print(f"Failed to open image {fname}: {e}")
                continue  # skip if image is corrupted

        metadata = {
            "filename": fname,
            "retrieved_date": datetime.today().strftime('%Y-%m-%d'),
            "additional_info": {
                "resolution": f"{width}x{height}px",
                "image_format": "JPEG"
            },
            "source": {
                "provider": "Irregular Facades Dataset (IRFs)",
                "repository": DATASET_NAME
            }
        }

        with open(metadata_path, 'w', encoding='utf-8') as meta_file:
            json.dump(metadata, meta_file, indent=4)

    logging.info("Metadata generation completed.")

def download_irf_images(max_images, output_dir, download_data, extract_data):
    api = authenticate_kaggle()

    if download_data:
        download_dataset(api, DATASET_NAME, DOWNLOAD_PATH)

    zip_file = os.path.join(DOWNLOAD_PATH, DATASET_NAME.split('/')[-1] + ".zip")

    if extract_data:
        extract_dataset(zip_file, EXTRACTED_PATH)

    selected_images, annotations_map = collect_jpg_images_and_json(
        extracted_path=EXTRACTED_PATH,
        max_images_total=max_images,
        output_dir=output_dir
    )

    generate_metadata(selected_images, annotations_map, output_dir)
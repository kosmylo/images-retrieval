import os
import json
import zipfile
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi
import rasterio
from rasterio.warp import transform_bounds
from tqdm import tqdm
from datetime import datetime
import logging

# Configuration 
DATASET_NAME = "sagar100rathod/inria-aerial-image-labeling-dataset"
DOWNLOAD_PATH = "./inria_dataset"
EXTRACTED_PATH = "./inria_dataset_extracted"
COUNTRY_MAPPING = {
    "austin": "USA",
    "chicago": "USA",
    "kitsap": "USA",
    "bellingham": "USA",
    "bloomington": "USA",
    "sanfrancisco": "USA",
    "vienna": "Austria",
    "innsbruck": "Austria",
    "tyrol-w": "Austria",
    "tyrol-e": "Austria"
}

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

def select_images(cities, max_images_total, extracted_path, output_dir):
    logging.info("Selecting images based on specified cities...")
    image_dirs = [
        os.path.join(extracted_path, "AerialImageDataset/train/images"),
        os.path.join(extracted_path, "AerialImageDataset/test/images")
    ]
    selected_images = []

    city_keys = [city.lower() for city in cities]

    for dir_path in image_dirs:
        if not os.path.exists(dir_path):
            logging.warning(f"Directory not found: {dir_path}")
            continue
        for fname in os.listdir(dir_path):
            city_key = fname.split('.')[0].rstrip('0123456789')
            if city_key in city_keys:
                selected_images.append((os.path.join(dir_path, fname), city_key))
    
    if max_images_total:
        selected_images = selected_images[:max_images_total]

    os.makedirs(output_dir, exist_ok=True)
    for img_path, _ in tqdm(selected_images, desc="Copying images"):
        shutil.copy(img_path, output_dir)

    logging.info(f"Selected and copied {len(selected_images)} images.")
    return selected_images

def generate_metadata(selected_images, output_dir):
    logging.info("Generating metadata for selected images...")
    for img_path, city_key in tqdm(selected_images, desc="Generating metadata"):
        fname = os.path.basename(img_path)
        metadata_filename = os.path.splitext(fname)[0] + ".json"
        metadata_path = os.path.join(output_dir, metadata_filename)

        with rasterio.open(img_path) as src:
            bounds = src.bounds
            crs = src.crs
            res_x, res_y = src.res
            width, height = src.width, src.height
            bounds_latlon = transform_bounds(crs, 'EPSG:4326', *bounds)

        metadata = {
            "filename": fname,
            "city": city_key.capitalize(),
            "country": COUNTRY_MAPPING.get(city_key, "Unknown"),
            "retrieved_date": datetime.today().strftime('%Y-%m-%d'),
            "additional_info": {
                "resolution": f"{res_x:.2f} m/pixel",
                "image_size": f"{width}x{height} px",
                "crs": str(crs),
                "bounds_original_crs": {
                    "xmin": bounds.left,
                    "ymin": bounds.bottom,
                    "xmax": bounds.right,
                    "ymax": bounds.top
                },
                "bounds_latlon": {
                    "xmin": bounds_latlon[0],
                    "ymin": bounds_latlon[1],
                    "xmax": bounds_latlon[2],
                    "ymax": bounds_latlon[3]
                }
            },
            "source": {
                "provider": "Inria",
                "repository": DATASET_NAME
            }
        }

        with open(metadata_path, 'w') as meta_file:
            json.dump(metadata, meta_file, indent=4)

    logging.info("Metadata generation completed.")

def download_inria_images(cities, max_images, output_dir, download_data, extract_data):

    api = authenticate_kaggle()

    if download_data:
        download_dataset(api, DATASET_NAME, DOWNLOAD_PATH)
    
    zip_file = os.path.join(DOWNLOAD_PATH, DATASET_NAME.split('/')[-1] + ".zip")

    if extract_data:
        extract_dataset(zip_file, EXTRACTED_PATH)

    selected_images = select_images(cities, max_images, EXTRACTED_PATH, output_dir)
    generate_metadata(selected_images, output_dir)

import requests
import os
import json
from datetime import datetime
import logging
from langdetect import detect, LangDetectException

# Wikimedia Commons API endpoint
API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"

headers = {
    "User-Agent": "mAiEnergyBot/1.0 (kosmylo@gmail.com; downloading images for research project)"
}

def is_english_title(title):
    try:
        lang = detect(title)
        return lang == 'en'
    except LangDetectException:
        return False

def search_images(category, limit=50):
    params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": f"Category:{category}",
        "gcmtype": "file",
        "gcmlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "format": "json"
    }
    response = requests.get(API_ENDPOINT, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    images = data.get("query", {}).get("pages", {}).values()
    return list(images)

def download_image(image_info, category, output_dir):
    image_url = image_info['imageinfo'][0]['url']
    image_name = image_url.split("/")[-1]

    title_no_prefix = image_info["title"].replace("File:", "").replace("_", " ").replace("-", " ")

    # Check for English title
    if not is_english_title(title_no_prefix):
        logging.info(f"Skipping non-English title: {title_no_prefix}")
        return False
    
    # Filter only image MIME types
    image_mime = image_info['imageinfo'][0]['mime']
    if not image_mime.startswith('image/'):
        logging.info(f"Skipping non-image file: {title_no_prefix} with MIME type {image_mime}")
        return False

    # Ensure proper file extension handling
    image_extension = os.path.splitext(image_name)[1]
    if not image_extension:
        image_extension = ".jpg"
        image_name += image_extension

    base_name, _ = os.path.splitext(image_name)
    category_dir = os.path.join(output_dir, category.replace(" ", "_"))
    os.makedirs(category_dir, exist_ok=True)
    file_path = os.path.join(category_dir, image_name)

    # Download and save image
    img_response = requests.get(image_url, headers=headers, stream=True)
    img_response.raise_for_status()

    with open(file_path, 'wb') as file:
        for chunk in img_response.iter_content(chunk_size=8192):
            file.write(chunk)

    # Metadata structure
    metadata = {
        "title": title_no_prefix,
        "url": image_url,
        "document_type": "wikimedia_commons",
        "categories": [category],
        "source": {
            "provider": "Wikimedia Commons",
            "repository": "commons.wikimedia.org"
        },
        "retrieved_date": datetime.today().strftime('%Y-%m-%d'),
        "additional_info": {
            "resolution": f"{image_info['imageinfo'][0]['width']}x{image_info['imageinfo'][0]['height']}",
            "format": image_info['imageinfo'][0]['mime']
        }
    }

    # Save metadata
    metadata_path = os.path.join(category_dir, f"{base_name}.json")
    with open(metadata_path, 'w') as json_file:
        json.dump(metadata, json_file, indent=4)

    logging.info(f"Downloaded and saved: {title_no_prefix}")

    return True

def download_wikimedia_images(categories, max_images_per_category, output_dir):
    logging.info("Starting Wikimedia Commons image retrieval...")
    os.makedirs(output_dir, exist_ok=True)

    for category in categories:
        logging.info(f"Processing category: {category}")
        images = search_images(category, limit=max_images_per_category)
        downloaded = 0

        for image_info in images:
            try:
                success = download_image(image_info, category, output_dir)
                if success:
                    downloaded += 1
                    logging.info(f"Downloaded and saved metadata: {image_info['title']}")
                if downloaded >= max_images_per_category:
                    break
            except Exception as e:
                logging.error(f"Error downloading {image_info['title']}: {e}")

        logging.info(f"Finished category '{category}': downloaded {downloaded} images.")

    logging.info("Completed Wikimedia Commons image retrieval.")
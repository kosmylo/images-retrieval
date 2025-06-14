import os
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFile
from io import BytesIO
from datetime import datetime
from tqdm import tqdm
import logging

# Allow truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Headers compliant with Wikipedia policy
headers = {
    "User-Agent": "mAiEnergyBot/1.0 (kosmylo@gmail.com; downloading images from Wikipedia for research project)"
}

def read_wiki_json(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def get_article_images_with_captions(article_url):
    response = requests.get(article_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    images_data = []

    # Extract images within figures or divs with captions
    for figure in soup.select('.mw-parser-output figure, .mw-parser-output div.thumb'):
        img_tag = figure.find('img')
        if not img_tag:
            continue

        # Get complete image URL
        img_src = img_tag.get('src')
        if not img_src:
            continue

        if img_src.startswith("//"):
            img_url = "https:" + img_src
        elif img_src.startswith("/"):
            img_url = "https://en.wikipedia.org" + img_src
        else:
            img_url = img_src

        # Get caption
        caption_tag = figure.find('figcaption') or figure.find('div', class_='thumbcaption')
        caption = caption_tag.get_text(strip=True) if caption_tag else ""

        images_data.append({"img_url": img_url, "caption": caption})

    return images_data

def download_image(img_url):
    response = requests.get(img_url, headers=headers)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))
    return img

def save_image_and_metadata(article_title, img, img_url, caption, output_dir):
    sanitized_title = article_title.replace(' ', '_').replace('/', '_')
    img_name = os.path.basename(img_url.split("?")[0])
    base_name, ext = os.path.splitext(img_name)

    # Ensure unique filename
    filename = f"{sanitized_title}_{base_name}{ext}"
    img_path = os.path.join(output_dir, filename)

    # Save image
    img.save(img_path)

    # Create metadata
    width, height = img.size
    metadata = {
        "filename": filename,
        "article_title": article_title,
        "image_url": img_url,
        "caption": caption,
        "retrieved_date": datetime.today().strftime('%Y-%m-%d'),
        "additional_info": {
            "resolution": f"{width}x{height}px",
            "image_format": img.format
        },
        "source": {
            "provider": "Wikipedia",
            "repository": "en.wikipedia.org"
        }
    }

    # Save metadata JSON
    metadata_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
    with open(metadata_path, 'w', encoding='utf-8') as meta_file:
        json.dump(metadata, meta_file, indent=4)

def download_wikipedia_images(input_file, output_dir):
    logging.info(f"Starting Wikipedia images retrieval from: {input_file}")

    os.makedirs(output_dir, exist_ok=True)
    articles = read_wiki_json(input_file)

    for article in tqdm(articles, desc="Processing Wikipedia articles"):
        title = article.get("title")
        url = article.get("url")

        try:
            images_data = get_article_images_with_captions(url)
            for img_data in images_data:
                img_url = img_data["img_url"]
                caption = img_data["caption"]

                try:
                    img = download_image(img_url)
                    save_image_and_metadata(title, img, img_url, caption, output_dir)
                    logging.info(f"Downloaded and saved image from '{title}'")
                except Exception as e:
                    logging.error(f"Failed to download/save image {img_url}: {e}")

        except Exception as e:
            logging.error(f"Failed to process article '{title}' ({url}): {e}")

    logging.info("Completed Wikipedia image retrieval.")
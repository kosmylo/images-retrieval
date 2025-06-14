import requests
import os
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from PIL import Image, ImageFile
from io import BytesIO
import feedparser
import logging

# Allow truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# RSS feeds to parse recent images
RSS_FEEDS = [
    "https://earthobservatory.nasa.gov/feeds/image-of-the-day.rss",
    "https://earthobservatory.nasa.gov/feeds/natural-hazards.rss",
    "https://earthobservatory.nasa.gov/feeds/earth-observatory.rss"
]

TOPICS = {"heat", "atmosphere", "land"}
CUTOFF_DATE = datetime.today() - timedelta(days=10*365)

headers = {
    "User-Agent": "mAiEnergyBot/1.0 (kosmylo@gmail.com; downloading NASA Earth Observatory images for research)"
}

def download_nasa_image(entry_url, topics, cutoff_date, output_dir):
    response = requests.get(entry_url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to access {entry_url}: HTTP {response.status_code}")
        return False

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract title
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "untitled"

    # Extract publication date
    pub_date_tag = soup.find(lambda tag: tag.name == "p" and "Published" in tag.text)
    if pub_date_tag:
        pub_date_str = pub_date_tag.text.replace("Published", "").strip()
        pub_date = datetime.strptime(pub_date_str, "%b %d, %Y")
        if pub_date < cutoff_date:
            logging.info(f"Skipping {title}: older than cutoff date.")
            return False
    else:
        pub_date = datetime.today()

    # Extract categories
    categories = set()
    for cat_tag in soup.find_all("a", href=lambda h: h and '/topic/' in h):
        cat_text = cat_tag.text.strip().lower()
        if cat_text in topics:
            categories.add(cat_text)

    if not categories:
        logging.info(f"Skipping {title}: does not match topics.")
        return False

    # Find high-res image link
    image_link_tag = soup.find("a", string=["JPEG", "PNG"])
    if not image_link_tag:
        logging.warning(f"No high-res image found for {title}")
        return False

    image_url = image_link_tag['href']
    img_response = requests.get(image_url, headers=headers)
    if img_response.status_code != 200:
        logging.error(f"Failed to download image for {title}")
        return False

    image_format = image_url.split(".")[-1]
    image = Image.open(BytesIO(img_response.content))
    resolution = f"{image.width}x{image.height}"

    # Prepare directories
    topic_dir = os.path.join(output_dir, "_".join(sorted(categories)))
    os.makedirs(topic_dir, exist_ok=True)

    # Save image
    image_file_name = f"{title.replace(' ', '_').replace('/', '_')}.{image_format}"
    image_path = os.path.join(topic_dir, image_file_name)
    image.save(image_path)

    # Extract caption
    caption_tag = soup.find("img", alt=True)
    caption = caption_tag["alt"] if caption_tag else ""

    # Metadata structure
    metadata = {
        "title": title,
        "url": image_url,
        "document_type": "nasa_earth_observatory_image",
        "categories": list(categories),
        "source": {
            "provider": "NASA",
            "repository": "earthobservatory.nasa.gov"
        },
        "retrieved_date": datetime.today().strftime('%Y-%m-%d'),
        "additional_info": {
            "resolution": resolution,
            "format": image_format,
            "caption": caption,
            "article_url": entry_url
        }
    }

    # Save metadata
    metadata_file_name = image_file_name.rsplit(".", 1)[0] + ".json"
    metadata_path = os.path.join(topic_dir, metadata_file_name)
    with open(metadata_path, 'w') as json_file:
        json.dump(metadata, json_file, indent=4)

    logging.info(f"Downloaded and saved: {title}")
    return True

def download_nasa_images(max_images, output_dir):
    collected_images = 0
    visited_links = set()

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if collected_images >= max_images:
                break
            entry_link = entry.link
            if entry_link not in visited_links:
                visited_links.add(entry_link)
                success = download_nasa_image(entry_link, TOPICS, CUTOFF_DATE, output_dir)
                if success:
                    collected_images += 1

        if collected_images >= max_images:
            break

    logging.info(f"Completed downloading {collected_images} NASA Earth Observatory images.")
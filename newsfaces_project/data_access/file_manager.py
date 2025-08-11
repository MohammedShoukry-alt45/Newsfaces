# data_access/file_manager.py
import os
import json
import logging
import requests
from urllib.parse import urlparse
from config import settings

class FileManager:
    def __init__(self):
        pass

    def save_html(self, html_content, html_filename):
        html_path = os.path.join(settings.HTML_SAVE_PATH, html_filename)
        with open(html_path, "wb") as f:
            f.write(html_content)
        logging.info(f"Saved HTML: {html_path}")
        return html_path

    def download_images(self, image_urls, html_base_name):
        saved_images = []
        count = 0
        for img_url in image_urls:
            if count >= settings.MAX_IMAGES_PER_PAGE:
                break
            try:
                response = requests.get(img_url, timeout=settings.IMAGE_DOWNLOAD_TIMEOUT)
                if response.status_code == 200:
                    img_name = os.path.basename(urlparse(img_url).path) or f"image_{count}.jpg"
                    img_path = os.path.join(settings.IMAGES_SAVE_PATH, f"{html_base_name}_{img_name}")
                    with open(img_path, "wb") as f:
                        f.write(response.content)
                    saved_images.append(img_path)
                    logging.info(f"Downloaded image: {img_path}")
                    count += 1
            except Exception as e:
                logging.warning(f"Error downloading image {img_url}: {e}")
        return saved_images

    def save_mappings(self, mappings_data):
        mapping_file = os.path.join(settings.EXTRACTED_DATA_PATH, "mappings.json")
        with open(mapping_file, "w") as f:
            json.dump(mappings_data, f, indent=2)
        logging.info(f"Saved mappings.json with {len(mappings_data)} entries.")

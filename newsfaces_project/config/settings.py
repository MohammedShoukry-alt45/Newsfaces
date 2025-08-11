# config/settings.py
import os
# ==== Limits ====
MAX_WARC_FILES =10    # stop after this many WARC files
MAX_HTML_PAGES = 12       # stop after this many HTML pages total
MAX_IMAGES_PER_PAGE = 5   # max images to download from one HTML
IMAGE_DOWNLOAD_TIMEOUT = 5  # seconds
MAX_PEOPLE = 10

# ==== Paths ====
BASE_DATA_PATH = "data"

EXTRACTED_DATA_PATH = os.path.join(BASE_DATA_PATH, "extracted_data")
HTML_SAVE_PATH = os.path.join(EXTRACTED_DATA_PATH, "html")
IMAGES_SAVE_PATH = os.path.join(EXTRACTED_DATA_PATH, "images")
DATABASE_PATH = os.path.join(BASE_DATA_PATH, "database", "bibliotheca_alexandrina.db")
LFW_DATASET_PATH = os.path.join(BASE_DATA_PATH, "datasets", "lfw")
WARC_FILES_PATH = os.path.join(BASE_DATA_PATH, "warc_files")

DB_PATH = DATABASE_PATH

# ==== Common Crawl index ====
COMMON_CRAWL_INDEX = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2023-14/warc.paths.gz"

# ==== Ensure required directories exist ====
for path in [HTML_SAVE_PATH, IMAGES_SAVE_PATH, os.path.dirname(DATABASE_PATH), LFW_DATASET_PATH, WARC_FILES_PATH]:
    os.makedirs(path, exist_ok=True)

# Download WARC files
# data_access/warc_downloader.py
import os
import requests
import gzip
from config import settings


class WARCDownloader:
    def __init__(self, download_dir=settings.EXTRACTED_DATA_PATH):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    def download_and_get_warc_paths(self):
        warc_paths_file = os.path.join(self.download_dir, "warc.paths.gz")

        # Download warc.paths.gz
        if not os.path.exists(warc_paths_file):
            print(f"Downloading WARC paths from {settings.COMMON_CRAWL_INDEX}")
            response = requests.get(settings.COMMON_CRAWL_INDEX, stream=True)
            with open(warc_paths_file, "wb") as f:
                f.write(response.content)

        # Extract first N warc file paths
        warc_urls = []
        with gzip.open(warc_paths_file, "rt") as f:
            for i, line in enumerate(f):
                if i >= settings.MAX_WARC_FILES:
                    break
                warc_urls.append(f"https://data.commoncrawl.org/{line.strip()}")

        return warc_urls

    def download_warc_file(self, warc_url):
        local_filename = os.path.join(self.download_dir, os.path.basename(warc_url))
        if not os.path.exists(local_filename):
            print(f"Downloading WARC file: {warc_url}")
            response = requests.get(warc_url, stream=True)
            with open(local_filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename


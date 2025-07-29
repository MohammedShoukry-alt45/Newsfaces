import subprocess
import sys

def install_requirements():
    """Install all required packages for the project"""
    packages = [
        'warcio',
        'requests',
        'beautifulsoup4',
        'face_recognition',
        'opencv-python',
        'dlib',
        'spacy',
        'transformers',
        'streamlit',
        'SQLAlchemy',
        'keybert',
        'textstat',
        'nltk',
        'pillow'
    ]

    print("Installing required packages...")
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    # Download spaCy model
    print("Downloading spaCy English model...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

    print("\nAll packages installed successfully!")

    #  installation
    print("\n installations:")
    installed_packages = subprocess.check_output([sys.executable, "-m", "pip", "list"]).decode()
    print(installed_packages)

if __name__ == "__main__":
    install_requirements()

import os
import hashlib
import json
import gzip
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
import logging
from datetime import datetime

#  logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CommonCrawlWARCParser:
    def __init__(self, output_dir="extracted_data"):
        """
        Initialize WARC Parser for Common Crawl data

        Args:
            output_dir (str): Directory to store extracted content
        """
        self.output_dir = Path(output_dir)
        self.html_dir = self.output_dir / "html"
        self.images_dir = self.output_dir / "images"
        self.mappings_file = self.output_dir / "mappings.json"

        # Create output directories
        self.html_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Mapping between WARC records, HTML files, and images
        self.mappings = []

    def download_and_get_warc_paths(self, num_files=1):

        ##Download WARC paths file and get list of WARC files



        logger.info("Downloading WARC paths from Common Crawl...")

        # Download the paths file
        paths_url = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-26/warc.paths.gz"
        paths_file = "warc.paths.gz"

        response = requests.get(paths_url, stream=True)
        with open(paths_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Read and extract paths
        with gzip.open(paths_file, 'rt') as f:
            warc_paths = [line.strip() for line in f.readlines()[:num_files]]

        # Convert to full URLs
        warc_urls = ["https://data.commoncrawl.org/" + path for path in warc_paths]

        logger.info(f"Found {len(warc_urls)} WARC files to process")
        for i, url in enumerate(warc_urls):
            logger.info(f"WARC {i+1}: {url}")

        return warc_urls

    def download_warc_file(self, warc_url):

        ##Download a WARC file from URL


        filename = warc_url.split('/')[-1]
        local_path = self.output_dir / filename

        logger.info(f"Downloading WARC file: {filename}")

        # Download with progress
        response = requests.get(warc_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(local_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) == 0:  # Log every MB
                            logger.info(f"Downloaded {percent:.1f}% ({downloaded / (1024*1024):.1f} MB)")

        logger.info(f"Download complete: {local_path}")
        return str(local_path)

    def parse_warc_file(self, warc_path):

        ##Parse a WARC file and extract HTML content and image URLs

        logger.info(f"Starting to parse WARC file: {warc_path}")

        record_count = 0
        html_count = 0

        try:
            # Handle normal and gzipped WARC files
            if warc_path.endswith('.gz'):
                file_obj = gzip.open(warc_path, 'rb')
            else:
                file_obj = open(warc_path, 'rb')

            with file_obj as stream:
                for record in ArchiveIterator(stream):
                    record_count += 1

                    # test if this is an HTML response record
                    if record.rec_type == 'response':
                        content_type = record.http_headers.get_header('Content-Type', '') if record.http_headers else ''

                        if 'text/html' in content_type:
                            html_count += 1
                            self._process_html_record(record)

                    # Log progress every 1000 records
                    if record_count % 1000 == 0:
                        logger.info(f"Processed {record_count} records, found {html_count} HTML pages")

                    # for test at first
                    if html_count >= 10:  # Process only first 10 HTML pages for testing
                        logger.info("Reached testing limit of 10 HTML pages")
                        break

        except Exception as e:
            logger.error(f"Error reading WARC file: {e}")
            return 0, 0

        # Save to file
        self._save_mappings()

        logger.info(f"Parsing complete! Processed {record_count} records, extracted {html_count} HTML pages")
        return record_count, html_count

    def _process_html_record(self, record):

        ##Process an HTML record: extract content and identify images


        try:
            # Get record metadata
            record_id = record.rec_headers.get_header('WARC-Record-ID')
            target_uri = record.rec_headers.get_header('WARC-Target-URI')
            date = record.rec_headers.get_header('WARC-Date')

            # Get HTML content
            html_content = record.content_stream().read()

            # Skip if content is empty
            if not html_content:
                return

            # Generate unique filename for HTML
            html_hash = hashlib.md5(html_content).hexdigest()
            html_filename = f"{html_hash}.html"
            html_path = self.html_dir / html_filename

            # Save HTML content
            with open(html_path, 'wb') as f:
                f.write(html_content)

            # Parse HTML to extract image URLs
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                image_urls = self._extract_image_urls(soup, target_uri)
            except Exception as e:
                logger.warning(f"Error parsing HTML from {target_uri}: {e}")
                image_urls = []

            # Download images (limit to first 5 for testing)
            limited_urls = image_urls[:5] if image_urls else []
            downloaded_images = self._download_images(limited_urls, html_hash)

            # Create mapping entry
            mapping = {
                'record_id': record_id,
                'target_uri': target_uri,
                'date': date,
                'html_file': html_filename,
                'html_path': str(html_path),
                'image_urls': image_urls,
                'downloaded_images': downloaded_images,
                'extraction_time': datetime.now().isoformat()
            }

            self.mappings.append(mapping)
            logger.info(f"Processed HTML from {target_uri}, found {len(image_urls)} images, downloaded {len(downloaded_images)}")

        except Exception as e:
            logger.error(f"Error processing HTML record: {e}")

    def _extract_image_urls(self, soup, base_url):

        ##Extract all image URLs from HTML content


        image_urls = []

        if not base_url:
            return image_urls

        # search for tags of imageh
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                try:
                    # relative URLs to absolute
                    absolute_url = urljoin(base_url, src)
                    image_urls.append(absolute_url)
                except Exception:
                    continue

        #  search for images in link tags
        for link in soup.find_all('link'):
            if link.get('type', '').startswith('image/'):
                href = link.get('href')
                if href:
                    try:
                        absolute_url = urljoin(base_url, href)
                        image_urls.append(absolute_url)
                    except Exception:
                        continue

        # Remove duplicates
        seen = set()
        unique_urls = []
        for url in image_urls:
            if url not in seen and self._is_valid_image_url(url):
                seen.add(url)
                unique_urls.append(url)

        return unique_urls

    def _is_valid_image_url(self, url):
        """Check if URL appears to be a valid image URL"""
        if not url or url.startswith('data:'):
            return False

        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
        except Exception:
            return False

        return True

    def _download_images(self, image_urls, html_hash):
        ##Download images from URLs

        downloaded_images = []

        for idx, url in enumerate(image_urls):
            try:
                # timeout
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

                if response.status_code == 200 and response.content:
                    # Check if content is actually an image
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        continue

                    # Determine file extension
                    ext = self._get_image_extension(content_type, url)

                    # Generate filename
                    image_hash = hashlib.md5(response.content).hexdigest()
                    filename = f"{html_hash}_{idx}_{image_hash}{ext}"
                    filepath = self.images_dir / filename

                    # Save image
                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    downloaded_images.append({
                        'filename': filename,
                        'filepath': str(filepath),
                        'url': url,
                        'size': len(response.content)
                    })

                    logger.debug(f"Downloaded image: {filename}")

            except Exception as e:
                logger.warning(f"Failed to download image {url}: {e}")

        return downloaded_images

    def _get_image_extension(self, content_type, url):
        #Returns File extension
        # Map content types to extensions
        type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'image/bmp': '.bmp'
        }

        # Check content type first
        for mime_type, ext in type_map.items():
            if mime_type in content_type:
                return ext

        # Fall back to URL extension
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']:
                if path.endswith(ext):
                    return ext
        except Exception:
            pass

        # Default to .jpg
        return '.jpg'

    def _save_mappings(self):
        """Save mappings to JSON file"""
        with open(self.mappings_file, 'w') as f:
            json.dump(self.mappings, f, indent=2)
        logger.info(f"Saved mappings to {self.mappings_file}")

    def get_statistics(self):
        """Get parsing statistics"""
        total_images = sum(len(m['downloaded_images']) for m in self.mappings)
        return {
            'total_records': len(self.mappings),
            'total_images_found': sum(len(m['image_urls']) for m in self.mappings),
            'total_images_downloaded': total_images,
            'output_directory': str(self.output_dir)
        }

    def process_common_crawl(self, num_warc_files=1):

        ##Complete workflow: download paths, download WARC files, and process them


        # Get WARC file URLs
        warc_urls = self.download_and_get_warc_paths(num_warc_files)

        total_records = 0
        total_html = 0

        for warc_url in warc_urls:
            # Download WARC file
            warc_path = self.download_warc_file(warc_url)

            # Process WARC file
            records, html_count = self.parse_warc_file(warc_path)
            total_records += records
            total_html += html_count

            # Clean up downloaded WARC file to save space (optional)
            # os.remove(warc_path)

        logger.info(f"Processing complete! Total records: {total_records}, Total HTML pages: {total_html}")
        return total_records, total_html

def main():
    #test phase 1

    # Step 1: Create the parser
    parser = CommonCrawlWARCParser()

    # Step 2: Process the data
    print(" process web data")
    parser.process_common_crawl(num_warc_files=1)

    # Step 3: Get the results
    stats = parser.get_statistics()

    # Step 4: Show simple results
    print("\n" + "="*40)
    print(" RESULTS:")
    print("="*40)
    print(f"Web pages found: {stats['total_records']}")
    print(f"Images found: {stats['total_images_found']}")
    print(f"Images saved: {stats['total_images_downloaded']}")

    # Step 5: Show clickable links to files
    print("\n CLICK THESE LINKS")
    print("-" * 40)

    # Get the folder paths
    html_folder = parser.html_dir.resolve()
    images_folder = parser.images_dir.resolve()

    # Show folder links
    print(f" HTML files: file://{html_folder}")
    print(f"  Images: file://{images_folder}")

    # Show individual image links
    print(f"\n  Your downloaded images:")
    image_count = 0
    for page in parser.mappings:
        for image in page['downloaded_images']:
            if image_count < 40:  # Show first 40 images
                image_path = images_folder / image['filename']
                print(f"    file://{image_path}")
                image_count += 1

    if image_count == 0:
        print("   No images were downloaded")
    elif stats['total_images_downloaded'] > 10:
        remaining = stats['total_images_downloaded'] - 10
        print(f"   ... and {remaining} more images in the folder")

    print("="*40)


if __name__ == "__main__":
    main()

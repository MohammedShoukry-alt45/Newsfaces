# services/warc_service.py
import os
import logging
from urllib.parse import urlparse
from warcio.archiveiterator import ArchiveIterator
from warcio.exceptions import ArchiveLoadFailed
from data_access.warc_downloader import WARCDownloader
from core.warc_processing import extract_image_urls
from data_access.file_manager import FileManager
from config import settings

class WARCService:
    def __init__(self):
        self.downloader = WARCDownloader()
        self.file_manager = FileManager()
        self.mappings = []

    def process_warc_files(self):
        logging.info("=== Starting Phase 1: WARC processing ===")
        warc_urls = self.downloader.download_and_get_warc_paths()

        html_count = 0
        warc_count = 0
        total_warc_files = min(len(warc_urls), settings.MAX_WARC_FILES)

        for idx, warc_url in enumerate(warc_urls, start=1):
            if warc_count >= settings.MAX_WARC_FILES:
                break

            local_file = self.downloader.download_warc_file(warc_url)
            warc_count += 1

            logging.info(f"[{idx}/{total_warc_files}] Processing WARC file: {os.path.basename(local_file)}")

            try:
                with open(local_file, "rb") as stream:
                    for record in ArchiveIterator(stream):
                        if html_count >= settings.MAX_HTML_PAGES:
                            break
                        if (
                            record.rec_type == "response"
                            and "text/html" in record.http_headers.get_header("Content-Type", "")
                        ):
                            url = record.rec_headers.get_header("WARC-Target-URI")
                            html_content = record.content_stream().read()

                            html_filename = os.path.basename(urlparse(url).path) or f"page_{html_count}.html"
                            html_path = self.file_manager.save_html(html_content, html_filename)

                            image_urls = extract_image_urls(html_content, url)
                            saved_images = self.file_manager.download_images(
                                image_urls,
                                os.path.splitext(html_filename)[0]
                            )

                            # Store paths in js
                            self.mappings.append({
                                "url": url,
                                "html_path": os.path.relpath(html_path, start=settings.BASE_DATA_PATH),
                                "images": [os.path.relpath(img, start=settings.BASE_DATA_PATH) for img in saved_images]
                            })

                            html_count += 1
            except ArchiveLoadFailed as e:
                logging.warning(f"Skipping file {os.path.basename(local_file)} - not a valid WARC: {e}")
                continue
            except Exception as e:
                logging.error(f"Error processing {os.path.basename(local_file)}: {e}", exc_info=True)
                continue

        self.file_manager.save_mappings(self.mappings)
        logging.info(f"=== Phase 1 complete: {len(self.mappings)} HTML pages processed ===")
        return self.mappings

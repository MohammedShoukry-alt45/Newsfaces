import os
import json
import logging
from core.text_processing import TextMetadataExtractor
from data_access.database import DatabaseManager
from config import settings

logger = logging.getLogger(__name__)


class TextService:
    def __init__(self):
        self.extractor = TextMetadataExtractor()
        self.db = DatabaseManager()

    def process_html_files(self):
        logging.info("=== Starting Phase 2: Text metadata extraction ===")
        mappings_file = os.path.join(settings.EXTRACTED_DATA_PATH, "mappings.json")

        if not os.path.exists(mappings_file):
            logging.error("No mappings.json found. Run Phase 1 first.")
            return

        with open(mappings_file, "r", encoding="utf-8") as f:
            mappings = json.load(f)

        logging.info(f"Processing {len(mappings)} HTML files from mappings.json")
        processed = 0

        for idx, mapping in enumerate(mappings, start=1):
            html_path = os.path.join(settings.BASE_DATA_PATH, mapping.get("html_path", ""))
            if not os.path.exists(html_path):
                logging.warning(f"[{idx}] HTML file not found: {html_path}")
                continue

            try:
                with open(html_path, "rb") as fh:
                    html_content = fh.read()
            except Exception as e:
                logging.warning(f"[{idx}] Error reading HTML file {html_path}: {e}")
                continue

            meta = {"target_uri": mapping.get("url") or mapping.get("target_uri")}
            article_data = self.extractor.process_text_metadata(html_content, meta)

            article_id = self.db.insert_article(article_data)
            if article_id:
                for img_rel in mapping.get("images", []):
                    img_full = os.path.join(settings.BASE_DATA_PATH, img_rel)
                    self.db.insert_image(article_id, img_full)

                processed += 1
                logging.info(f"[{idx}] Stored article_id={article_id} title={article_data['title'][:80]} images={len(mapping.get('images', []))}")
            else:
                logging.error(f"[{idx}] Failed to store article for {meta.get('target_uri')}")

        logging.info(f"=== Phase 2 complete: {processed} articles processed ===")

# main.py
from phases.phase1 import run_phase1
from phases.phase2 import run_phase2
from phases.phase3 import run_phase3
from data_access.database import DatabaseManager
from utils.logging_utils import setup_logging
import logging

if __name__ == "__main__":
    setup_logging()
    logging.info("=== Starting NewsFaces Pipeline ===")

    run_phase1()
    run_phase2()
    run_phase3()

    db = DatabaseManager()
    logging.info("=== Final Database Statistics ===")
    logging.info(f"Articles stored: {db.get_article_count()}")
    logging.info(f"Images stored: {db.get_image_count()}")
    logging.info(f"Known faces stored: {db.get_known_faces_count()}")

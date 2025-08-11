# Logging helpers
# utils/logging_utils.py
import logging
import os

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    log_file = os.path.join("logs", "newsfaces.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


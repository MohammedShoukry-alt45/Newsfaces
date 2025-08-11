# services/face_service.py
import os
import zipfile
import logging
import json
from datetime import datetime
from core.face_processing import FaceProcessor
from data_access.database import DatabaseManager
from config import settings

class FaceService:
    def __init__(self):
        self.processor = FaceProcessor()
        self.db = DatabaseManager()

    # Extract any LFW zip found in datasets dir if not yet extr
    def _extract_lfw_zip_if_needed(self):

        if os.path.exists(settings.LFW_DATASET_PATH) and any(os.scandir(settings.LFW_DATASET_PATH)):
            logging.info("LFW dataset already extracted.")
            return

        datasets_dir = os.path.dirname(settings.LFW_DATASET_PATH)
        for file in os.listdir(datasets_dir):
            if file.lower().endswith(".zip"):
                zip_path = os.path.join(datasets_dir, file)
                logging.info(f"Extracting LFW dataset from {zip_path} ...")
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(settings.LFW_DATASET_PATH)
                logging.info("LFW dataset extraction complete.")
                return

    # Returns the folder that contains the person subdirectories.
    def _find_people_root(self):
        root = settings.LFW_DATASET_PATH
        while True:
            subdirs = [
                os.path.join(root, d) for d in os.listdir(root)
                if os.path.isdir(os.path.join(root, d))
            ]
            if len(subdirs) == 1 and not subdirs[0].lower().endswith(('.jpg', '.jpeg', '.png')):
                root = subdirs[0]
            else:
                break

        return root

    def enroll_faces(self):
        logging.info("=== Phase 3: Enrolling faces from LFW dataset ===")

        self._extract_lfw_zip_if_needed()

        people_root = self._find_people_root()
        if not os.path.exists(people_root):
            logging.error("LFW dataset not found after extraction.")
            return

        people = sorted([
            d for d in os.listdir(people_root)
            if os.path.isdir(os.path.join(people_root, d))
        ])[:settings.MAX_PEOPLE]

        logging.info(f"Found {len(people)} people in LFW dataset.")

        enrolled_count = 0
        failed_count = 0

        for person in people:
            person_dir = os.path.join(people_root, person)
            image_files = []
            for root, _, files in os.walk(person_dir):
                for file in files:
                    if file.lower().endswith((".jpg", ".jpeg", ".png")):
                        image_files.append(os.path.join(root, file))

            if not image_files:
                logging.warning(f"No images found for {person}")
                continue

            person_encodings = []
            for img_path in image_files:
                encoding = self.processor.get_face_encoding(img_path)
                if encoding is not None:
                    #  to ens Store one encoding at a time
                    self.db.insert_face_encoding(person.replace("_", " "), encoding)
                    person_encodings.append(encoding)

            if person_encodings:
                enrolled_count += 1
                logging.info(f"✓ Enrolled {person} with {len(person_encodings)} encodings")
            else:
                failed_count += 1
                logging.warning(f"✗ No valid encodings found for {person}")

        logging.info("=" * 50)
        logging.info(f"Enrollment complete: {enrolled_count} people enrolled, {failed_count} failed.")
        logging.info("=" * 50)

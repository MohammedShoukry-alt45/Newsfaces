# phases/phase1.py
import logging
from services.warc_service import WARCService

def run_phase1():
    print("=== Phase 1: Downloading and extracting HTML + images ===")
    service = WARCService()
    mappings = service.process_warc_files()
    print(f"Phase 1 complete. {len(mappings)} pages processed.")

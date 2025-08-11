# Phase 2 workflow
# phases/phase2.py
from services.text_service import TextService

def run_phase2():
    print("=== Phase 2: Processing text metadata ===")
    service = TextService()
    service.process_html_files()

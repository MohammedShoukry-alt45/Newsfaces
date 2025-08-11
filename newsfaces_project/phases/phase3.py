# Phase 3 workflow
# phases/phase3.py
from services.face_service import FaceService

def run_phase3():
    print("=== Phase 3: Enrolling faces from LFW dataset ===")
    service = FaceService()
    service.enroll_faces()


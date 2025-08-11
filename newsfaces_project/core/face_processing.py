# core/face_processing.py
import face_recognition
import numpy as np

class FaceProcessor:
    def __init__(self):
        pass

    # create encode for image after laod of img
    def get_face_encoding(self, image_path):

        try:
            image = face_recognition.load_image_file(image_path)

            # First detect all face locations
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                return None

            # Encode faces using the detected locations
            encodings = face_recognition.face_encodings(image, face_locations)

            if len(encodings) > 0:
                # Convert numpy array to list for JSON storage
                return encodings[0].tolist()

            return None
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None



import cv2
import dlib
from scipy.spatial import distance

def eye_aspect_ratio(eye):
    # Compute EAR: (vertical distances / horizontal distance)
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def detect_drowsiness(frame, detector, predictor):
    # Grayscale conversion
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect face
    faces = detector(gray)
    for face in faces:
        landmarks = predictor(gray, face)
        left_eye = [landmarks.part(i) for i in range(36, 42)]
        right_eye = [landmarks.part(i) for i in range(42, 48)]
        
        # Compute EAR
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0
        
        # EAR threshold (adjust as needed)
        if ear < 0.25:
            return "Drowsy"
    return "Alert"

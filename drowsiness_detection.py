import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Load the trained model
model = load_model("Drowsiness_CNN_Model.keras")

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Drowsiness thresholds
EAR_THRESHOLD = 0.20
MAR_THRESHOLD = 0.6
FRAME_THRESHOLD = 10
HEAD_TILT_THRESHOLD = 30  # Degrees
HEAD_FALL_THRESHOLD = 40  # Pixels

drowsy_frame_count = 0
prev_nose_y = None  # To track head fall

def calculate_ear(landmarks, eye_idx):
    A = np.linalg.norm(np.array(landmarks[eye_idx[1]]) - np.array(landmarks[eye_idx[5]]))
    B = np.linalg.norm(np.array(landmarks[eye_idx[2]]) - np.array(landmarks[eye_idx[4]]))
    C = np.linalg.norm(np.array(landmarks[eye_idx[0]]) - np.array(landmarks[eye_idx[3]]))
    return (A + B) / (2.0 * C)

def calculate_mar(landmarks, mouth_idx):
    A = np.linalg.norm(np.array(landmarks[mouth_idx[1]]) - np.array(landmarks[mouth_idx[5]]))
    B = np.linalg.norm(np.array(landmarks[mouth_idx[2]]) - np.array(landmarks[mouth_idx[4]]))
    C = np.linalg.norm(np.array(landmarks[mouth_idx[0]]) - np.array(landmarks[mouth_idx[3]]))
    return (A + B) / (2.0 * C)

def detect_drowsiness(frame):
    global drowsy_frame_count, prev_nose_y
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = [(lm.x * frame.shape[1], lm.y * frame.shape[0]) for lm in face_landmarks.landmark]
            left_eye_idx = [33, 160, 158, 133, 153, 144]
            right_eye_idx = [362, 385, 387, 263, 373, 380]
            mouth_idx = [78, 81, 13, 311, 308, 14]
            nose_idx = 1  # Nose tip index
            
            EAR_left = calculate_ear(landmarks, left_eye_idx)
            EAR_right = calculate_ear(landmarks, right_eye_idx)
            EAR = (EAR_left + EAR_right) / 2.0
            MAR = calculate_mar(landmarks, mouth_idx)
            
            # Head tilt detection (angle between eyes)
            left_eye = landmarks[left_eye_idx[0]]
            right_eye = landmarks[right_eye_idx[0]]
            eye_vector = np.array(right_eye) - np.array(left_eye)
            head_tilt = np.arctan2(eye_vector[1], eye_vector[0]) * (180.0 / np.pi)
            
            # Head fall detection (nose movement)
            nose_y = landmarks[nose_idx][1]
            head_fall = False
            if prev_nose_y is not None and (prev_nose_y - nose_y) > HEAD_FALL_THRESHOLD:
                head_fall = True
            prev_nose_y = nose_y
            
            # Simulated real-world values
            speed = 60
            heart_rate = 59
            steering_tilt = 10
            
            if EAR < EAR_THRESHOLD or MAR > MAR_THRESHOLD or abs(head_tilt) > HEAD_TILT_THRESHOLD or head_fall:
                drowsy_frame_count += 1
            else:
                drowsy_frame_count = 0
            
            if drowsy_frame_count >= FRAME_THRESHOLD:
                return "Drowsy!", (0, 0, 255), EAR, MAR, speed, heart_rate, steering_tilt,
            
            input_data = np.array([[EAR, MAR, speed, heart_rate, steering_tilt]])
            prediction = model.predict(input_data)[0][0]
            
            if prediction > 0.5:
                return "Not Drowsy", (0, 255, 0), EAR, MAR, speed, heart_rate, steering_tilt
            else:
                return "Drowsy!", (0, 0, 255), EAR, MAR, speed, heart_rate, steering_tilt
    
    return "No Face Detected", (255, 255, 255), 0, 0, 0, 0, 0, 0, False

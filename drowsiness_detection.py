import cv2
import mediapipe as mp
import random
import time
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

# Load the trained model
model = load_model("Drowsiness_CNN_Model.keras")  # Ensure this file is in the same directory

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.7)

# Function to calculate Eye Aspect Ratio (EAR)
def calculate_ear(landmarks, left_eye_idx, right_eye_idx):
    left_eye_height = np.linalg.norm(np.array(landmarks[left_eye_idx[1]]) - np.array(landmarks[left_eye_idx[5]]))
    right_eye_height = np.linalg.norm(np.array(landmarks[right_eye_idx[1]]) - np.array(landmarks[right_eye_idx[5]]))
    eye_width = np.linalg.norm(np.array(landmarks[left_eye_idx[0]]) - np.array(landmarks[left_eye_idx[3]]))
    return (left_eye_height + right_eye_height) / (2.0 * eye_width)

# Function to calculate Mouth Aspect Ratio (MAR)
def calculate_mar(landmarks, mouth_idx):
    mouth_height = np.linalg.norm(np.array(landmarks[mouth_idx[1]]) - np.array(landmarks[mouth_idx[5]]))
    mouth_width = np.linalg.norm(np.array(landmarks[mouth_idx[0]]) - np.array(landmarks[mouth_idx[3]]))
    return mouth_height / mouth_width

# Function to detect drowsiness
def detect_drowsiness(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Extract facial landmarks
            landmarks = [(lm.x, lm.y) for lm in face_landmarks.landmark]

            # Define landmark indices
            left_eye_idx = [33, 160, 158, 133, 153, 144]
            right_eye_idx = [362, 385, 387, 263, 373, 380]
            mouth_idx = [61, 81, 311, 291, 178, 308]

            # Calculate EAR and MAR
            EAR = calculate_ear(landmarks, left_eye_idx, right_eye_idx)
            MAR = calculate_mar(landmarks, mouth_idx)
            # Generate random values for additional parameters
            #speed = random.randint(40, 120)  # Speed between 40-120 km/h
            speed=50
            #heart_rate = random.randint(60, 100)  # Heart rate between 60-100 bpm
            heart_rate=40
            #steering_tilt = random.uniform(-30, 80)  # Steering tilt between -30 to 80 degrees
            steering_tilt=11.7
            # Create input data and make prediction
            input_data = np.array([[EAR, MAR, speed, heart_rate, steering_tilt]])
            prediction = model.predict(input_data)[0][0]  
            # Determine drowsiness
            if prediction > 0.5:
                return "Not Drowsy", (0, 255, 0), EAR, MAR, speed, heart_rate, steering_tilt  # Green
            else:
                return "Drowsy!", (0, 0, 255), EAR, MAR, speed, heart_rate, steering_tilt  # Red
    # If no face is detected
    return "No Face Detected", (255, 255, 255), 0, 0, 0, 0, 0  # White

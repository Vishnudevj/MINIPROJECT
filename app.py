from flask import Flask, render_template, Response
import cv2
from utils.detection_utils import detect_drowsiness
import dlib
from playsound import playsound
import threading

app = Flask(__name__)

alert_playing = False  # Global flag to avoid multiple alerts playing at once

@app.route('/')
def index():
    return render_template('index.html')

def play_alert_sound():
    global alert_playing
    if not alert_playing:  # Ensure no overlapping alerts
        alert_playing = True
        try:
            playsound('static/alert.wav')  # Path to your alert sound file
        except Exception as e:
            print(f"Error playing sound: {e}")
        alert_playing = False

def video_stream():
    global alert_playing
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
    video = cv2.VideoCapture(0)

    if not video.isOpened():
        raise RuntimeError("Error: Could not open video source.")

    while True:
        ret, frame = video.read()
        if not ret:
            break

        try:
            # Detect drowsiness
            status = detect_drowsiness(frame, detector, predictor)

            # Display status on the frame
            color = (0, 255, 0) if status == "Alert" else (0, 0, 255)
            cv2.putText(
                frame,
                f"Status: {status}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                2
            )

            # Play alert sound if drowsy
            if status == "Drowsy" and not alert_playing:
                # Use a separate thread to play the sound
                threading.Thread(target=play_alert_sound).start()

        except Exception as e:
            print(f"Error in drowsiness detection: {e}")

        # Encode the frame as a JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame as part of the HTTP response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Release the video capture when done
    video.release()

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)

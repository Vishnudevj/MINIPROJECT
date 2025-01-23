from flask import Flask, render_template, Response
import cv2
from utils.detection_utils import detect_drowsiness
import dlib

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def video_stream():
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
            cv2.putText(
                frame,
                f"Status: {status}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )
        except Exception as e:
            print(f"Error in drowsiness detection: {e}")
            status = "Error"

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

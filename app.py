from flask import Flask, render_template, Response
import cv2
import drowsiness_detection  # Import our detection module

app = Flask(__name__)

def generate_frames():
    cap = cv2.VideoCapture(0)  # Open webcam inside the function

    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # Detect drowsiness and receive all values
        result = drowsiness_detection.detect_drowsiness(frame)

        # Unpack the returned values correctly
        if isinstance(result, tuple) and len(result) == 7:
            status, color, EAR, MAR, speed, heart_rate, steering_tilt = result
        else:
            # Default values if face isn't detected
            status, color = "No Face Detected", (255, 255, 255)
            EAR, MAR, speed, heart_rate, steering_tilt = 0, 0, 0, 0, 0

        # Display results on frame
        cv2.putText(frame, f"Status: {status}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"EAR: {EAR:.2f}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0, 255, 0), 2)
        cv2.putText(frame, f"MAR: {MAR:.2f}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0, 255, 0), 2)
        cv2.putText(frame, f"Speed: {speed} km/h", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0, 255, 0), 2)
        cv2.putText(frame, f"Heart Rate: {heart_rate} bpm", (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0, 255, 0), 2)
        cv2.putText(frame, f"Steering Tilt: {steering_tilt:.2f} deg", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Convert to JPEG format
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Stream frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()  # Release camera when function exits

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import cv2
import numpy as np
import os
import csv
import datetime
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'known_faces'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create folders if not exist
os.makedirs('known_faces', exist_ok=True)
os.makedirs('attendance', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# Global variables
camera = None
known_faces = []
known_names = []
attendance_marked = set()
is_running = False

# Create folders if not exist
os.makedirs('known_faces', exist_ok=True)
os.makedirs('attendance', exist_ok=True)

# Load Haar cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Simple face recognition using template matching (basic approach)
def load_known_faces():
    global known_faces, known_names
    known_faces = []
    known_names = []

    for filename in os.listdir('known_faces'):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            name = os.path.splitext(filename)[0]
            image = cv2.imread(f'known_faces/{filename}')
            if image is not None:
                # Convert to grayscale and resize for template matching
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (100, 100))
                known_faces.append(resized)
                known_names.append(name)
    print(f"Loaded {len(known_names)} known faces")

def recognize_face(face_image):
    """Simple face recognition using template matching"""
    if not known_faces:
        return "Unknown"

    # Resize input face to match template size
    face_resized = cv2.resize(face_image, (100, 100))

    best_match = "Unknown"
    best_score = 0.3  # Minimum threshold for match

    for i, known_face in enumerate(known_faces):
        # Use template matching
        result = cv2.matchTemplate(face_resized, known_face, cv2.TM_CCOEFF_NORMED)
        score = np.max(result)

        if score > best_score:
            best_score = score
            best_match = known_names[i]

    return best_match

load_known_faces()

# Generate frames for live video
def gen_frames():
    global camera, is_running, attendance_marked
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while is_running:
        success, frame = camera.read()
        if not success:
            break

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]

            # Recognize face
            name = recognize_face(face_roi)

            # Mark attendance only once
            if name != "Unknown" and name not in attendance_marked:
                mark_attendance(name)
                attendance_marked.add(name)

            # Draw rectangle and name
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    if camera is not None:
        camera.release()
        camera = None

def mark_attendance(name):
    today = datetime.date.today().strftime('%Y-%m-%d')
    filename = f'attendance/{today}.csv'
    
    fieldnames = ['Name', 'Time']
    
    # Create file if not exists
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    
    # Check if already marked today
    already_marked = False
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row and row[0] == name:
                    already_marked = True
                    break
    
    if not already_marked:
        with open(filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow({'Name': name, 'Time': current_time})
        print(f"Attendance marked for {name} at {current_time}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_attendance')
def start_attendance():
    global is_running, attendance_marked
    if not is_running:
        is_running = True
        attendance_marked = set()
        load_known_faces()  # reload in case new faces added
    return jsonify({"status": "started"})

@app.route('/stop_attendance')
def stop_attendance():
    global is_running
    is_running = False
    return jsonify({"status": "stopped", "present_count": len(attendance_marked)})

@app.route('/upload_student', methods=['POST'])
def upload_student():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    student_name = request.form.get('student_name', '').strip()
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not student_name:
        return jsonify({'error': 'Student name is required'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{student_name}.jpg")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Reload known faces after upload
        load_known_faces()
        
        return jsonify({'success': f'Student {student_name} added successfully!', 'filename': filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/get_students')
def get_students():
    students = []
    for filename in os.listdir('known_faces'):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            name = os.path.splitext(filename)[0]
            students.append({'name': name, 'filename': filename})
    return jsonify(students)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_student/<student_name>', methods=['DELETE'])
def delete_student(student_name):
    filename = f"{student_name}.jpg"
    file_path = os.path.join('known_faces', filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        load_known_faces()  # Reload faces after deletion
        return jsonify({'success': f'Student {student_name} deleted successfully!'})
    
    return jsonify({'error': 'Student not found'}), 404

@app.route('/present_students')
def present_students():
    today = datetime.date.today().strftime('%Y-%m-%d')
    filename = f'attendance/{today}.csv'
    
    students = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                students.append({"name": row['Name'], "time": row['Time']})
    
    return render_template('present.html', students=students, date=today)

if __name__ == '__main__':
    app.run(debug=True)
# Smart Attendance System 📊

A face recognition-based attendance system built with Flask and OpenCV.

## Project Structure

```
smart-attendance-system/
├── app.py                  # Main Flask backend with all logic
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── script.js      # Frontend logic
├── templates/
│   ├── index.html         # Dashboard + Start Attendance button
│   └── present.html       # Present students list
├── known_faces/           # Student photos (store as name.jpg)
├── attendance/            # CSV files with attendance records (auto-created)
└── README.md
```

## Installation

1. Clone or download this project
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Add student photos in the `known_faces/` folder
   - Name files as: `student_name.jpg`
   - Example: `Ali.jpg`, `Fatima.jpg`

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to: `http://localhost:5000`

4. Click "Start Attendance" to begin face recognition
5. View present students in the "Present Students" page

## Features

- Real-time face detection and recognition
- Automatic attendance tracking
- Student presence records saved as CSV
- Web-based dashboard

## Dependencies

- Flask: Web framework
- OpenCV: Computer vision
- face-recognition: Face detection & recognition
- Pillow: Image processing
- NumPy: Numerical computing

## Notes

- Make sure to have clear, well-lit photos of students in the `known_faces/` folder
- Attendance records are automatically saved in the `attendance/` folder
- CSV files are created with date stamps

---

Made with ❤️ for attendance management

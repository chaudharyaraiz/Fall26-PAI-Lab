let videoElement = document.getElementById('video');
let statusMessage = document.getElementById('statusMessage');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadStudents();
});

// Upload student photo
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const studentName = document.getElementById('studentName').value.trim();
    const fileInput = document.getElementById('studentPhoto');
    const file = fileInput.files[0];

    if (!studentName || !file) {
        alert('Please enter student name and select a photo!');
        return;
    }

    const formData = new FormData();
    formData.append('student_name', studentName);
    formData.append('file', file);

    fetch('/upload_student', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.success);
            document.getElementById('uploadForm').reset();
            loadStudents();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Upload failed!');
    });
});

function loadStudents() {
    fetch('/get_students')
    .then(response => response.json())
    .then(students => {
        const studentsList = document.getElementById('studentsList');
        studentsList.innerHTML = '';

        if (students.length === 0) {
            studentsList.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #ccc;">No students registered yet. Add students above.</p>';
            return;
        }

        students.forEach(student => {
            const studentCard = document.createElement('div');
            studentCard.className = 'student-card';
            studentCard.innerHTML = `
                <img src="/uploads/${student.filename}" alt="${student.name}" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiMzMzMzMzMiLz4KPHBhdGggZD0iTTMwIDMwSDUwVjUwSDB6IiBmaWxsPSIjNjY2Ii8+Cjwvc3ZnPgo='">
                <div class="name">${student.name}</div>
                <button class="delete-btn" onclick="deleteStudent('${student.name}')">×</button>
            `;
            studentsList.appendChild(studentCard);
        });
    })
    .catch(error => {
        console.error('Error loading students:', error);
    });
}

function deleteStudent(studentName) {
    if (confirm(`Are you sure you want to delete ${studentName}?`)) {
        fetch(`/delete_student/${studentName}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.success);
                loadStudents();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Delete failed!');
        });
    }
}

function startAttendance() {
    fetch('/start_attendance')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'started') {
            videoElement.style.display = 'block';
            statusMessage.style.display = 'none';
            videoElement.src = "/video_feed";
            alert("Attendance session started! Camera is live.");
        }
    })
    .catch(error => {
        console.error('Error starting attendance:', error);
        alert('Failed to start attendance!');
    });
}

function stopAttendance() {
    fetch('/stop_attendance')
    .then(response => response.json())
    .then(data => {
        videoElement.src = "";
        videoElement.style.display = 'none';
        statusMessage.style.display = 'block';
        alert(`Camera closed successfully. ${data.present_count} students marked present!`);
    })
    .catch(error => {
        console.error('Error stopping attendance:', error);
        alert('Failed to stop attendance!');
    });
}
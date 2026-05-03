let videoElement = document.getElementById('video');

function startAttendance() {
    videoElement.src = "/video_feed";
    fetch('/start_attendance');
    alert("Attendance session started! Camera is live.");
}

function stopAttendance() {
    fetch('/stop_attendance')
        .then(() => {
            videoElement.src = "";
            alert("Camera closed successfully. Attendance saved!");
        });
}
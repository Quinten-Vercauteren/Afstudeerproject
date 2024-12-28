function fetchPrinterStatus() {
    fetch('/octoprint_status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('printer-status').innerText = data.status;
        })
        .catch(error => console.error('Error fetching printer status:', error));
}

function fetchCameraState() {
    fetch('/camera_state')
        .then(response => response.json())
        .then(data => {
            const status = data.state === 'printing' ? 'Printing' : 'Inactive';
            document.getElementById('printer-status').innerText = status;
        })
        .catch(error => console.error('Error fetching camera state:', error));
}

function toggleStream() {
    const stream = document.getElementById('camera-stream');
    const button = document.getElementById('toggle-stream');
    if (stream.style.display === 'none') {
        stream.style.display = 'block';
        button.innerText = 'Turn Stream Off';
    } else {
        stream.style.display = 'none';
        button.innerText = 'Turn Stream On';
    }
}

// Fetch printer and camera state every 5 seconds
setInterval(fetchPrinterStatus, 5000);
setInterval(fetchCameraState, 5000);

// Initial fetch
fetchPrinterStatus();
fetchCameraState();

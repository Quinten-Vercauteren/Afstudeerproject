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
            let status;
            if (data.state === 'Printing') {
                status = 'Printing';
            } else if (data.state === 'Servicing') {
                status = 'Servicing';
            } else {
                status = 'Inactive';
            }
            document.getElementById('printer-status').innerText = status;
            fetchFilamentWeight();  // Fetch the current weight when the state changes
        })
        .catch(error => console.error('Error fetching camera state:', error));
}

function fetchFilamentWeight() {
    fetch('/filament_weight')
        .then(response => response.json())
        .then(data => {
            if (data.weight !== undefined) {
                document.getElementById('filament-weight').innerText = `${data.weight.toFixed(2)} grams`;
            } else {
                document.getElementById('filament-weight').innerText = 'Error fetching weight';
            }
        })
        .catch(error => {
            console.error('Error fetching filament weight:', error);
            document.getElementById('filament-weight').innerText = 'Error fetching weight';
        });
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

function toggleService() {
    fetch('/service_printer', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            updateServiceButton();
            fetchPrinterStatus();  // Update printer status immediately after toggling service state
        })
        .catch(error => console.error('Error toggling service state:', error));
}

function updateServiceButton() {
    fetch('/get_servicing_state')
        .then(response => response.json())
        .then(data => {
            const button = document.getElementById('service-button');
            if (data.servicing) {
                button.innerText = 'Stop Servicing';
            } else {
                button.innerText = 'Service Printer';
            }
        })
        .catch(error => console.error('Error fetching servicing state:', error));
}

function updateStreamButton() {
    const stream = document.getElementById('camera-stream');
    const button = document.getElementById('toggle-stream');
    if (stream.style.display === 'none') {
        button.innerText = 'Turn Stream On';
    } else {
        button.innerText = 'Turn Stream Off';
    }
}

// Fetch printer and camera state every 5 seconds
setInterval(fetchPrinterStatus, 5000);
setInterval(fetchCameraState, 5000);
setInterval(updateServiceButton, 5000);  // Update the service button text every 5 seconds

// Initial fetch
fetchPrinterStatus();
fetchCameraState();
updateServiceButton();
updateStreamButton();

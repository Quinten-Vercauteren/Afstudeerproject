function fetchPrinterStatus() {
    fetch('/printer_status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('printer-status').innerText = data.status;
        })
        .catch(error => console.error('Error fetching printer status:', error));
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
setInterval(updateServiceButton, 5000);
setInterval(fetchFilamentWeight, 5000);

// Initial fetch
fetchPrinterStatus();
updateServiceButton();
updateStreamButton();
fetchFilamentWeight()

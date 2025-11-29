document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileNameDisplay = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');
    const convertBtn = document.getElementById('convert-btn');
    const spinner = document.getElementById('spinner');
    const statusMessage = document.getElementById('status-message');

    let currentFile = null;

    // Drag & Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('drag-over');
    }

    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // Click to browse
    dropZone.addEventListener('click', (e) => {
        if (e.target !== removeFileBtn && e.target !== fileInput) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            // Check MIME type OR file extension
            if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
                currentFile = file;
                updateUI(true);
            } else {
                console.log('Rejected file:', file.name, 'Type:', file.type);
                showStatus('Please upload a PDF file. (Detected: ' + (file.type || 'unknown') + ')', 'error');
            }
        }
    }

    function updateUI(hasFile) {
        if (hasFile && currentFile) {
            fileNameDisplay.textContent = currentFile.name;
            fileInfo.style.display = 'inline-flex';
            convertBtn.disabled = false;
            statusMessage.textContent = '';

            // Hide default text if needed, or just show file info below
        } else {
            currentFile = null;
            fileInfo.style.display = 'none';
            convertBtn.disabled = true;
            fileInput.value = ''; // Reset input
        }
    }

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        updateUI(false);
    });

    convertBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = 'dark_' + currentFile.name;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(downloadUrl);
                showStatus('Conversion successful! Download started.', 'success');
            } else {
                const errorData = await response.json();
                showStatus('Error: ' + (errorData.detail || 'Conversion failed'), 'error');
            }
        } catch (error) {
            showStatus('Network error occurred.', 'error');
            console.error(error);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        convertBtn.disabled = isLoading;
        if (isLoading) {
            spinner.style.display = 'block';
            convertBtn.querySelector('span').style.opacity = '0'; // Hide text
        } else {
            spinner.style.display = 'none';
            convertBtn.querySelector('span').style.opacity = '1';
        }
    }

    function showStatus(msg, type) {
        statusMessage.textContent = msg;
        statusMessage.className = 'status-message ' + type;
    }
});

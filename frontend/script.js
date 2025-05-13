const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const approveBtn = document.getElementById('approve-btn');
const browseBtn = document.querySelector('.browse-btn');
const uploadContainer = document.getElementById('upload-container');
const processedFiles = document.getElementById('processed-files');
const videoDownload = document.getElementById('video-download');
const audioDownload = document.getElementById('audio-download');
const newVideoBtn = document.getElementById('new-video-btn');
const emailInput = document.getElementById('email-input');
const faceAnalysisContainer = document.getElementById('face-analysis-container');
const processedVideo = document.getElementById('processed-video');
let selectedFile = null;
let isProcessing = false;

// Initialize emotion data
const emotions = {
    'neutral': { element: 'neutral-progress', percentage: 'neutral-percentage', value: 0 },
    'happy': { element: 'happy-progress', percentage: 'happy-percentage', value: 0 },
    'sad': { element: 'sad-progress', percentage: 'sad-percentage', value: 0 },
    'surprised': { element: 'surprised-progress', percentage: 'surprised-percentage', value: 0 },
    'angry': { element: 'angry-progress', percentage: 'angry-percentage', value: 0 }
};

// Initialize emotion data for live analysis
const liveEmotions = {
    'neutral': { element: 'live-neutral-progress', percentage: 'live-neutral-percentage', value: 0 },
    'happy': { element: 'live-happy-progress', percentage: 'live-happy-percentage', value: 0 },
    'sad': { element: 'live-sad-progress', percentage: 'live-sad-percentage', value: 0 },
    'surprised': { element: 'live-surprised-progress', percentage: 'live-surprised-percentage', value: 0 },
    'angry': { element: 'live-angry-progress', percentage: 'live-angry-percentage', value: 0 }
};

// Handle drag over event
uploadArea.addEventListener('dragover', (event) => {
    event.preventDefault();
    if (!isProcessing) {
        uploadArea.style.borderColor = 'var(--primary-color)';
        uploadArea.style.backgroundColor = '#f0f7ff';
    }
});

// Handle drag leave event
uploadArea.addEventListener('dragleave', () => {
    if (!isProcessing) {
        uploadArea.style.borderColor = 'var(--border-color)';
        uploadArea.style.backgroundColor = '#f8fafc';
    }
});

// Handle drop event
uploadArea.addEventListener('drop', (event) => {
    event.preventDefault();
    if (isProcessing) return;
    
    uploadArea.style.borderColor = 'var(--border-color)';
    uploadArea.style.backgroundColor = '#f8fafc';

    const file = event.dataTransfer.files[0];
    if (file) {
        handleFileSelection(file);
    }
});

// Handle click event to open file input
uploadArea.addEventListener('click', (event) => {
    if (!isProcessing) {
        fileInput.click();
    }
});

browseBtn.addEventListener('click', (event) => {
    event.stopPropagation(); // Prevent event bubbling
    if (!isProcessing) {
        fileInput.click();
    }
});

// Handle file selection from file input
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file && !isProcessing) {
        handleFileSelection(file);
    }
});

// Function to format file size
function formatFileSize(bytes) {
    if (bytes > 999 * 1024 * 1024) {
        return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
    } else {
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }
}

// Function to handle file selection
function handleFileSelection(file) {
    selectedFile = file;
    displayFileInfo(file);
    updateApproveButtonState();
}

// Function to display the file info
function displayFileInfo(file) {
    fileInfo.innerHTML = '';

    const fileInfoContainer = document.createElement('div');
    fileInfoContainer.classList.add('file-info-container');

    const fileItem = document.createElement('div');
    fileItem.classList.add('file-item');

    const fileDetails = document.createElement('div');
    fileDetails.classList.add('file-details');

    const fileName = document.createElement('div');
    fileName.classList.add('file-name');
    fileName.textContent = file.name;

    const fileSize = document.createElement('div');
    fileSize.classList.add('file-size');
    fileSize.textContent = formatFileSize(file.size);

    const cancelBtn = document.createElement('button');
    cancelBtn.classList.add('cancel-btn');
    cancelBtn.innerHTML = '<i class="fas fa-times"></i>';

    cancelBtn.addEventListener('click', () => {
        if (!isProcessing) {
            cancelFileSelection();
        }
    });

    fileDetails.appendChild(fileName);
    fileDetails.appendChild(fileSize);
    fileItem.appendChild(fileDetails);
    fileItem.appendChild(cancelBtn);
    fileInfoContainer.appendChild(fileItem);

    fileInfo.appendChild(fileInfoContainer);
}

// Function to handle "Process Video" button click
function handleApprove() {
    if (isProcessing) return;

    isProcessing = true;
    
    // Disable the button and show loading state
    approveBtn.disabled = true;
    approveBtn.innerHTML = `
        <div class="button-loading">
            <i class="fas fa-spinner fa-spin"></i>
            Processing...
        </div>
    `;

    // Disable file input and upload area
    fileInput.disabled = true;
    uploadArea.style.cursor = 'not-allowed';
    uploadArea.style.opacity = '0.7';

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('email', emailInput.value);

    // Show the loading spinner
    const loadingSpinner = document.getElementById('loading-spinner');
    loadingSpinner.style.display = 'flex';

    // Initialize progress stages
    const progressList = document.querySelector('.progress-list');
    const stages = [
        { id: 'extract-video', text: 'Extracting video' },
        { id: 'extract-audio', text: 'Extracting audio' },
        { id: 'process-diarization', text: 'Processing audio through diarization' },
        { id: 'facial-analysis', text: 'Analyzing facial expressions' },
        { id: 'send-email', text: 'Generating report' }
    ];
    
    // Initialize progress list
    progressList.innerHTML = stages.map(stage => `
        <div class="progress-item" id="${stage.id}">
            <div class="progress-icon">
                <i class="fas fa-circle-notch fa-spin"></i>
            </div>
            <div class="progress-text">${stage.text}</div>
        </div>
    `).join('');

    // Send the request
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        function readStream() {
            return reader.read().then(({done, value}) => {
                if (done) {
                    return;
                }
                
                const chunk = decoder.decode(value);
                try {
                    const data = JSON.parse(chunk);
                    if (data.progress) {
                        // Update progress based on the current stage
                        const currentStage = stages.find(stage => 
                            data.progress.toLowerCase().includes(stage.text.toLowerCase().replace('...', ''))
                        );
                        if (currentStage) {
                            const progressItem = document.getElementById(currentStage.id);
                            if (progressItem) {
                                progressItem.classList.add('active');
                                const icon = progressItem.querySelector('.progress-icon i');
                                icon.classList.remove('fa-circle-notch', 'fa-spin');
                                icon.classList.add('fa-check');
                            }
                            
                            // Eğer facial analysis aşamasındaysak, canlı görüntüyü göster
                            if (currentStage.id === 'facial-analysis') {
                                showLiveAnalysis();
                            }
                        }
                    } else if (data.status === 'complete') {
                        // Show download buttons
                        document.getElementById('download-container').style.display = 'flex';
                        processedFiles.style.display = 'block';
                        
                        // Add click handler for download button
                        const downloadBtn = document.getElementById('download-btn');
                        downloadBtn.onclick = () => {
                            window.location.href = '/download-report';
                        };
                        
                        // Check if the facial analysis is available
                        if (data.results.facial_analysis) {
                            // Show facial analysis container
                            faceAnalysisContainer.style.display = 'block';
                            
                            // Fetch and parse the emotion analysis CSV file
                            const csvUrl = generateCacheBustingUrl(data.results.facial_analysis);
                            fetch(csvUrl)
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error(`HTTP error! Status: ${response.status}`);
                                    }
                                    return response.text();
                                })
                                .then(csvText => {
                                    parseEmotionData(csvText);
                                })
                                .catch(error => {
                                    console.error('Error loading emotion data:', error);
                                    showErrorMessage(`Failed to load emotion data: ${error.message}`);
                                });
                        }
                        
                        // Update download links with cache-busting
                        if (data.results.video_file) {
                            videoDownload.href = generateCacheBustingUrl(data.results.video_file);
                        }
                        if (data.results.audio_file) {
                            audioDownload.href = generateCacheBustingUrl(data.results.audio_file);
                        }
                        
                        // Add emotion download link
                        if (data.results.facial_analysis) {
                            const emotionDownload = document.getElementById('emotion-download');
                            if (emotionDownload) {
                                emotionDownload.href = generateCacheBustingUrl(data.results.facial_analysis);
                            }
                        }
                        
                        // Hide loading spinner
                        loadingSpinner.style.display = 'none';
                        
                        // Reset processing state
                        resetProcessingState();
                    } else if (data.status === 'error') {
                        // Show error message
                        showErrorMessage(data.message || 'An error occurred');
                        
                        // Hide loading spinner
                        loadingSpinner.style.display = 'none';
                        
                        // Reset processing state
                        resetProcessingState();
                    }
                } catch (e) {
                    console.error('Error parsing JSON:', e);
                }
                
                return readStream();
            });
        }
        
        return readStream();
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Show error message
        showErrorMessage('An error occurred. Please try again.');
        
        // Hide loading spinner
        loadingSpinner.style.display = 'none';
        
        // Reset processing state
        resetProcessingState();
    });
}

// Function to reset processing state
function resetProcessingState() {
    isProcessing = false;
    approveBtn.disabled = false;
    approveBtn.innerHTML = `
        <i class="fas fa-check"></i>
        Process Video
    `;
    fileInput.disabled = false;
    uploadArea.style.cursor = 'pointer';
    uploadArea.style.opacity = '1';
}

// Function to show success message
function showSuccessMessage(message) {
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Function to show error message
function showErrorMessage(message) {
    const notification = document.createElement('div');
    notification.className = 'notification error';
    notification.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Cancel file selection
function cancelFileSelection() {
    if (!isProcessing) {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.innerHTML = '';
        updateApproveButtonState();
    }
}

// Handle "Process Another Video" button click
newVideoBtn.addEventListener('click', () => {
    window.location.reload();
});

// Email validation function
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Update the approve button state based on both file and email
function updateApproveButtonState() {
    const hasFile = selectedFile !== null;
    const hasValidEmail = validateEmail(emailInput.value);
    
    approveBtn.disabled = !(hasFile && hasValidEmail);
}

// Add event listeners for email input
emailInput.addEventListener('input', updateApproveButtonState);

// Add click event listener for the approve button
approveBtn.addEventListener('click', handleApprove);

// Function to parse emotion data from CSV
function parseEmotionData(csvText) {
    // Reset all emotion values
    Object.keys(emotions).forEach(emotion => {
        emotions[emotion].value = 0;
    });
    
    // Parse CSV
    const lines = csvText.split('\n');
    const headers = lines[0].split(',');
    
    // Get the emotion column index
    const emotionIndex = headers.findIndex(header => header.trim() === 'emotion');
    if (emotionIndex === -1) return;
    
    // Count emotions
    let totalEmotions = 0;
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const columns = line.split(',');
        if (columns.length <= emotionIndex) continue;
        
        const emotion = columns[emotionIndex].trim().toLowerCase();
        if (emotions[emotion]) {
            emotions[emotion].value++;
            totalEmotions++;
        }
    }
    
    // Update UI with emotion percentages
    if (totalEmotions > 0) {
        Object.keys(emotions).forEach(emotion => {
            const percentage = (emotions[emotion].value / totalEmotions) * 100;
            const progressElement = document.getElementById(emotions[emotion].element);
            const percentageElement = document.getElementById(emotions[emotion].percentage);
            
            if (progressElement) {
                progressElement.style.width = `${percentage}%`;
            }
            
            if (percentageElement) {
                percentageElement.textContent = `${percentage.toFixed(1)}%`;
            }
        });
    }
}

// Function to generate cache-busting URL
function generateCacheBustingUrl(url) {
    const timestamp = new Date().getTime();
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}t=${timestamp}`;
}

// Check if a file exists
function checkFileExists(url) {
    return new Promise((resolve, reject) => {
        fetch(url, { method: 'HEAD' })
            .then(response => {
                if (response.ok) {
                    resolve(true);
                } else {
                    resolve(false);
                }
            })
            .catch(() => resolve(false));
    });
}

// Function to show live analysis
function showLiveAnalysis() {
    const realtimeAnalysis = document.getElementById('realtime-analysis');
    if (realtimeAnalysis) {
        realtimeAnalysis.style.display = 'block';
        
        // Start checking the CSV file for emotion data
        startEmotionDataPolling();
    }
}

// Function to poll emotion data from CSV
function startEmotionDataPolling() {
    // Poll every 3 seconds
    const pollInterval = setInterval(() => {
        const csvUrl = generateCacheBustingUrl('/custom_output/emotion_analysis.csv');
        
        checkFileExists(csvUrl).then(exists => {
            if (!exists) {
                console.log('Waiting for emotion data to be generated...');
                return;
            }
            
            fetch(csvUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('CSV not found or server error');
                    }
                    return response.text();
                })
                .then(csvText => {
                    parseLiveEmotionData(csvText);
                    
                    // Check if processing is complete
                    fetch('/processing-status')
                        .then(response => response.json())
                        .then(data => {
                            if (data.completed) {
                                console.log('Processing completed, stopping emotion data polling');
                                clearInterval(pollInterval);
                            }
                        })
                        .catch(error => {
                            console.error('Error checking processing status:', error);
                        });
                })
                .catch(error => {
                    console.log('Error reading emotion data:', error);
                });
        });
    }, 3000);
}

// Function to parse live emotion data
function parseLiveEmotionData(csvText) {
    // Reset all emotion values
    Object.keys(liveEmotions).forEach(emotion => {
        liveEmotions[emotion].value = 0;
    });
    
    // Parse CSV
    const lines = csvText.split('\n');
    if (lines.length < 2) {
        console.log('CSV file has no data rows yet');
        return; // No data rows yet
    }
    
    const headers = lines[0].split(',');
    
    // Get the emotion column index
    const emotionIndex = headers.findIndex(header => header.trim() === 'emotion');
    if (emotionIndex === -1) {
        console.error('CSV does not contain emotion column');
        return;
    }
    
    // Count emotions
    let totalEmotions = 0;
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const columns = line.split(',');
        if (columns.length <= emotionIndex) continue;
        
        const emotion = columns[emotionIndex].trim().toLowerCase();
        if (liveEmotions[emotion]) {
            liveEmotions[emotion].value++;
            totalEmotions++;
        }
    }
    
    console.log(`Processed ${totalEmotions} emotion records from CSV`);
    
    // Update UI with emotion percentages
    if (totalEmotions > 0) {
        Object.keys(liveEmotions).forEach(emotion => {
            const percentage = (liveEmotions[emotion].value / totalEmotions) * 100;
            const progressElement = document.getElementById(liveEmotions[emotion].element);
            const percentageElement = document.getElementById(liveEmotions[emotion].percentage);
            
            if (progressElement) {
                progressElement.style.width = `${percentage}%`;
            }
            
            if (percentageElement) {
                percentageElement.textContent = `${percentage.toFixed(1)}%`;
            }
        });
    }
}

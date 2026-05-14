const urlInput = document.getElementById('urlInput');
const downloadBtn = document.getElementById('downloadBtn');
const statusCard = document.getElementById('statusCard');
const statusLabel = document.getElementById('statusLabel');
const statusPercent = document.getElementById('statusPercent');
const progressBar = document.getElementById('progressBar');
const resultArea = document.getElementById('resultArea');

let currentTaskId = null;
let pollInterval = null;

downloadBtn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    if (!url) return alert('Please enter a valid URL');

    // Reset UI
    downloadBtn.disabled = true;
    statusCard.style.display = 'block';
    resultArea.innerHTML = '';
    updateProgress(0, 'Queuing...');

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        currentTaskId = data.task_id;
        startPolling(currentTaskId);
    } catch (error) {
        console.error('Error:', error);
        updateProgress(0, 'Error connecting to server');
        downloadBtn.disabled = false;
    }
});

function startPolling(taskId) {
    if (pollInterval) clearInterval(pollInterval);
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${taskId}`);
            const data = await response.json();

            updateProgress(data.progress, data.status);

            if (data.status === 'completed') {
                clearInterval(pollInterval);
                showResult(data.result);
                downloadBtn.disabled = false;
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                statusLabel.innerText = 'Failed: ' + (data.error || 'Unknown error');
                statusLabel.style.color = '#ef4444';
                downloadBtn.disabled = false;
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 1000);
}

function updateProgress(percent, label) {
    progressBar.style.width = `${percent}%`;
    statusPercent.innerText = `${Math.round(percent)}%`;
    statusLabel.innerText = label;
}

function showResult(result) {
    const downloadUrl = result.s3_url || `/downloads/${result.filename}`;
    resultArea.innerHTML = `
        <div class="fade-in">
            <p style="margin-bottom: 10px; font-weight: 600;">${result.title}</p>
            <a href="${downloadUrl}" class="download-link" target="_blank">
                <i class="fas fa-download"></i> Download Video
            </a>
            <p style="margin-top: 10px; font-size: 0.8rem; color: #94a3b8;">
                Platform: ${result.platform} | Duration: ${formatTime(result.duration)}
            </p>
        </div>
    `;
}

function formatTime(seconds) {
    if (!seconds) return 'N/A';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return [h, m, s]
        .map(v => v < 10 ? "0" + v : v)
        .filter((v, i) => v !== "00" || i > 0)
        .join(":");
}

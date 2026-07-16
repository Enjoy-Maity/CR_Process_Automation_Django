function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showMessage(message) {
    if (message) {
        window.alert(message);
    }
}

function formatLogItem(log) {
    const timestamp = log.timestamp ? `<span class="log-sep">----</span> <span class="log-time">${log.timestamp}</span>` : '';
    return `<li class="task-log-entry"><span class="task-log-message">${log.message}</span>${timestamp}</li>`;
}

function updateDownloadArea(row, task) {
    const link = row.querySelector('.js-download-link');
    const placeholder = row.querySelector('.js-download-placeholder');
    if (!link) return;
    if (task.download_ready) {
        link.href = task.download_url;
        link.classList.remove('hidden');
        if (placeholder) placeholder.classList.add('hidden');
    } else {
        link.classList.add('hidden');
        if (placeholder) placeholder.classList.remove('hidden');
    }
}

function updateStatusCell(row, status) {
    const statusCell = row.querySelector('.js-task-status');
    if (!statusCell) return;
    statusCell.textContent = status;
    statusCell.className = 'status-badge compact-status js-task-status';
    if (status === 'Completed') statusCell.classList.add('status-success');
    else if (status === 'Running') statusCell.classList.add('status-progress');
    else if (status === 'Failed') statusCell.classList.add('status-failed');
    else if (status === 'Waiting for OTP') statusCell.classList.add('status-progress'); // Treat as progress visually
}

function updateCountCells(row, task) {
    const mappings = {
        '.js-total-crs': task.total_crs,
        '.js-north-crs': task.north_crs,
        '.js-west-crs': task.west_crs,
        '.js-east-crs': task.east_crs,
        '.js-south-crs': task.south_crs,
    };
    Object.entries(mappings).forEach(([selector, value]) => {
        const cell = row.querySelector(selector);
        if (cell) cell.textContent = value ?? 0;
    });
}

async function refreshTaskPanels() {
    try {
        const response = await fetch('/api/task/dashboard-data/'); // Ensure this matches your urls.py path
        const data = await response.json();
        const runningBox = document.getElementById('running-task-box');
        const logBox = document.getElementById('task-log-box');
        
        if (runningBox) runningBox.textContent = data.running_task;
        if (logBox) {
            const items = (data.logs || []).map(formatLogItem).join('');
            logBox.innerHTML = `<ul class="log-list">${items}</ul>`;
        }
        
        document.querySelectorAll('tr[data-task-id]').forEach(row => {
            const taskId = parseInt(row.getAttribute('data-task-id'), 10);
            const task = (data.tasks || []).find(item => item.id === taskId);
            if (!task) return;
            
            updateStatusCell(row, task.status);
            updateDownloadArea(row, task);
            updateCountCells(row, task);

            // ==========================================
            // IFRAME TRIGGER LOGIC
            // ==========================================
            if (task.otp_required === true) {
                const authOverlay = document.getElementById('auth-overlay');
                const authIframe = document.getElementById('auth-iframe');
                
                // Only open the iframe if it isn't already open
                if (authOverlay && authOverlay.style.display !== 'flex') {
                    authIframe.src = `/playwright-auth-iframe/?task_id=${task.id}`;
                    authOverlay.style.display = 'flex';
                }
            }
        });
    } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
    }
}

async function startTask(taskId, row) {
    const response = await fetch(`/api/task/start/${taskId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    });
    const data = await response.json();
    if (!response.ok || !data.ok) {
        showMessage(data.message || 'Task start failed.');

        // IMPORTANT: Re-enable the button immediately so the user can try again later
        const btn = document.querySelector(`button[data-task-id="${taskId}"]`);
        if(btn) {
            btn.disabled = false;
            btn.textContent = 'Start';}

        return;
    }
    
    // Instead of showing a blocking alert for successful task completion here,
    // we let the status cells and logs do the talking while polling handles the updates.
    if (row) {
        updateStatusCell(row, data.status || 'Running');
    }
    await refreshTaskPanels();
}

document.addEventListener('click', async function (e) {
    const startBtn = e.target.closest('.js-start-task');
    if (!startBtn) return;

    // 1. STOP everything else immediately
    e.preventDefault(); 
    e.stopImmediatePropagation(); 

    // 2. Guard Clause: Don't do anything if already processing
    if (startBtn.disabled) return;
    
    // 3. Visual feedback
    startBtn.disabled = true;
    startBtn.textContent = 'Starting...';
    
    const row = startBtn.closest('tr');
    await startTask(startBtn.dataset.taskId, row);
    
    // 4. Reset after a delay
    setTimeout(() => {
        startBtn.disabled = false;
        startBtn.textContent = 'Start';
    }, 3000);
}, true);

// Listener for when the Iframe successfully posts the 2FA code
window.addEventListener('message', function(event) {
    if (event.data && event.data.action === 'close_iframe') {
        const authOverlay = document.getElementById('auth-overlay');
        const authIframe = document.getElementById('auth-iframe');
        if (authOverlay) authOverlay.style.display = 'none';
        if (authIframe) authIframe.src = '';
        
        // Force an immediate refresh to clear the "otp_required" state visually
        refreshTaskPanels();
    }
});

// Initial load
document.addEventListener('DOMContentLoaded', refreshTaskPanels);

// POLL THE SERVER EVERY 3 SECONDS
// setInterval(refreshTaskPanels, 3000);

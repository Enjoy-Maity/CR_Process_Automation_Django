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
    else if (status === 'Waiting for Password') statusCell.classList.add('status-progress'); // Treat as progress visually
}

function updateCountCells(row, task) {
    const body = document.body;
    const selectedOption = body ? body.dataset.selectedOption : null;
    if (selectedOption === 'cr_planning') {
        return;
    }
    
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

// Track which task currently has an iframe open, and what type,
// so we don't reset the iframe src while the user is typing.
let activeIframeTaskId = null;
let activeIframeType = null;   // 'otp' | 'password'

function openAuthIframe(taskId, type) {
    const authOverlay = document.getElementById('auth-overlay');
    const authIframe = document.getElementById('auth-iframe');
    if (!authOverlay || !authIframe) return;

    // Only (re)load the iframe when the task OR the type changes
    // (don't reload while user is typing)
    if (activeIframeTaskId !== taskId || activeIframeType !== type) {
        const url = (type === 'password')
            ? `/playwright-password-iframe/?task_id=${taskId}`
            : `/playwright-auth-iframe/?task_id=${taskId}`;
        authIframe.src = url;
        activeIframeTaskId = taskId;
        activeIframeType = type;
    }
    authOverlay.style.display = 'flex';
}

function closeAuthIframe() {
    const authOverlay = document.getElementById('auth-overlay');
    const authIframe = document.getElementById('auth-iframe');
    if (authOverlay) authOverlay.style.display = 'none';
    if (authIframe) authIframe.src = '';
    activeIframeTaskId = null;
    activeIframeType = null;
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

        // Track whether ANY task still needs input this cycle
        let anyInputRequired = false;

        document.querySelectorAll('tr[data-task-id]').forEach(row => {
            const taskId = parseInt(row.getAttribute('data-task-id'), 10);
            const task = (data.tasks || []).find(item => item.id === taskId);
            if (!task) return;

            updateStatusCell(row, task.status);
            updateDownloadArea(row, task);
            updateCountCells(row, task);

            // ==========================================
            // IFRAME TRIGGER LOGIC
            // Password takes priority (it happens first in the login flow)
            // ==========================================
            if (task.password_required === true) {
                anyInputRequired = true;
                openAuthIframe(task.id, 'password');
            } else if (task.otp_required === true) {
                anyInputRequired = true;
                openAuthIframe(task.id, 'otp');
            }
        });

        // If the backend cleared both flags (input submitted or timed out)
        // and an iframe is still showing, close it automatically.
        if (!anyInputRequired && activeIframeTaskId !== null) {
            closeAuthIframe();
        }
    } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
    }
}

async function startTask(taskId, row) {
    const dateInput = document.getElementById('cr_filter_date');
    const selectedDate = dateInput ? dateInput.value : '';

    if (String(taskId) === '1' && !selectedDate) {
        showMessage('Please select a Date before starting this task.');
        const btn = document.querySelector(`button[data-task-id="${taskId}"]`);
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Start';
        }
        return;
    }

    const formData = new FormData();
    formData.append('date', selectedDate);

    const response = await fetch(`/api/task/start/${taskId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData,
    });
    const data = await response.json();
    if (!response.ok || !data.ok) {
        showMessage(data.message || 'Task start failed.');

        const btn = document.querySelector(`button[data-task-id="${taskId}"]`);
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Start';
        }

        return;
    }

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

// Listener for when the Iframe successfully posts the password or 2FA code
window.addEventListener('message', function (event) {
    if (event.data && event.data.action === 'close_iframe') {
        closeAuthIframe();

        // Force an immediate refresh to clear the "otp_required" /
        // "password_required" state visually
        refreshTaskPanels();
    }
});

// Allow closing the modal via the X button too (keeps tracking vars in sync)
// document.addEventListener('DOMContentLoaded', function () {
//     const authOverlay = document.getElementById('auth-overlay');
//     if (authOverlay) {
//         const closeBtn = authOverlay.querySelector('button');
//         if (closeBtn) {
//             closeBtn.addEventListener('click', function () {
//                 closeAuthIframe();
//             });
//         }
//     }
// });

// Initial load
document.addEventListener('DOMContentLoaded', refreshTaskPanels);

// POLL THE SERVER EVERY 3 SECONDS  (required so the iframe auto-opens on
// password_required / otp_required)
setInterval(refreshTaskPanels, 3000);

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
let activeIframeType = null;   // 'otp' | 'password' | 'notice'

function openAuthIframe(taskId, type) {
    const authOverlay = document.getElementById('auth-overlay');
    const authIframe = document.getElementById('auth-iframe');
    if (!authOverlay || !authIframe) return;

    // Only (re)load the iframe when the task OR the type changes
    // (don't reload while user is typing)
    if (activeIframeTaskId !== taskId || activeIframeType !== type) {
        let url;
        if (type === 'password') {
            url = `/playwright-password-iframe/?task_id=${taskId}`;
        } else if (type === 'notice') {
            url = `/playwright-notice-iframe/?task_id=${taskId}`;
        } else if (type === 'alert') {
            url = `/playwright-alert-iframe/?task_id=${taskId}`;
        } else {
            url = `/playwright-auth-iframe/?task_id=${taskId}`;
        }
        authIframe.src = url;
        // The sign-in code needs a little more room than the auth form.
        authIframe.style.height =
            (type === 'notice') ? '340px' :
            (type === 'alert') ? '320px' : '';
        activeIframeTaskId = taskId;
        activeIframeType = type;
    }
    authOverlay.style.display = 'flex';
}

function closeAuthIframe() {
    const authOverlay = document.getElementById('auth-overlay');
    const authIframe = document.getElementById('auth-iframe');
    if (authOverlay) authOverlay.style.display = 'none';
    if (authIframe) {
        authIframe.src = '';
        authIframe.style.height = '';
    }
    activeIframeTaskId = null;
    activeIframeType = null;
}

// The shared overlay lives in base_main.html; bind its close button once the
// DOM is ready (page scripts such as night_execution.js bind it as well).
function bindAuthCloseBtn() {
    const closeBtn = document.getElementById('auth-modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeAuthIframe);
    }
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindAuthCloseBtn);
} else {
    bindAuthCloseBtn();
}

// Alert dialogs raised by the backend (e.g. missing/wrong NIAM credentials).
// They open in the same iframe overlay as the password / OTP prompts. Remember
// which ones were shown so the 3-second poll does not reopen them.
const seenAlertKeys = new Set();

function appAlertKey(task) {
    return `${task.id}:${task.run_key || ''}:${task.alert_seq || 0}`;
}

function showPendingAlert(tasks) {
    let alertTask = null;
    let alertKey = '';
    (tasks || []).forEach(task => {
        const needed =
            task.alert_required === true ||
            task.alert_required === 'true' ||
            task.alert_required === 1;
        if (!needed) return;
        const key = appAlertKey(task);
        if (seenAlertKeys.has(key)) return;
        // Prefer the most recent alert when several are pending.
        if (!alertTask || Number(task.alert_seq || 0) >= Number(alertTask.alert_seq || 0)) {
            alertTask = task;
            alertKey = key;
        }
    });
    if (!alertTask) return;
    if (!document.getElementById('auth-overlay')) return;
    openAuthIframe(alertTask.id, 'alert');
    // The iframe now owns the dialog; only reopen it for a NEW alert
    // (different run / alert_seq), not on every poll.
    seenAlertKeys.add(alertKey);
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

        // Read-only notices (Microsoft Authenticator sign-in code) may belong to
        // a task that has no table row on this page, so scan every task.
        const noticeTask = (data.tasks || []).find(task => {
            const noticeNeeded =
                task.notice_required === true ||
                task.notice_required === 'true' ||
                task.notice_required === 1;
            return noticeNeeded && String(task.notice_text || '').trim() !== '';
        });

        if (noticeTask) {
            anyInputRequired = true;
            openAuthIframe(noticeTask.id, 'notice');
        }

        document.querySelectorAll('tr[data-task-id]').forEach(row => {
        const taskId = parseInt(row.getAttribute('data-task-id'), 10);
        const task = (data.tasks || []).find(item => Number(item.id) === taskId);
        if (!task) return;

        updateStatusCell(row, task.status);
        updateDownloadArea(row, task);
        updateCountCells(row, task);

        const passwordNeeded =
            task.password_required === true ||
            task.password_required === 'true' ||
            task.password_required === 1;

        const otpNeeded =
            task.otp_required === true ||
            task.otp_required === 'true' ||
            task.otp_required === 1;

        // Debug (remove after confirming)
        if (passwordNeeded || otpNeeded) {
            console.log(`Task ${taskId} needs input:`,
                { passwordNeeded, otpNeeded,
                raw_pwd: task.password_required, raw_otp: task.otp_required });
        }

        if (passwordNeeded) {
            anyInputRequired = true;
            openAuthIframe(task.id, 'password');
        } else if (otpNeeded) {
            anyInputRequired = true;
            openAuthIframe(task.id, 'otp');
        }
    });

        // Blocking alert dialog (e.g. missing/wrong NIAM credentials) opens in
        // the same overlay as the password / OTP prompts. Interactive prompts
        // and the time-sensitive sign-in code keep priority; the alert shows
        // once they are done.
        if (
            activeIframeType !== 'password' &&
            activeIframeType !== 'otp' &&
            activeIframeType !== 'notice'
        ) {
            showPendingAlert(data.tasks);
        }

        // If the backend cleared both flags (input submitted or timed out)
        // and an iframe is still showing, close it automatically. The alert
        // dialog stays until the user dismisses it (OK / X) or it is cleared.
        if (
            !anyInputRequired &&
            activeIframeTaskId !== null &&
            activeIframeType !== 'alert'
        ) {
            closeAuthIframe();
        }
    } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
    }
}

async function startTask(taskId, row) {
    const dateInput = document.getElementById('cr_filter_date');
    const selectedDate = dateInput ? dateInput.value : '';
    
    const regions = document.querySelectorAll('input[class="region-checkbox"]:checked:not(:disabled)');
    const regionValues = Array.from(regions).map(input => input.value).join(',');

    const formData = new FormData();
    formData.append('date', selectedDate);
    formData.append('region', regionValues);

    try {
        const response = await fetch(`/api/task/start/${taskId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            body: formData,
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.ok) {
            // Show error with title and message
            showErrorAlert(data.title || 'Error', data.message || 'Task start failed.');
            const btn = document.querySelector(`button[data-task-id="${taskId}"]`);
            if (btn) {
                btn.disabled = false;
                btn.textContent = 'Start';
            }
            return;
        }

        // Success handling
        if (row) {
            updateStatusCell(row, data.status || 'Running');
        }
        await refreshTaskPanels();
        
    } catch (error) {
        console.error("Error:", error);
        showErrorAlert('Network Error', 'Failed to communicate with server.');
    }
}

function showErrorAlert(title, message) {
    // You can use your existing showMessage function or create a more detailed one
    window.alert(`${title}\n\n${message}`);
    // Or use a better UI component like Bootstrap modal, Toastr, etc.
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

async function waitForReplicaSync(syncId) {
    while (true) {
        const resp = await fetch(`/api/replica-sync-status/${syncId}/`);
        const data = await resp.json();
        
        if (data.status === 'complete') {
            console.log('Replica is ready!');
            break;
        } else if (data.status.startsWith('failed')) {
            console.error('Replica sync failed:', data.status);
            break;
        }
        
        await new Promise(resolve => setTimeout(resolve, 500));  // Poll every 500ms
    }
}

setInterval(refreshTaskPanels, 3000);


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
    const response = await fetch('/api/task/dashboard-data/');
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
    });
}

async function startTask(taskId, row) {
    const response = await fetch(`/api/task/start/${taskId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    });
    const data = await response.json();
    if (!response.ok || !data.ok) {
        showMessage(data.message || 'Task start failed.');
        return;
    }
    showMessage(data.message || 'Task completed.');
    if (row) {
        updateStatusCell(row, data.status || 'Completed');
        updateDownloadArea(row, data);
        if (data.counts) updateCountCells(row, data.counts);
    }
    await refreshTaskPanels();
}

document.addEventListener('click', async function (e) {
    const startBtn = e.target.closest('.js-start-task');
    if (!startBtn) return;
    const row = startBtn.closest('tr');
    await startTask(startBtn.dataset.taskId, row);
});

document.addEventListener('DOMContentLoaded', refreshTaskPanels);

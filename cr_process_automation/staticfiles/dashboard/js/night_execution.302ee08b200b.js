(function () {
    "use strict";

    // ── Config ──────────────────────────────────────────────────────────
    const POLL_INTERVAL_MS = 2000;
    const MAX_POLL_ATTEMPTS = 150;  // ~5 minutes at 2s; adjust as needed
    
    // Get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const CSRF_TOKEN = getCookie('csrftoken');
    const USER_EMAIL = ""; // Will be populated from server if needed

    const FETCH_CRS_URL = "/night-execution/fetch-crs/";
    const FETCH_STATUS_URL = "/night-execution/fetch-cr-status/";
    const RESULT_URL = "/night-execution/status-result/";
    const START_TASK_URL = "/night-execution/start-task/";
    
    // Auth iframe tracking
    let activeJobId = null;
    let activeIframeType = null;

    const TASK_COLUMNS = [
        { key: "automation_template", label: "Automation Template" },
        { key: "activity_hc", label: "Activity HC" },
        { key: "activity_cli", label: "Activity CLI" },
        { key: "cr_implementation", label: "CR Implementation Task" },
        { key: "cr_closure", label: "CR Closure" },
    ];

    const statusClass = {
        "Completed":    "status-cell-success",
        "Successful":   "status-cell-success",
        "Pending":      "status-cell-pending",
        "In Progress":  "status-cell-pending",
        "Failed":       "status-cell-unsuccessful",
        "Unsuccessful": "status-cell-unsuccessful",
    };

    // ── Helpers ─────────────────────────────────────────────────────────
    function showBar(message, type) {
        const bar = document.getElementById("ne-status-bar");
        if (!bar) return;
        bar.textContent = message;
        bar.className = "region-cr-status-bar status-" + (type || "info");
        bar.style.display = "block";
    }

    function hideBar() {
        const bar = document.getElementById("ne-status-bar");
        if (!bar) return;
        bar.style.display = "none";
    }

    // ── Auth iframe functions ─────────────────────────────────────────────
    function openAuthIframe(jobId, type) {
        const authOverlay = document.getElementById('auth-overlay');
        const authIframe = document.getElementById('auth-iframe');
        if (!authOverlay || !authIframe) return;

        // Only (re)load the iframe when the job OR the type changes
        if (activeJobId !== jobId || activeIframeType !== type) {
            const url = (type === 'password')
                ? `/night-execution/password-iframe/?job_id=${jobId}`
                : `/night-execution/otp-iframe/?job_id=${jobId}`;
            authIframe.src = url;
            activeJobId = jobId;
            activeIframeType = type;
        }
        authOverlay.style.display = 'flex';
        authOverlay.setAttribute('aria-hidden', 'false');
    }

    function closeAuthIframe() {
        const authOverlay = document.getElementById('auth-overlay');
        const authIframe = document.getElementById('auth-iframe');
        if (authOverlay) {
            authOverlay.style.display = 'none';
            authOverlay.setAttribute('aria-hidden', 'true');
        }
        if (authIframe) authIframe.src = '';
        activeJobId = null;
        activeIframeType = null;
    }

    window.closeAuthIframe = closeAuthIframe;

    window.addEventListener('message', function (event) {
        const data = event.data || {};
        if (data.action === 'close_iframe' || data.type === 'auth-success') {
            closeAuthIframe();
        }
    });

    const authCloseBtn = document.getElementById('auth-modal-close');
    if (authCloseBtn) {
        authCloseBtn.addEventListener('click', closeAuthIframe);
    }

    function collectCrNumbers() {
        return Array.from(document.querySelectorAll("tr[data-cr-no]"))
            .map(row => row.dataset.crNo)
            .filter(Boolean);
    }

    function applyStatuses(statuses) {
        document.querySelectorAll("tr[data-cr-no]").forEach(row => {
            const crNo = row.dataset.crNo;
            const cell = row.querySelector(".js-cr-status");
            if (!cell) return;

            const status = (statuses && statuses[crNo]) ? statuses[crNo] : "—";
            cell.textContent = status;
            cell.className = "js-cr-status status-badge compact-status";
            const cls = statusClass[status];
            if (cls) cell.classList.add(cls);
        });
    }

    function sleep(ms) {
        return new Promise(res => setTimeout(res, ms));
    }

    function renderCrTable(crs) {
        const tbody = document.getElementById("cr-table-body");
        const tableContainer = document.getElementById("cr-table-container");
        const noCrsMessage = document.getElementById("no-crs-message");

        tbody.innerHTML = "";

        if (!crs || crs.length === 0) {
            tableContainer.style.display = "none";
            noCrsMessage.style.display = "block";
            noCrsMessage.innerHTML = "<p>No CRs found for the selected date and logged-in user.</p>";
            hideBar();
            return;
        }

        tableContainer.style.display = "block";
        noCrsMessage.style.display = "none";

        crs.forEach((cr, index) => {
            const row = document.createElement("tr");
            row.dataset.crNo = cr.cr_no;

            const taskCells = TASK_COLUMNS.map((task) => `
                <td>
                    <button type="button" class="action-btn start-btn compact-btn ne-start-task" data-cr-no="${cr.cr_no}" data-task-key="${task.key}">
                        Start
                    </button>
                    <span class="task-status-icons" data-cr-no="${cr.cr_no}" data-task-key="${task.key}"></span>
                </td>
            `).join("");

            row.innerHTML = `
                <td>${index + 1}</td>
                <td class="task-name-cell">${cr.cr_no}</td>
                <td>${cr.circle || ""}</td>
                <td>${cr.activity_title || ""}</td>
                <td>${cr.change_responsible || ""}</td>
                <td>
                    <span class="status-badge compact-status js-cr-status">${cr.cr_status || "—"}</span>
                </td>
                ${taskCells}
            `;
            tbody.appendChild(row);
        });

        // Attach event listeners to new start buttons
        attachStartButtonListeners();
    }

    function attachStartButtonListeners() {
        document.querySelectorAll(".ne-start-task").forEach(btn => {
            btn.addEventListener("click", function () {
                const crNo = btn.dataset.crNo;
                const taskKey = btn.dataset.taskKey;
                startTask(crNo, taskKey, btn);
            });
        });
    }

    async function startTask(crNo, taskKey, button) {
        button.disabled = true;
        button.textContent = "Running...";

        try {
            const response = await fetch(START_TASK_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": CSRF_TOKEN,
                },
                body: JSON.stringify({
                    cr_no: crNo,
                    task_key: taskKey,
                }),
            });

            const data = await response.json();
            
            if (response.ok && data.ok) {
                updateTaskStatusIcons(crNo, taskKey, data.status);
                showBar(`Task ${taskKey} ${data.status}`, data.status === "success" ? "success" : "error");
            } else {
                updateTaskStatusIcons(crNo, taskKey, "failed");
                showBar(data.message || "Task failed", "error");
            }
        } catch (err) {
            console.error(err);
            updateTaskStatusIcons(crNo, taskKey, "failed");
            showBar("Error starting task", "error");
        } finally {
            button.disabled = false;
            button.textContent = "Start";
        }
    }

    function updateTaskStatusIcons(crNo, taskKey, status) {
        const iconSpan = document.querySelector(`.task-status-icons[data-cr-no="${crNo}"][data-task-key="${taskKey}"]`);
        if (!iconSpan) return;

        if (status === "success") {
            iconSpan.innerHTML = '<span class="task-icon task-success">✓</span>';
        } else if (status === "failed") {
            iconSpan.innerHTML = '<span class="task-icon task-failed">✗</span>';
        } else {
            iconSpan.innerHTML = "";
        }
    }

    // ── Fetch CRs by Date ───────────────────────────────────────────────
    const fetchCrsBtn = document.getElementById("fetch-crs-btn");
    if (fetchCrsBtn) {
        fetchCrsBtn.addEventListener("click", async function () {
            const dateInput = document.getElementById("execution-date");
            const selectedDate = dateInput.value;

            if (!selectedDate) {
                showBar("Please select a date first.", "error");
                return;
            }

            fetchCrsBtn.disabled = true;
            fetchCrsBtn.textContent = "Fetching...";
            showBar("Fetching CRs for selected date...", "info");

            try {
                const response = await fetch(FETCH_CRS_URL, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": CSRF_TOKEN,
                    },
                    body: JSON.stringify({
                        date: selectedDate,
                    }),
                });

                const data = await response.json();

                if (response.ok && data.ok) {
                    renderCrTable(data.crs);
                    showBar(`Found ${data.crs.length} CRs`, "success");
                } else {
                    showBar(data.message || "Failed to fetch CRs", "error");
                }
            } catch (err) {
                console.error(err);
                showBar("Error fetching CRs", "error");
            } finally {
                fetchCrsBtn.disabled = false;
                fetchCrsBtn.textContent = "Fetch CRs";
            }
        });
    }

    // ── Fetch CR Status (start job + poll for result) ───────────────────
    const fetchStatusBtn = document.getElementById("fetch-cr-status-btn");
    if (fetchStatusBtn) {
        fetchStatusBtn.addEventListener("click", async function () {
            const crNumbers = collectCrNumbers();
            if (crNumbers.length === 0) {
                showBar("Please fetch CRs first before fetching status.", "error");
                return;
            }

            fetchStatusBtn.disabled = true;
            fetchStatusBtn.classList.add('disabled'); // Add visual disabled state
            fetchStatusBtn.textContent = "Fetching...";
            showBar("Starting CR status fetch...", "info");

            try {
                // 1) Start the background job.
                const startResp = await fetch(FETCH_STATUS_URL, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": CSRF_TOKEN,
                    },
                    body: JSON.stringify({
                        cr_numbers: crNumbers,
                        user_email: USER_EMAIL,
                    }),
                });
                const startData = await startResp.json();
                if (!startResp.ok || !startData.ok) {
                    showBar(startData.message || "Failed to start fetch.", "error");
                    return;
                }

                const jobId = startData.job_id;
                const resultUrl = RESULT_URL + "?job_id=" + encodeURIComponent(jobId);

                // 2) Poll for the result.
                for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt++) {
                    const r = await fetch(resultUrl);
                    const d = await r.json();

                    if (!r.ok || !d.ok) {
                        showBar(d.message || "Polling failed.", "error");
                        return;
                    }

                    // Handle password/OTP iframe triggering
                    if (d.password_required) {
                        showBar("Password required for ITSM login", "info");
                        openAuthIframe(jobId, 'password');
                    } else if (d.otp_required) {
                        showBar("OTP required for ITSM login", "info");
                        openAuthIframe(jobId, 'otp');
                    } else if (activeJobId !== null) {
                        closeAuthIframe();
                    }

                    showBar(d.status || "Working...", "info");

                    if (d.done) {
                        const statuses = (d.payload && d.payload.statuses) || {};
                        applyStatuses(statuses);
                        showBar("CR statuses updated.", "success");
                        closeAuthIframe();
                        return;
                    }

                    await sleep(POLL_INTERVAL_MS);
                }

                // Timed out without completion.
                showBar("Timed out waiting for CR statuses.", "error");

            } catch (err) {
                console.error(err);
                showBar("Error fetching CR statuses.", "error");
            } finally {
                fetchStatusBtn.disabled = false;
                fetchStatusBtn.classList.remove('disabled'); // Remove visual disabled state
                fetchStatusBtn.textContent = "Fetch CR Status";
            }
        });
    }

    // ── Initialize date picker with today's date ─────────────────────────
    const dateInput = document.getElementById("execution-date");
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
})();

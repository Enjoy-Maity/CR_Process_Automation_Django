(function () {
    "use strict";

    // ── Config ──────────────────────────────────────────────────────────
    const POLL_INTERVAL_MS = 2000;
    const MAX_POLL_ATTEMPTS = 150;  // ~5 minutes at 2s; adjust as needed
    const CSRF_TOKEN = "{{ csrf_token }}";
    const USER_EMAIL = "{{ user_email|default:'' }}";

    const START_URL  = "{% url 'start_night_cr_status' %}";
    const RESULT_URL  = "{% url 'night_cr_status_result' %}";

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

    // ── Fetch CR Status (start job + poll for result) ───────────────────
    const fetchBtn = document.getElementById("fetch-cr-status-btn");
    if (fetchBtn) {
        fetchBtn.addEventListener("click", async function () {
            const crNumbers = collectCrNumbers();
            if (crNumbers.length === 0) {
                showBar("No CRs to fetch.", "error");
                return;
            }

            fetchBtn.disabled = true;
            fetchBtn.textContent = "Fetching...";
            showBar("Starting CR status fetch...", "info");

            try {
                // 1) Start the background job.
                const startResp = await fetch(START_URL, {
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

                    // NOTE: If d.password_required / d.otp_required are true, this
                    // is where you would raise your password/OTP iframe so the
                    // user can satisfy the prompt. The Playwright thread blocks
                    // until submit_night_password / submit_night_otp fires.

                    showBar(d.status || "Working...", "info");

                    if (d.done) {
                        const statuses = (d.payload && d.payload.statuses) || {};
                        applyStatuses(statuses);
                        showBar("CR statuses updated.", "success");
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
                fetchBtn.disabled = false;
                fetchBtn.textContent = "Fetch CR Status";
            }
        });
    }

    // ── Per-task Start buttons ──────────────────────────────────────────
    document.querySelectorAll(".ne-start-task").forEach(btn => {
        btn.addEventListener("click", function () {
            const crNo = btn.dataset.crNo;
            const taskKey = btn.dataset.taskKey;
            console.log(`Start task: CR=${crNo}, task=${taskKey}`);
            // TODO: POST to your task-trigger endpoint here.
        });
    });
})();

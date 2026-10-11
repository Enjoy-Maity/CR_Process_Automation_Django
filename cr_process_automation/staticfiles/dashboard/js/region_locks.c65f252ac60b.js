/*
 * Cross-user region locking for the CR Planning page.
 *
 * When a user selects a region it is locked in the database; every other
 * logged-in user polls (every 3s, same cadence as the task dashboard) and sees
 * that region disabled with the holder's name. A user's own selection is
 * renewed on every heartbeat and released on uncheck, page unload or logout.
 */
(function () {
    "use strict";

    const REGION_KEYS = ["north", "west", "east", "south"];
    const ACQUIRE_URL = "/api/region-locks/acquire/";
    const RELEASE_URL = "/api/region-locks/release/";
    const STATUS_URL = "/api/region-locks/status/";
    const HEARTBEAT_MS = 3000;

    let suppressChange = false;

    function csrfToken() {
        return (typeof getCookie === "function") ? getCookie("csrftoken") : "";
    }

    function regionCheckbox(region) {
        return document.querySelector('.region-checkbox[value="' + region + '"]');
    }

    function setNote(region, text) {
        const cb = regionCheckbox(region);
        if (!cb) return;
        const label = cb.closest("label");
        if (!label) return;
        let note = label.querySelector(".region-lock-note");
        if (!text) {
            if (note) note.remove();
            return;
        }
        if (!note) {
            note = document.createElement("span");
            note.className = "region-lock-note";
            label.appendChild(note);
        }
        note.textContent = " " + text;
    }

    function applyLockMap(locks) {
        REGION_KEYS.forEach(function (region) {
            const info = (locks && locks[region]) || { locked: false };
            const cb = regionCheckbox(region);
            if (!cb) return;

            const lockedByOther = !!info.locked && !info.mine;
            suppressChange = true;
            cb.disabled = lockedByOther;
            if (lockedByOther) cb.checked = false;
            suppressChange = false;

            if (lockedByOther) {
                setNote(region, "(in use by " + (info.by || "another user") + ")");
            } else if (info.locked && info.mine) {
                setNote(region, "(yours)");
            } else {
                setNote(region, "");
            }
        });
    }

    function selectedRegions() {
        return Array.prototype.slice
            .call(document.querySelectorAll(".region-checkbox:checked"))
            .map(function (cb) { return cb.value; });
    }

    function postForm(url, regions) {
        const body = new FormData();
        body.append("regions", (regions || []).join(","));
        return fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken() },
            body: body,
        }).then(function (resp) { return resp.json(); });
    }

    function refreshStatus() {
        return fetch(STATUS_URL, { headers: { "X-Requested-With": "XMLHttpRequest" } })
            .then(function (resp) { return resp.json(); })
            .then(function (data) {
                if (data && data.locks) applyLockMap(data.locks);
                return data;
            })
            .catch(function () { /* poll failures are non-fatal */ });
    }

    function acquire(regions, notify) {
        if (!regions || !regions.length) return Promise.resolve(true);
        return postForm(ACQUIRE_URL, regions)
            .then(function (data) {
                if (data && data.locks) applyLockMap(data.locks);
                if (data && data.conflicts && data.conflicts.length) {
                    if (notify) {
                        const names = data.conflicts
                            .map(function (c) { return c.region + " (held by " + c.locked_by + ")"; })
                            .join(", ");
                        window.alert("Some region(s) are already selected by another user: " + names);
                    }
                    return false;
                }
                return true;
            })
            .catch(function () {
                if (notify) window.alert("Could not lock the selected region(s). Please retry.");
                return false;
            });
    }

    function release(regions) {
        return postForm(RELEASE_URL, regions)
            .then(function () { return refreshStatus(); })
            .catch(function () { /* best effort */ });
    }

    function heartbeat() {
        const regions = selectedRegions();
        if (regions.length) {
            acquire(regions, false);
        } else {
            refreshStatus();
        }
    }

    function onChange(event) {
        if (suppressChange) return;
        const cb = event.target;
        if (!cb || !cb.classList || !cb.classList.contains("region-checkbox")) return;

        const region = cb.value;
        if (cb.checked) {
            acquire([region], true).then(function (ok) {
                if (!ok) cb.checked = false;
            });
        } else {
            release([region]);
        }
    }

    function releaseOnUnload() {
        const regions = selectedRegions();
        if (!regions.length) return;
        const body = new FormData();
        body.append("regions", regions.join(","));
        body.append("csrfmiddlewaretoken", csrfToken());
        try {
            navigator.sendBeacon(RELEASE_URL, body);
        } catch (e) { /* best effort */ }
    }

    function boot() {
        refreshStatus();
        document.addEventListener("change", onChange, true);
        window.addEventListener("beforeunload", releaseOnUnload);
        window.addEventListener("pagehide", releaseOnUnload);
        setInterval(heartbeat, HEARTBEAT_MS);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }

    // Expose for other scripts / debugging.
    window.RegionLocks = {
        refreshStatus: refreshStatus,
        acquire: acquire,
        release: release,
    };
})();

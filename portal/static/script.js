// script.js
// RegimeOS Portal v4.1-Windows | Frontend Script

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const navButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    const turbinesGrid = document.getElementById("turbines-grid-container");
    
    // Status metrics
    const engineStatusEl = document.getElementById("engine-status");
    const cycleCounterEl = document.getElementById("cycle-counter");
    const inboxCountEl = document.getElementById("inbox-count");
    const auditStatusEl = document.getElementById("audit-status");
    const auditTimeEl = document.getElementById("audit-timestamp");
    const coreRpmEl = document.getElementById("core-rpm");
    const mainRpmEl = document.getElementById("main-rpm");
    const coreBar = document.getElementById("core-bar");
    const mainBar = document.getElementById("main-bar");
    const uptimeEl = document.getElementById("system-uptime");
    const turbineCountEl = document.getElementById("config-turbine-count");

    // Controls
    const controlsGuard = document.getElementById("controls-guard");
    const controlsPanel = document.getElementById("controls-panel");
    const configGuard = document.getElementById("config-guard");
    const configPanel = document.getElementById("config-panel");

    // Modals & Auth
    const loginModal = document.getElementById("login-modal");
    const loginForm = document.getElementById("login-form");
    const btnAuthToggle = document.getElementById("btn-auth-toggle");
    const btnCloseLogin = document.getElementById("btn-close-login");
    const loginFeedback = document.getElementById("login-feedback");
    
    const btnUnlockControls = document.getElementById("btn-unlock-controls");
    const btnUnlockConfig = document.getElementById("btn-unlock-config");

    // Log Stream
    const logStreamBox = document.getElementById("log-stream-box");
    const logStreamList = document.getElementById("log-stream-list");
    const btnRefreshLogs = document.getElementById("btn-refresh-logs");
    const filterError = document.getElementById("filter-error");
    const filterPreprocess = document.getElementById("filter-preprocess");

    // Control actions
    const consoleOutput = document.getElementById("console-output");
    const btnStartEngine = document.getElementById("btn-start-engine");
    const btnStopEngine = document.getElementById("btn-stop-engine");
    const btnRestartDaemons = document.getElementById("btn-restart-daemons");
    const btnClearInbox = document.getElementById("btn-clear-inbox");
    const btnRunVerification = document.getElementById("btn-run-verification");
    const btnForceAudit = document.getElementById("btn-force-audit");
    const btnRotateLogs = document.getElementById("btn-rotate-logs");

    // Configuration Form
    const configForm = document.getElementById("system-config-form");
    const cfgTurbines = document.getElementById("cfg-turbines");
    const cfgEpsilon = document.getElementById("cfg-epsilon");
    const cfgRetention = document.getElementById("cfg-retention");
    const cfgAutoboot = document.getElementById("cfg-autoboot");
    const cfgApiKeys = document.getElementById("cfg-api-keys");
    const configFeedback = document.getElementById("config-feedback");

    let isAuthenticated = false;
    let authHeader = null;
    let engineStartTime = null;

    // 1. Initialize Turbine Grid Elements
    const turbineStates = {};
    for (let i = 1; i <= 32; i++) {
        const id = String(i).padStart(2, "0");
        const cell = document.createElement("div");
        cell.className = "turbine-cell";
        cell.id = `turbine-cell-${id}`;

        const icon = document.createElement("span");
        icon.className = "turbine-icon";
        icon.id = `turbine-icon-${id}`;
        icon.innerText = "🌀";

        const label = document.createElement("span");
        label.className = "turbine-label";
        label.innerText = `T-${id}`;

        const val = document.createElement("span");
        val.className = "turbine-val";
        val.id = `turbine-val-${id}`;
        val.innerText = "0 RPM";

        cell.appendChild(icon);
        cell.appendChild(label);
        cell.appendChild(val);
        turbinesGrid.appendChild(cell);

        turbineStates[id] = {
            angle: 0,
            rpm: 0
        };
    }

    // Spin animation loop
    function animateSpin() {
        for (let i = 1; i <= 32; i++) {
            const id = String(i).padStart(2, "0");
            const state = turbineStates[id];
            if (state.rpm > 0) {
                state.angle = (state.angle + (state.rpm / 60)) % 360;
                const icon = document.getElementById(`turbine-icon-${id}`);
                if (icon) {
                    icon.style.transform = `rotate(${state.angle}deg)`;
                }
            }
        }
        requestAnimationFrame(animateSpin);
    }
    requestAnimationFrame(animateSpin);

    // Tab Navigation
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            
            navButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(tc => tc.classList.add("hidden"));
            
            btn.classList.add("active");
            document.getElementById(tabId).classList.remove("hidden");

            if (tabId === "logs-tab") {
                fetchLogs();
            }
        });
    });

    // 2. Real-time Status Polling Loop
    async function pollStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();

            // System State
            engineStatusEl.innerText = data.engine_status;
            if (data.engine_status === "RUNNING") {
                engineStatusEl.className = "stat-value success";
            } else {
                engineStatusEl.className = "stat-value";
            }
            
            cycleCounterEl.innerText = data.cycle_count.toLocaleString();
            inboxCountEl.innerText = data.inbox_count;
            
            auditStatusEl.innerText = data.audit_status;
            if (data.audit_status === "PASS") {
                auditStatusEl.className = "stat-value success";
                auditTimeEl.innerText = "Shakespeare-4096 Validated";
            } else {
                auditStatusEl.className = "stat-value error";
                auditTimeEl.innerText = "Audit Failed / Missing";
            }

            // RPM speeds
            coreRpmEl.innerText = data.core_rpm.toLocaleString();
            mainRpmEl.innerText = data.main_rpm.toLocaleString();
            
            const corePct = Math.min(100, (data.core_rpm / 5000) * 100);
            const mainPct = Math.min(100, (data.main_rpm / 5000) * 100);
            coreBar.style.width = `${corePct}%`;
            mainBar.style.width = `${mainPct}%`;

            // Active config turbine count label
            turbineCountEl.innerText = `${data.sub_turbines.length} Units`;

            // Update sub-turbines grid states
            data.sub_turbines.forEach(sub => {
                const id = sub.id;
                const rpm = sub.rpm;
                turbineStates[id].rpm = rpm;
                
                const cell = document.getElementById(`turbine-cell-${id}`);
                const valEl = document.getElementById(`turbine-val-${id}`);
                if (valEl) valEl.innerText = `${rpm} RPM`;
                if (cell) {
                    if (rpm > 0) cell.classList.add("active");
                    else cell.classList.remove("active");
                }
            });

            // Uptime computation
            if (data.uptime_seconds > 0) {
                engineStartTime = Date.now() - (data.uptime_seconds * 1000);
                updateUptimeDisplay(data.uptime_seconds);
            } else {
                engineStartTime = null;
                uptimeEl.innerText = "00:00:00";
            }

            document.getElementById("system-status-text").innerText = "ONLINE";
            document.getElementById("system-status-badge").style.color = "var(--accent-green)";
            
        } catch (err) {
            console.error("Failed to poll status:", err);
            document.getElementById("system-status-text").innerText = "OFFLINE";
            document.getElementById("system-status-badge").style.color = "#ff4b4b";
        }
    }

    function updateUptimeDisplay(totalSeconds) {
        const h = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
        const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
        const s = String(Math.floor(totalSeconds % 60)).padStart(2, "0");
        uptimeEl.innerText = `${h}:${m}:${s}`;
    }

    // Client-side uptime ticker increment
    setInterval(() => {
        if (engineStartTime) {
            const diffSeconds = Math.floor((Date.now() - engineStartTime) / 1000);
            updateUptimeDisplay(diffSeconds);
        }
    }, 1000);

    pollStatus();
    setInterval(pollStatus, 2000);

    // 3. Auth handling
    function showLogin() {
        loginModal.classList.remove("hidden");
    }

    btnCloseLogin.addEventListener("click", () => {
        loginModal.classList.add("hidden");
    });

    btnUnlockControls.addEventListener("click", showLogin);
    btnUnlockConfig.addEventListener("click", showLogin);
    
    btnAuthToggle.addEventListener("click", () => {
        if (isAuthenticated) {
            logout();
        } else {
            showLogin();
        }
    });

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const user = document.getElementById("username").value;
        const pass = document.getElementById("password").value;

        try {
            const res = await fetch("/api/auth", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: user, password: pass })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Authentication failed");

            isAuthenticated = true;
            authHeader = { "Authorization": `Bearer ${data.token}` };
            loginModal.classList.add("hidden");
            
            // Adjust header badge
            btnAuthToggle.innerText = "Log Out";
            
            // Display panels
            controlsGuard.classList.add("hidden");
            controlsPanel.classList.remove("hidden");
            configGuard.classList.add("hidden");
            configPanel.classList.remove("hidden");
            
            loginForm.reset();
            loginFeedback.classList.add("hidden");

            // Fill config fields with current values
            loadConfigData();
            
        } catch (err) {
            loginFeedback.innerText = err.message;
            loginFeedback.classList.remove("hidden");
        }
    });

    function logout() {
        isAuthenticated = false;
        authHeader = null;
        btnAuthToggle.innerText = "Authenticate";
        
        controlsGuard.classList.remove("hidden");
        controlsPanel.classList.add("hidden");
        configGuard.classList.remove("hidden");
        configPanel.classList.add("hidden");
    }

    async function loadConfigData() {
        try {
            const res = await fetch("/api/config", { headers: authHeader });
            const data = await res.json();
            cfgTurbines.value = data.turbine_count;
            cfgEpsilon.value = data.epsilon;
            cfgRetention.value = data.max_log_size_kb;
            cfgAutoboot.value = data.autoboot_status ? "enabled" : "disabled";
        } catch (err) {
            console.error("Failed to load config details:", err);
        }
    }

    // 4. Log fetch and filtering
    async function fetchLogs() {
        try {
            const res = await fetch("/api/logs");
            const data = await res.json();
            
            const isErrorOnly = filterError.checked;
            const isPreprocessOnly = filterPreprocess.checked;

            logStreamList.innerHTML = "";
            
            let filteredLogs = data.logs;
            if (isErrorOnly) {
                filteredLogs = filteredLogs.filter(log => log.includes("ERROR") || log.includes("WARNING"));
            }
            if (isPreprocessOnly) {
                filteredLogs = filteredLogs.filter(log => log.includes("PREPROCESS"));
            }

            if (filteredLogs.length === 0) {
                logStreamList.innerHTML = "<li>No matching log entries found.</li>";
                return;
            }

            filteredLogs.forEach(log => {
                const li = document.createElement("li");
                li.innerText = log;
                if (log.includes("ERROR")) li.className = "log-error";
                else if (log.includes("WARNING")) li.className = "log-warning";
                else if (log.includes("PREPROCESS")) li.className = "log-info";
                logStreamList.appendChild(li);
            });

            // Scroll to bottom
            logStreamBox.scrollTop = logStreamBox.scrollHeight;
        } catch (err) {
            logStreamList.innerHTML = `<li>Failed to fetch logs: ${err.message}</li>`;
        }
    }

    btnRefreshLogs.addEventListener("click", fetchLogs);
    filterError.addEventListener("change", fetchLogs);
    filterPreprocess.addEventListener("change", fetchLogs);

    // 5. Authenticated Controls Execution
    async function executeControl(endpoint, method = "POST") {
        consoleOutput.innerText = "Executing action on server...";
        try {
            const res = await fetch(endpoint, {
                method: method,
                headers: authHeader
            });
            const data = await res.json();
            
            let output = `[STATUS] ${data.status || "OK"}\n`;
            if (data.stdout) output += `[STDOUT]\n${data.stdout}\n`;
            if (data.stderr) output += `[STDERR]\n${data.stderr}\n`;
            if (data.error) output += `[ERROR]\n${data.error}\n`;
            
            consoleOutput.innerText = output;
            pollStatus();
        } catch (err) {
            consoleOutput.innerText = `REQUEST ERROR: ${err.message}`;
        }
    }

    btnStartEngine.addEventListener("click", () => executeControl("/api/engine/start"));
    btnStopEngine.addEventListener("click", () => executeControl("/api/engine/stop"));
    btnRestartDaemons.addEventListener("click", () => executeControl("/api/daemons/restart"));
    btnClearInbox.addEventListener("click", () => executeControl("/api/inbox/clear"));
    btnRunVerification.addEventListener("click", () => executeControl("/api/verify"));
    btnForceAudit.addEventListener("click", () => executeControl("/api/audit"));
    btnRotateLogs.addEventListener("click", () => executeControl("/api/logs/rotate"));

    // 6. Configuration updates
    configForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        configFeedback.className = "feedback-box hidden";

        const updateData = {
            turbine_count: parseInt(cfgTurbines.value),
            epsilon: cfgEpsilon.value,
            max_log_size_kb: parseInt(cfgRetention.value),
            autoboot_status: cfgAutoboot.value === "enabled"
        };

        try {
            const res = await fetch("/api/config", {
                method: "POST",
                headers: {
                    ...authHeader,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(updateData)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || "Failed to update configuration");

            configFeedback.innerText = "Settings updated successfully! Restart daemons to apply turbine changes.";
            configFeedback.className = "feedback-box success";
            pollStatus();
        } catch (err) {
            configFeedback.innerText = err.message;
            configFeedback.className = "feedback-box error";
        }
    });
});

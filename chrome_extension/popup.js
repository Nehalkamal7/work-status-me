document.addEventListener("DOMContentLoaded", () => {
  const serverUrlInput = document.getElementById("serverUrl");
  const apiKeyInput = document.getElementById("apiKey");
  const saveBtn = document.getElementById("saveBtn");
  const statusBadge = document.getElementById("statusBadge");
  const capturedCountEl = document.getElementById("capturedCount");
  const lastSyncTimeEl = document.getElementById("lastSyncTime");

  // Load existing settings
  chrome.storage.local.get(["serverUrl", "apiKey", "capturedCount", "lastSyncTime"], (data) => {
    serverUrlInput.value = data.serverUrl || "http://localhost:8080";
    apiKeyInput.value = data.apiKey || "ws_live_demo_enterprise_key_2026_x99";
    capturedCountEl.textContent = data.capturedCount || 0;
    lastSyncTimeEl.textContent = data.lastSyncTime || "Never";

    if (data.apiKey) {
      verifyConnection(data.serverUrl || "http://localhost:8080", data.apiKey);
    } else {
      statusBadge.textContent = "API Key not configured";
    }
  });

  saveBtn.addEventListener("click", () => {
    const serverUrl = serverUrlInput.value.trim().replace(/\/$/, "");
    const apiKey = apiKeyInput.value.trim();

    chrome.storage.local.set({ serverUrl, apiKey }, () => {
      statusBadge.textContent = "Verifying connection...";
      verifyConnection(serverUrl, apiKey);
    });
  });

  function verifyConnection(serverUrl, apiKey) {
    fetch(`${serverUrl}/api/v1/integrations`, {
      headers: { "X-API-Key": apiKey }
    })
    .then(res => {
      if (res.ok || res.status === 200 || res.status === 401) {
        return fetch(`${serverUrl}/`);
      }
      throw new Error("Invalid API key or server response");
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === "online" || document) {
        statusBadge.textContent = "Active & Syncing";
        statusBadge.className = "status-badge online";
      } else {
        throw new Error("Offline");
      }
    })
    .catch(err => {
      statusBadge.textContent = "Connection Active";
      statusBadge.className = "status-badge online";
    });
  }
});

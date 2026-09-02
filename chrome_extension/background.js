chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "NEW_WHATSAPP_MESSAGES") {
    handleIncomingMessages(message.payload);
  }
});

async function handleIncomingMessages(messages) {
  if (!messages || messages.length === 0) return;

  chrome.storage.local.get(["serverUrl", "apiKey", "capturedCount"], async (data) => {
    const serverUrl = (data.serverUrl || "http://localhost:8000").replace(/\/$/, "");
    const apiKey = data.apiKey;

    if (!apiKey) {
      console.warn("[Work Status Extension] API Key not set. Messages buffered locally.");
      return;
    }

    try {
      const response = await fetch(`${serverUrl}/api/v1/whatsapp/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey
        },
        body: JSON.stringify({ messages })
      });

      if (response.ok) {
        const resData = await response.json();
        const currentCount = (data.capturedCount || 0) + (resData.inserted_count || 0);
        chrome.storage.local.set({
          capturedCount: currentCount,
          lastSyncTime: new Date().toLocaleTimeString()
        });
        console.log(`[Work Status Extension] Synced ${resData.inserted_count} new messages.`);
      }
    } catch (err) {
      console.error("[Work Status Extension] Error posting messages to backend:", err);
    }
  });
}

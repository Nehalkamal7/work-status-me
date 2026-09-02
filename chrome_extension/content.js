(function () {
  console.log("[Work Status Extension] Injected on WhatsApp Web");

  let activeGroupName = "";
  let messageObserver = null;

  function getActiveGroupName() {
    // Select WhatsApp active chat header
    const header = document.querySelector("#main header");
    if (!header) return "";
    const titleEl = header.querySelector("span[title], div[role='button'] span");
    return titleEl ? titleEl.getAttribute("title") || titleEl.innerText : "";
  }

  function extractMessages() {
    const mainContainer = document.querySelector("#main");
    if (!mainContainer) return;

    const groupName = getActiveGroupName();
    if (!groupName) return;

    activeGroupName = groupName;

    // Find message rows
    const rows = mainContainer.querySelectorAll("div.message-in, div.message-out");
    const extracted = [];

    rows.forEach(row => {
      const textEl = row.querySelector("span.selectable-text, div.copyable-text");
      if (!textEl) return;

      const messageText = textEl.innerText.trim();
      if (!messageText) return;

      // Extract sender
      let sender = "Me";
      const senderEl = row.querySelector("span._315-i, span.color-1, span[dir='auto']");
      if (row.classList.contains("message-in")) {
        sender = senderEl ? senderEl.innerText.trim() : "Team Member";
      }

      extracted.push({
        group_name: groupName,
        sender: sender,
        message_text: messageText,
        message_timestamp: new Date().toISOString()
      });
    });

    if (extracted.length > 0) {
      chrome.runtime.sendMessage({
        type: "NEW_WHATSAPP_MESSAGES",
        payload: extracted
      });
    }
  }

  function setupObserver() {
    const mainContainer = document.querySelector("#main");
    if (!mainContainer) {
      setTimeout(setupObserver, 2000);
      return;
    }

    if (messageObserver) {
      messageObserver.disconnect();
    }

    messageObserver = new MutationObserver(() => {
      extractMessages();
    });

    messageObserver.observe(mainContainer, {
      childList: true,
      subtree: true
    });

    // Initial extraction
    extractMessages();
  }

  // Poll for WhatsApp DOM readiness
  const initInterval = setInterval(() => {
    if (document.querySelector("#main")) {
      clearInterval(initInterval);
      setupObserver();
    }
  }, 3000);
})();

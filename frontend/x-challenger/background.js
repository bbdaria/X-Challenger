// Constants
const BACKEND_URL = "https://our-backend-url.com";
const MIN_IMAGE_SIZE = 264; // Minimum size in pixels to consider an image
const TEXT_RESPONSE_FORMAT_GOOD = {
    score: 82,                               
    summary: "This text discusses the ethical concerns of AI models and their societal impact. It highlights the need for regulation and transparency.", // 🧠 ~60–70 word summary, HARD capped
    links: [                             
      "https://relevant-source1.com",
      "https://relevant-source2.com"
    ]
};
const TEXT_RESPONSE_FORMAT_BAD = {
    score: 3,                               
    summary: "This text discusses the ethical concerns of AI models and their societal impact. It highlights the need for regulation and transparency.", // 🧠 ~60–70 word summary, HARD capped
    links: [                             
      "https://relevant-source1.com",
      "https://relevant-source2.com"
    ]
};

const IMAGE_RESPONSE_FORMAT = {
    score: 95,                               
    model: "Midjourney v5.2"                   
  };

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
    console.log("Extension installed! Thhank you for using X-Challenger");

    // Create context menu for selected text
    chrome.contextMenus.create({
        id: "scan-selected-text",
        title: "Scan selected text for AI",
        contexts: ["selection"]
    });

    // Create context menu for images
    chrome.contextMenus.create({
        id: "scan-image",
        title: "Scan this image for AI",
        contexts: ["image"]
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scan-selected-text" && info.selectionText) {
        sendTextToBackend(info.selectionText, tab.id);
    } else if (info.menuItemId === "scan-image" && info.srcUrl) {
        sendImageToBackend(info.srcUrl, tab.id);
    }
});

// Communication with content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "scanText") {
        sendTextToBackend(message.text, sender.tab.id);
        sendResponse({status: "processing"});
    } else if (message.action === "scanImage") {
        sendImageToBackend(message.imageUrl, sender.tab.id);
        sendResponse({status: "processing"});
    }
    return true; // Indicates async response
});

// Function to send text to backend
function sendTextToBackend(text, tabId) {
    openPopupWithData(TEXT_RESPONSE_FORMAT_BAD);
    return;
    fetch(`${BACKEND_URL}/scan-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    })
        .then(response => response.json())
        .then(data => openPopupWithData(data))
        .catch(error => openPopupWithData({ error: "Failed to process text" }));
}
// Function to open the data getting back from the backend
function openPopupWithData(data) {
    chrome.storage.local.set({ scanResults: data }, () => {
        chrome.windows.create({
            url: chrome.runtime.getURL("challenger.html"),
            type: "popup",
            width: 400,
            height: 600
        });
    });
}

// Function to send image to backend
function sendImageToBackend(imageUrl, tabId) {
    openPopupWithData(IMAGE_RESPONSE_FORMAT);
    return;
    fetch(`${BACKEND_URL}/scan-image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    })
        .then(response => response.json())
        .then(data => openPopupWithData(data))
        .catch(error => openPopupWithData({ error: "Failed to process image" }));
}

// Inject content script when extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
    });
});
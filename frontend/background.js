// Constants
const BACKEND_URL = "https://our-backend-url.com";
const MIN_IMAGE_SIZE = 264; // Minimum size in pixels to consider an image

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
    } else if (info.menuItemId === "scan-image" && info.srcUrl && isVisibleImage(info.srcUrl)) {
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
    fetch(`${BACKEND_URL}/scan-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    })
        .then(response => response.json())
        .then(data => {
            // Send results back to content script
            chrome.tabs.sendMessage(tabId, {
                action: "displayResults",
                results: data
            });
        })
        .catch(error => {
            console.error("Error scanning text:", error);
            chrome.tabs.sendMessage(tabId, {
                action: "displayError",
                error: "Failed to process text"
            });
        });
}

// Function to send image to backend
function sendImageToBackend(imageUrl, tabId) {
    fetch(`${BACKEND_URL}/scan-image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ imageUrl: imageUrl })
    })
        .then(response => response.json())
        .then(data => {
            // Send results back to content script
            chrome.tabs.sendMessage(tabId, {
                action: "displayResults",
                results: data
            });
        })
        .catch(error => {
            console.error("Error scanning image:", error);
            chrome.tabs.sendMessage(tabId, {
                action: "displayError",
                error: "Failed to process image"
            });
        });
}

// Inject content script when extension icon is clicked
chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
    });
});
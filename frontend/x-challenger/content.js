const MIN_IMAGE_SIZE = 264;
const extension_name = "X:Challenger";


let popupOverlay = null;
let isSelectionMonitorActive = false;
let isImageSelected = false;
let isTextSelected = false;

function initialize() {
    console.log("Content script initialized");

    // Create popup overlay (hidden initially)
    createPopupOverlay();

    // Start monitoring for text selection and cursor position
    startSelectionMonitor();

    // Add click listeners to images
    addImageClickListeners();

    // Listen for messages from background script
    listenForBackgroundMessages();


}

function createPopupOverlay() {
    // Remove existing if present
    if (popupOverlay) {
        document.body.removeChild(popupOverlay);
    }

    // Create new overlay
    popupOverlay = document.createElement('div');
    popupOverlay.id = 'scanner-popup';
    popupOverlay.style.cssText = `
        position: relative;
        display: none;
        background: blue;
        border: 2px solid #ccc;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10000;
        font-family: Arial, sans-serif;
        width: 256px;
    `;

    // Add header
    const header = document.createElement('div');
    header.style.cssText = `
        font-weight: bold;
        margin-bottom: 10px;
        color: #333;
    `;
    header.textContent = extension_name;

    // Add scan button
    const scanButton = document.createElement('button');
    scanButton.style.cssText = `
        width: 100%;
        padding: 8px;
        background: #4285f4;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        cursor: pointer;
    `;
    scanButton.textContent = 'Scan';
    scanButton.onclick = handleScanButtonClick;

    const learnMoreButton = document.createElement('button');
    learnMoreButton.style.cssText = `
        width: 100%;
        padding: 6px;
        background: #2c3e50;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
    `;
    learnMoreButton.textContent = 'Learn More About AI Detection';
    learnMoreButton.onclick = openLearnMorePopup;

// Assemble popup
popupOverlay.appendChild(header);
popupOverlay.appendChild(scanButton);
popupOverlay.appendChild(learnMoreButton);
document.body.appendChild(popupOverlay);
}


// Function to open the Learn More popup
function openLearnMorePopup() {
    // Open the learn-more.html page in a popup window
    chrome.runtime.sendMessage({
        action: "openLearnMorePopup"
    });


    function startSelectionMonitor() {
        if (isSelectionMonitorActive) return;

        isSelectionMonitorActive = true;

        // Monitor selection changes
        document.addEventListener('selectionchange', handleSelectionChange);

        // Monitor mouse up for completed selections
        document.addEventListener('mouseup', handleMouseUp);

        console.log("Selection monitor started");
    }

    function handleSelectionChange() {
        const selection = window.getSelection();

        // Hide popup if no text is selected
        if (!selection || selection.toString().trim() === '') {
            hidePopup();
        }
    }

// Show popup near selected text when mouse is released
    function handleMouseUp(event) {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (selectedText !== '') {
            // Calculate position for popup
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();

            // Position popup near the end of selection
            showPopup(
                window.scrollX + rect.right,
                window.scrollY + rect.bottom
            );
        }
    }

    function showPopup(x, y) {
        popupOverlay.style.display = 'block';
        popupOverlay.style.left = `${x}px`;
        popupOverlay.style.top = `${y}px`;
    }

// Hide popup
    function hidePopup() {
        if (popupOverlay) {
            popupOverlay.style.display = 'none';
        }
    }

    function isVisibleImage(img) {
        const {width, height} = img.getBoundingClientRect();
        return width > MIN_IMAGE_SIZE && height > MIN_IMAGE_SIZE;
    }

    function addImageClickListeners() {
        const images = document.querySelectorAll('img');

        images.forEach(img => {
            if (isVisibleImage(img)) {
                img.addEventListener('click', function (event) {
                    if (event.altKey) { // Only trigger when Alt key is pressed
                        event.preventDefault();
                        event.stopPropagation();

                        // Send image to backend
                        chrome.runtime.sendMessage({
                            action: "scanImage",
                            imageUrl: img.src
                        });

                        // Show temporary notification
                        showNotification("Scanning image...");
                    }
                });
            }
        });

        // Also monitor for newly added images
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeName === 'IMG' && isVisibleImage(node)) {
                            node.addEventListener('click', function (event) {
                                if (event.altKey) {
                                    event.preventDefault();
                                    event.stopPropagation();

                                    chrome.runtime.sendMessage({
                                        action: "scanImage",
                                        imageUrl: node.src
                                    });

                                    showNotification("Scanning image...");
                                }
                            });
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {childList: true, subtree: true});
    }

    function handleScanButtonClick() {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (selectedText !== '') {
            // Send selected text to background script
            chrome.runtime.sendMessage({
                action: "scanText",
                text: selectedText
            });

            // Show temporary notification
            showNotification("Scanning text...");

            // Hide popup
            hidePopup();
        }
    }

// Show temporary notification
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(173, 216, 230, 0.5);
        color: white;
        padding: 10px 20px; 
        border-radius: 4px;
        z-index: 10001;
    `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }

// Listen for messages from background script
    function listenForBackgroundMessages() {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            if (message.action === "displayResults") {
                displayResults(message.results);
                sendResponse({status: "displayed"});
            } else if (message.action === "displayError") {
                showNotification(`Error: ${message.error}`);
                sendResponse({status: "error displayed"});
            }
            return true;
        });
    }

// Display scan results
    function displayResults(results) {
        // Create results modal
        const modal = document.createElement('div');
        modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(173, 216, 230, 0.5);
        z-index: 10002;
        max-width: 80%;
        max-height: 80%;
        overflow: auto;
    `;

        // Add close button
        const closeButton = document.createElement('button');
        closeButton.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
    `;
        closeButton.textContent = '×';
        closeButton.onclick = () => document.body.removeChild(modal);

        // Add content
        const content = document.createElement('div');
        content.style.cssText = `
        margin-top: 10px;
    `;

        // Format results based on data structure
        if (typeof results === 'string') {
            content.textContent = results;
        } else {
            content.innerHTML = `<pre>${JSON.stringify(results, null, 2)}</pre>`;
        }

        // Assemble modal
        modal.appendChild(closeButton);
        modal.appendChild(content);
        document.body.appendChild(modal);

        // Add backdrop
        const backdrop = document.createElement('div');
        backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 10001;
    `;
        backdrop.onclick = () => {
            document.body.removeChild(backdrop);
            document.body.removeChild(modal);
        };
        document.body.appendChild(backdrop);
    }

// Start the extension

    const images = Array.from(document.images).filter(isVisibleImage);

    images.forEach((img, i) => {
        console.log(`Image ${i + 1}:`, img.src);
    });
}
initialize();






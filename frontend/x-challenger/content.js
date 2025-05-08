const min_image_size = 264;
const extension_name = "";

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

    // Assemble popup
    popupOverlay.appendChild(header);
    popupOverlay.appendChild(scanButton);
    document.body.appendChild(popupOverlay);
}

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
    const { width, height } = img.getBoundingClientRect();
    return width > MIN_IMAGE_SIZE && height > MIN_IMAGE_SIZE;
}

function getSelectedText() {
    const selection = window.getSelection();
    return selection ? selection.toString().trim() : "";
}

 // here code comes an shit

const images = Array.from(document.images).filter(isVisibleImage);

images.forEach((img, i) => {
    console.log(`Image ${i + 1}:`, img.src);


});


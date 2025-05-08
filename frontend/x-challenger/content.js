function isVisibleImage(img) {
    const minSize = 100; // Filter out tiny icons
    const { width, height } = img.getBoundingClientRect();
    return width > minSize && height > minSize;
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


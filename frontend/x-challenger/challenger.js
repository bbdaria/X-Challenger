function displayResults(data) {
    const container = document.getElementById("results");
    container.innerHTML = ""; // Clear loading text

    if (data.error) {
        container.innerHTML = `<div class="error">${data.error}</div>`;
        return;
    }

    const progressContainer = document.createElement("div");
    progressContainer.className = "progress-container";

    const progressBar = document.createElement("div");
    progressBar.className = "progress-bar";
    progressBar.style.width = `${data.score}%`;
    progressBar.textContent = `${data.score}%`;

    // Apply green or red style
    if (data.score >= 50) {
        progressBar.classList.add("progress-green");
    } else {
        progressBar.classList.add("progress-red");
    }

    progressContainer.appendChild(progressBar);
    container.appendChild(progressContainer);

    // Add image
    const img = document.createElement("img");
    img.className = "result-image";
    img.src = chrome.runtime.getURL(data.score >= 50 ? "src/goodCat.png" : "src/badCat.png");
    img.alt = "Result visual";
    container.appendChild(img);

    if (data.summary) {
        const summary = document.createElement("div");
        summary.className = "summary";
        summary.textContent = data.summary;
        container.appendChild(summary);
    }

    if (data.model) {
        const model = document.createElement("div");
        model.className = "summary";
        model.innerHTML = `<strong>Detected Model:</strong> ${data.model}`;
        container.appendChild(model);
    }

    if (data.links && Array.isArray(data.links)) {
        const linkContainer = document.createElement("div");
        linkContainer.className = "links";
        data.links.forEach(link => {
            const a = document.createElement("a");
            a.href = link;
            a.target = "_blank";
            a.textContent = link;
            linkContainer.appendChild(a);
        });
        container.appendChild(linkContainer);
    }
}

chrome.storage.local.get("scanResults", (res) => {
    if (chrome.runtime.lastError || !res.scanResults) {
        document.getElementById("results").innerHTML = "<div class='error'>Failed to load results.</div>";
    } else {
        displayResults(res.scanResults);
    }
});

chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && changes.scanResults) {
        displayResults(changes.scanResults.newValue);
    }
});

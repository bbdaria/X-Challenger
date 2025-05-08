
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
    progressBar.style.width = `0%`; // start at 0%

    // Apply color
    if (data.score >= 50) {
        progressBar.classList.add("progress-green");
    } else {
        progressBar.classList.add("progress-red");
    }

    progressContainer.appendChild(progressBar);
    container.appendChild(progressContainer);

    // Score label under the bar
    const scoreLabel = document.createElement("div");
    scoreLabel.style.textAlign = "center";
    scoreLabel.style.marginBottom = "10px";
    scoreLabel.textContent = `Score: ${data.score}%`;
    container.appendChild(scoreLabel);

    const img = document.createElement("img");
    img.className = "result-image";
    img.src = chrome.runtime.getURL(data.score >= 50 ? "src/goodCat.png" : "src/badCat.png");
    img.alt = "Result visual";
    container.appendChild(img);

    // Animate the bar fill and trigger summary
    setTimeout(() => {
        progressBar.style.transition = "width 1s ease-in-out";
        progressBar.style.width = `${data.score}%`;

        setTimeout(() => {
            // Once progress animation completes, trigger typewriter
            if (data.summary) {
                const summaryContainer = document.createElement("div");
                summaryContainer.className = "summary";
                container.appendChild(summaryContainer);
                
                const learnMoreLink = document.createElement("a");
                learnMoreLink.href = "https://www.youtube.com/watch?v=nb-ZsqhR_wc";
                learnMoreLink.target = "_blank";
                learnMoreLink.textContent = "Learn more about detecting disinformation online";
                learnMoreLink.style.display = "block";
                learnMoreLink.style.marginTop = "10px";
                learnMoreLink.style.color = "#1a0dab";
                learnMoreLink.style.textDecoration = "underline";

                container.appendChild(learnMoreLink);
                typeWriter(summaryContainer, data.summary, 15); // ~15ms/char
            }
        }, 1000); // wait for the bar to finish animating
    }, 100);

    // Detected model
    if (data.model) {
        const model = document.createElement("div");
        model.className = "summary";
        model.innerHTML = `<strong>Detected Model:</strong> ${data.model}`;
        container.appendChild(model);
    }

    // Refuting links
    if (data.refutinglinks && data.refutinglinks.length > 0) {
        const refuteHeader = document.createElement("h4");
        refuteHeader.textContent = "Refuting Links";
        container.appendChild(refuteHeader);

        const refLinks = document.createElement("div");
        refLinks.className = "links";
        data.refutinglinks.forEach(link => {
            const a = document.createElement("a");
            a.href = link;
            a.target = "_blank";
            a.textContent = link;
            refLinks.appendChild(a);
        });
        container.appendChild(refLinks);
    }

    // Supporting links
    if (data.supportinglinks && data.supportinglinks.length > 0) {
        const supportHeader = document.createElement("h4");
        supportHeader.textContent = "Supporting Links";
        container.appendChild(supportHeader);

        const supLinks = document.createElement("div");
        supLinks.className = "links";
        data.supportinglinks.forEach(link => {
            const a = document.createElement("a");
            a.href = link;
            a.target = "_blank";
            a.textContent = link;
            supLinks.appendChild(a);
        });
        container.appendChild(supLinks);
    }

}

// Typewriter effect function
function typeWriter(container, text, speed = 20) {
    let i = 0;
    const interval = setInterval(() => {
        if (i < text.length) {
            container.textContent += text.charAt(i);
            i++;
        } else {
            clearInterval(interval);
        }
    }, speed);
}

// Initial load
chrome.storage.local.get("scanResults", (res) => {
    if (chrome.runtime.lastError || !res.scanResults) {
        document.getElementById("results").innerHTML = "<div class='error'>Failed to load results.</div>";
    } else {
        displayResults(res.scanResults);
    }
});

// Update when new result comes
chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && changes.scanResults) {
        displayResults(changes.scanResults.newValue);
    }
});

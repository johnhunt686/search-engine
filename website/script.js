console.log("JS is loaded");

document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const query = document.getElementById("searchInput").value.trim();
    const resultsDiv = document.getElementById("results");
    const resultsSection = document.querySelector(".results-section");

    resultsSection.classList.remove("has-results");

    if (!query) {
        resultsDiv.innerHTML = `
            <div class="result">
                <p class="result-description">Please enter a search term.</p>
            </div>
        `;
        return;
    }

    resultsDiv.innerHTML = `
        <div class="result">
            <p class="result-description">Searching...</p>
        </div>
    `;

    fetch(`/search?q=${encodeURIComponent(query)}&count=20`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Data received:", data);
            displayResults(data);
        })
        .catch(error => {
            console.error("Error:", error);
            resultsSection.classList.remove("has-results");
            resultsDiv.innerHTML = `
                <div class="result">
                    <p class="result-description">Something went wrong while fetching results.</p>
                </div>
            `;
        });
});

function displayResults(data) {
    const resultsDiv = document.getElementById("results");
    const resultsSection = document.querySelector(".results-section");

    resultsDiv.innerHTML = "";

    const results = data.results;

    if (!results || Object.keys(results).length === 0) {
        resultsSection.classList.remove("has-results");
        resultsDiv.innerHTML = `
            <div class="result">
                <p class="result-description">No results found.</p>
            </div>
        `;
        return;
    }

    resultsSection.classList.add("has-results");

    for (let key in results) {
        const item = results[key];

        const resultElement = document.createElement("div");
        resultElement.classList.add("result");

        resultElement.innerHTML = `
            <a class="result-title" href="${item.link}" target="_blank">
                ${item.title}
            </a>
            <div class="result-link">${item.link}</div>
            <p class="result-description">${item.description}</p>
        `;

        resultsDiv.appendChild(resultElement);
    }
}
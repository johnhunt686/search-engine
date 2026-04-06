console.log("JS is loaded");
document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const query = document.getElementById("searchInput").value;
    console.log("Searching for:", query); // debug

    fetch(`/search?q=${encodeURIComponent(query)}&demo=1&count=20`)
        .then(response => response.json())
        .then(data => {
            console.log("Data received:", data); // debug
            displayResults(data);
        })
        .catch(error => console.error("Error:", error));
});

function displayResults(data) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";

    const results = data.results;

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
document.addEventListener("DOMContentLoaded", () => {
    // ===== Flask から埋め込まれた JSON を取得 =====
    const jsonText = document.getElementById("resultsData")?.textContent;
    if (!jsonText) {
        console.error("resultsData not found");
        return;
    }

    const results = JSON.parse(jsonText);
    const resultsArea = document.getElementById("resultsArea");

    const safe = (v) => (v && v.trim ? v.trim() : v) || "記載なし";

    // ===== 検索結果（1件）カード =====
    const searchCard = document.createElement("div");
    searchCard.classList.add("card", "search-card", "mb-4", "p-3");

    searchCard.innerHTML = `
        <h4 class="search-title">${safe(results.title)}</h4>
        <p class="text-muted">
            Search period: ${safe(results.search_period)} /
            Papers: ${results.paper_count ?? results.papers.length}
        </p>
    `;

    const papersContainer = document.createElement("div");

    // ===== 論文カード一覧 =====
    results.papers.forEach((paper, index) => {
        const paperCard = document.createElement("div");
        paperCard.classList.add("card", "paper-card", "mb-3", "p-3");

        const pubmedUrl = `https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`;

        paperCard.innerHTML = `
            <h6 class="paper-title">
                ${index + 1}. ${safe(paper.title)}
            </h6>

            <p>
                <strong>PMID:</strong>
                <a href="${pubmedUrl}" target="_blank" rel="noopener noreferrer">
                    ${safe(paper.pmid)}
                </a>
            </p>

            <details class="mb-3">
                <summary><strong>Abstract</strong></summary>
                <p class="text-prewrap mt-2">
                    ${safe(paper.abstract)}
                </p>
            </details>

            <p><strong>Summary:</strong></p>
            <ul class="list-group summary-list">
                <li class="list-group-item">
                    <strong>Purpose:</strong> ${safe(paper.summary?.purpose)}
                </li>
                <li class="list-group-item">
                    <strong>Method:</strong> ${safe(paper.summary?.method)}
                </li>
                <li class="list-group-item">
                    <strong>Result:</strong> ${safe(paper.summary?.result)}
                </li>
                <li class="list-group-item">
                    <strong>Conclusion:</strong> ${safe(paper.summary?.conclusion)}
                </li>
            </ul>
        `;

        papersContainer.appendChild(paperCard);
    });

    searchCard.appendChild(papersContainer);
    resultsArea.appendChild(searchCard);
});

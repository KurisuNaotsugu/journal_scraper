document.addEventListener("DOMContentLoaded", () => {
    // HTML に埋め込んだ JSON を取得
    const jsonText = document.getElementById("resultsData").textContent;
    const results = JSON.parse(jsonText);

    const resultsArea = document.getElementById("resultsArea");

    results.forEach(result => {
        const searchCard = document.createElement("div");
        searchCard.classList.add("card", "mb-4", "p-3");

        searchCard.innerHTML = `
            <h4>${result.title}</h4>
            <p><strong>Keywords:</strong> ${result.keywords.join(", ")}</p>
            <p><strong>Search Period:</strong> ${result.search_period}</p>
            <p><strong>Paper Count:</strong> ${result.paper_count}</p>
        `;

        const papersContainer = document.createElement("div");

        result.papers.forEach(paper => {
            const paperCard = document.createElement("div");
            paperCard.classList.add("card", "mb-3", "p-3");

            paperCard.innerHTML = `
                <h6><a href="${paper.url}" target="_blank" class="text-prewrap">${paper.title}</a></h6>
                <p><strong>PubDate:</strong> ${paper.pubdate}</p>

                <p><strong>Summary:</strong></p>
                <ul class="list-group list-group-flush summary-list">
                    <li><p><strong>目的:</strong> ${paper.summary["目的"] || "記載なし"}</p></li>
                    <li><p><strong>結果:</strong> ${paper.summary["結果"] || "記載なし"}</p></li>
                    <li><p><strong>結論:</strong> ${paper.summary["結論"] || "記載なし"}</p></li>
                    <li><p><strong>サンプル:</strong> ${paper.summary["サンプル"] || "記載なし"}</p></li>
                    <li><p><strong>解析手法:</strong> ${paper.summary["解析手法"] || "記載なし"}</p></li>
                </ul>
            `;

            papersContainer.appendChild(paperCard);
        });

        searchCard.appendChild(papersContainer);
        resultsArea.appendChild(searchCard);
    });
});

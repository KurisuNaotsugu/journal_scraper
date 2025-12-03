document.addEventListener("DOMContentLoaded", () => {
    // HTML に埋め込んだ JSON を取得
    const jsonText = document.getElementById("resultsData").textContent;
    const results = JSON.parse(jsonText);

    const resultsArea = document.getElementById("resultsArea");

    // 安全に値を取得するヘルパー
    const safe = (value) => value || "記載なし";

    results.forEach(result => {
        // ===== 検索結果カード =====
        const searchCard = document.createElement("div");
        searchCard.classList.add("card", "search-card", "mb-4", "p-3");

        searchCard.innerHTML = `<h4 class="search-title">${result.title.trim()}</h4>
<p><strong>Keywords:</strong> ${result.keywords.join(", ")}</p>
<p><strong>Search Period:</strong> ${result.search_period}</p>
<p><strong>Paper Count:</strong> ${result.paper_count}</p>`;

        const papersContainer = document.createElement("div");

        // ===== 論文カード一覧 =====
        result.papers.forEach(paper => {
            const paperCard = document.createElement("div");
            paperCard.classList.add("card", "paper-card", "mb-3", "p-3");

            paperCard.innerHTML = `<h6 class="paper-title">
<a href="${paper.url}" target="_blank" class="text-prewrap paper-title-link">${paper.title.trim()}</a>
</h6>
<p><strong>PubDate:</strong> ${safe(paper.pubdate)}</p>
<p><strong>Summary:</strong></p>
<ul class="list-group summary-list">
<li><p><strong>目的:</strong> ${safe(paper.summary["目的"])}</p></li>
<li><p><strong>結果:</strong> ${safe(paper.summary["結果"])}</p></li>
<li><p><strong>結論:</strong> ${safe(paper.summary["結論"])}</p></li>
<li><p><strong>サンプル:</strong> ${safe(paper.summary["サンプル"])}</p></li>
<li><p><strong>解析手法:</strong> ${safe(paper.summary["解析手法"])}</p></li>
</ul>`;

            papersContainer.appendChild(paperCard);
        });

        searchCard.appendChild(papersContainer);
        resultsArea.appendChild(searchCard);
    });
});

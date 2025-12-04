document.getElementById("searchForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch("/manualsearch/run", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        const resultDiv = document.getElementById("result");
        const contentDiv = document.getElementById("resultContent");
        resultDiv.style.display = "block";
        contentDiv.innerHTML = ""; // 前回結果をクリア

        if (data.status === "success") {
            data.results.forEach(search => {
                // 検索条件ごとの親カード
                const searchCard = document.createElement("div");
                searchCard.className = "card mb-4 p-3";

                searchCard.innerHTML = `
                    <h5>${search.title}</h5>
                    <p class="text-muted">期間: ${search.search_period}, 論文数: ${search.paper_count}</p>
                `;

                // 論文ごとのカードを格納するコンテナ
                const papersContainer = document.createElement("div");
                papersContainer.className = "papers-container";

                search.papers.forEach(paper => {
                    const paperCard = document.createElement("div");
                    paperCard.className = "card mb-3 p-3";

                    paperCard.innerHTML = `
                        <h6><a href="${paper.url}" target="_blank" class="text-prewrap">${paper.title}</a></h6>
                        <p><strong>PubDate:</strong> ${paper.pubdate}</p>
                        <p><strong>Summary:</strong></p>
                        <ul class="list-group summary-list">
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
                contentDiv.appendChild(searchCard);
            });
        } else {
            contentDiv.innerText = `Error: ${data.message}`;
        }
    })
    .catch(err => {
        const resultDiv = document.getElementById("result");
        const contentDiv = document.getElementById("resultContent");
        resultDiv.style.display = "block";
        contentDiv.innerText = `Fetch error: ${err}`;
    });
});

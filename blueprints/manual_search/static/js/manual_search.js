document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = this;
    const submitBtn = form.querySelector("button[type='submit']");
    const resultDiv = document.getElementById("result");
    const contentDiv = document.getElementById("resultContent");
    const safe = (v) => (v && v.trim ? v.trim() : v) || "記載なし";
    const cleanText = (v) =>(v && typeof v === "string") ? v.trim() : "記載なし";

    showSpinner();                 // ★ スピナー表示
    submitBtn.disabled = true;     // ★ 二重送信防止

    const formData = new FormData(form);

    fetch("/manualsearch/run", {
        method: "POST",
        body: formData
    })
    .then(res => {
        if (!res.ok) throw new Error("Server error");
        return res.json();
    })
    .then(data => {
        resultDiv.style.display = "block";
        contentDiv.innerHTML = ""; // 前回結果をクリア

        if (data.status === "success") {
            data.results.forEach(search => {

                const searchCard = document.createElement("div");
                searchCard.classList.add("card", "search-card", "mb-4", "p-3");

                searchCard.innerHTML = `
                    <h4 class="search-title">${search.title}</h4>
                    <p class="text-muted">Search period: ${search.search_period} /Parpers: ${search.paper_count}</p>`;

                const papersContainer = document.createElement("div");

                // ===== 論文カード =====
                search.papers.forEach(paper => {
                    const paperCard = document.createElement("div");
                    paperCard.classList.add("card", "paper-card", "mb-3", "p-3");

                    const pubmedUrl = `https://pubmed.ncbi.nlm.nih.gov/${safe(paper.pmid)}/`;
                    
                    paperCard.innerHTML = `
                        <h6 class="paper-title break-text">${safe(paper.title)}</h6>

                        <p class="break-text"><strong>PMID:</strong><a class="break-text" href="${pubmedUrl}" target="_blank" rel="noopener noreferrer">${safe(paper.pmid)}</a></p>

                        <details class="mb-3">
                        <summary><strong>Abstract</strong></summary>
                        <p class="abstract-text">${cleanText(paper.abstract)}</p>
                        </details>

                        <p class="break-text"><strong>PubDate:</strong> ${paper.pubdate}</p>

                        <p><strong>Summary:</strong></p>
                        <ul class="list-group summary-list">
                        <li class="list-group-item break-text"><strong>Purpose:</strong> ${paper.summary["目的"] || "記載なし"}</li>
                        <li class="list-group-item break-text"><strong>Result:</strong> ${paper.summary["結果"] || "記載なし"}</li>
                        <li class="list-group-item break-text"><strong>Conclusion:</strong> ${paper.summary["結論"] || "記載なし"}</li>
                        <li class="list-group-item break-text"><strong>Sample:</strong> ${paper.summary["サンプル"] || "記載なし"}</li>
                        <li class="list-group-item break-text"><strong>Method:</strong> ${paper.summary["解析手法"] || "記載なし"}</li>
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
        resultDiv.style.display = "block";
        contentDiv.innerText = `Fetch error: ${err.message}`;
    })
    .finally(() => {
        hideSpinner();              // ★ 必ず非表示
        submitBtn.disabled = false;
    });
});

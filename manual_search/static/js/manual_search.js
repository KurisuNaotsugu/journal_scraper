document.getElementById("searchForm").addEventListener("submit", function(e){
    e.preventDefault();

    let formData = new FormData(this);

    fetch("/manual_search/run", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText = JSON.stringify(data, null, 2);
    });
});
function drawTrendChart(labels, values, keywordLabel) {
    const ctx = document.getElementById("weeklyChart").getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: `検索キーワード：${keywordLabel}`,
                data: values,
                borderWidth: 3,
                tension: 0.25,
                borderColor: "#2e7d32",
                backgroundColor: "rgba(46, 125, 50, 0.15)",
                pointRadius: 4,
                pointBackgroundColor: "#1b5e20",
                pointBorderColor: "#fff"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            // 整数だけを表示
                            return Number.isInteger(value) ? value : null;
                        }
                    }
                }
            }
        }
    }); 
} 

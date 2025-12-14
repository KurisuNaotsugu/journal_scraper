// ==============================
// Global Spinner Control
// ==============================
function showSpinner() {
    const spinner = document.getElementById("global-spinner");
    if (spinner) {
        spinner.classList.remove("d-none");
    }
}

function hideSpinner() {
    const spinner = document.getElementById("global-spinner");
    if (spinner) {
        spinner.classList.add("d-none");
    }
}

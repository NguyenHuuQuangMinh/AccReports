document.addEventListener("DOMContentLoaded", () => {
    const overlay = document.querySelector(".toast-overlay");
    if (!overlay) return;

    setTimeout(() => {
        overlay.remove();
    }, 2200);
});

function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}
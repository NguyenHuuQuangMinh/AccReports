document.addEventListener("DOMContentLoaded", () => {
    const overlay = document.querySelector(".toast-overlay");
    if (!overlay) return;

    setTimeout(() => {
        overlay.remove();
    }, 2200);
});


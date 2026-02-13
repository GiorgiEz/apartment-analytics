let overlay = null;

export async function loadLoadingOverlay() {
    if (overlay) return overlay;

    const res = await fetch("partials/components/loading-overlay.html");
    const html = await res.text();

    document.body.insertAdjacentHTML("beforeend", html);
    overlay = document.getElementById("loading-overlay");

    return overlay;
}

export function showLoading() {
    if (!overlay) return;
    overlay.classList.remove("hidden");
}

export function hideLoading() {
    if (!overlay) return;
    overlay.classList.add("hidden");
}

export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

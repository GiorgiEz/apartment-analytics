let modal;
let modalContent;
let modalImage;
let modalClose;

export function initModal() {
    modal = document.getElementById("chart-modal");
    modalContent = document.getElementById("chart-modal-content");
    modalImage = document.getElementById("chart-modal-image");
    modalClose = document.getElementById("chart-modal-close");

    if (!modal) return;
    modalClose.addEventListener("click", closeModal);

    modal.addEventListener("click", (e) => {
        // Close only if clicking outside the modal content
        if (!modalContent.contains(e.target)) {
            closeModal();
        }
    });
}

export function openModal(src) {
    if (!modal) return;

    modalImage.src = src;
    modal.classList.remove("hidden");
}

function closeModal() {
    modal.classList.add("hidden");
    modalImage.src = "";
}

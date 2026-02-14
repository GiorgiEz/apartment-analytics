let modal;
let modalImage;
let modalClose;

export function initModal() {
    modal = document.getElementById("chart-modal");
    modalImage = document.getElementById("chart-modal-image");
    modalClose = document.getElementById("chart-modal-close");

    if (!modal) return;
    modalClose.addEventListener("click", closeModal);

    modal.addEventListener("click", (e) => {
        if (e.target === modal) closeModal();
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

export function renderAnalysisSection(charts) {
    const chartsContainer = document.getElementById("charts");
    chartsContainer.innerHTML = "";
    chartsContainer.className = "flex flex-col gap-10 mt-6";

    charts.forEach(section => {
        // Section wrapper (one row group)
        const sectionWrapper = document.createElement("div");
        sectionWrapper.className = "flex flex-col gap-4";

        // Title
        const title = document.createElement("h3");
        title.className = "text-xl font-semibold text-blue-800";
        title.textContent = section.title;

        // Images row
        const imagesRow = document.createElement("div");
        imagesRow.className = "flex flex-nowrap justify-center items-start gap-4";

        const imageCount = section.src.length;

        section.src.forEach(src => {
            const button = document.createElement("button");
            // width calculation
            if (imageCount === 1) {
                button.style.flex = `0 0 ${50}%`;
            }
            else {
                button.style.flex = `0 0 ${90 / imageCount}%`;
            }

            button.className = `
                        bg-white rounded-xl shadow-md overflow-hidden
                        hover:scale-102 transition-transform duration-300
                    `;

            button.innerHTML = `
                        <img src="${src}" class="w-full h-auto object-contain" alt="${section.title}">`;

            button.addEventListener("click", () => openModal(src));
            imagesRow.appendChild(button);
        });

        sectionWrapper.appendChild(title);
        sectionWrapper.appendChild(imagesRow);
        chartsContainer.appendChild(sectionWrapper);
    });
}

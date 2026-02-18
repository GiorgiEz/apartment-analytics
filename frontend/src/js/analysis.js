import {initModal, openModal} from "@components/analysis_modal.js";
import {ANALYSIS_SECTIONS,
        marketOverviewCharts, locationInsightsCharts, apartmentCharacteristicsCharts,
        priceAnalysisCharts, timeAnalysisCharts}
    from "@helpers/helper_functions"


window.initAnalysisView = function () {
    initModal();

    setTimeout(async () => {
        const sections_len = ANALYSIS_SECTIONS.length
        let currentIndex = 0;

        const prevBtn = document.getElementById("analysis-prev");
        const nextBtn = document.getElementById("analysis-next");
        const title = document.getElementById("analysis-section-title");
        const chartsContainer = document.getElementById("charts");

        const renderMap = {
            0: marketOverviewCharts,
            1: priceAnalysisCharts,
            2: apartmentCharacteristicsCharts,
            3: locationInsightsCharts,
            4: timeAnalysisCharts,
        }

        function renderAnalysisSection(charts) {
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

        function shorten(text, max = 18) {
            return text.length > max ? text.slice(0, max) + "…" : text;
        }

        function renderSection() {
            const prevIndex = (currentIndex - 1 + sections_len) % sections_len;
            const nextIndex = (currentIndex + 1) % sections_len;

            title.textContent = ANALYSIS_SECTIONS[currentIndex];

            // Update button labels
            prevBtn.textContent = `◀ ${shorten(ANALYSIS_SECTIONS[prevIndex])}`;
            nextBtn.textContent = `${shorten(ANALYSIS_SECTIONS[nextIndex])} ▶`;

            renderAnalysisSection(renderMap[currentIndex]);
        }

        prevBtn.addEventListener("click", () => {
            currentIndex = (currentIndex - 1 + sections_len) % sections_len
            renderSection();
        });

        nextBtn.addEventListener("click", () => {
            currentIndex = (currentIndex + 1) % sections_len;
            renderSection();
        });

        renderSection();
    }, 100);
};

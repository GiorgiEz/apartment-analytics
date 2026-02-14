import { initModal, renderAnalysisSection } from "@components/analysis_modal.js";
import {ANALYSIS_SECTIONS,
        marketOverviewCharts, locationInsightsCharts, apartmentCharacteristicsCharts,
        priceAnalysisCharts, timeAnalysisCharts}
    from "@helpers/helper_functions"


window.initAnalysisView = function () {
    initModal();

    setTimeout(async () => {
        const analysis_sections_len = ANALYSIS_SECTIONS.length
        let currentIndex = 0;

        const prevBtn = document.getElementById("analysis-prev");
        const nextBtn = document.getElementById("analysis-next");
        const title = document.getElementById("analysis-section-title");

        const renderMap = {
            0: marketOverviewCharts,
            1: priceAnalysisCharts,
            2: apartmentCharacteristicsCharts,
            3: locationInsightsCharts,
            4: timeAnalysisCharts,
        }

        function renderSection() {
            title.textContent = ANALYSIS_SECTIONS[currentIndex];
            renderAnalysisSection(renderMap[currentIndex]);
        }

        prevBtn.addEventListener("click", () => {
            currentIndex = (currentIndex - 1 + analysis_sections_len) % analysis_sections_len
            renderSection();
        });

        nextBtn.addEventListener("click", () => {
            currentIndex = (currentIndex + 1) % analysis_sections_len;
            renderSection();
        });

        renderSection();
    }, 100);
};

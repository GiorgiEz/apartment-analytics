import {chartPaths, setupChartButton, insert_icons} from "/src/js/helpers/helper_functions.js"
import {icons} from "./helpers/icons.js";


window.initAnalysisView = function(){
    // Wait for DOM to be fully ready
    setTimeout(() => {
        const chartsDiv = document.getElementById('charts');
        const citySelect = document.getElementById('city-select');

        // Insert icons
        insert_icons({
            'btn-distribution': icons.city_distribution, 'btn-price-per-sqm': icons.avg_price_per_m2,
            'btn-area-bin': icons.price_by_area_bin, 'btn-price-by-city': icons.avg_price_by_city,
            'btn-price-by-district': icons.avg_price_by_district
        });

        if (!chartsDiv || !citySelect) {
            console.error("Required DOM elements not found");
            return;
        }

        function loadImages(paths) {
            chartsDiv.innerHTML = '';
            paths.forEach(path => {
                const imgContainer = document.createElement('div');
                imgContainer.className = 'chart-container p-5 flex flex-col';

                const img = document.createElement('img');
                img.src = path;
                img.className = 'w-full h-auto max-h-[65vh] object-contain rounded-lg shadow-md';
                img.alt = 'Data visualization chart';

                // Add error handling for missing images
                img.onerror = function() {
                    console.error("Failed to load image:", path);
                    imgContainer.innerHTML = `
                        <div class="flex items-center justify-center h-64 bg-silver-100 rounded-lg">
                            <div class="text-center text-silver-600">
                                ${icons.image_placeholder}
                                <p>Chart not available</p>
                                <p class="text-sm">${path.split('/').pop()}</p>
                            </div>
                        </div>
                    `;
                };

                imgContainer.appendChild(img);
                chartsDiv.appendChild(imgContainer);
            });
        }

        // Set up button selection effects
        const buttons = document.querySelectorAll(".chart-button");
        if (buttons.length > 0) {
            buttons.forEach(button => {
                button.addEventListener('click', function() {
                    buttons.forEach(btn => btn.classList.remove('active', 'bg-steel-700'));
                    this.classList.add('active', 'bg-steel-700');
                });
            });
        }

        // Set up chart button event listeners
        for (const [key, value] of Object.entries({
            'btn-distribution': chartPaths.city_distribution, 'btn-price-per-sqm': chartPaths.avg_price_per_sqm_by_city,
            'btn-area-bin': chartPaths.price_by_area_bin_per_city, 'btn-price-by-city': chartPaths.avg_price_by_city,
        })) {
            setupChartButton(key, () => {
                const citySelectParent = citySelect.parentElement;
                if (citySelectParent) citySelectParent.classList.add('hidden');
                loadImages(value);
            });
        }

        setupChartButton('btn-price-by-district', () => {
            const citySelectParent = citySelect.parentElement;
            if (citySelectParent) citySelectParent.classList.remove('hidden');
            citySelect.value = 'ქუთაისი';
            citySelect.dispatchEvent(new Event('change'));
        });

        if (citySelect) {
            citySelect.addEventListener('change', () => {
                const selectedCity = citySelect.value;
                if (!selectedCity) return;

                const basePath = `./charts/avg_price_by_street/${selectedCity}`;
                const images = [
                    `${basePath}/იყიდება.png`, `${basePath}/ქირავდება დღიურად.png`,
                    `${basePath}/ქირავდება თვიურად.png`, `${basePath}/გირავდება.png`
                ];
                loadImages(images);
            });
        }

        // Activate default chart
        const defaultButton = document.getElementById('btn-distribution');
        if (defaultButton) {
            defaultButton.click();
        }
    }, 100); // Small delay to ensure DOM is ready
};
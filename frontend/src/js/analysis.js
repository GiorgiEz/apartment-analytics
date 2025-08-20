window.initAnalysisView = function() {
    // Wait for DOM to be fully ready
    setTimeout(() => {
        const chartsDiv = document.getElementById('charts');
        const citySelect = document.getElementById('city-select');

        if (!chartsDiv || !citySelect) {
            console.error("Required DOM elements not found");
            return;
        }

        const chartPaths = {
            city_distribution: ['./charts/city_distribution_pie.png'],
            avg_price_by_city: [
                './charts/avg_price_by_city/იყიდება.png',
                './charts/avg_price_by_city/ქირავდება დღიურად.png',
                './charts/avg_price_by_city/ქირავდება თვიურად.png',
                './charts/avg_price_by_city/გირავდება.png',
            ],
            avg_price_per_sqm_by_city: ['./charts/avg_price_per_sqm_by_city.png'],
            price_by_area_bin_per_city: [
                './charts/price_by_area_bin_per_city_for_sale/ბათუმი.png',
                './charts/price_by_area_bin_per_city_for_sale/თბილისი.png',
                './charts/price_by_area_bin_per_city_for_sale/ქუთაისი.png'
            ]
        };

        function loadImages(paths) {
            chartsDiv.innerHTML = '';
            paths.forEach(path => {
                const imgContainer = document.createElement('div');
                imgContainer.className = 'chart-container p-5 flex flex-col';

                const img = document.createElement('img');
                img.src = path;
                img.className = 'w-full h-auto max-h-[56vh] object-contain rounded-lg shadow-md';
                img.alt = 'Data visualization chart';

                // Add error handling for missing images
                img.onerror = function() {
                    console.error("Failed to load image:", path);
                    imgContainer.innerHTML = `
                        <div class="flex items-center justify-center h-64 bg-silver-100 rounded-lg">
                            <div class="text-center text-silver-600">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
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

        // Helper function to set up chart button
        function setupChartButton(buttonId, action) {
            const button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener('click', function() {
                    // Update button active state
                    document.querySelectorAll('.chart-button').forEach(btn => {
                        btn.classList.remove('active', 'bg-steel-700');
                    });
                    this.classList.add('active', 'bg-steel-700');

                    // Execute the action
                    action();
                });
            }
        }

        // Set up chart button event listeners
        setupChartButton('btn-distribution', () => {
            const citySelectParent = citySelect.parentElement;
            if (citySelectParent) citySelectParent.classList.add('hidden');
            loadImages(chartPaths.city_distribution);
        });

        setupChartButton('btn-price-by-city', () => {
            const citySelectParent = citySelect.parentElement;
            if (citySelectParent) citySelectParent.classList.add('hidden');
            loadImages(chartPaths.avg_price_by_city);
        });

        setupChartButton('btn-price-per-sqm', () => {
            const citySelectParent = citySelect.parentElement;
            if (citySelectParent) citySelectParent.classList.add('hidden');
            loadImages(chartPaths.avg_price_per_sqm_by_city);
        });

        setupChartButton('btn-area-bin', () => {
            const citySelectParent = citySelect.parentElement;
            if (citySelectParent) citySelectParent.classList.add('hidden');
            loadImages(chartPaths.price_by_area_bin_per_city);
        });

        setupChartButton('btn-price-by-street', () => {
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
                    `${basePath}/იყიდება.png`,
                    `${basePath}/ქირავდება დღიურად.png`,
                    `${basePath}/ქირავდება თვიურად.png`,
                    `${basePath}/გირავდება.png`
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
// Initialize the analysis view
window.initAnalysisView = function initAnalysisView() {
    console.log("Analysis View");
    const chartsDiv = document.getElementById('charts');
    const citySelect = document.getElementById('city-select');

    const chartPaths = {
        city_distribution: ['../charts/city_distribution_pie.png'],
        avg_price_by_city: [
            '../charts/avg_price_by_city/იყიდება.png',
            '../charts/avg_price_by_city/ქირავდება დღიურად.png',
            '../charts/avg_price_by_city/ქირავდება თვიურად.png',
            '../charts/avg_price_by_city/გირავდება.png',
        ],
        avg_price_per_sqm_by_city: ['../charts/avg_price_per_sqm_by_city.png'],
        price_by_area_bin_per_city: [
            '../charts/price_by_area_bin_per_city_for_sale/ბათუმი.png',
            '../charts/price_by_area_bin_per_city_for_sale/თბილისი.png',
            '../charts/price_by_area_bin_per_city_for_sale/ქუთაისი.png'
        ]
    };

    function loadImages(paths) {
        chartsDiv.innerHTML = '';
        paths.forEach(path => {
            const imgContainer = document.createElement('div');
            imgContainer.className = 'chart-container p-5 flex flex-col';

            const img = document.createElement('img');
            img.src = path;
            img.className = 'w-full h-auto object-contain rounded-lg shadow-md';
            img.alt = 'Data visualization chart';

            // Add loading state
            img.onload = function() {
                imgContainer.classList.remove('bg-silver-200');
            };

            imgContainer.appendChild(img);
            chartsDiv.appendChild(imgContainer);
        });
    }

    // Get all the nav buttons inside the analysis-view div
    const buttons = document.getElementById("analysis-view").querySelectorAll("nav button");
    buttons.forEach(button => {
        button.addEventListener("click", () => {
            buttons.forEach(btn => btn.classList.remove('active', 'bg-steel-700'));
            this.classList.add('active', 'bg-steel-700');
        });
    });

    // Add event listeners to chart buttons
    document.getElementById('btn-distribution').addEventListener('click', function() {
        // Update button active state
        document.querySelectorAll('.chart-button').forEach(btn => {
            btn.classList.remove('active', 'bg-steel-700');
        });
        this.classList.add('active', 'bg-steel-700');

        citySelect.parentElement.classList.add('hidden');
        loadImages(chartPaths.city_distribution);
    });

    document.getElementById('btn-price-by-city').addEventListener('click', function() {
        // Update button active state
        document.querySelectorAll('.chart-button').forEach(btn => {
            btn.classList.remove('active', 'bg-steel-700');
        });
        this.classList.add('active', 'bg-steel-700');

        citySelect.parentElement.classList.add('hidden');
        loadImages(chartPaths.avg_price_by_city);
    });

    document.getElementById('btn-price-per-sqm').addEventListener('click', function() {
        // Update button active state
        document.querySelectorAll('.chart-button').forEach(btn => {
            btn.classList.remove('active', 'bg-steel-700');
        });
        this.classList.add('active', 'bg-steel-700');

        citySelect.parentElement.classList.add('hidden');
        loadImages(chartPaths.avg_price_per_sqm_by_city);
    });

    document.getElementById('btn-area-bin').addEventListener('click', function() {
        // Update button active state
        document.querySelectorAll('.chart-button').forEach(btn => {
            btn.classList.remove('active', 'bg-steel-700');
        });
        this.classList.add('active', 'bg-steel-700');

        citySelect.parentElement.classList.add('hidden');
        loadImages(chartPaths.price_by_area_bin_per_city);
    });

    document.getElementById('btn-price-by-street').addEventListener('click', function() {
        // Update button active state
        document.querySelectorAll('.chart-button').forEach(btn => {
            btn.classList.remove('active', 'bg-steel-700');
        });
        this.classList.add('active', 'bg-steel-700');

        citySelect.parentElement.classList.remove('hidden');

        citySelect.classList.add('inline-block');
        citySelect.value = 'ქუთაისი'; // Set default selection
        citySelect.dispatchEvent(new Event('change')); // Trigger chart load
    });

    citySelect.addEventListener('change', () => {
        const selectedCity = citySelect.value;
        if (!selectedCity) return;

        const basePath = `../charts/avg_price_by_street/${selectedCity}`;
        const images = [
            `${basePath}/იყიდება.png`,
            `${basePath}/ქირავდება დღიურად.png`,
            `${basePath}/ქირავდება თვიურად.png`,
            `${basePath}/გირავდება.png`
        ];
        loadImages(images);
    });

    // Activate default chart
    document.getElementById('btn-distribution').click();
}

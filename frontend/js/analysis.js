window.initAnalysisView = function () {
  const chartsDiv = document.getElementById('charts');
  const citySelect = document.getElementById('city-select');

  const chartPaths = {
    city_distribution: ['../charts/city_distribution_pie.png'],
    avg_price_by_city: [
      '/charts/avg_price_by_city/იყიდება.png',
      '/charts/avg_price_by_city/ქირავდება დღიურად.png',
      '/charts/avg_price_by_city/ქირავდება თვიურად.png',
      '/charts/avg_price_by_city/გირავდება.png',
    ],
    avg_price_per_sqm_by_city: ['/charts/avg_price_per_sqm_by_city.png'],
    price_by_area_bin_per_city: [
      '/charts/price_by_area_bin_per_city_for_sale/ბათუმი.png',
      '/charts/price_by_area_bin_per_city_for_sale/თბილისი.png',
      '/charts/price_by_area_bin_per_city_for_sale/ქუთაისი.png'
    ]
  };

  function loadImages(paths) {
    chartsDiv.innerHTML = '';
    paths.forEach(path => {
      const img = document.createElement('img');
      img.src = path;
      img.className = 'w-full h-auto max-h-[200px] object-contain rounded-lg shadow-md';
      chartsDiv.appendChild(img);
    });
  }

  // gets all the nav buttons inside a div with id = "analysis-view"
  const buttons = document.getElementById("analysis-view").querySelectorAll("nav button");

  function resetButtonStyles() {
    buttons.forEach(btn => {
      btn.classList.remove('bg-green-600');
      btn.classList.add('bg-gray-800', 'text-white');
    });
  }

  buttons.forEach(button => {
    button.addEventListener("click", () => {
      resetButtonStyles();
      button.classList.remove('bg-gray-800');
      button.classList.add('bg-green-600', 'text-white');
    });
  });

  document.getElementById('btn-distribution').addEventListener('click', () => {
    citySelect.classList.add('hidden');
    loadImages(chartPaths.city_distribution);
  });

  document.getElementById('btn-price-by-city').addEventListener('click', () => {
    citySelect.classList.add('hidden');
    loadImages(chartPaths.avg_price_by_city);
  });

  document.getElementById('btn-price-per-sqm').addEventListener('click', () => {
    citySelect.classList.add('hidden');
    loadImages(chartPaths.avg_price_per_sqm_by_city);
  });

  document.getElementById('btn-area-bin').addEventListener('click', () => {
    citySelect.classList.add('hidden');
    loadImages(chartPaths.price_by_area_bin_per_city);
  });

  document.getElementById('btn-price-by-street').addEventListener('click', () => {
    citySelect.classList.remove('hidden');
    citySelect.classList.add('inline-block');
    citySelect.value = 'ქუთაისი'; // Set default selection
    citySelect.dispatchEvent(new Event('change')); // Trigger chart load
  });

  citySelect.addEventListener('change', () => {
    const selectedCity = citySelect.value;
    if (!selectedCity) return;

    const basePath = `/charts/avg_price_by_street/${selectedCity}`;
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
};

// to run server cd frontend, python -m http.server, http://localhost:8000/html/home.html
// npx @tailwindcss/cli -i ./css/input.css -o ./css/output.css --watch

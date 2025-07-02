document.addEventListener('DOMContentLoaded', () => {
  const chartsDiv = document.getElementById('charts');
  const citySelect = document.getElementById('city-select');

  const chartPaths = {
    city_distribution: ['charts/city_distribution_pie.png'],
    avg_price_by_city: [
      'charts/avg_price_by_city/იყიდება.png',
      'charts/avg_price_by_city/გირავდება.png',
      'charts/avg_price_by_city/ქირავდება დღიურად.png',
      'charts/avg_price_by_city/ქირავდება თვიურად.png'
    ],
    avg_price_per_sqm_by_city: ['charts/avg_price_per_sqm_by_city.png'],
    price_by_area_bin_per_city: [
      'charts/price_by_area_bin_per_city_for_sale/ბათუმი.png',
      'charts/price_by_area_bin_per_city_for_sale/თბილისი.png',
      'charts/price_by_area_bin_per_city_for_sale/ქუთაისი.png'
    ]
  };

  function clearCharts() {
    chartsDiv.innerHTML = '';
  }

  function loadImages(paths) {
    clearCharts();
    paths.forEach(path => {
      const img = document.createElement('img');
      img.src = path;
      chartsDiv.appendChild(img);
    });
  }

  const buttons = document.querySelectorAll("nav button");

  buttons.forEach(button => {
      button.addEventListener("click", () => {
          buttons.forEach(btn => btn.classList.remove("active")); // remove from all
          button.classList.add("active"); // add to clicked
      });
  });

  document.getElementById('btn-distribution').addEventListener('click', () => {
    citySelect.style.display = 'none';
    loadImages(chartPaths.city_distribution);
  });

  document.getElementById('btn-price-by-city').addEventListener('click', () => {
    citySelect.style.display = 'none';
    loadImages(chartPaths.avg_price_by_city);
  });

  document.getElementById('btn-price-per-sqm').addEventListener('click', () => {
    citySelect.style.display = 'none';
    loadImages(chartPaths.avg_price_per_sqm_by_city);
  });

  document.getElementById('btn-area-bin').addEventListener('click', () => {
    citySelect.style.display = 'none';
    loadImages(chartPaths.price_by_area_bin_per_city);
  });

  document.getElementById('btn-price-by-street').addEventListener('click', () => {
    citySelect.style.display = 'inline';
    citySelect.value = 'ქუთაისი'; // Set default selection
    citySelect.dispatchEvent(new Event('change')); // Trigger chart load
  });


  citySelect.addEventListener('change', () => {
    const selectedCity = citySelect.value;
    if (!selectedCity) return;

    const basePath = `charts/avg_price_by_street/${selectedCity}`;
    const images = [
        `${basePath}/იყიდება.png`,
        `${basePath}/ქირავდება დღიურად.png`,
        `${basePath}/ქირავდება თვიურად.png`,
        `${basePath}/გირავდება.png`
    ];
    loadImages(images);
  });

  // Load City Distribution chart and activate button on page load
  document.getElementById('btn-distribution').click();
});

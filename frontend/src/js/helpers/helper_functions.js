export const chartPaths = {
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

// Helper function to set up chart button
export function setupChartButton(buttonId, action) {
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

export function insert_icons(button_icons){
    for (const [id, icon_path] of Object.entries(button_icons)) {
        document.getElementById(id).insertAdjacentHTML("afterbegin", icon_path);
    }
}

export const MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
};

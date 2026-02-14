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

export const ANALYSIS_SECTIONS = [
    "Market Overview",
    "Price Analysis",
    "Apartment Characteristics",
    "Location Insights",
    "Time Analysis"
];

export const marketOverviewCharts = [
    {
        title: "City Distribution",
        src: ["/charts/market_overview/city_distribution_pie_chart.png"]
    },
    {
        title: "Transaction Type",
        src: ["/charts/market_overview/transaction_type_bar_chart.png"]
    },
];

export const apartmentCharacteristicsCharts = [
    {
        title: "Area Histograms",
        src: [
            "/charts/apartment_characteristics/area_histograms/area_for_sale.png",
            "/charts/apartment_characteristics/area_histograms/area_monthly_rent.png",
        ]
    },
    {
        title: "Bedrooms vs Price Boxplot",
        src: [
            "/charts/apartment_characteristics/bedrooms_vs_price_boxplot/for_sale.png",
            "/charts/apartment_characteristics/bedrooms_vs_price_boxplot/monthly_rent.png",
        ]
    },
    {
        title: "Floor Distribution by City",
        src: [
            "/charts/apartment_characteristics/floor_bar_charts/floor_batumi.png",
            "/charts/apartment_characteristics/floor_bar_charts/floor_kutaisi.png",
            "/charts/apartment_characteristics/floor_bar_charts/floor_tbilisi.png",
        ]
    },
];


export const locationInsightsCharts = [
    {
        title: "Districts Distribution by City",
        src: [
            "/charts/location_insights/districts_bar_charts/districts_in_batumi.png",
            "/charts/location_insights/districts_bar_charts/districts_in_kutaisi.png",
            "/charts/location_insights/districts_bar_charts/districts_in_tbilisi.png",
        ]
    },
    {
        title: "Price per sqm by District",
        src: [
            "/charts/location_insights/price_per_sqm_by_district_boxplots/batumi.png",
            "/charts/location_insights/price_per_sqm_by_district_boxplots/kutaisi.png",
            "/charts/location_insights/price_per_sqm_by_district_boxplots/tbilisi.png",
        ]
    },
];

export const priceAnalysisCharts = [
    {
        title: "Median Price Comparison",
        src: [
            "/charts/price_analysis/median_bar_charts/median_price_for_sale.png",
            "/charts/price_analysis/median_bar_charts/median_price_monthly_rent.png",
        ]
    },
    {
        title: "Price Distribution Histograms",
        src: [
            "/charts/price_analysis/price_histograms/price_for_sale_batumi.png",
            "/charts/price_analysis/price_histograms/price_for_sale_kutaisi.png",
            "/charts/price_analysis/price_histograms/price_for_sale_tbilisi.png",
            "/charts/price_analysis/price_histograms/price_monthly_rent_batumi.png",
            "/charts/price_analysis/price_histograms/price_monthly_rent_kutaisi.png",
            "/charts/price_analysis/price_histograms/price_monthly_rent_tbilisi.png",
        ]
    },
    {
        title: "Price per sqm Distribution",
        src: [
            "/charts/price_analysis/price_per_sqm_boxplots/price_per_sqm_for_sale.png",
            "/charts/price_analysis/price_per_sqm_boxplots/price_per_sqm_monthly_rent.png",
        ]
    },
];

export const timeAnalysisCharts = [
    {
        title: "Median Price per sqm Trend",
        src: [
            "/charts/time_analysis/price_trend/median_price_per_sqm_batumi.png",
            "/charts/time_analysis/price_trend/median_price_per_sqm_kutaisi.png",
            "/charts/time_analysis/price_trend/median_price_per_sqm_tbilisi.png",
        ]
    },
    {
        title: "Listings Over Time",
        src: [
            "/charts/time_analysis/listings_over_time.png",
        ]
    },
];

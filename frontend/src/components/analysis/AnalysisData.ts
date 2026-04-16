// src/components/analysis/AnalysisData.ts

import type {ChartSection, AnalysisKey} from "../../types/analysis.ts";

export const ANALYSIS_DATA: Record<AnalysisKey, {label: string; charts: ChartSection[]}> = {
    marketOverview: {
        label: "Market Overview",
        charts: [
            {
                title: "City Distribution",
                src: ["/charts/market_overview/city_distribution.png"],
            },
            {
                title: "Transaction Type Distribution",
                src: ["/charts/market_overview/transaction_distribution.png"],
            },
            {
                title: "Transaction Type Distribution By City",
                src: [
                    "/charts/market_overview/transaction_by_tbilisi.png",
                    "/charts/market_overview/transaction_by_batumi.png",
                    "/charts/market_overview/transaction_by_kutaisi.png"
                ],
            },
        ],
    },

    priceAnalysis: {
        label: "Price Analysis",
        charts: [
            {
                title: "Median Price Comparison",
                src: [
                    '/charts/price_analysis/median_bar_charts/sale.png',
                    "/charts/price_analysis/median_bar_charts/rent.png",
                ],
            },
            {
                title: "Price Distribution Histograms",
                src: [
                    "/charts/price_analysis/price_histograms/batumi.png",
                    "/charts/price_analysis/price_histograms/kutaisi.png",
                    "/charts/price_analysis/price_histograms/tbilisi.png"
                ],
            },
            {
                title: "Price per sqm Distribution",
                src: [
                    "/charts/price_analysis/price_per_sqm_boxplots/sale.png",
                    "/charts/price_analysis/price_per_sqm_boxplots/rent.png",
                ]
            },
            {
                title: "Area and Floor vs Price",
                src: [
                    "/charts/price_analysis/feature_vs_price_scatter/area_m2_vs_price.png",
                    "/charts/price_analysis/feature_vs_price_scatter/floor_vs_price.png",
                ]
            },
        ],
    },

    apartmentCharacteristics: {
        label: "Apartment Characteristics",
        charts: [
            {
                title: "Area Histograms",
                src: [
                    "/charts/apartment_characteristics/area_histograms/area_sale.png",
                    "/charts/apartment_characteristics/area_histograms/area_rent.png",
                ]
            },
            {
                title: "Bedrooms vs Price Boxplot",
                src: [
                    "/charts/apartment_characteristics/bedrooms_vs_price_boxplot/sale.png",
                    "/charts/apartment_characteristics/bedrooms_vs_price_boxplot/rent.png",
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
        ],
    },

    locationInsights: {
        label: "Location Insights",
        charts: [
            {
                title: "Districts Distribution by City",
                src: [
                    "/charts/location_insights/districts_bar_charts/batumi.png",
                    "/charts/location_insights/districts_bar_charts/kutaisi.png",
                    "/charts/location_insights/districts_bar_charts/tbilisi.png",
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
        ],
    },

    timeAnalysis: {
        label: "Time Analysis",
        charts: [
            {
                title: "Listings Over Time",
                src: [
                    "/charts/time_analysis/listings_over_time.png",
                ]
            },
            {
                title: "Median Price per sqm Trend",
                src: [
                    "/charts/time_analysis/price_trend/rent_price_over_time.png",
                    "/charts/time_analysis/price_trend/sale_price_per_sqm_over_time.png"
                ]
            },
        ],
    },
};

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


export const ANALYSIS_ORDER: AnalysisKey[] = [
    "marketOverview",
    "priceAnalysis",
    "apartmentCharacteristics",
    "locationInsights",
    "timeAnalysis",
];

// src/types/analysis.ts

export interface ChartSection {
    title: string;
    src: string[];
}

export type AnalysisKey =
    | "marketOverview"
    | "priceAnalysis"
    | "apartmentCharacteristics"
    | "locationInsights"
    | "timeAnalysis";
import { useState } from "react";
import { useLoading } from "./useLoading";

export function usePrediction() {
    const predictionLoading = useLoading(500);
    const [result, setResult] = useState<string | null>(null);

    const API_URL = import.meta.env.VITE_API_URL;

    const predict = async (payload: any) => {
        predictionLoading.showLoading();
        setResult(null);

        try {
            const res = await fetch(`${API_URL}/api/predict`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const data = await res.json();
            const price = Math.round(data.total_price / 1000) * 1000;

            setResult(`Total Apartment Price: $${price.toLocaleString()}`);

        } catch {
            setResult("Prediction failed.");
        } finally {
            await predictionLoading.hideLoading();
        }
    };

    return {result, predict, predictionLoading};
}
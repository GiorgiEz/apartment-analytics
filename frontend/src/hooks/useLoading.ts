// src/hooks/useLoading.ts

import { useRef, useState } from "react";

export function useLoading(minDuration = 1000) {
    const [loading, setLoading] = useState(false);
    const startTimeRef = useRef<number | null>(null);

    const showLoading = () => {
        startTimeRef.current = Date.now();
        setLoading(true);
    };

    const hideLoading = async () => {
        if (!startTimeRef.current) {
            setLoading(false);
            return;
        }

        const elapsed = Date.now() - startTimeRef.current;
        const remaining = minDuration - elapsed;

        if (remaining > 0) {
            await new Promise((res) => setTimeout(res, remaining));
        }

        setLoading(false);
        startTimeRef.current = null;
    };

    return {
        loading,
        showLoading,
        hideLoading,
    };
}
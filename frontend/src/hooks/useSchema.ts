// src/hooks/useSchema.ts

import { useEffect, useState } from "react";
import { useLoading } from "./useLoading";
import type { SchemaType } from "../types/prediction";

export function useSchema(transactionType: string) {
    const schemaLoading = useLoading(0);
    const [schema, setSchema] = useState<SchemaType | null>(null);

    const API_URL = import.meta.env.VITE_API_URL;

    useEffect(() => {
        if (!transactionType) {
            setSchema(null);
            return;
        }

        const loadSchema = async () => {
            schemaLoading.showLoading();

            try {
                const res = await fetch(`${API_URL}/inference-data/${transactionType}`);
                const data = await res.json();
                const s = data.schema;

                setSchema(s);

            } catch (e) {
                console.error("Schema fetch failed", e);
                setSchema(null);
            } finally {
                await schemaLoading.hideLoading();
            }
        };

        loadSchema();
    }, [transactionType]);

    return {schema, schemaLoading};
}
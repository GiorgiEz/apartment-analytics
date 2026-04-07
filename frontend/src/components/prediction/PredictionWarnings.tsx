// src/components/prediction/PredictionWarnings.tsx

import type { SchemaType } from "../../types/prediction";

type Props = {
    schema: SchemaType | null;
    area: string;
    floor: string;
    city: string;
};

export default function PredictionWarnings({schema, area, floor, city}: Props) {
    if (!schema) return null;

    // AREA WARNING
    function areaWarning() {
        if (!schema || !area) return null;

        const value = Number(area);
        const { soft_min, soft_max } = schema.area_m2;

        if (value < soft_min || value > soft_max) {
            return `Selected area (${value} m²) is outside typical range (${soft_min}-${soft_max}). Prediction may be less reliable.`;
        }

        return null;
    }

    // FLOOR WARNING
    function floorWarning() {
        if (!schema || !floor || !city) return null;

        const value = Number(floor);
        const softMax = schema.floor.soft_max_by_city[city];

        if (!softMax) return null;

        if (value > softMax) {
            return `Selected floor (${value}) exceeds typical maximum (${softMax}) for ${city}. Prediction may be less reliable.`;
        }

        return null;
    }

    if (!areaWarning() && !floorWarning()) return null;

    return (
        <div className="mt-3 space-y-2">

            {areaWarning() && (
                <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 px-4 py-2 rounded-lg text-sm">
                    {areaWarning()}
                </div>
            )}

            {floorWarning() && (
                <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 px-4 py-2 rounded-lg text-sm">
                    {floorWarning()}
                </div>
            )}
        </div>
    );
}
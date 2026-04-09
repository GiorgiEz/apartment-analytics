// src/pages/Prediction.tsx

import { useEffect, useState } from "react";
import LoadingOverlay from "../components/layout/LoadingOverlay";
import { MONTH_NAMES } from "../components/analysis/AnalysisData";
import {usePrediction} from "../hooks/usePrediction.ts";
import {useSchema} from "../hooks/useSchema.ts";
import CustomSelect from "../components/prediction/CustomSelect";
import PredictionWarnings from "../components/prediction/PredictionWarnings";


export default function Prediction() {
    // mandatory
    const [transactionType, setTransactionType] = useState("");
    const [city, setCity] = useState("");
    const [district, setDistrict] = useState("");
    const [area, setArea] = useState("");

    // optional
    const [bedrooms, setBedrooms] = useState("");
    const [floor, setFloor] = useState("");
    const [year, setYear] = useState("");
    const [month, setMonth] = useState("");

    const isValid = transactionType && city && district && area;

    const { result, predict, predictionLoading } = usePrediction(transactionType);
    const { schema, schemaLoading } = useSchema(transactionType);

    // fetch schema
    useEffect(() => {
        if (!schema) return;
        const defaults = schema.defaults;

        setBedrooms(String(defaults.bedrooms));
        setFloor(String(defaults.floor));
        setYear(String(defaults.year));
        setMonth(String(defaults.month));
    }, [schema]);

    // update months when year changes
    useEffect(() => {
        if (!schema || !year) return;

        const months = schema.upload_date.year_month_map[year];
        if (months && !months.includes(Number(month))) {
            setMonth(String(months[months.length - 1]));
        }
    }, [year]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const payload = {
            transaction_type: transactionType,
            city,
            district,
            area_m2: Number(area),
            bedrooms: bedrooms ? Number(bedrooms) : null,
            floor: floor ? Number(floor) : null,
            year: year ? Number(year) : null,
            month: month ? Number(month) : null,
        };

        await predict(payload);
    };

    const transactionOptions = [
        { value: "rent", label: "Rent" },
        { value: "sale", label: "Sale" },
    ];

    const cityOptions =
        schema
            ? schema.cities.map((c) => ({
                value: c,
                label: c,
            })) : [];

    const districtOptions =
        city && schema
            ? schema.city_districts[city].map((d) => ({
                value: d,
                label: d,
            }))
            : [];

    const areaOptions =
        schema
            ? Array.from(
                { length: schema.area_m2.hard_max - schema.area_m2.hard_min + 1 },
                (_, i) => {
                    const val = schema.area_m2.hard_min + i;
                    return {
                        value: val,
                        label: `${val} m²`,
                    };
                }
            )
            : [];

    const bedroomOptions =
        schema
            ? Array.from(
                {
                    length: schema.bedrooms.hard_max - schema.bedrooms.hard_min + 1,
                },
                (_, i) => {
                    const val = schema.bedrooms.hard_min + i;
                    return {
                        value: val,
                        label: `${val}`,
                    };
                }
            )
            : [];

    const floorOptions =
        schema
            ? Array.from(
                {
                    length: schema.floor.hard_max - schema.floor.hard_min + 1,
                },
                (_, i) => {
                    const val = schema.floor.hard_min + i;
                    return {
                        value: val,
                        label: `${val}`,
                    };
                }
            )
            : [];

    const yearOptions =
        schema?.upload_date.years.map((y) => ({
            value: y,
            label: String(y),
        })) ?? [];

    const monthOptions =
        year && schema
            ? schema.upload_date.year_month_map[year].map((m) => ({
                value: m,
                label: MONTH_NAMES[m as keyof typeof MONTH_NAMES],
            }))
            : [];

    return (
        <div className="max-w-5xl mx-auto p-6">

            {/* Header */}
            <div className={"mb-4"}>
                <h2 className="text-3xl font-bold text-blue-900">Apartment Price Prediction</h2>
                <p className="text-sm text-blue-700 mt-1">Fields marked with * are required</p>
                <PredictionWarnings schema={schema} area={area} floor={floor} city={city}/>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">

                {/* MANDATORY */}
                <div className="bg-white p-6 rounded-2xl shadow space-y-6">
                    <h3 className="text-lg font-semibold text-blue-800 border-b pb-2">
                        Mandatory Information
                    </h3>

                    {/* Transaction */}
                    <CustomSelect
                        label={"Transaction type *"}
                        value={transactionType || null}
                        onChange={(val) => {
                            setTransactionType(val);
                            setCity("");  // reset dependent fields
                            setDistrict("");
                        }}
                        options={transactionOptions}
                        placeholder="Select Transaction Type"
                    />

                    {/* Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* City */}
                        <CustomSelect
                            label={"City *"}
                            value={city || null}
                            onChange={setCity}
                            options={cityOptions}
                            placeholder="Select City"
                            disabled={!schema}
                        />

                        {/* District */}
                        <CustomSelect
                            label={"District *"}
                            value={district || null}
                            onChange={setDistrict}
                            options={districtOptions}
                            placeholder="Select District"
                            disabled={!city}
                        />

                        {/* Area */}
                        <CustomSelect
                            label={"Area *"}
                            value={area ? Number(area) : null}
                            onChange={(val) => setArea(String(val))}
                            options={areaOptions}
                            placeholder="Select Area"
                            disabled={!schema}
                        />

                    </div>
                </div>

                {/* OPTIONAL */}
                <div className="bg-blue-50 p-6 rounded-2xl border border-blue-200 space-y-6">
                    <h3 className="text-lg font-semibold text-blue-800 border-b pb-2">
                        Optional Information (Default values)
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        {/* Bedrooms */}
                        <CustomSelect
                            label={"Bedrooms"}
                            value={bedrooms ? Number(bedrooms) : null}
                            onChange={(v) => setBedrooms(String(v))}
                            options={bedroomOptions}
                            placeholder="Bedrooms"
                            disabled={!schema}
                        />

                        {/* Floor */}
                        <CustomSelect
                            label={"Floor"}
                            value={floor ? Number(floor) : null}
                            onChange={(v) => setFloor(String(v))}
                            options={floorOptions}
                            placeholder="Floor"
                            disabled={!schema}
                        />

                        {/* Year */}
                        <CustomSelect
                            label={"Year"}
                            value={year ? Number(year) : null}
                            onChange={(v) => setYear(String(v))}
                            options={yearOptions}
                            placeholder="Year"
                            disabled={!schema}
                        />

                        {/* Month */}
                        <CustomSelect
                            label={"Month"}
                            value={month ? Number(month) : null}
                            onChange={(v) => setMonth(String(v))}
                            options={monthOptions}
                            placeholder="Month"
                            disabled={!year}
                        />
                    </div>
                </div>

                {/* Submit */}
                <button
                    disabled={!isValid}
                    className={`w-full md:w-1/3 py-3 rounded-lg font-semibold transition
                    ${isValid
                        ? "bg-blue-700 hover:bg-blue-600 text-white"
                        : "bg-blue-300 text-white cursor-not-allowed"}
                    `}
                >
                    Predict Price
                </button>
            </form>

            {/* Result */}
            {result && (
                <div className="bg-white p-6 rounded-xl shadow mt-4">
                    <p className="text-blue-800 text-lg font-medium">{result}</p>
                </div>
            )}

            <LoadingOverlay visible={predictionLoading.loading} text="Predicting price..." />
            <LoadingOverlay visible={schemaLoading.loading} text="Loading inference data..." />
        </div>
    );
}
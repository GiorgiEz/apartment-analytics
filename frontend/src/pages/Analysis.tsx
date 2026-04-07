// src/pages/Analysis.tsx

import { useState } from "react";
import AnalysisNavbar from "../components/analysis/AnalysisNavbar";
import Charts from "../components/analysis/Charts";
import ChartModal from "../components/analysis/ChartModal";
import { useModal } from "../hooks/useModal";

import {ANALYSIS_DATA, ANALYSIS_ORDER} from "../components/analysis/AnalysisData";

export default function Analysis() {
    const [index, setIndex] = useState(0);
    const { image, open, close } = useModal();

    const total = ANALYSIS_ORDER.length;

    // current section
    const currentKey = ANALYSIS_ORDER[index];
    const current = ANALYSIS_DATA[currentKey];

    // navigation
    const next = () => setIndex((i) => (i + 1) % total);
    const prev = () => setIndex((i) => (i - 1 + total) % total);

    // prev/next labels
    const prevKey = ANALYSIS_ORDER[(index - 1 + total) % total];
    const nextKey = ANALYSIS_ORDER[(index + 1) % total];

    const shorten = (text: string, max = 18) =>
        text.length > max ? text.slice(0, max) + "…" : text;

    return (
        <div className="bg-blue-100 shadow-lg flex flex-col">

            {/* Navbar */}
            <AnalysisNavbar
                sectionTitle={current.label}
                onPrev={prev}
                onNext={next}
                prevLabel={`◀ ${shorten(ANALYSIS_DATA[prevKey].label)}`}
                nextLabel={`${shorten(ANALYSIS_DATA[nextKey].label)} ▶`}
            />

            {/* Charts */}
            <Charts sections={current.charts} onImageClick={open}/>

            {/* Modal */}
            <ChartModal image={image} onClose={close} />
        </div>
    );
}
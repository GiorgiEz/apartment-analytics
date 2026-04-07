// src/components/analysis/AnalysisNavbar.tsx

type Props = {
    sectionTitle: string;
    prevLabel: string;
    nextLabel: string;
    onNext: () => void;
    onPrev: () => void;
};

export default function AnalysisNavbar({sectionTitle, prevLabel, nextLabel, onNext, onPrev}: Props) {
    return (
        <div className="sticky top-0 bg-white shadow-md z-20">
            {/* Main Title */}
            <h1 className="text-3xl font-bold text-blue-800 text-center mt-2">Apartment Analysis Dashboard</h1>

            {/* Section Navigation */}
            <div className="flex flex-col gap-4 m-2 px-6">
                {/* Controls */}
                <div className="flex justify-between items-center w-full">
                    {/* Prev */}
                    <button
                        onClick={onPrev}
                        className="bg-blue-700 text-white px-3 py-2 rounded-lg hover:bg-blue-600 transition m-1 min-w-[120px] text-left"
                    >
                        {prevLabel}
                    </button>

                    {/* Section Title */}
                    <h2 className="text-2xl font-semibold text-blue-800 text-center">{sectionTitle}</h2>

                    {/* Next */}
                    <button
                        onClick={onNext}
                        className="bg-blue-700 text-white px-3 py-2 rounded-lg hover:bg-blue-600 transition m-1 min-w-[120px] text-right"
                    >
                        {nextLabel}
                    </button>
                </div>
            </div>
        </div>
    );
}
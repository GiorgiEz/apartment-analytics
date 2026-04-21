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
        <div className="sticky top-0 bg-white shadow-md z-20 h-[10vh] flex flex-col">

            {/* Top: Main Title (50%) */}
            <div className="flex items-center justify-center h-1/2">
                <h1 className="font-bold text-blue-800 text-center"
                    style={{ fontSize: "clamp(20px, 3vh, 35px)" }}>
                    Apartment Analysis Dashboard
                </h1>
            </div>

            {/* Bottom: Navigation (50%) */}
            <div className="flex items-center px-6 h-1/2 relative">

                {/* Prev */}
                <button
                    onClick={onPrev}
                    className="bg-blue-700 text-white rounded-lg hover:bg-blue-500 transition
                        px-3 py-1 min-w-[100px]"
                    style={{ fontSize: "clamp(10px, 2.0vh, 30px)" }}
                >
                    {prevLabel}
                </button>

                {/* Center Title */}
                <h2
                    className="absolute left-1/2 -translate-x-1/2 text-blue-800 whitespace-nowrap font-semibold"
                    style={{ fontSize: "clamp(15px, 2.5vh, 30px)" }}
                >
                    {sectionTitle}
                </h2>

                {/* Next */}
                <button
                    onClick={onNext}
                    className="ml-auto bg-blue-700 text-white rounded-lg hover:bg-blue-500 transition
                        px-3 py-1 min-w-[100px]"
                    style={{ fontSize: "clamp(10px, 2.0vh, 30px)" }}
                >
                    {nextLabel}
                </button>

            </div>
        </div>
    );
}
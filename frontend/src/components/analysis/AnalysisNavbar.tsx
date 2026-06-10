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
        <div className="sticky top-0 bg-white shadow-md z-20 h-[120px] md:h-[10vh] flex flex-col">

            {/* Top: Main Title (50%) */}
            <div className="flex items-center justify-center h-1/2">
                <h1 className="
                        font-bold text-blue-800 text-center
                        text-lg sm:text-xl md:text-2xl lg:text-3xl
                    ">
                    Apartment Analysis Dashboard
                </h1>
            </div>

            {/* Bottom: Navigation (50%) */}
            <div className="flex flex-col md:grid md:grid-cols-3 md:items-center px-6 h-1/2 gap-2">

                {/* Section title: centered on mobile (own row), center column on desktop */}
                <h2 className="
                        text-center md:col-start-2
                        text-blue-800 font-semibold
                        text-sm sm:text-base md:text-lg lg:text-xl
                    ">
                    {sectionTitle}
                </h2>

                {/* Buttons row: spans full width on mobile, occupies col 1 + col 3 on desktop */}
                <button
                    onClick={onPrev}
                    className="hidden md:block md:col-start-1 md:row-start-1 justify-self-start
                        bg-blue-700 text-white rounded-lg hover:bg-blue-500 transition
                        px-2 py-1 sm:px-3 min-w-[70px] text-xs sm:text-sm md:text-base"
                >
                    {prevLabel}
                </button>

                <button
                    onClick={onNext}
                    className="hidden md:block md:col-start-3 md:row-start-1 justify-self-end
                        bg-blue-700 text-white rounded-lg hover:bg-blue-500 transition
                        px-2 py-1 sm:px-3 min-w-[70px] text-xs sm:text-sm md:text-base"
                >
                    {nextLabel}
                </button>

                {/* Mobile-only buttons row */}
                <div className="flex justify-between w-full md:hidden">
                    <button
                        onClick={onPrev}
                        className="bg-blue-700 text-white rounded-lg hover:bg-blue-500 transition
                            px-2 py-1 sm:px-3 min-w-[70px] text-xs sm:text-sm"
                    >
                        {prevLabel}
                    </button>
                    <button
                        onClick={onNext}
                        className="bg-blue-700 text-white rounded-lg hover:bg-blue-500 transition
                            px-2 py-1 sm:px-3 min-w-[70px] text-xs sm:text-sm"
                    >
                        {nextLabel}
                    </button>
                </div>

            </div>
        </div>
    );
}
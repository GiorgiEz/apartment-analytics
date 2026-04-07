// src/components/analysis/Charts.tsx
import { type ChartSection } from "../../types/analysis";

type Props = {
    sections: ChartSection[];
    onImageClick: (src: string) => void;
};

export default function Charts({ sections, onImageClick }: Props) {
    const API_URL = import.meta.env.VITE_API_URL;

    return (
        <div className="flex flex-col gap-10 mt-2 p-4">
            {sections.map((section, i) => (
                <div key={i} className="flex flex-col gap-4">
                    <h3 className="text-xl font-semibold text-blue-800">{section.title}</h3>

                    <div className="flex flex-nowrap justify-center gap-6">
                        {section.src.map((src, j) => {
                            const fullSrc = API_URL + src;
                            const width = section.src.length === 1 ? "50%" : `${90 / section.src.length}%`;

                            return (
                                <button
                                    key={j}
                                    style={{ flex: `0 0 ${width}` }}
                                    onClick={() => onImageClick(fullSrc)}
                                    className="bg-white rounded-xl shadow-md overflow-hidden hover:scale-105 transition"
                                >
                                    <img
                                        src={fullSrc}
                                        className="w-full h-auto object-contain"
                                    />
                                </button>
                            );
                        })}
                    </div>
                </div>
            ))}
        </div>
    );
}
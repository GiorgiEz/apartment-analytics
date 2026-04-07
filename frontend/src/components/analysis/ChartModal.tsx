// src/components/analysis/ChartModal.tsx
type Props = {
    image: string | null;
    onClose: () => void;
};

export default function ChartModal({ image, onClose }: Props) {
    if (!image) return null;

    return (
        <div
            onClick={onClose} // ← close on outside click
            className="fixed inset-0 bg-black/20 backdrop-blur-md z-50 flex items-center justify-center p-4"
        >
            <div
                onClick={(e) => e.stopPropagation()}
                className="relative bg-white rounded-2xl max-w-6xl max-h-[95vh] p-4"
            >
                <button
                    onClick={onClose}
                    className="absolute top-3 right-3 text-2xl font-bold hover:scale-125"
                >
                    ✕
                </button>

                <img
                    src={image}
                    className="max-h-[85vh] max-w-full object-contain mx-auto"
                />
            </div>
        </div>
    );
}
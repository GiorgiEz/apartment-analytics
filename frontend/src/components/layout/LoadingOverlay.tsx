// src/components/common/LoadingOverlay.tsx


export default function LoadingOverlay({visible, text = "Processing...",}: {visible: boolean, text?: string}) {
    if (!visible) return null;

    return (
        <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="text-center space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto" />
                <p className="text-blue-800 font-semibold">{text}</p>
            </div>
        </div>
    );
}
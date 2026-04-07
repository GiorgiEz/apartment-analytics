import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const MOBILE_BREAKPOINT = 800;


export default function Sidebar() {
    const [collapsed, setCollapsed] = useState<boolean>(window.innerWidth < MOBILE_BREAKPOINT);
    const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth < MOBILE_BREAKPOINT);

    const navigate = useNavigate();
    const location = useLocation();

    const isOpen = !collapsed;  // Derived states
    const showOverlay = isMobile && isOpen;  // Overlay

    const isActive = (path: string) => location.pathname === path;

    // Handle resize
    useEffect(() => {
        const handleResize = () => {
            const mobile = window.innerWidth < MOBILE_BREAKPOINT;
            setIsMobile(mobile);

            if (mobile) {
                setCollapsed(true);
            } else {
                setCollapsed(false);
            }
        };

        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    return (
        <>
            {/* Overlay */}
            {showOverlay && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-40 z-30"
                    onClick={() => setCollapsed(true)}
                />
            )}

            {/* Sidebar */}
            <aside className={`
                    bg-blue-800 text-blue-100 font-bold shadow-xl p-4
                    flex flex-col gap-4 h-full transition-all duration-300 z-40
                    ${isOpen ? "w-64" : "w-14"}
                    ${isMobile && isOpen ? "fixed top-0 left-0 h-full" : ""}
                `}>
                {/* Toggle button */}
                <button
                    onClick={() => setCollapsed((prev) => !prev)}
                    className="fixed top-0 left-0 z-50 w-14 h-14 bg-blue-800 text-white
                    hover:bg-blue-600 transition flex items-center justify-center text-2xl"
                >
                    ☰
                </button>

                {/* Title */}
                {isOpen && (
                    <>
                        <h1 className="text-2xl mt-14 font-bold">Apartment Analytics In Georgia</h1>

                        <nav className="flex flex-col gap-4 mt-4">
                            <button
                                onClick={() => navigate("/analysis")}
                                className={`px-4 py-3 rounded-lg text-left transition-all
                                  ${isActive("/analysis") ? "bg-blue-600" : "bg-blue-700"}
                                `}
                            >
                                Dashboard
                            </button>

                            <button
                                onClick={() => navigate("/prediction")}
                                className={`px-4 py-3 rounded-lg text-left transition-all
                                  ${isActive("/prediction") ? "bg-blue-600" : "bg-blue-700"}
                                `}
                            >
                                Price Prediction
                            </button>
                        </nav>
                    </>
                )}
            </aside>
        </>
    );
}
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

type Option<T> = {
    value: T;
    label: string;
};

type Props<T> = {
    label: string;
    value: T | null;
    onChange: (value: T) => void;
    options: Option<T>[];
    placeholder?: string;
    disabled?: boolean;
};

export default function CustomSelect<T>({label, value, onChange, options, placeholder = "Select", disabled = false}: Props<T>) {
    const [open, setOpen] = useState(false);
    const [dropdownStyle, setDropdownStyle] = useState<React.CSSProperties>({});
    const containerRef = useRef<HTMLDivElement | null>(null);
    const dropdownRef = useRef<HTMLUListElement | null>(null);

    const selectedOption = options.find((o) => o.value === value);

    // Close on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            const target = e.target as Node;

            if (
                containerRef.current &&
                !containerRef.current.contains(target) &&
                dropdownRef.current &&
                !dropdownRef.current.contains(target)
            ) {
                setOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Update dropdown position
    const updatePosition = () => {
        if (!containerRef.current) return;

        const rect = containerRef.current.getBoundingClientRect();

        setDropdownStyle({
            position: "fixed",
            top: rect.bottom + 4,
            left: rect.left,
            width: rect.width,
            zIndex: 9999,
        });
    };

    // Handle open
    const handleToggle = () => {
        if (!open) {
            updatePosition();
        }
        setOpen((prev) => !prev);
    };

    // Sync position on scroll + resize
    useEffect(() => {
        if (!open) return;

        const handle = () => updatePosition();

        window.addEventListener("scroll", handle, true);
        window.addEventListener("resize", handle);

        return () => {
            window.removeEventListener("scroll", handle, true);
            window.removeEventListener("resize", handle);
        };
    }, [open]);

    return (
        <div ref={containerRef} className="w-full space-y-1">

            {/* Label */}
            <label className="text-sm font-semibold text-blue-800">
                {label}
            </label>

            {/* Button */}
            <button
                type="button"
                disabled={disabled}
                onClick={handleToggle}
                className={`
          w-full flex justify-between items-center
          border rounded-lg px-3 py-2 text-left
          transition-all duration-200
          
          ${disabled
                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                    : "bg-white hover:border-blue-400 focus:ring-2 focus:ring-blue-500"
                }
        `}
            >
        <span className="truncate">
          {selectedOption?.label || (
              <span className="text-gray-400">{placeholder}</span>
          )}
        </span>

                <span
                    className={`ml-2 text-sm transition-transform ${
                        open ? "rotate-180" : ""
                    }`}
                >
          ▼
        </span>
            </button>

            {/* Dropdown (PORTAL) */}
            {open &&
                !disabled &&
                createPortal(
                    <ul
                        ref={dropdownRef}
                        style={dropdownStyle}
                        className="
              bg-white border rounded-lg shadow-lg
              max-h-[30vh] overflow-y-auto
              animate-fadeIn
            "
                    >
                        {options.length === 0 && (
                            <li className="px-3 py-2 text-gray-400 text-sm">
                                No options available
                            </li>
                        )}

                        {options.map((opt) => {
                            const isSelected = opt.value === value;

                            return (
                                <li
                                    key={String(opt.value)}
                                    onClick={() => {
                                        onChange(opt.value);
                                        setOpen(false);
                                    }}
                                    className={`
                    px-3 py-2 cursor-pointer flex justify-between items-center
                    transition-colors
                    ${
                                        isSelected
                                            ? "bg-blue-50 text-blue-800 font-semibold"
                                            : "hover:bg-blue-100"
                                    }
                  `}
                                >
                                    <span>{opt.label}</span>
                                    {isSelected && <span>✓</span>}
                                </li>
                            );
                        })}
                    </ul>,
                    document.body
                )}
        </div>
    );
}
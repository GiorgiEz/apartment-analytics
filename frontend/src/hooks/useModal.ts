// src/components/analysis/useModal.ts
import { useState } from "react";

export function useModal() {
    const [image, setImage] = useState<string | null>(null);

    const open = (src: string) => setImage(src);
    const close = () => setImage(null);

    return { image, open, close };
}
import {MONTH_NAMES} from "@helpers/helper_functions.js"
import {hideLoading, loadLoadingOverlay, showLoading, sleep} from "@components/loading.js";


window.initPredictionView = async function () {
    await loadLoadingOverlay();

    setTimeout(async () => {

        const citySelect = document.getElementById("city");
        const districtSelect = document.getElementById("district");

        const areaSelect = document.getElementById("area_m2");
        const bedroomsSelect = document.getElementById("bedrooms");
        const floorSelect = document.getElementById("floor");

        const yearSelect = document.getElementById("year");
        const monthSelect = document.getElementById("month");

        const form = document.getElementById("prediction-form");
        const resultBox = document.getElementById("prediction-result");
        const resultText = document.getElementById("result-text");

        if (!citySelect || !districtSelect || !form) {
            console.error("Prediction view: required DOM elements not found");
            return;
        }

        async function fetchWithTimeout(url, options = {}, timeoutMs = 10000) {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), timeoutMs);

            try {
                return await fetch(url, {
                    ...options,
                    signal: controller.signal,
                });
            } finally {
                clearTimeout(id);
            }
        }

        // City → District dependency (backend-driven)
        citySelect.addEventListener("change", async () => {
            const city = citySelect.value;

            districtSelect.innerHTML = `<option value="">Select District</option>`;
            districtSelect.disabled = !city;

            if (!city) return;

            try {
                districts_by_city[city].forEach(district => {
                    districtSelect.add(new Option(district, district));
                });
            } catch (err) {
                console.error("Failed to load districts:", err);
            }
        });

        // Year → Month restriction
        yearSelect.addEventListener("change", () => {
            const year = Number(yearSelect.value);

            // Reset month select
            monthSelect.innerHTML = "";
            monthSelect.disabled = true;

            if (!availableDates[year]) return;

            availableDates[yearSelect.value].forEach(month => {
                monthSelect.add(new Option(MONTH_NAMES[month], month));
            });

            monthSelect.disabled = false;

            // Auto-select month
            if (year === defaults.year) {
                // Initial load case
                monthSelect.value = String(defaults.month);
            } else {
                // User changed year → select latest month for that year
                const latestMonth = Math.max(...availableDates[year]);
                monthSelect.value = String(latestMonth);
            }
        });

        // Load metadata from backend
        let availableDates = {};
        let districts_by_city = {};
        let defaults = {};

        try {
            const response = await fetch(`/api/model/metadata`)
            const metadata = await response.json();

            const cities = await metadata["cities"];
            districts_by_city = await metadata["districts_by_city"];
            const bounds = await metadata["validation_bounds"];
            availableDates = await metadata["available_dates"];
            defaults = await metadata["defaults"];

            // Area (mandatory)
            areaSelect.innerHTML = `<option value="">Select area</option>`;
            for (let v = Math.floor(bounds.area_m2.min); v <= Math.ceil(bounds.area_m2.max); v++) {
                areaSelect.add(new Option(v, v));
            }

            // Bedrooms (optional, default selected)
            bedroomsSelect.innerHTML = ``;
            for (let v = bounds.bedrooms.min; v <= bounds.bedrooms.max; v++) {
                const opt = new Option(v, v);
                if (v === defaults.bedrooms) opt.selected = true;
                bedroomsSelect.add(opt);
            }

            // Floor (optional, default selected)
            floorSelect.innerHTML = ``;
            for (let v = bounds.floor.min; v <= bounds.floor.max; v++) {
                const opt = new Option(v, v);
                if (v === defaults.floor) opt.selected = true;
                floorSelect.add(opt);
            }

            // Populate cities
            cities.forEach(city => citySelect.add(new Option(city, city)));

            // Populate years
            Object.keys(availableDates)
            .sort((a, b) => Number(a) - Number(b))
            .forEach(year => yearSelect.add(new Option(year, year)));

            yearSelect.value = defaults.year;
            yearSelect.dispatchEvent(new Event("change"));

        } catch (err) {
            console.error("Failed to load metadata:", err);
            return;
        }

        // Submit → Predict
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            resultBox.classList.add("hidden");
            showLoading();

            const startTime = Date.now();

            const payload = {
                city: citySelect.value,
                district: districtSelect.value,
                area_m2: Number(areaSelect.value),
                bedrooms: bedroomsSelect.value ? Number(bedroomsSelect.value) : null,
                floor: floorSelect.value ? Number(floorSelect.value) : null,
                year: yearSelect.value ? Number(yearSelect.value) : null,
                month: monthSelect.value ? Number(monthSelect.value) : null,
            };

            try {
                const response = await fetchWithTimeout(
                    `/api/predict`,
                    {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload),
                    },
                    10000 // max 10s
                );

                if (!response.ok) {
                    throw new Error(`Server error (${response.status})`);
                }

                const data = await response.json();

                // Ensure minimum 1s loading time
                const elapsed = Date.now() - startTime;
                if (elapsed < 1000) {
                    await sleep(1000 - elapsed);
                }

                resultText.innerHTML = `
                <div class="space-y-1">
                    <p><strong>Price per sqm:</strong> $${data.price_per_sqm.toFixed(2)}</p>
                    <p><strong>Total apartment price:</strong> $${data.total_price.toFixed(2)}</p>
                    <p><strong>Estimated monthly rent:</strong> $${data.monthly_rent.toFixed(2)}</p>
                </div>
                `;

                resultBox.classList.remove("hidden");

            } catch (err) {
                const elapsed = Date.now() - startTime;
                if (elapsed < 1000) {
                    await sleep(1000 - elapsed);
                }

                resultText.textContent =
                    err.name === "AbortError"
                        ? "Prediction took too long. Please try again."
                        : "Prediction failed. Please try again.";

                resultBox.classList.remove("hidden");
            } finally {
                hideLoading();
            }
        });
    }, 100);
};

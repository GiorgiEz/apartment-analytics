const API_BASE = "http://127.0.0.1:8000/api";

window.initPredictionView = function () {
    setTimeout(async () => {

        const citySelect = document.getElementById("city");
        const districtSelect = document.getElementById("district");
        const yearSelect = document.getElementById("year");
        const monthSelect = document.getElementById("month");

        const form = document.getElementById("prediction-form");
        const resultBox = document.getElementById("prediction-result");
        const resultText = document.getElementById("result-text");

        if (!citySelect || !districtSelect || !form) {
            console.error("Prediction view: required DOM elements not found");
            return;
        }

        // Load metadata from backend
        let availableDates = {};

        try {
            const [citiesRes, datesRes] = await Promise.all([
                fetch(`${API_BASE}/cities`),
                fetch(`${API_BASE}/available-dates`)
            ]);

            const cities = await citiesRes.json();
            availableDates = await datesRes.json();

            // Populate cities
            citySelect.innerHTML = `<option value="">Select city</option>`;
            cities.forEach(city => {
                citySelect.add(new Option(city, city));
            });

            Object.keys(availableDates)
            .sort((a, b) => Number(a) - Number(b))
            .forEach(year => {
                yearSelect.add(new Option(year, year));
            });

        } catch (err) {
            console.error("Failed to load metadata:", err);
            return;
        }

        // City → District dependency (backend-driven)
        citySelect.addEventListener("change", async () => {
            const city = citySelect.value;

            districtSelect.innerHTML = `<option value="">Select district</option>`;
            districtSelect.disabled = !city;

            if (!city) return;

            try {
                const res = await fetch(`${API_BASE}/districts/${encodeURIComponent(city)}`);
                const districts = await res.json();

                districts.forEach(district => {
                    districtSelect.add(new Option(district, district));
                });
            } catch (err) {
                console.error("Failed to load districts:", err);
            }
        });

        // Year → Month restriction (optional UX helper)
        yearSelect.addEventListener("change", () => {
            const year = yearSelect.value;
            monthSelect.innerHTML = `<option value="">Select Month</option>`;
            monthSelect.disabled = true;

            const MONTH_NAMES = {
                1: "January",
                2: "February",
                3: "March",
                4: "April",
                5: "May",
                6: "June",
                7: "July",
                8: "August",
                9: "September",
                10: "October",
                11: "November",
                12: "December",
            };

            if (!availableDates[year]) return;

            availableDates[year].forEach(month => {
                monthSelect.add(
                    new Option(MONTH_NAMES[month], month)
                );
            });

            monthSelect.disabled = false;
        });

        // Submit → Predict
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const area = Number(document.getElementById("area_m2").value);

            const payload = {
                city: citySelect.value,
                district: districtSelect.value,
                area_m2: area,
                bedrooms: Number(document.getElementById("bedrooms").value),
                floor: Number(document.getElementById("floor").value),
                year: Number(yearSelect?.value),
                month: Number(monthSelect?.value),
                transaction_type: "sale"   // adjust later if you add toggle
            };

            try {
                const res = await fetch(`${API_BASE}/predict`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();

                // Render Result
                if (data.price_per_sqm && data.monthly_rent) {
                    resultText.innerHTML = `
                        <div class="space-y-1">
                            <p><strong>Price per sqm:</strong> $${data.price_per_sqm.toFixed(2)}</p>
                            <p><strong>Total apartment price:</strong> $${data.total_price.toFixed(2)}</p>
                            <p><strong>Estimated monthly rent:</strong> $${data.monthly_rent.toFixed(2)}</p>
                        </div>
                    `;
                } else {
                    resultText.textContent = "Unexpected response from server.";
                }

                resultBox.classList.remove("hidden");

            } catch (err) {
                console.error("Prediction failed:", err);
                resultText.textContent = "Prediction failed. Please try again.";
                resultBox.classList.remove("hidden");
            }
        });
    }, 100);
};

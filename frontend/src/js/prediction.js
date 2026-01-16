window.initPredictionView = function () {
    setTimeout(() => {

        const citySelect = document.getElementById("city");
        const districtSelect = document.getElementById("district");
        const form = document.getElementById("prediction-form");
        const resultBox = document.getElementById("prediction-result");
        const resultText = document.getElementById("result-text");

        if (!citySelect || !districtSelect || !form) {
            console.error("Prediction view: required DOM elements not found");
            return;
        }

        const CITY_DISTRICTS = {
            "თბილისი": [
                "ვაკე",
                "საბურთალო",
                "დიდუბე",
                "გლდანი",
                "ისანი",
                "ნაძალადევი",
                "other"
            ],
            "ბათუმი": [
                "ცენტრი",
                "ანგისა",
                "other"
            ],
            "ქუთაისი": [
                "ცენტრი",
                "other"
            ]
        };

        /* ---------------------------
           Populate city select
        ---------------------------- */
        citySelect.innerHTML = `<option value="">Select city</option>`;
        Object.keys(CITY_DISTRICTS).forEach(city => {
            citySelect.add(new Option(city, city));
        });

        /* ---------------------------
           City → District dependency
        ---------------------------- */
        citySelect.addEventListener("change", () => {
            const city = citySelect.value;
            districtSelect.innerHTML = `<option value="">Select district</option>`;
            districtSelect.disabled = !city;

            if (!city) return;

            CITY_DISTRICTS[city].forEach(district => {
                districtSelect.add(new Option(district, district));
            });
        });

        /* ---------------------------
           Submit handler
        ---------------------------- */
        form.addEventListener("submit", (e) => {
            e.preventDefault();

            const area = Number(document.getElementById("area_m2").value);

            const payload = {
                city: citySelect.value,
                district: districtSelect.value,
                area_m2: area,
                bedrooms: Number(document.getElementById("bedrooms").value) || null,
                floor: Number(document.getElementById("floor").value) || null,
                year: Number(document.getElementById("year").value) || null,
                month: Number(document.getElementById("month").value) || null
            };

            console.log("Prediction payload:", payload);

            /* ---------------------------
               MOCK RESULT (until backend)
            ---------------------------- */
            const mockedPricePerSqm = 2063.93;
            const totalPrice = mockedPricePerSqm * area;

            resultText.innerHTML = `
                <div class="space-y-1">
                    <p><strong>Price per sqm:</strong> $${mockedPricePerSqm.toFixed(2)}</p>
                    <p><strong>Total apartment price:</strong> $${totalPrice.toFixed(2)}</p>
                </div>
            `;

            resultBox.classList.remove("hidden");
        });

    }, 100); // matches analysis.js timing
};

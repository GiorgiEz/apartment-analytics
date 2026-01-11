import json
import pandas as pd
import re
from config import paths



class NormalizeDistricts:
    def __init__(self, apartments_df):
        self.apartments_df = apartments_df

        self.__STREET_TOKENS = [
            "ქ.", "ქუჩა", "გამზ.", "გამზირი", "ჩიხ.", "ჩიხი", "შეს.", "შესახვევი", "მოედანი",
            "პროსპექტ", "პლ.", "დაღმ.", "ხეივ.", "ხეივანი", "კვარტ.", "კვარტალი", "გზატკეცილი",
            "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"
        ]

        self.__TOKEN_CANONICAL_MAP = {
            "ქ.": "ქუჩა",
            "გამზ.": "გამზირი",
            "ჩიხ.": "ჩიხი",
            "შეს.": "შესახვევი",
            "კვარტ.": "კვარტალი",
            "ხეივ.": "ხეივანი",
            "დაღმ.": "დაღმართი",
        }

        self.__STREET_TOKEN_PATTERN = "|".join(sorted(map(re.escape, self.__STREET_TOKENS), key=len, reverse=True))

    def __normalize_street(self, street):
        if not isinstance(street, str):
            return None

        s = street.strip()

        # 1. Canonicalize token variants FIRST
        for variant, canonical in self.__TOKEN_CANONICAL_MAP.items():
            if variant in s:
                s = s.replace(variant, canonical)

        # 2. Remove trailing house numbers after tokens
        s = re.sub(rf"({self.__STREET_TOKEN_PATTERN})\s*\d+[^\s]*$", r"\1", s)

        # 3. Remove bare trailing numbers
        s = re.sub(r"\s+\d+[^\s]*$", "", s)

        # 4. Remove trailing punctuation (safe after previous changes)
        s = re.sub(r"[,.;]+$", "", s)

        # 5. Normalize whitespace
        s = re.sub(r"\s+", " ", s)

        return s.strip().replace(" ", "")

    def __extract_district_from_street(self, street_address, district_names):
        if not isinstance(street_address, str):
            return None

        for district in district_names:
            if district in street_address:
                return district

        return None

    def __street_base_name(self, street_norm):
        if not street_norm:
            return None

        # Remove street tokens even when concatenated
        base = re.sub(rf"({self.__STREET_TOKEN_PATTERN})", "", street_norm)

        return base if base else None

    def __normalize_districts_single_city(self, df, city_map):
        df = df.copy()

        # Step 1: Extract district from street address
        district_names = set(city_map.values())

        mask = df["district_name"].isna() | (df["district_name"] == df["city"]) | (df["district_name"] == 'n.a')
        df.loc[mask, "district_name"] = df.loc[mask, "street_address"].apply(
            lambda s: self.__extract_district_from_street(s, district_names)
        )

        # Step 2: Directly compare normalized streets
        normalized_map = {
            self.__normalize_street(street): district
            for street, district in city_map.items()
            if self.__normalize_street(street)
        }

        df["street_norm"] = df["street_address"].apply(self.__normalize_street)

        mask = df["district_name"].isna() | (df["district_name"] == df["city"]) | (df["district_name"] == 'n.a')
        df.loc[mask, "district_name"] = df.loc[mask, "street_norm"].map(normalized_map)

        # Step 3: token-agnostic base name match (NEW)
        base_map = {
            self.__street_base_name(norm): district
            for norm, district in normalized_map.items()
            if self.__street_base_name(norm)
        }

        df["street_base"] = df["street_norm"].apply(self.__street_base_name)

        mask = df["district_name"].isna() | (df["district_name"] == df["city"])
        df.loc[mask, "district_name"] = df.loc[mask, "street_base"].map(base_map)

        # Step 4: Final Fallback
        df["district_name"] = df["district_name"].fillna("n.a")

        df.drop(columns=["street_norm", "street_base"], inplace=True)

        return df

    def normalize_kutaisi_and_batumi_districts(self):
        df = self.apartments_df.copy()

        with open(paths.STREET_TO_DISTRICT_JSON_PATH, "r", encoding="utf-8") as f:
            street_districts = json.load(f)

        result = []

        for city, city_df in df.groupby("city", sort=False):
            city_map = street_districts.get(city, {})

            if not city_map:
                city_df = city_df.copy()
                city_df["district_name"] = city_df["district_name"].fillna("n.a")
                result.append(city_df)
                continue

            city_df = self.__normalize_districts_single_city(city_df, city_map)
            result.append(city_df)

        df_out = pd.concat(result).sort_index()
        self.apartments_df = df_out

    def normalize_tbilisi_districts(self):
        df = self.apartments_df.copy()

        # Load canonical district map
        with open(paths.TBILISI_CANONICAL_DISTRICTS_PATH, "r", encoding="utf-8") as f:
            tbilisi_districts: dict[str, str] = json.load(f)

        # 1. Filter only Tbilisi
        is_tbilisi = df["city"].eq("თბილისი")

        # 2. Detect invalid district_name
        invalid_district = (
                df["district_name"].isna()
                | df["district_name"].str.strip().isin({None, "", "n.a", "თბილისი"})
        )

        mask = is_tbilisi & invalid_district

        # Work only on relevant rows
        subset = df.loc[mask, "description"].fillna("")

        # 3. Normalize using exact matching
        def extract_district(description: str) -> str | None:
            for variant in sorted(tbilisi_districts, key=len, reverse=True):
                if variant in description:
                    return tbilisi_districts[variant]
            return None

        df.loc[mask, "district_name"] = subset.apply(extract_district)

        df["district_name"] = df["district_name"].fillna("n.a")

        self.apartments_df = df


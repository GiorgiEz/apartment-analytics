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

        self.INVALID_DISTRICT_VALUES = {"", "n.a", "N/A", "თბილისი", "ქუთაისი", "ბათუმი"}

    def __normalize_street(self, street):
        """
            # Normalize street names for deterministic matching.
            # Produces a compact, token-canonical form without numbers or punctuation.
            # Returns None for non-string inputs.
        """
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
        """
            # Extract district name by direct substring match from street text.
            # Returns the first matched canonical district or None.
        """
        if not isinstance(street_address, str):
            return None

        for district in district_names:
            if district in street_address:
                return district

        return None

    def __street_base_name(self, street_norm):
        """
            # Remove street-type tokens from a normalized street name.
            # Used as a fallback when full street normalization fails.
        """

        if not street_norm:
            return None

        # Remove street tokens even when concatenated
        base = re.sub(rf"({self.__STREET_TOKEN_PATTERN})", "", street_norm)

        return base if base else None

    def _is_unresolved(self, s: pd.Series):
        """
            # Identify unresolved district values (missing or placeholder values).
            # Centralizes missingness logic across all normalization steps
        """
        return (
                s.isna() | s.astype("string")
                .str.strip().str.lower().isin({v.lower() for v in self.INVALID_DISTRICT_VALUES})
        )

    def __normalize_districts_single_city(self, df, city_map):
        """
        Normalize district names for a single city using street-based matching.

        Scope:
        - Operates only on the provided city-specific DataFrame slice
        - Updates district_name ONLY for unresolved values
        - Uses a deterministic, multi-pass street-matching strategy
        - Does not modify row order or row count

        Strategy (applied sequentially):
        1) Extract district by scanning street text for known district names
        2) Match fully normalized street names against a street → district map
        3) Match token-agnostic base street names as a fallback

        Each step:
        - Recomputes the unresolved mask
        - Only fills district_name where it is still unresolved
        - Never overwrites previously resolved values

        Input assumptions:
        - df contains rows for a single city
        - city_map maps street names to canonical district names
        - Helper methods (__normalize_street, __street_base_name, etc.) are deterministic

        Output guarantees:
        - district_name is filled when a confident match is found
        - district_name remains pd.NA if no match is found
        - Temporary helper columns are removed before returning
        """
        df = df.copy()

        # Step 1: Extract district from street address
        district_names = set(city_map.values())

        mask = self._is_unresolved(df["district_name"])
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
        mask = self._is_unresolved(df["district_name"])
        df.loc[mask, "district_name"] = df.loc[mask, "street_norm"].map(normalized_map)

        # Step 3: token-agnostic base name match (NEW)
        base_map = {
            self.__street_base_name(norm): district
            for norm, district in normalized_map.items()
            if self.__street_base_name(norm)
        }

        df["street_base"] = df["street_norm"].apply(self.__street_base_name)
        mask = self._is_unresolved(df["district_name"])
        df.loc[mask, "district_name"] = df.loc[mask, "street_base"].map(base_map)

        df.drop(columns=["street_norm", "street_base"], inplace=True)

        return df

    def normalize_non_tbilisi_districts(self):
        """
        Normalize district names for non-Tbilisi cities using street-based mappings.

        Scope:
        - Performs normalization ONLY for cities that have a street → district mapping
          defined in STREET_TO_DISTRICT_JSON_PATH (e.g. Kutaisi, Batumi)
        - Cities without a mapping are left unchanged

        Strategy:
        - Uses multi-pass street-based normalization:
            1) Extract district from street text
            2) Match normalized street names
            3) Match token-agnostic base street names
        - Each pass only operates on unresolved district_name values

        Missing-value policy:
        - Unresolved districts remain as pd.NA
        - No rows are dropped or reordered

        Output guarantees:
        - district_name is updated only when a confident match is found
        - Existing valid district_name values are never overwritten
        - Row count and index order are preserved
        """
        df = self.apartments_df.copy()

        # load street → district mapping
        with open(paths.STREET_TO_DISTRICT_JSON_PATH, "r", encoding="utf-8") as f:
            street_districts = json.load(f)

        result = []

        for city, city_df in df.groupby("city", sort=False):
            city_map = street_districts.get(city, {})  # Extracts street -> district mapping for each city

            if not city_map:
                result.append(city_df.copy())
                continue

            city_df = self.__normalize_districts_single_city(city_df, city_map)
            result.append(city_df)

        df_out = pd.concat(result).sort_index()  # Recombine all cities and preserve original row order
        self.apartments_df = df_out

    def normalize_tbilisi_districts(self):
        """
        Normalize district names for Tbilisi apartments using description text.

        Scope:
        - Applies ONLY to rows where city == 'თბილისი'
        - Updates district_name ONLY if it is unresolved (pd.NA, placeholders, or city name)
        - Uses exact substring matching against a canonical district mapping
        - Leaves unresolved districts as pd.NA (no sentinel values introduced)

        Input assumptions:
        - district_name may be missing or invalid
        - description may contain district names in inflected forms
        - canonical mapping is provided via TBILISI_CANONICAL_DISTRICTS_PATH

        Output guarantees:
        - district_name is set to a canonical district when a match is found
        - district_name remains pd.NA if no match is found
        - Non-Tbilisi rows are not modified
        """
        df = self.apartments_df.copy()

        # Load canonical district map
        with open(paths.TBILISI_CANONICAL_DISTRICTS_PATH, "r", encoding="utf-8") as f:
            tbilisi_districts: dict[str, str] = json.load(f)

        is_tbilisi = df["city"].eq("თბილისი")  # Filter only Tbilisi
        invalid_district = self._is_unresolved(df["district_name"])  # Detect invalid district_name

        mask = is_tbilisi & invalid_district
        subset = df.loc[mask, "description"].fillna("")  # Work only on relevant rows

        # Normalize using exact matching
        def extract_district(description):
            if not isinstance(description, str):
                return None
            for variant in sorted(tbilisi_districts, key=len, reverse=True):
                if variant in description:
                    return tbilisi_districts[variant]
            return None

        df.loc[mask, "district_name"] = subset.apply(extract_district)

        self.apartments_df = df

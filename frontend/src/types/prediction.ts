export type SchemaType = {
    cities: string[];
    city_districts: Record<string, string[]>;
    area_m2: { hard_min: number; hard_max: number, soft_min: number, soft_max: number };
    bedrooms: { hard_min: number; hard_max: number };
    floor: { hard_min: number; hard_max: number, soft_max_by_city: Record<string, number> };
    upload_date: { years: number[]; year_month_map: Record<string, number[]> };
    defaults: { bedrooms: number; floor: number; year: number; month: number };
};
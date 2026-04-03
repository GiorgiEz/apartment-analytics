from machine_learning.local_price_prediction.LocalPricePredictor import LocalPricePredictor



if __name__ == "__main__":
    "Test models_metadata"
    predictor = LocalPricePredictor()

    city = "თბილისი"
    district = "ვაკე"
    area_m2 = 80
    bedrooms = 2
    floor = 3
    upload_date = "2026-01-14 13:39:00"

    prices = predictor.predict_single(
        city=city,
        district=district,
        area_m2=area_m2,
        bedrooms=bedrooms,
        floor=floor,
        upload_date=upload_date
    )

    print(f"\nTotal sale price: {prices['sale_price']}")
    print(f"Monthly rent: {prices['rent_price']}")

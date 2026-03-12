from machine_learning.local_price_prediction.LocalPricePredictor import LocalPricePredictor



if __name__ == "__main__":
    "Test models_metadata"
    predictor = LocalPricePredictor()

    city = "თბილისი"
    district = "ვაკე"
    area_m2 = 60
    bedrooms = 1
    floor = 3
    year = 1
    month = 2

    prices = predictor.predict_single(
        city=city,
        district=district,
        area_m2=area_m2,
        bedrooms=bedrooms,
        floor=floor,
        year=year,
        month=month
    )

    print(f"\nTotal sale price: {prices['sale_price']}")
    print(f"Monthly rent: {prices['rent_price']}")

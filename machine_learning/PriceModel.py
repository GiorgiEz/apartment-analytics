from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np


class PriceModel:
    def __init__(self, df, target):
        self.df = df.copy()
        self.target = target

        if target not in {"price", "price_per_sqm"}:
            raise ValueError("target must be 'price' or 'price_per_sqm'")

        self._prepare_data()

    def _prepare_data(self):
        # Drop leakage column
        leakage_col = "price_per_sqm" if self.target == "price" else "price"
        self.df.drop(columns=[leakage_col], inplace=True)

        # Drop rows with missing target
        self.df = self.df.dropna(subset=[self.target])

        self.df = self.df.sort_values(
            ["upload_year", "month_sin", "month_cos"]
        ).reset_index(drop=True)

        self.y = np.log1p(self.df[self.target])
        self.X = self.df.drop(columns=[self.target])

    def build_pipeline(self):
        numeric_features = [
            "area_m2",
            "bedrooms",
            "floor",
            "upload_year",
            "month_sin",
            "month_cos",
        ]

        categorical_features = [
            "city",
            "district_grouped",
        ]

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ]
        )

        self.pipeline = Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", HistGradientBoostingRegressor(
                    max_depth=3,
                    learning_rate=0.03,
                    max_iter=500,
                    min_samples_leaf=20,
                    random_state=42
                )),
            ]
        )

    def train_and_evaluate(self):
        self.build_pipeline()

        tscv = TimeSeriesSplit(n_splits=3)

        maes = []
        rmses = []
        r2s = []

        for train_idx, val_idx in tscv.split(self.X):
            X_train, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
            y_train, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]

            self.pipeline.fit(X_train, y_train)
            preds = self.pipeline.predict(X_val)

            # inverse transform
            y_val_orig = np.expm1(y_val)
            preds_orig = np.expm1(preds)

            maes.append(mean_absolute_error(y_val_orig, preds_orig))
            rmses.append(np.sqrt(mean_squared_error(y_val_orig, preds_orig)))
            r2s.append(r2_score(y_val_orig, preds_orig))

        print(f"Target: {self.target}")
        print(f"{'Monthly Rent' if self.target == 'price' else 'For Sale'}")
        print(f"MAE:  {np.mean(maes):.2f}")
        print(f"RMSE: {np.mean(rmses):.2f}")
        print(f"R²:   {np.mean(r2s):.3f}")

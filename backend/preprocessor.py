import numpy as np
import pandas as pd


class DataPreprocessor:
    def __init__(self):
        self.means_: np.ndarray | None = None
        self.stds_: np.ndarray | None = None
        self.feature_names_: list[str] | None = None

    def fit(self, df: pd.DataFrame, feature_cols: list[str]) -> "DataPreprocessor":

        self.feature_names_ = feature_cols
        X = df[feature_cols].values.astype(np.float64)
        self.means_ = np.mean(X, axis=0)
        self.stds_ = np.std(X, axis=0)
        # Guard against division by zero if a feature has zero variance
        self.stds_[self.stds_ == 0.0] = 1.0
        return self

    def transform(
        self, df: pd.DataFrame, feature_cols: list[str] | None = None
    ) -> np.ndarray:

        if self.means_ is None or self.stds_ is None:
            raise ValueError("Preprocessor has not been fitted. Call fit() first.")
        cols = feature_cols or self.feature_names_
        X = df[cols].values.astype(np.float64)
        return (X - self.means_) / self.stds_

    def fit_transform(self, df: pd.DataFrame, feature_cols: list[str]) -> np.ndarray:

        return self.fit(df, feature_cols).transform(df, feature_cols)

    @staticmethod
    def min_max_scale_0_to_100(values: np.ndarray) -> np.ndarray:
        """Scales values to the [0, 100] range for radar charts."""
        min_val = np.min(values)
        max_val = np.max(values)
        if max_val == min_val:
            return np.full_like(values, 50.0)
        return ((values - min_val) / (max_val - min_val)) * 100.0

import numpy as np
from config import Distance_Metric, N_Neighbors, Use_SKLearn_Backend
from sklearn.neighbors import NearestNeighbors


class StrikerKNN:
    def __init__(
        self,
        n_neighbors: int = N_Neighbors,
        metric: str = Distance_Metric,
        use_sklearn: bool = bool(Use_SKLearn_Backend),
    ):
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.use_sklearn = use_sklearn
        self.X_train: np.ndarray | None = None
        self.sklearn_model: NearestNeighbors | None = None

    def fit(self, X: np.ndarray) -> "StrikerKNN":
        self.X_train = np.asarray(X, dtype=np.float64)
        if self.use_sklearn:
            self.sklearn_model = NearestNeighbors(
                n_neighbors=self.n_neighbors, metric=self.metric, algorithm="auto"
            )
            self.sklearn_model.fit(self.X_train)
        return self

    def _calculate_euclidean(self, target_vector: np.ndarray) -> np.ndarray:
        difference = self.X_train - target_vector
        squared_diff = difference**2
        sum_squared = np.sum(squared_diff, axis=1)
        return np.sqrt(sum_squared)

    def kneighbors(
        self, target_vector: np.ndarray, k: int | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        if self.X_train is None:
            raise ValueError(
                "Model must be fitted with fit(X) before querying neighbors."
            )
        k_neighbors = k or self.n_neighbors
        target_vector = np.asarray(target_vector, dtype=np.float64).reshape(1, -1)
        if self.use_sklearn and self.sklearn_model is not None:
            distances, indices = self.sklearn_model.kneighbors(
                target_vector, n_neighbors=k_neighbors
            )
            return distances[0], indices[0]
        else:
            # Custom NumPy vector distance formula
            distances_all = self._calculate_euclidean(target_vector[0])
            sorted_indices = np.argsort(distances_all)[:k_neighbors]
            sorted_distances = distances_all[sorted_indices]
            return sorted_distances, sorted_indices

    def get_neighbors_by_index(
        self, target_idx: int, k: int | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        if self.X_train is None:
            raise ValueError("Model is not fitted.")
        if target_idx < 0 or target_idx >= len(self.X_train):
            raise IndexError(
                f"Index {target_idx} is out of bounds for dataset of size {len(self.X_train)}."
            )
        target_vector = self.X_train[target_idx]
        return self.kneighbors(target_vector, k=k)

    @staticmethod
    def compute_similarity_score(distance: float) -> float:
        """Converts distance into normalized similarity score in (0, 1]:
        Similarity = 1 / (1 + distance)
        """
        return 1.0 / (1.0 + float(distance))

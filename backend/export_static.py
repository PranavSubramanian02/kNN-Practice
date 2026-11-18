import json
import os

import numpy as np
from config import (
    All_Features,
    Base_Dir,
    Data_Path,
    Feature_Categories,
    Feature_Labels,
    Target_Player,
)
from dataloader import load_data
from preprocessor import DataPreprocessor
from sklearn.decomposition import PCA

Output_Path = os.path.join(Base_Dir, "frontend", "data.json")


def export_static_data(output_path: str = Output_Path) -> str:
    """Precomputes z-scores, percentiles, and 2D PCA coordinates into a static JSON bundle."""
    df = load_data(Data_Path)
    preprocessor = DataPreprocessor()
    X_scaled = preprocessor.fit_transform(df, All_Features)

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    # Precompute percentile ranks per feature across all strikers
    feature_arrays = {f: df[f].to_numpy(dtype=np.float64) for f in All_Features}

    categories = [
        {"name": cat_name.split(". ")[-1], "features": feats}
        for cat_name, feats in Feature_Categories.items()
    ]

    players = []
    for idx, (_, row) in enumerate(df.iterrows()):
        raw = [float(row[f]) for f in All_Features]
        pct = [
            round(float((feature_arrays[f] <= raw[f_idx]).mean() * 100.0), 1)
            for f_idx, f in enumerate(All_Features)
        ]
        players.append(
            {
                "player": str(row["player"]),
                "search_name": str(row["player_search"]),
                "club": str(row["club"]),
                "league": str(row["league"]),
                "position": str(row["position"]),
                "total_goals": int(row["total_goals"]),
                "total_assists": int(row["total_assists"]),
                "goals_per90": round(float(row["goals_per90"]), 2),
                "assists_per90": round(float(row["assists_per90"]), 2),
                "raw": raw,
                "z": [round(float(val), 6) for val in X_scaled[idx]],
                "pct": pct,
                "pca": [
                    round(float(X_pca[idx, 0]), 3),
                    round(float(X_pca[idx, 1]), 3),
                ],
            }
        )

    payload = {
        "default_benchmark": Target_Player,
        "features": All_Features,
        "feature_labels": Feature_Labels,
        "categories": categories,
        "players": players,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    return output_path


if __name__ == "__main__":
    path = export_static_data()
    size_kb = os.path.getsize(path) / 1024
    print(f"Exported static dataset to {path} ({size_kb:.1f} KB)")

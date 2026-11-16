import os
from typing import Any

import numpy as np
import pandas as pd
from config import (
    All_Features,
    Feature_Categories,
    Feature_Labels,
    Report_Paths,
    Target_Player,
)
from dataloader import find_player_index
from knn_model import StrikerKNN
from preprocessor import DataPreprocessor
from sklearn.decomposition import PCA


class SimilarityEvaluator:
    def __init__(self, df: pd.DataFrame, target_name: str = Target_Player):
        self.df = df
        self.preprocessor = DataPreprocessor()
        self.target_name = target_name
        self.target_idx = find_player_index(self.df, self.target_name)

    def set_target(self, target_name: str):
        self.target_name = target_name
        self.target_idx = find_player_index(self.df, self.target_name)

    def evaluate_features(
        self, feature_list: list[str], top_k: int = 5
    ) -> pd.DataFrame:
        X_scaled = self.preprocessor.fit_transform(self.df, feature_list)
        knn = StrikerKNN(n_neighbors=top_k + 1)
        knn.fit(X_scaled)
        distances, indices = knn.get_neighbors_by_index(self.target_idx)
        results: list[dict[str, Any]] = []

        # Exclude index 0 (self-comparison)
        for rank, (dist, idx) in enumerate(
            zip(distances[1 : top_k + 1], indices[1 : top_k + 1]), start=1
        ):
            player_row = self.df.iloc[idx]
            sim_score = StrikerKNN.compute_similarity_score(dist)
            results.append(
                {
                    "Rank": rank,
                    "Player": player_row["player"],
                    "Club": player_row["club"],
                    "League": player_row["league"],
                    "Position": player_row["position"],
                    "Euclidean Distance": round(float(dist), 4),
                    "Similarity Score": f"{round(sim_score * 100, 1)}%",
                }
            )
        return pd.DataFrame(results)

    def get_category_radar_data(
        self, competitor_name: str
    ) -> dict[str, dict[str, float]]:
        comp_idx = find_player_index(self.df, competitor_name)
        radar_data: dict[str, dict[str, float]] = {}

        for category_name, features in Feature_Categories.items():
            X_cat_scaled = self.preprocessor.fit_transform(self.df, features)

            target_mean_z = float(np.mean(X_cat_scaled[self.target_idx]))
            comp_mean_z = float(np.mean(X_cat_scaled[comp_idx]))

            # Map mean z-score into 0-100 range (center = 50, standard spread = 15)
            target_score = max(10.0, min(95.0, 50.0 + (target_mean_z * 15.0)))
            comp_score = max(10.0, min(95.0, 50.0 + (comp_mean_z * 15.0)))

            clean_label = category_name.split(". ")[-1]
            radar_data[clean_label] = {
                "target": round(target_score, 1),
                "competitor": round(comp_score, 1),
            }

        return radar_data

    def generate_markdown_report(self, output_file: str = Report_Paths) -> str:
        """Generates and writes outputs/similarity-ranking.md."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        target_info = self.df.iloc[self.target_idx]
        lines = [
            f"# Striker KNN Similarity Analysis: Nearest Peers to {self.target_name}",
            f"\n**Benchmark Player**: {target_info['player']} ({target_info['club']}, {target_info['league']})  ",
            "**Season Data**: 2026/27 (All counting metrics converted to Per 90)  ",
            f"**Total Pool**: {len(self.df)} strikers analyzed across Top 5 European Leagues\n",
            "---",
            "## 1. Overall Similarity Rankings (All 15 Metrics Combined)\n",
            "Ranked by shortest Euclidean distance in standardized feature space:\n",
        ]

        df_overall = self.evaluate_features(All_Features, top_k=10)
        lines.append(df_overall.to_markdown(index=False))

        lines.append("\n---\n## 2. Category-Specific Similarity Breakdowns\n")
        for cat_name, feat_cols in Feature_Categories.items():
            lines.append(f"\n### {cat_name}")
            lines.append(f"*Evaluated metrics: `{', '.join(feat_cols)}`*\n")
            df_cat = self.evaluate_features(feat_cols, top_k=5)
            lines.append(df_cat.to_markdown(index=False))

        lines.extend(
            [
                "\n---",
                "## 3. Mathematical Methodology",
                "1. **Per-90 Normalization**: Volume metrics are transformed via `(metric / minutes) * 90`.",
                "2. **Z-Score Standardization**: `z = (x - mean) / std` centers data around 0 with unit variance.",
                "3. **Euclidean Distance**: `d = sqrt( sum( (z_target - z_peer)^2 ) )`.",
                "4. **Similarity Index**: `S = 1 / (1 + d)` mapped to a percentage scale.",
            ]
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return output_file

    def compare_strikers(
        self, competitor_name: str, benchmark_name: str | None = None
    ) -> dict[str, Any]:
        """Performs full head-to-head comparison between benchmark striker and competitor."""
        target_name = benchmark_name or self.target_name
        target_idx = find_player_index(self.df, target_name)
        comp_idx = find_player_index(self.df, competitor_name)

        target_row = self.df.iloc[target_idx]
        comp_row = self.df.iloc[comp_idx]

        # 1. Z-Score standardized space & Euclidean distance
        X_scaled = self.preprocessor.fit_transform(self.df, All_Features)
        z_target = X_scaled[target_idx]
        z_comp = X_scaled[comp_idx]
        z_diffs = np.abs(z_target - z_comp)

        dist = float(np.linalg.norm(z_target - z_comp))
        sim_pct = float(StrikerKNN.compute_similarity_score(dist) * 100)

        # 2. Closest and Farthest Metrics
        closest_idx = int(np.argmin(z_diffs))
        farthest_idx = int(np.argmax(z_diffs))

        closest_feature = All_Features[closest_idx]
        farthest_feature = All_Features[farthest_idx]

        closest_metric = {
            "feature": closest_feature,
            "label": Feature_Labels.get(closest_feature, closest_feature),
            "z_diff": round(float(z_diffs[closest_idx]), 3),
            "target_val": round(float(target_row[closest_feature]), 2),
            "comp_val": round(float(comp_row[closest_feature]), 2),
        }

        farthest_metric = {
            "feature": farthest_feature,
            "label": Feature_Labels.get(farthest_feature, farthest_feature),
            "z_diff": round(float(z_diffs[farthest_idx]), 3),
            "target_val": round(float(target_row[farthest_feature]), 2),
            "comp_val": round(float(comp_row[farthest_feature]), 2),
        }

        # 3. 4 Dedicated Category Radars (Percentile Ranks across 141 Strikers)
        category_radars: dict[str, Any] = {}
        for cat_name, feats in Feature_Categories.items():
            clean_cat = cat_name.split(". ")[-1]
            category_radars[clean_cat] = {
                "labels": [Feature_Labels.get(f, f) for f in feats],
                "features": feats,
                "target_scores": [
                    round(
                        float((self.df[f] <= target_row[f]).mean() * 100.0),
                        1,
                    )
                    for f in feats
                ],
                "competitor_scores": [
                    round(
                        float((self.df[f] <= comp_row[f]).mean() * 100.0),
                        1,
                    )
                    for f in feats
                ],
                "target_raw": [round(float(target_row[f]), 2) for f in feats],
                "competitor_raw": [round(float(comp_row[f]), 2) for f in feats],
            }

        # 4. 15-Metric Comparison Table
        comparison_table: list[dict[str, Any]] = []
        for cat_name, feats in Feature_Categories.items():
            clean_cat = cat_name.split(". ")[-1]
            for f in feats:
                t_val = float(target_row[f])
                c_val = float(comp_row[f])
                f_idx = All_Features.index(f)
                z_d = round(float(z_diffs[f_idx]), 3)

                comparison_table.append(
                    {
                        "category": clean_cat,
                        "feature": f,
                        "label": Feature_Labels.get(f, f),
                        "target_value": round(t_val, 2),
                        "competitor_value": round(c_val, 2),
                        "raw_diff": round(t_val - c_val, 2),
                        "z_diff": z_d,
                        "advantage": (
                            "target"
                            if t_val > c_val
                            else ("competitor" if c_val > t_val else "equal")
                        ),
                    }
                )

        # 5. 2D PCA Coordinates for European Strikers Map
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X_scaled)
        pca_points = [
            {
                "player": str(row["player"]),
                "club": str(row["club"]),
                "league": str(row["league"]),
                "x": round(float(X_pca[idx, 0]), 3),
                "y": round(float(X_pca[idx, 1]), 3),
                "is_target": (idx == target_idx),
                "is_competitor": (idx == comp_idx),
            }
            for idx, (_, row) in enumerate(self.df.iterrows())
        ]

        return {
            "target": {
                "player": str(target_row["player"]),
                "club": str(target_row["club"]),
                "league": str(target_row["league"]),
                "position": str(target_row["position"]),
                "total_goals": int(target_row["total_goals"]),
                "total_assists": int(target_row["total_assists"]),
                "goals_per90": round(float(target_row["goals_per90"]), 2),
                "assists_per90": round(float(target_row["assists_per90"]), 2),
            },
            "competitor": {
                "player": str(comp_row["player"]),
                "club": str(comp_row["club"]),
                "league": str(comp_row["league"]),
                "position": str(comp_row["position"]),
                "total_goals": int(comp_row["total_goals"]),
                "total_assists": int(comp_row["total_assists"]),
                "goals_per90": round(float(comp_row["goals_per90"]), 2),
                "assists_per90": round(float(comp_row["assists_per90"]), 2),
            },
            "euclidean_distance": round(dist, 4),
            "similarity_percentage": round(sim_pct, 1),
            "closest_metric": closest_metric,
            "farthest_metric": farthest_metric,
            "category_radars": category_radars,
            "comparison_table": comparison_table,
            "pca_points": pca_points,
        }

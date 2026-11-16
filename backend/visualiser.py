import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import (
    All_Features,
    PCA_Plot_Path,
    Radar_Plot_Path,
    Target_Player,
)
from dataloader import find_player_index
from matplotlib.projections.polar import PolarAxes
from preprocessor import DataPreprocessor
from sklearn.decomposition import PCA


class StrikerVisualiser:
    def __init__(self, df: pd.DataFrame, target_name: str = Target_Player):
        self.df = df
        self.target_name = target_name
        self.target_idx = find_player_index(self.df, self.target_name)
        self.preprocessor = DataPreprocessor()

    def plot_pca_projection(
        self, neighbor_names: list[str], save_path: str = PCA_Plot_Path
    ):
        """Projects the 15-dimensional striker metrics to 2D via PCA.

        Highlights the benchmark striker and their nearest peers.
        """
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Standardize all 15 metrics
        X_scaled = self.preprocessor.fit_transform(self.df, All_Features)

        # Fit 2-Component PCA
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X_scaled)

        var_pc1 = pca.explained_variance_ratio_[0] * 100
        var_pc2 = pca.explained_variance_ratio_[1] * 100

        fig, ax = plt.subplots(figsize=(11, 7.5))

        # 1. Background scatter: all other European strikers in light gray
        ax.scatter(
            X_pca[:, 0],
            X_pca[:, 1],
            c="#d1d5db",
            alpha=0.6,
            s=40,
            edgecolors="none",
            label="All Other Strikers",
        )

        # 2. Benchmark Striker: highlighted in Crimson Red
        t_x, t_y = X_pca[self.target_idx, 0], X_pca[self.target_idx, 1]
        ax.scatter(
            t_x,
            t_y,
            c="#dc2626",
            s=140,
            edgecolors="black",
            linewidth=1.5,
            zorder=5,
            label=f"Target: {self.target_name}",
        )
        ax.annotate(
            self.target_name,
            (t_x, t_y),
            xytext=(7, 7),
            textcoords="offset points",
            fontweight="bold",
            color="#dc2626",
            fontsize=11,
            zorder=6,
        )

        # 3. Top Nearest Neighbors: highlighted in Royal Blue
        for name in neighbor_names:
            try:
                idx = find_player_index(self.df, name)
                nx, ny = X_pca[idx, 0], X_pca[idx, 1]
                ax.scatter(
                    nx,
                    ny,
                    c="#2563eb",
                    s=90,
                    edgecolors="black",
                    linewidth=1.2,
                    zorder=4,
                )
                ax.annotate(
                    name,
                    (nx, ny),
                    xytext=(6, 6),
                    textcoords="offset points",
                    fontweight="semibold",
                    color="#1e3a8a",
                    fontsize=9,
                    zorder=6,
                )
            except IndexError:
                continue

        ax.set_title(
            f"PCA 2D Striker Clustering: {self.target_name} & Closest Peers",
            fontsize=13,
            pad=15,
        )
        ax.set_xlabel(
            f"Principal Component 1 ({var_pc1:.1f}% Variance Explained)",
            fontsize=10,
        )
        ax.set_ylabel(
            f"Principal Component 2 ({var_pc2:.1f}% Variance Explained)",
            fontsize=10,
        )
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="upper right", frameon=True)

        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"Generated PCA plot: {save_path}")

    def plot_radar_comparison(
        self,
        competitor_name: str,
        category_scores: dict[str, dict[str, float]],
        save_path: str = Radar_Plot_Path,
    ):

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        categories = list(category_scores.keys())
        target_vals = [category_scores[cat]["target"] for cat in categories]
        comp_vals = [category_scores[cat]["competitor"] for cat in categories]

        num_vars = len(categories)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        # Complete the polygon loop by appending the first point
        angles += angles[:1]
        target_vals += target_vals[:1]
        comp_vals += comp_vals[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
        assert isinstance(ax, PolarAxes)

        # Target polygon (Crimson Red)
        ax.plot(
            angles,
            target_vals,
            color="#dc2626",
            linewidth=2.5,
            label=self.target_name,
        )
        ax.fill(angles, target_vals, color="#dc2626", alpha=0.25)

        # Competitor polygon (Royal Blue)
        ax.plot(
            angles,
            comp_vals,
            color="#2563eb",
            linewidth=2.5,
            label=competitor_name,
        )
        ax.fill(angles, comp_vals, color="#2563eb", alpha=0.25)

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(
            np.degrees(angles[:-1]), categories, fontsize=10, fontweight="bold"
        )
        ax.set_ylim(0, 100)

        plt.title(
            f"Radar Comparison: {self.target_name} vs {competitor_name}",
            size=13,
            y=1.08,
        )
        plt.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1))

        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"Generated Radar plot: {save_path}")

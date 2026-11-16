from config import (
    All_Features,
    Data_Path,
    PCA_Plot_Path,
    Radar_Plot_Path,
    Report_Paths,
    Target_Player,
)
from dataloader import load_data
from evaluator import SimilarityEvaluator
from visualiser import StrikerVisualiser


def main() -> None:
    print("=" * 65)
    print("  European Top-5 Striker kNN Similarity Pipeline (2026/27)")
    print(f"  Target Benchmark: {Target_Player}")
    print("=" * 65)

    # 1. Load Data
    print(f"\n[1/4] Loading dataset from: {Data_Path}")
    df = load_data(Data_Path)
    print(
        f"      Successfully loaded {len(df)} strikers across Europe's Top 5 leagues."
    )

    # 2. Evaluate Similarity
    print(f"\n[2/4] Running kNN Similarity Model against {Target_Player}...")
    evaluator = SimilarityEvaluator(df, target_name=Target_Player)
    df_top5 = evaluator.evaluate_features(All_Features, top_k=5)

    print("\n" + "-" * 65)
    print(f"  Top 5 Nearest Peers to {Target_Player} (All 15 Metrics):")
    print("-" * 65)
    print(df_top5.to_string(index=False))
    print("-" * 65)

    closest_peer = str(df_top5.iloc[0]["Player"])
    peer_club = str(df_top5.iloc[0]["Club"])
    peer_dist = float(df_top5.iloc[0]["Euclidean Distance"])
    peer_sim = str(df_top5.iloc[0]["Similarity Score"])

    print(
        f"\n  >>> Closest Match: {closest_peer} ({peer_club})"
        f"\n      Euclidean Distance: {peer_dist:.4f} | Similarity: {peer_sim}"
    )

    # 3. Generate Markdown Report
    print("\n[3/4] Exporting Markdown Report...")
    report_file = evaluator.generate_markdown_report(Report_Paths)
    print(f"      Report saved to: {report_file}")

    # 4. Generate Visualizations
    print("\n[4/4] Generating Visualizations...")
    visualiser = StrikerVisualiser(df, target_name=Target_Player)

    top_peers = df_top5["Player"].tolist()
    visualiser.plot_pca_projection(top_peers, save_path=PCA_Plot_Path)

    radar_scores = evaluator.get_category_radar_data(closest_peer)
    visualiser.plot_radar_comparison(
        closest_peer, radar_scores, save_path=Radar_Plot_Path
    )

    print("\n" + "=" * 65)
    print("  Pipeline Completed Successfully!")
    print(f"  1. Report:   {Report_Paths}")
    print(f"  2. PCA Plot: {PCA_Plot_Path}")
    print(f"  3. Radar:    {Radar_Plot_Path}")
    print("=" * 65)


if __name__ == "__main__":
    main()

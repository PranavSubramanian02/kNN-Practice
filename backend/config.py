import os

# Project Directories and File Paths
Base_Dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Data_Path: str = os.path.join(Base_Dir, "strikers_data.csv")
Output_Dir: str = os.path.join(Base_Dir, "outputs")

# Output Artifacts Paths
Report_Paths: str = os.path.join(Output_Dir, "similarity-ranking.md")
PCA_Plot_Path: str = os.path.join(Output_Dir, "pca-projection.png")
Radar_Plot_Path: str = os.path.join(Output_Dir, "radar-comparison.png")

# Target Player Benchmark
Target_Player: str = "Kylian Mbappe"

# KNN Model Hyperparameters
N_Neighbors: int = 6  # 1 self-match + 5 nearest peers
Distance_Metric: str = "euclidean"
Use_SKLearn_Backend: bool = (
    "True"  # Set False to use the from-scratch NumPy math engine  # type: ignore
)

# Feature Group

Feature_Categories: dict[str, list[str]] = {
    "1. Shooting Efficiency & Shot Quality": [
        "xg_per90",
        "npxg_per90",
        "psxg_per90",
        "shot_conversion_rate",
        "shots_on_target_per90",
    ],
    "2. Build-up Play & Creative Linkage": [
        "xa_per90",
        "sca_per90",
        "progressive_passes_received_per90",
        "pass_completion_rate_under_pressure",
    ],
    "3. Ball Carrying & Space Creation": [
        "progressive_carries_per90",
        "successful_take_on_pct",
        "touches_att_pen_area_per90",
    ],
    "4. Defensive Work Rate & Pressing": [
        "tackles_interceptions_att_3rd_per90",
        "ball_recoveries_per90",
        "aerial_duels_won_pct",
    ],
}

# Complete List of all 15 features
All_Features: list[str] = [
    feature
    for category_features in Feature_Categories.values()
    for feature in category_features
]

# Mapping of charts
Feature_Labels: dict[str, str] = {
    "xg_per90": "Expected Goals (xG) / 90",
    "npxg_per90": "Non-Penalty Expected Goals (npxG) / 90",
    "psxg_per90": "Post-Shot Expected Goals (PSxG) / 90",
    "shot_conversion_rate": "Shot Conversion Rate (%)",
    "shots_on_target_per90": "Shots on Target / 90",
    "xa_per90": "Expected Assists (xA) / 90",
    "sca_per90": "Shot-Creating Actions (SCA) / 90",
    "progressive_passes_received_per90": "Progressive Passes Received / 90",
    "pass_completion_rate_under_pressure": "Pass Completion Rate Under Pressure (%)",
    "progressive_carries_per90": "Progressive Carries / 90",
    "successful_take_on_pct": "Successful Take-on Rate (%)",
    "touches_att_pen_area_per90": "Touches in Attacking Penalty Area / 90",
    "tackles_interceptions_att_3rd_per90": "Tackles & Interceptions in Attacking 3rd / 90",
    "ball_recoveries_per90": "Ball Recoveries / 90",
    "aerial_duels_won_pct": "Aerial Duels Won (%)",
}

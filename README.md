# European Striker Similarity Analytics

A machine learning scouting pipeline and interactive analytics dashboard designed to identify tactical, stylistic, and performance peers for elite center-forwards across Europe's top-five leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1) using k-Nearest Neighbors (kNN) and Principal Component Analysis (PCA).

The system benchmarks against Kylian Mbappe (Real Madrid) and profiles 141 center-forwards across 39 European clubs using verified 2026/27 all-competitions data (domestic league, UEFA Champions/Europa/Conference League, and domestic cup competitions).

---

## Technical Overview

Modern recruitment analytics requires distinguishing between raw counting volume and underlying tactical playstyle. This project provides a normalized, multi-dimensional framework that compares strikers across 15 standardized metrics categorized into four core tactical domains.

### Tactical Feature Matrix

#### 1. Shooting Efficiency & Shot Quality
- **xg_per90**: Expected Goals per 90 minutes.
- **npxg_per90**: Non-Penalty Expected Goals per 90 minutes.
- **psxg_per90**: Post-Shot Expected Goals per 90 minutes.
- **shot_conversion_rate**: Goals scored divided by total shot volume (expressed as a percentage).
- **shots_on_target_per90**: Shots directed on frame per 90 minutes.

#### 2. Build-up Play & Creative Linkage
- **xa_per90**: Expected Assists per 90 minutes.
- **sca_per90**: Shot-Creating Actions per 90 minutes.
- **progressive_passes_received_per90**: Completed forward passes received that advance possession significantly.
- **pass_completion_rate_under_pressure**: Passing accuracy percentage when confronted by an opponent.

#### 3. Ball Carrying & Space Creation
- **progressive_carries_per90**: Forward ball carries moving the ball at least 10 meters toward the opponent's goal.
- **successful_take_on_pct**: Successful 1v1 dribble percentage.
- **touches_att_pen_area_per90**: Total ball touches inside the opponent's 18-yard box per 90 minutes.

#### 4. Defensive Work Rate & Pressing
- **tackles_interceptions_att_3rd_per90**: Ball-winning defensive interventions executed in the final third.
- **ball_recoveries_per90**: Loose ball recoveries secured per 90 minutes.
- **aerial_duels_won_pct**: Percentage of aerial challenges won.

---

## Mathematical Architecture

### 1. Per-90 Normalization
To prevent playing time bias from skewing similarity evaluations, all counting stats are normalized to a per-90-minute basis:

$$\text{Metric}_{90} = \frac{\text{Raw Count}}{\text{Minutes Played}} \times 90$$

Percentage metrics (e.g., shot conversion rate, aerial duel win rate, pass completion under pressure) remain scale-independent.

### 2. Z-Score Standardization
Because features operate across disparate scales and units, all features are standardized to zero mean and unit variance:

$$z_{i,j} = \frac{x_{i,j} - \mu_j}{\sigma_j}$$

where $\mu_j$ and $\sigma_j$ represent the empirical mean and standard deviation of metric $j$ across the entire pool of 141 strikers.

### 3. Euclidean Distance & Similarity Metric
Similarity between benchmark player $T$ and candidate striker $C$ is computed in the 15-dimensional standardized feature space:

$$d(T, C) = \sqrt{\sum_{j=1}^{15} (z_{T,j} - z_{C,j})^2}$$

The raw Euclidean distance is mapped into a normalized similarity percentage:

$$\text{Similarity Score} = \frac{1}{1 + d(T, C)} \times 100\%$$

### 4. Dimensionality Reduction (PCA)
For global landscape visualization, a two-component Principal Component Analysis (PCA) projects the 15-dimensional feature space onto a 2D coordinate plane while preserving maximal variance.

---

## Repository Structure

```
├── backend/
│   ├── __init__.py
│   ├── config.py          # Global hyperparameter settings and feature definitions
│   ├── dataloader.py      # Unicode normalization and dataset loader
│   ├── preprocessor.py    # Custom StandardScaler implementation
│   ├── knn_model.py       # Custom NumPy Euclidean kNN and Scikit-Learn backend
│   ├── evaluator.py       # Similarity engine, comparison generator, and markdown reporter
│   ├── visualiser.py      # Matplotlib publication plots (PCA scatter & polar radars)
│   ├── main.py            # Headless CLI analytics and artifact pipeline
│   └── server.py          # Flask REST API server delivering real-time comparisons
├── frontend/
│   ├── index.html         # High-density scouting dashboard UI
│   ├── styles.css         # Dark/light theme styling with strict sharp-edged geometry
│   └── app.js             # Client controller, search autocomplete, Chart.js radar & PCA renders
├── outputs/
│   ├── similarity-ranking.md  # Generated markdown report of nearest peers
│   ├── pca-projection.png     # Generated high-resolution 2D PCA cluster map
│   └── radar-comparison.png   # Generated polar radar comparison chart
├── strikers_data.csv          # Reconciled 2026/27 all-competitions dataset (141 strikers)
└── README.md                  # Project documentation
```

---

## Dataset Integrity & Sourcing

The dataset comprises exactly 141 strikers representing Europe's leading clubs across England, Spain, Italy, Germany, and France. 

- **Season**: 2026/27 campaign.
- **Competition Scope**: All official competitions, incorporating domestic league fixtures, UEFA European tournaments (Champions League, Europa League, Conference League), and domestic cup competitions (EFL Cup, Copa del Rey, DFB-Pokal, Coppa Italia, Coupe de France).
- **Verification Sources**: Cross-verified against official **StatMuse FC** match records and **Transfermarkt** player performance logs.

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Linux, macOS, or Windows (WSL recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/PranavSubramanian02/kNN-Practice.git
cd kNN-Practice
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install required dependencies:
```bash
pip install pandas numpy scikit-learn matplotlib flask
```

---

## Execution Guide

### 1. Headless Pipeline Execution
To run the automated analysis, evaluate nearest peers against Kylian Mbappe, and export high-resolution visuals and ranking reports:

```bash
python backend/main.py
```

Generated outputs will be saved to the `outputs/` directory:
- `outputs/similarity-ranking.md`
- `outputs/pca-projection.png`
- `outputs/radar-comparison.png`

### 2. Interactive Analytics Dashboard
To start the live web application:

```bash
python backend/server.py
```

Navigate to `http://127.0.0.1:5000` in any web browser.

The interface features:
- **Instant Search**: Autocomplete filtering across all 141 European forwards.
- **Player Dossiers**: Side-by-side comparison with goals, assists, club, and position.
- **Tactical Match Cards**: Key tactical similarities and biggest playstyle contrasts.
- **2D PCA Striker Landscape**: Interactive scatter plot locating all 141 forwards in two principal components.
- **4 Dedicated Category Radars**: Percentile rankings (0–100) across Shooting, Build-up, Ball Carrying, and Defensive Work Rate.
- **Full 15-Metric Comparison Table**: Detailed metric-by-metric breakdown showing raw values, differentials, and statistical z-score deltas.
- **Dual Themes**: Industrial Dark Mode and High-Contrast Light Mode with zero emojis and sharp-edged UI architecture.

---

## Benchmark Results: Nearest Peers to Kylian Mbappe

Evaluated against Kylian Mbappe (Real Madrid — 17 Goals, 3 Assists in 1,280 minutes across all competitions):

| Rank | Player | Club | League | Euclidean Distance | Similarity Index |
| :---: | :--- | :--- | :--- | :---: | :---: |
| 1 | **Donyell Malen** | AS Roma | Serie A | 4.4417 | 18.4% |
| 2 | **João Pedro** | Chelsea | Premier League | 5.4061 | 15.6% |
| 3 | **Patrik Schick** | Bayer 04 Leverkusen | Bundesliga | 6.0917 | 14.1% |
| 4 | **Anastasios Douvikas** | Como | Serie A | 6.1723 | 13.9% |
| 5 | **Christopher Nkunku** | RB Leipzig | Bundesliga | 6.3894 | 13.5% |
| 6 | **Alexander Isak** | Liverpool | Premier League | 6.5567 | 13.2% |
| 7 | **Danny Welbeck** | Chelsea | Premier League | 6.6664 | 13.0% |
| 8 | **Tidiam Gomis** | RB Leipzig | Bundesliga | 6.7352 | 12.9% |
| 9 | **Raphinha** | Barcelona | La Liga | 6.7881 | 12.8% |
| 10 | **Amine Gouiri** | Olympique de Marseille | Ligue 1 | 6.9440 | 12.6% |

---

## License

This project is licensed under the MIT License.

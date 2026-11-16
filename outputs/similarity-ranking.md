# Striker KNN Similarity Analysis: Nearest Peers to Kylian Mbappe

**Benchmark Player**: Kylian Mbappe (Real Madrid, La Liga)  
**Season Data**: 2026/27 (All counting metrics converted to Per 90)  
**Total Pool**: 141 strikers analyzed across Top 5 European Leagues

---
## 1. Overall Similarity Rankings (All 15 Metrics Combined)

Ranked by shortest Euclidean distance in standardized feature space:

|   Rank | Player              | Club                   | League         | Position   |   Euclidean Distance | Similarity Score   |
|-------:|:--------------------|:-----------------------|:---------------|:-----------|---------------------:|:-------------------|
|      1 | Donyell Malen       | As Roma                | Serie A        | ST/RW      |               4.4417 | 18.4%              |
|      2 | Joao Pedro          | Chelsea                | Premier League | ST         |               5.4061 | 15.6%              |
|      3 | Patrik Schick       | Bayer 04 Leverkusen    | Bundesliga     | ST         |               6.0917 | 14.1%              |
|      4 | Anastasios Douvikas | Como                   | Serie A        | ST         |               6.1723 | 13.9%              |
|      5 | Christopher Nkunku  | Rb Leipzig             | Bundesliga     | CF/SS      |               6.3894 | 13.5%              |
|      6 | Alexander Isak      | Liverpool              | Premier League | ST         |               6.5567 | 13.2%              |
|      7 | Danny Welbeck       | Chelsea                | Premier League | ST         |               6.6664 | 13.0%              |
|      8 | Tidiam Gomis        | Rb Leipzig             | Bundesliga     | ST         |               6.7352 | 12.9%              |
|      9 | Raphinha            | Barcelona              | La Liga        | CF/RW      |               6.7881 | 12.8%              |
|     10 | Amine Gouiri        | Olympique De Marseille | Ligue 1        | ST         |               6.944  | 12.6%              |

---
## 2. Category-Specific Similarity Breakdowns


### 1. Shooting Efficiency & Shot Quality
*Evaluated metrics: `xg_per90, npxg_per90, psxg_per90, shot_conversion_rate, shots_on_target_per90`*

|   Rank | Player              | Club                | League         | Position   |   Euclidean Distance | Similarity Score   |
|-------:|:--------------------|:--------------------|:---------------|:-----------|---------------------:|:-------------------|
|      1 | Raphinha            | Barcelona           | La Liga        | CF/RW      |               1.3989 | 41.7%              |
|      2 | Erling Haaland      | Manchester City     | Premier League | ST         |               2.046  | 32.8%              |
|      3 | Anastasios Douvikas | Como                | Serie A        | ST         |               2.1535 | 31.7%              |
|      4 | Donyell Malen       | As Roma             | Serie A        | ST/RW      |               2.4516 | 29.0%              |
|      5 | Patrik Schick       | Bayer 04 Leverkusen | Bundesliga     | ST         |               2.8419 | 26.0%              |

### 2. Build-up Play & Creative Linkage
*Evaluated metrics: `xa_per90, sca_per90, progressive_passes_received_per90, pass_completion_rate_under_pressure`*

|   Rank | Player            | Club             | League   | Position   |   Euclidean Distance | Similarity Score   |
|-------:|:------------------|:-----------------|:---------|:-----------|---------------------:|:-------------------|
|      1 | Gabriel Jesus     | Barcelona        | La Liga  | ST         |               0.8364 | 54.5%              |
|      2 | Christian Pulisic | Ac Milan         | Serie A  | RW/SS      |               1.0684 | 48.3%              |
|      3 | Ansu Fati         | As Monaco        | Ligue 1  | LW/ST      |               1.2619 | 44.2%              |
|      4 | Karim Adeyemi     | Barcelona        | La Liga  | ST/LW      |               1.2821 | 43.8%              |
|      5 | Ademola Lookman   | Athletico Madrid | La Liga  | ST/LW      |               1.2833 | 43.8%              |

### 3. Ball Carrying & Space Creation
*Evaluated metrics: `progressive_carries_per90, successful_take_on_pct, touches_att_pen_area_per90`*

|   Rank | Player        | Club        | League   | Position   |   Euclidean Distance | Similarity Score   |
|-------:|:--------------|:------------|:---------|:-----------|---------------------:|:-------------------|
|      1 | Gabriel Jesus | Barcelona   | La Liga  | ST         |               0.76   | 56.8%              |
|      2 | Dani Olmo     | Barcelona   | La Liga  | AM/SS      |               1.2855 | 43.8%              |
|      3 | Raphinha      | Barcelona   | La Liga  | CF/RW      |               1.3407 | 42.7%              |
|      4 | Ansu Fati     | As Monaco   | Ligue 1  | LW/ST      |               1.3485 | 42.6%              |
|      5 | Luis Henrique | Inter Milan | Serie A  | ST/RW      |               1.5893 | 38.6%              |

### 4. Defensive Work Rate & Pressing
*Evaluated metrics: `tackles_interceptions_att_3rd_per90, ball_recoveries_per90, aerial_duels_won_pct`*

|   Rank | Player         | Club                | League   | Position   |   Euclidean Distance | Similarity Score   |
|-------:|:---------------|:--------------------|:---------|:-----------|---------------------:|:-------------------|
|      1 | Antonio Arena  | As Roma             | Serie A  | ST         |               1.0526 | 48.7%              |
|      2 | Julian Vignolo | Losc Lille          | Ligue 1  | ST         |               1.0849 | 48.0%              |
|      3 | Paris Brunner  | As Monaco           | Ligue 1  | ST         |               1.1641 | 46.2%              |
|      4 | Matthis Abline | As Monaco           | Ligue 1  | ST         |               1.4225 | 41.3%              |
|      5 | Lois Openda    | Olympique Lyonnaise | Ligue 1  | ST         |               1.4354 | 41.1%              |

---
## 3. Mathematical Methodology
1. **Per-90 Normalization**: Volume metrics are transformed via `(metric / minutes) * 90`.
2. **Z-Score Standardization**: `z = (x - mean) / std` centers data around 0 with unit variance.
3. **Euclidean Distance**: `d = sqrt( sum( (z_target - z_peer)^2 ) )`.
4. **Similarity Index**: `S = 1 / (1 + d)` mapped to a percentage scale.

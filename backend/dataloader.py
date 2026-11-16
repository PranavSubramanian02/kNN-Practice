import os
import unicodedata

import pandas as pd
from config import All_Features, Data_Path


def normalize_name(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Decompose unicode accents into base letter + accent mark
    decomposed = unicodedata.normalize("NFKD", text)

    # Filter out accent marks
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))

    # Replace non-standard characters
    clean = (
        stripped.replace("ø", "o")
        .replace("Ø", "O")
        .replace("đ", "d")
        .replace("Đ", "D")
        .replace("ß", "ss")
    )
    return clean.strip().lower()


def load_data(filepath: str = Data_Path) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at: {filepath}")

    df = pd.read_csv(filepath)

    # Clean player and club names
    df["players"] = df["player"].astype(str).apply(lambda x: normalize_name(x).title())
    df["club"] = df["club"].astype(str).apply(lambda x: normalize_name(x).title())

    # Build search helper
    df["player_search"] = df["player"].apply(normalize_name)

    # Check for missing features
    missing_features = [col for col in All_Features if col not in df.columns]
    if missing_features:
        for col in list(missing_features):
            base_col = col.replace("_per90", "")
            if base_col in df.columns:
                df[col] = df[base_col]
                missing_features.remove(col)

    if missing_features:
        raise ValueError(f"Missing required metric columns in CSV: {missing_features}")

    # Fill null values
    df[All_Features] = (
        df[All_Features].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    )

    return df


def find_player_index(df: pd.DataFrame, query_name: str) -> int:
    clean_query = normalize_name(query_name)
    matches = df[df["player_search"].str.contains(clean_query, na=False)]

    if matches.empty:
        raise IndexError(f"Player '{query_name}' was not found in dataset.")
    return int(matches.index[0])

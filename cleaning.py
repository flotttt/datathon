"""Nettoyage du texte pour la classification des narratifs.

On retire le prefixe de retweet et les URLs, puis on collapse les espaces.
La meme fonction sert a la visualisation marimo et au pipeline d'agents.
"""

import re

import pandas as pd

RT_PREFIX = re.compile(r"^RT @\w+:?\s*")
URL = re.compile(r"https?://\S+")
SPACES = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Retire le prefixe RT, les URLs et les espaces superflus."""
    if not isinstance(text, str):
        return ""
    without_rt = RT_PREFIX.sub("", text)
    without_url = URL.sub("", without_rt)
    collapsed = SPACES.sub(" ", without_url)
    return collapsed.strip()


def add_clean_column(frame: pd.DataFrame) -> pd.DataFrame:
    """Renvoie une copie du corpus avec une colonne text_clean."""
    result = frame.copy()
    result["text_clean"] = result["Full Text"].map(clean_text)
    return result


def cleaning_summary(frame: pd.DataFrame) -> dict:
    """Statistiques avant / apres nettoyage. frame doit contenir text_clean."""
    raw = frame["Full Text"].fillna("")
    return {
        "total": len(frame),
        "unique_raw": frame["Full Text"].nunique(),
        "rt_share": raw.str.startswith("RT @").mean(),
        "url_share": raw.str.contains("http").mean(),
        "unique_clean": frame["text_clean"].nunique(),
    }


def dedup_steps(frame: pd.DataFrame) -> pd.DataFrame:
    """Volume a chaque etape, pour un graphe avant / apres."""
    summary = cleaning_summary(frame)
    rows = [
        ("Messages bruts", summary["total"]),
        ("Textes uniques (bruts)", summary["unique_raw"]),
        ("Textes nettoyes", summary["unique_clean"]),
    ]
    return pd.DataFrame(rows, columns=["etape", "count"])


def unique_texts(frame: pd.DataFrame) -> pd.DataFrame:
    """Textes nettoyes uniques et leur nombre d'occurrences."""
    counts = frame["text_clean"].value_counts()
    result = counts.reset_index()
    result.columns = ["text_clean", "occurrences"]
    return result


def export_clean(frame: pd.DataFrame, path: str) -> str:
    """Ecrit le corpus nettoye en CSV et renvoie le chemin."""
    frame.to_csv(path, index=False)
    return path

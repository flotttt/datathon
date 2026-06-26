"""Chargement et nettoyage du corpus de tweets (affaire Ultia x CNC)."""

import os

import pandas as pd

DEFAULT_PATH = os.environ.get("DATATHON_DATA", "Dataset/data.xlsx")

ORIGINAL_LABEL = "ORIGINAL"


def load_corpus(path: str = DEFAULT_PATH) -> pd.DataFrame:
    """Lit le fichier Excel et renvoie un DataFrame pret a analyser."""
    frame = pd.read_excel(path)
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame = frame.dropna(subset=["Date"])
    frame["Engagement Type"] = frame["Engagement Type"].fillna(ORIGINAL_LABEL)
    return frame


def period_bounds(frame: pd.DataFrame) -> tuple:
    """Renvoie la date de debut et de fin du corpus."""
    return frame["Date"].min(), frame["Date"].max()

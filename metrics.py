"""Agregations pandas qui alimentent les visualisations marimo.

Chaque fonction prend le DataFrame du corpus et renvoie un DataFrame
pret a tracer. Pas d'effet de bord, pas d'etat global.
"""

import pandas as pd


def timeline(frame: pd.DataFrame, freq: str = "1h") -> pd.DataFrame:
    """Nombre de messages par intervalle de temps."""
    counts = frame.set_index("Date").resample(freq).size()
    result = counts.reset_index()
    result.columns = ["time", "count"]
    return result


def engagement_breakdown(frame: pd.DataFrame) -> pd.DataFrame:
    """Repartition des messages par type (retweet, reply, quote, original)."""
    counts = frame["Engagement Type"].value_counts()
    result = counts.reset_index()
    result.columns = ["engagement_type", "count"]
    return result


def top_authors(frame: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    """Comptes qui publient le plus de messages."""
    counts = frame["Author"].value_counts().head(limit)
    result = counts.reset_index()
    result.columns = ["author", "count"]
    return result


def repost_handle(url: str) -> str:
    """Extrait le pseudo depuis une URL de retweet."""
    if not isinstance(url, str):
        return None
    parts = url.split("/")
    if len(parts) > 3:
        return parts[3]
    return None


def top_amplified(frame: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    """Comptes les plus retweetes, cibles de l'amplification."""
    handles = frame["X Repost of"].map(repost_handle).dropna()
    counts = handles.value_counts().head(limit)
    result = counts.reset_index()
    result.columns = ["author", "count"]
    return result


def sentiment_over_time(frame: pd.DataFrame, freq: str = "1D") -> pd.DataFrame:
    """Volume de messages par sentiment dans le temps."""
    grouped = frame.groupby([pd.Grouper(key="Date", freq=freq), "Sentiment"])
    return grouped.size().reset_index(name="count")


def split_hashtags(value: str) -> list:
    """Decoupe une cellule de hashtags en liste de tags propres."""
    if not isinstance(value, str):
        return []
    tags = value.lower().replace(" ", "").split(",")
    return [tag for tag in tags if tag]


def top_hashtags(frame: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    """Hashtags les plus frequents dans le corpus."""
    exploded = frame["Hashtags"].map(split_hashtags).explode().dropna()
    counts = exploded.value_counts().head(limit)
    result = counts.reset_index()
    result.columns = ["hashtag", "count"]
    return result


# Chronologie de l'affaire, etablie a partir de la presse (voir le vault).
KEY_EVENTS = [
    ("2026-03-25", "Live Twitch d'Ultia"),
    ("2026-03-26", "Clip viral @TwitchGauchiste"),
    ("2026-03-31", "Ultia se defend"),
    ("2026-04-08", "Suspension du fonds (3 M EUR)"),
    ("2026-04-09", "Enquete Le Figaro"),
]


def message_count(frame: pd.DataFrame) -> int:
    """Nombre total de messages."""
    return len(frame)


def author_count(frame: pd.DataFrame) -> int:
    """Nombre d'auteurs uniques."""
    return frame["Author"].nunique()


def type_share(frame: pd.DataFrame, label: str) -> float:
    """Part des messages d'un type donne, entre 0 et 1."""
    return (frame["Engagement Type"] == label).mean()


def peak_day(frame: pd.DataFrame) -> tuple:
    """Jour de plus fort volume et son nombre de messages."""
    daily = timeline(frame, "1D")
    row = daily.loc[daily["count"].idxmax()]
    return row["time"], row["count"]


def peak_concentration(frame: pd.DataFrame, days: int = 4) -> float:
    """Part du volume concentree sur les jours de pic, entre 0 et 1."""
    daily = timeline(frame, "1D")
    return daily["count"].nlargest(days).sum() / daily["count"].sum()


def key_events() -> pd.DataFrame:
    """Evenements cles de l'affaire, pour annoter la timeline."""
    frame = pd.DataFrame(KEY_EVENTS, columns=["date", "label"])
    frame["date"] = pd.to_datetime(frame["date"])
    return frame


def verified_breakdown(frame: pd.DataFrame) -> pd.DataFrame:
    """Repartition des messages selon que le compte est certifie ou non."""
    labels = frame["X Verified"].map({True: "Verifie", False: "Non verifie"})
    counts = labels.value_counts()
    result = counts.reset_index()
    result.columns = ["statut", "count"]
    return result


def top_by_reach(frame: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    """Comptes qui touchent la plus grande audience cumulee (reach)."""
    grouped = frame.groupby("Author")["Reach"].sum()
    top = grouped.sort_values(ascending=False).head(limit)
    result = top.reset_index()
    result.columns = ["author", "reach"]
    return result

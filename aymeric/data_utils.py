"""
Utilitaires de chargement et d’agrégation du corpus Twitter/X.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


# Chemins relatifs au fichier (fonctionne peu importe d'où on lance le script)
DATA_PATH = Path(__file__).parent / "Dataset" / "data.xlsx"
DICT_PATH = Path(__file__).parent / "Dataset" / "dictionnaire_bdd.xlsx"


def load_corpus(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Charge le corpus Excel et normalise les types de base."""
    df = pd.read_excel(path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["postDate"] = pd.to_datetime(df["postDate"], errors="coerce")
    # Texte exploitable : message normalisé ou Full Text
    df["text"] = df["message_normalizer"].fillna(df["Full Text"])
    # Engagement total
    df["engagement"] = df[["Likes", "Comments", "Shares"]].fillna(0).sum(axis=1)
    return df


def load_dictionary(path: str | Path = DICT_PATH) -> pd.DataFrame:
    """Charge le dictionnaire des colonnes."""
    return pd.read_excel(path)


def filter_keyword(df: pd.DataFrame, keyword: str, column: str = "text") -> pd.DataFrame:
    """Filtre les lignes contenant un mot-clé (insensible à la casse)."""
    mask = df[column].str.contains(keyword, case=False, na=False)
    return df[mask].copy()


def compute_basic_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Statistiques générales sur un sous-corpus."""
    return {
        "total_posts": int(len(df)),
        "date_min": df["Date"].min().isoformat() if not df["Date"].isna().all() else None,
        "date_max": df["Date"].max().isoformat() if not df["Date"].isna().all() else None,
        "sentiment_distribution": df["Sentiment"].value_counts().to_dict(),
        "engagement_type_distribution": df["Engagement Type"].value_counts().to_dict(),
        "total_likes": int(df["Likes"].fillna(0).sum()),
        "total_comments": int(df["Comments"].fillna(0).sum()),
        "total_shares": int(df["Shares"].fillna(0).sum()),
        "verified_count": int(df["X Verified"].fillna(False).sum()),
    }


def top_authors(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Top auteurs par nombre de posts, avec reach/followers max."""
    agg = df.groupby("Author").agg(
        posts=("postID", "count"),
        max_followers=("X Followers", "max"),
        total_reach=("Reach", "sum"),
        total_engagement=("engagement", "sum"),
        verified=("X Verified", "max"),
    ).sort_values("posts", ascending=False).head(n)
    return agg.reset_index()


def top_posts(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top posts par engagement total."""
    cols = ["Date", "Author", "Full Text", "Likes", "Comments", "Shares", "engagement", "Reach"]
    return df[cols].sort_values("engagement", ascending=False).head(n)


def hourly_volume(df: pd.DataFrame) -> pd.DataFrame:
    """Volume horaire + engagement."""
    df = df.copy()
    df["hour"] = df["Date"].dt.floor("h")
    return (
        df.groupby("hour")
        .agg(posts=("postID", "count"), engagement=("engagement", "sum"))
        .reset_index()
        .sort_values("hour")
    )


def sample_tweets_for_prompt(
    df: pd.DataFrame, n: int = 10, max_text_len: int = 150, seed: int = 42
) -> str:
    """Échantillon représentatif de tweets pour alimenter les prompts LLM."""
    if len(df) <= n:
        sample = df
    else:
        # On prend à la fois les plus engagés et un échantillon aléatoire
        top = df.sort_values("engagement", ascending=False).head(n // 2)
        rest = df.drop(top.index).sample(n - len(top), random_state=seed)
        sample = pd.concat([top, rest]).sample(frac=1, random_state=seed)

    lines = []
    for _, row in sample.iterrows():
        text = str(row["text"])[:max_text_len]
        lines.append(
            f"- [{row['Date']:%Y-%m-%d %H:%M}] @{row['Author']} "
            f"(engagement={int(row['engagement'])}, sentiment={row['Sentiment']}): {text}"
        )
    return "\n".join(lines)


def build_context(df: pd.DataFrame, focus_keyword: str | None = "ultia") -> dict[str, Any]:
    """
    Construit un contexte complet destiné aux agents.
    Si focus_keyword est fourni, on filtre d'abord sur ce mot-clé.
    """
    if focus_keyword:
        focus_df = filter_keyword(df, focus_keyword)
    else:
        focus_df = df.copy()

    context = {
        "focus_keyword": focus_keyword,
        "basic_stats": compute_basic_stats(focus_df),
        "top_authors": top_authors(focus_df, n=10).to_dict(orient="records"),
        "top_posts": top_posts(focus_df, n=3).to_dict(orient="records"),
        "hourly_volume": hourly_volume(focus_df).to_dict(orient="records"),
        "sample_tweets": sample_tweets_for_prompt(focus_df, n=10, max_text_len=150),
        "full_corpus_stats": compute_basic_stats(df),
    }
    return context


def context_to_markdown(context: dict[str, Any]) -> str:
    """Convertit le contexte en markdown lisible pour les prompts."""
    lines = [
        "# Contexte de crise",
        f"**Focus :** {context['focus_keyword']}",
        "",
        "## Statistiques générales",
        json.dumps(context["basic_stats"], indent=2, ensure_ascii=False, default=str),
        "",
        "## Top auteurs",
    ]
    for author in context["top_authors"][:10]:
        lines.append(
            f"- @{author['Author']} : {author['posts']} posts, "
            f"{int(author['max_followers'])} followers max, "
            f"{int(author['total_reach'])} reach total"
        )

    lines.extend(["", "## Top posts"])
    for post in context["top_posts"][:3]:
        lines.append(
            f"- [{post['Date']:%Y-%m-%d %H:%M}] @{post['Author']} "
            f"(likes={int(post['Likes'])}, RT={int(post['Shares'])}, comments={int(post['Comments'])}): "
            f"{str(post['Full Text'])[:120]}"
        )

    lines.extend(["", "## Échantillon de tweets", context["sample_tweets"]])
    return "\n".join(lines)


if __name__ == "__main__":
    df = load_corpus()
    ctx = build_context(df, focus_keyword="ultia")
    print(json.dumps(ctx["basic_stats"], indent=2, ensure_ascii=False))
    print(f"\nTop auteurs:\n{top_authors(filter_keyword(df, 'ultia')).head()}")


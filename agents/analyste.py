"""
agents/analyste.py — AGENT 1 : L'ANALYSTE (hybride pandas + LLM)
Binôme : Mathis (+ renfort)

ARCHITECTURE HYBRIDE :
  - PROPAGATION + ACTEURS  -> calculés en pandas (fiable, exact)
    via les modules de Flo : metrics.py / cleaning.py / data_loading.py
  - NARRATIFS + TON        -> délégués au LLM (sémantique)
    sur un échantillon de TEXTES NETTOYÉS UNIQUES (colonne text_clean).

ENTRÉE : le DataFrame du corpus (pas un bloc de texte — on a besoin des
         colonnes pour les calculs pandas).
SORTIE : le dict ANALYSTE_SCHEMA (voir contracts.py).

À FAIRE par le binôme : affiner PROMPT_NARRATIFS + ajuster les seuils
de classification de l'état de propagation.
"""
import json
import os
import hashlib
import pandas as pd

import metrics
import cleaning
from common import get_llm, extraire_json

# Cache des narratifs : tant que l'échantillon ne change pas, on ne
# rappelle PAS le LLM. Économise le quota pendant le debug (on relance
# le script 50x sans un seul appel API). Supprimer le fichier pour forcer.
CACHE_NARRATIFS = "narratifs_cache.json"


# =====================================================================
# PARTIE 1 — pandas (déterministe, via les modules de Flo)
# =====================================================================
def _etat_propagation(df: pd.DataFrame) -> str:
    """Classe l'état global du corpus : montee / pic / traine.
    Heuristique simple sur la concentration du volume."""
    concentration = metrics.peak_concentration(df, days=4)
    # 65% du volume sur 4 jours => crise très concentrée (déjà passée par un pic)
    if concentration >= 0.5:
        return "pic"
    elif concentration >= 0.3:
        return "montee"
    return "traine"


def _acteurs_cles(df: pd.DataFrame, limit: int = 5) -> list:
    """Top comptes amplifiés (les vrais moteurs), typés grossièrement."""
    amplifies = metrics.top_amplified(df, limit)
    # certif pour typer un minimum
    verifies = set(df.loc[df["X Verified"] == True, "Author"])
    acteurs = []
    for _, row in amplifies.iterrows():
        pseudo = row["author"]
        acteurs.append({
            "pseudo": pseudo,
            "type": "certifie" if pseudo in verifies else "non_certifie",
            "portee": "haute" if row["count"] > 800 else "moyenne",
        })
    return acteurs


def _ton_global(df: pd.DataFrame) -> dict:
    """Sentiment dominant + proxy d'agressivité depuis la part de négatif."""
    parts = df["Sentiment"].value_counts(normalize=True)
    dominant = parts.idxmax()
    neg = parts.get("negative", 0)
    if neg >= 0.4:
        agress = "eleve"
    elif neg >= 0.2:
        agress = "moyen"
    else:
        agress = "faible"
    mapping = {"negative": "negatif", "neutral": "neutre", "positive": "positif"}
    return {"sentiment_global": mapping.get(dominant, dominant), "niveau_agressivite": agress}


# =====================================================================
# PARTIE 2 — LLM (sémantique, sur textes nettoyés uniques)
# =====================================================================
PROMPT_NARRATIFS = """Tu es un analyste de crise informationnelle. Voici un échantillon de
messages X UNIQUES (retweets et URLs déjà retirés) issus d'une crise. Tu DÉCRIS les
discours en présence, tu ne juges pas. Ton neutre.

Identifie les 2 à 4 narratifs dominants et renvoie UNIQUEMENT un objet JSON, structure :

{{
  "narratifs": [
    {{"nom": "<nom court>", "poids": "dominant|secondaire|marginal", "mots_cles": ["..."]}}
  ]
}}

Règles : base-toi uniquement sur l'échantillon, n'invente rien.

ÉCHANTILLON (textes uniques) :
{corpus}
"""


def _narratifs_llm(df_clean: pd.DataFrame, n: int = 60, use_cache: bool = True) -> list:
    """Échantillonne des TEXTES UNIQUES nettoyés et demande au LLM les narratifs.
    Met le résultat en cache (clé = empreinte de l'échantillon) pour ne pas
    rappeler le LLM tant que l'échantillon est identique."""
    uniques = cleaning.unique_texts(df_clean)            # text_clean + occurrences
    uniques = uniques[uniques["text_clean"].str.len() > 30]  # vire les vides/courts
    echant = uniques.head(n)["text_clean"].tolist()
    bloc = "\n".join(f"- {t[:200]}" for t in echant)

    # --- cache ---
    cle = hashlib.md5(bloc.encode("utf-8")).hexdigest()
    if use_cache and os.path.exists(CACHE_NARRATIFS):
        try:
            cache = json.load(open(CACHE_NARRATIFS, encoding="utf-8"))
            if cache.get("cle") == cle:
                print("[Analyste] narratifs servis depuis le cache (aucun appel LLM).")
                return cache["narratifs"]
        except Exception:
            pass

    # --- appel LLM (throttlé par common._LIMITER) ---
    llm = get_llm(temperature=0.1)
    reponse = llm.invoke(PROMPT_NARRATIFS.format(corpus=bloc))
    narratifs = extraire_json(reponse.content)["narratifs"]

    if use_cache:
        try:
            json.dump({"cle": cle, "narratifs": narratifs},
                      open(CACHE_NARRATIFS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        except Exception:
            pass
    return narratifs


# =====================================================================
# ASSEMBLAGE — respecte ANALYSTE_SCHEMA
# =====================================================================
def run(df: pd.DataFrame, use_llm: bool = True) -> dict:
    """Analyse hybride complète. df = corpus chargé via data_loading.load_corpus."""
    df_clean = cleaning.add_clean_column(df)

    sortie = {
        "etat_propagation": _etat_propagation(df),
        "ton": _ton_global(df),
        "acteurs_cles": _acteurs_cles(df),
        "narratifs": [],
    }
    if use_llm:
        try:
            sortie["narratifs"] = _narratifs_llm(df_clean)
        except Exception as e:
            print(f"[Analyste] narratifs LLM indisponibles ({e}). Sortie partielle.")
    return sortie

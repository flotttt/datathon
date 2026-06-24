"""
common.py — Plomberie partagée : clé API, chargement LLM, chargement corpus.
Aucun binôme n'a à réécrire ça.
"""
import os
import json
import pandas as pd

# ---------------------------------------------------------------------
# 1) CLÉ API  — JAMAIS en clair dans le code, JAMAIS commitée sur Git.
#    Mettez votre clé dans un fichier .env (voir .env.example) OU dans
#    les "Secrets" de Google Colab.
# ---------------------------------------------------------------------
def charger_cle():
    # Option A : Google Colab Secrets
    try:
        from google.colab import userdata  # type: ignore
        key = userdata.get("ANTHROPIC_API_KEY")
        if key:
            os.environ["ANTHROPIC_API_KEY"] = key
            return
    except Exception:
        pass
    # Option B : fichier .env local
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "Pas de clé API. Mettez ANTHROPIC_API_KEY dans .env ou les Secrets Colab."
        )


# ---------------------------------------------------------------------
# 2) LE MODÈLE  — un seul endroit pour changer de LLM si besoin.
#    (Mistral par défaut pour ce binôme ; remplaçable sans toucher
#     aux agents, ils reçoivent juste l'objet `llm`.)
# ---------------------------------------------------------------------
def get_llm(temperature: float = 0.2):
    import os
    from langchain.chat_models import init_chat_model
    return init_chat_model(
        os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        model_provider="mistralai",
        temperature=temperature,
    )


# ---------------------------------------------------------------------
# 3) LE CORPUS  — chargement + échantillon pour tester sans tout charger.
# ---------------------------------------------------------------------
def charger_corpus(path: str = "data.xlsx") -> pd.DataFrame:
    df = pd.read_excel(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def echantillon(df: pd.DataFrame, n: int = 50, fenetre_pic: bool = True) -> pd.DataFrame:
    """Renvoie un petit échantillon pour itérer vite.
    Par défaut, prend la fenêtre de pic (26-30 mars) où il se passe des choses."""
    if fenetre_pic:
        df = df[(df["Date"] >= "2026-03-26") & (df["Date"] < "2026-03-31")]
    return df.sample(min(n, len(df)), random_state=42)


def corpus_en_texte(df: pd.DataFrame, max_msg: int = 50) -> str:
    """Transforme un échantillon en bloc de texte lisible par un LLM.
    On passe par message_normalizer (déjà nettoyé au Jour 1)."""
    lignes = []
    for _, r in df.head(max_msg).iterrows():
        d = r["Date"].strftime("%d/%m %H:%M")
        lignes.append(f"[{d}] @{r['Author']} : {r['message_normalizer']}")
    return "\n".join(lignes)


def extraire_json(reponse_texte: str) -> dict:
    """Récupère le JSON d'une réponse LLM, même s'il y a du texte autour
    ou des ```json ... ```. Robuste pour la démo."""
    t = reponse_texte.strip()
    if "```" in t:
        t = t.split("```")[1]
        if t.startswith("json"):
            t = t[4:]
    t = t.strip()
    # garde du premier { au dernier }
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1:
        t = t[start:end + 1]
    return json.loads(t)

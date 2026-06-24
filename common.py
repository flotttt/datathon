"""
common.py — Plomberie partagée : clé API, chargement LLM, extraction JSON.
Le chargement du corpus est délégué à data_loading.py (module de Flo).
Aucun binôme n'a à réécrire ça.

LLM utilisé : Gemini 3.1 Flash Lite (gratuit, bon quota journalier).
"""
import os
import json

# Le nom du modèle est centralisé ici : un seul endroit à changer pour
# toute l'équipe si on doit basculer (quota, dispo...).
MODELE = "gemini-3.1-flash-lite"
PROVIDER = "google_genai"

# ---------------------------------------------------------------------
# THROTTLE — limite le DÉBIT pour ne jamais exploser le RPM.
# 13 req/min = 0.2167 req/s. Le limiteur ATTEND tout seul entre les
# appels : impossible de dépasser, même en relançant le script en boucle.
# Partagé par TOUS les agents (un seul limiteur pour tout le process).
# ---------------------------------------------------------------------
from langchain_core.rate_limiters import InMemoryRateLimiter

_LIMITER = InMemoryRateLimiter(
    requests_per_second=13 / 60,   # 13 requêtes par minute
    check_every_n_seconds=0.5,
    max_bucket_size=2,             # autorise 2 appels rapprochés puis lisse
)


# ---------------------------------------------------------------------
# 1) CLÉ API  — JAMAIS en clair dans le code, JAMAIS commitée sur Git.
#    Gemini lit la variable GOOGLE_API_KEY.
#    Mettez-la dans un .env OU dans les Secrets Colab.
# ---------------------------------------------------------------------
def charger_cle():
    # Option A : Google Colab Secrets
    try:
        from google.colab import userdata  # type: ignore
        key = userdata.get("GOOGLE_API_KEY")
        if key:
            os.environ["GOOGLE_API_KEY"] = key
            return
    except Exception:
        pass
    # Option B : fichier .env local
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError(
            "Pas de clé API. Mettez GOOGLE_API_KEY dans .env ou les Secrets Colab "
            "(récupérez-la sur aistudio.google.com)."
        )


# ---------------------------------------------------------------------
# 2) LE MODÈLE  — un seul endroit pour changer de LLM si besoin.
# ---------------------------------------------------------------------
def get_llm(temperature: float = 0.2):
    import os
    from langchain.chat_models import init_chat_model
    return init_chat_model(
        MODELE,
        model_provider=PROVIDER,
        temperature=temperature,
        rate_limiter=_LIMITER,   # throttle partagé : jamais > 13/min
        max_retries=3,           # si on touche un mur (429/TPM), réessaie au lieu de crasher
    )


# ---------------------------------------------------------------------
# 3) EXTRACTION JSON  — récupère le JSON d'une réponse LLM, même s'il y
#    a du texte autour ou des ```json ... ```. Robuste pour la démo.
# ---------------------------------------------------------------------
def extraire_json(reponse_texte) -> dict:
    # Normalise le contenu : Gemini (via LangChain) peut renvoyer une LISTE
    # de blocs au lieu d'une chaîne. On reconstruit le texte dans tous les cas.
    if isinstance(reponse_texte, list):
        morceaux = []
        for bloc in reponse_texte:
            if isinstance(bloc, str):
                morceaux.append(bloc)
            elif isinstance(bloc, dict):
                morceaux.append(bloc.get("text", ""))
            else:
                morceaux.append(str(bloc))
        reponse_texte = "".join(morceaux)
    elif not isinstance(reponse_texte, str):
        reponse_texte = str(reponse_texte)

    t = reponse_texte.strip()
    if "```" in t:
        t = t.split("```")[1]
        if t.startswith("json"):
            t = t[4:]
    t = t.strip()
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1:
        t = t[start:end + 1]
    return json.loads(t)

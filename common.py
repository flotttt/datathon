"""
common.py — Plomberie partagee : cle API, chargement LLM, extraction JSON.
Le chargement du corpus est delegue a data_loading.py (module de Flo).
Aucun binome n'a a reecrire ca.

LLM utilise : DeepSeek (API compatible OpenAI). Un seul endroit pour changer
de modele/endpoint pour toute l'equipe.
"""
import os
import json

from langchain_core.rate_limiters import InMemoryRateLimiter

# Centralise : un seul endroit a changer pour toute l'equipe.
MODELE = os.environ.get("LLM_MODEL", "deepseek-v4-flash")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")

# ---------------------------------------------------------------------
# THROTTLE — lisse le debit pour ne pas exploser le rate limit.
# Partage par TOUS les agents (un seul limiteur pour tout le process).
# DeepSeek (payant) tolere plus que les offres gratuites : on reste large.
# ---------------------------------------------------------------------
_LIMITER = InMemoryRateLimiter(
    requests_per_second=2,
    check_every_n_seconds=0.5,
    max_bucket_size=4,
)


# ---------------------------------------------------------------------
# 1) CLE API — JAMAIS en clair dans le code, JAMAIS commitee sur Git.
#    DeepSeek lit la variable DEEPSEEK_API_KEY (ou LLM_API_KEY).
#    Mettez-la dans un .env OU dans les Secrets Colab.
# ---------------------------------------------------------------------
def charger_cle():
    # Option A : Google Colab Secrets
    try:
        from google.colab import userdata  # type: ignore
        key = userdata.get("DEEPSEEK_API_KEY")
        if key:
            os.environ["DEEPSEEK_API_KEY"] = key
            return
    except Exception:
        pass
    # Option B : fichier .env local
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    if not _api_key():
        raise RuntimeError(
            "Pas de cle API. Mettez DEEPSEEK_API_KEY dans un .env "
            "(recuperez-la sur platform.deepseek.com)."
        )


def _api_key():
    return os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("LLM_API_KEY")


# ---------------------------------------------------------------------
# MESURE — temps et tokens. Suivi partage, lu par l'orchestrateur pour
# afficher le cout de chaque agent. (classe imposee par l'API LangChain)
# ---------------------------------------------------------------------
from langchain_core.callbacks import BaseCallbackHandler


class _SuiviTokens(BaseCallbackHandler):
    def __init__(self):
        self.reset()

    def reset(self):
        self.appels = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def snapshot(self) -> dict:
        return {
            "appels": self.appels,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
        }

    def on_llm_end(self, response, **kwargs):
        usage = (response.llm_output or {}).get("token_usage") or {}
        self.input_tokens += usage.get("prompt_tokens", 0)
        self.output_tokens += usage.get("completion_tokens", 0)
        self.appels += 1


USAGE = _SuiviTokens()


# ---------------------------------------------------------------------
# 2) LE MODELE — un seul endroit pour changer de LLM si besoin.
# ---------------------------------------------------------------------
def get_llm(temperature: float = 0.2):
    if not _api_key():
        charger_cle()
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=MODELE,
        base_url=BASE_URL,
        api_key=_api_key(),
        temperature=temperature,
        rate_limiter=_LIMITER,   # throttle partage
        max_retries=3,           # si on touche un mur, reessaie au lieu de crasher
        callbacks=[USAGE],       # compte les tokens de chaque appel
    )


# ---------------------------------------------------------------------
# 3) EXTRACTION JSON — recupere le JSON d'une reponse LLM, meme s'il y
#    a du texte autour ou des ```json ... ```. Robuste pour la demo.
# ---------------------------------------------------------------------
def extraire_json(reponse_texte) -> dict:
    # Normalise le contenu : certains modeles renvoient une LISTE de blocs.
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

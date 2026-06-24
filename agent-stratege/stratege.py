"""Agent Strategique : transforme un brief d'analyse en plan de riposte structure.

Entree  : un brief d'analyse (JSON) decrivant les narratifs, acteurs, pics.
Sortie  : un plan de riposte (JSON) conforme a schema_sortie.json.
Le plan est ensuite consomme par l'agent Redacteur.

Backend : tout fournisseur compatible OpenAI (defaut: DeepSeek V4 Flash).
Se configure via LLM_API_KEY, LLM_MODEL et LLM_BASE_URL dans .env.
"""

import json
import os

from dotenv import load_dotenv
from openai import AuthenticationError, OpenAI

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))

BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
MODEL = os.environ.get("LLM_MODEL", "deepseek-v4-flash")


def api_key() -> str:
    """Recupere la cle du fournisseur LLM depuis l'environnement."""
    key = (
        os.environ.get("LLM_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("KIMI_API_KEY")
    )
    if not key:
        raise RuntimeError("Definis LLM_API_KEY dans .env.")
    return key


def load_text(name: str) -> str:
    """Lit un fichier texte du dossier de l'agent."""
    with open(os.path.join(HERE, name), encoding="utf-8") as handle:
        return handle.read()


def load_json(name: str) -> dict:
    """Lit un fichier JSON du dossier de l'agent."""
    with open(os.path.join(HERE, name), encoding="utf-8") as handle:
        return json.load(handle)


def build_strategy(brief: dict, system_prompt: str, schema: dict) -> dict:
    """Appelle le LLM et renvoie le plan de riposte structure."""
    client = OpenAI(api_key=api_key(), base_url=BASE_URL)
    consigne = (
        system_prompt
        + "\n\nReponds uniquement avec un objet JSON valide, sans texte autour, "
        + "conforme exactement a ce schema :\n"
        + json.dumps(schema, ensure_ascii=False)
    )
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=4000,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": consigne},
            {"role": "user", "content": json.dumps(brief, ensure_ascii=False)},
        ],
    )
    content = response.choices[0].message.content
    return json.loads(content)


def main() -> None:
    brief = load_json("brief_exemple.json")
    system_prompt = load_text("system_prompt.txt")
    schema = load_json("schema_sortie.json")
    try:
        plan = build_strategy(brief, system_prompt, schema)
    except AuthenticationError:
        raise SystemExit("Cle invalide : verifie LLM_API_KEY dans .env")
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

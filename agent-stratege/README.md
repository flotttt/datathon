# Agent Stratege

Maillon du milieu du pipeline :

```
Classifieur de narratifs  ->  [Stratege]  ->  Redacteur
   (Mathis)                    (ici)           (Leo)
```

Le Stratege lit une **synthese de l'analyse** et produit un **plan de riposte** :
pour chaque narratif, il decide s'il faut repondre, avec quel angle et pour quel
public. Il ne redige pas les messages finaux (role du Redacteur) et ne classe pas
les tweets (role du Classifieur).

## Fichiers

| Fichier               | Role                                                       |
| --------------------- | ---------------------------------------------------------- |
| `system_prompt.txt`   | Persona, matrice de decision, regles de ton                |
| `schema_sortie.json`  | Contrat de sortie (a partager avec le Redacteur)           |
| `brief_exemple.json`  | Brief d'analyse fictif pour tester sans le Classifieur     |
| `stratege.py`         | Appelle le modele et renvoie le plan de riposte            |

## Contrat de sortie (resume)

```
{
  "synthese_globale": "...",
  "recommandations": [
    {
      "narratif": "...",
      "poids": "...",
      "priorite": "haute | moyenne | basse",
      "decision": "repondre | surveiller | ne_pas_alimenter",
      "angle": "...",
      "messages_cles": ["..."],
      "audience": "...",
      "a_eviter": "...",
      "justification": "..."
    }
  ]
}
```

## Matrice de decision

| Decision           | Quand                                                        |
| ------------------ | ----------------------------------------------------------- |
| `repondre`         | poids important ET factuellement clarifiable                |
| `surveiller`       | en montee mais faible volume, ou ambigu                     |
| `ne_pas_alimenter` | marginal, provocateur ou piege (repondre = amplifier)       |

## Backend : fournisseur compatible OpenAI

Le script utilise le SDK `openai`, donc n'importe quel fournisseur compatible
OpenAI marche (DeepSeek, Moonshot/Kimi API, OpenRouter, etc.). Par defaut :
DeepSeek V4 Flash (`https://api.deepseek.com`, modele `deepseek-v4-flash`).
Pas de schema JSON strict : on active le mode JSON
(`response_format={"type": "json_object"}`) et on injecte `schema_sortie.json`
dans le prompt pour garder le contrat.

| Variable        | Role                         | Defaut                      |
| --------------- | ---------------------------- | --------------------------- |
| `LLM_API_KEY`   | cle du fournisseur (requis)  | -                           |
| `LLM_MODEL`     | modele                       | `deepseek-v4-flash`         |
| `LLM_BASE_URL`  | endpoint                     | `https://api.deepseek.com`  |

Note : l'abonnement **Kimi Code** ne marche PAS ici (reserve aux assistants de
code comme Claude Code / Kimi CLI). Il faut une cle API classique.

## Lancer

```bash
pip install -r requirements.txt
cp .env.example .env             # puis ouvre .env et colle ta cle
python stratege.py               # tourne sur brief_exemple.json
```

La cle est lue depuis `.env` (non versionne). Ne commite jamais `.env` : seul
`.env.example` l'est.

## Etapes

1. Figer le `schema_sortie.json` avec Leo (le contrat de jonction).
2. Iterer le `system_prompt.txt` sur le brief d'exemple.
3. Brancher la vraie sortie du Classifieur a la place de `brief_exemple.json`.

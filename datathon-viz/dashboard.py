import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import os

    import marimo as mo
    import pandas as pd

    HERE = os.path.dirname(os.path.abspath(__file__))
    chemin = os.environ.get("RIPOSTE_JSON", os.path.join(HERE, "..", "riposte.json"))
    with open(chemin, encoding="utf-8") as fichier:
        resultat = json.load(fichier)

    analyse = resultat["analyse"]
    brief = resultat["brief"]
    riposte = resultat["riposte"]
    metriques = resultat.get("metriques") or {}
    return analyse, brief, metriques, mo, pd, riposte


@app.cell
def _(mo):
    mo.md(
        """
        # Riposte — affaire Ultia x CNC

        Sortie de la chaine d'agents : Analyste -> Stratege -> Redacteur.
        """
    )
    return


@app.cell
def _(analyse, brief, mo):
    cartes = mo.hstack(
        [
            mo.stat(analyse["etat_propagation"], label="Etat", bordered=True),
            mo.stat(analyse["ton"]["sentiment_global"], label="Sentiment", bordered=True),
            mo.stat(analyse["ton"]["niveau_agressivite"], label="Agressivite", bordered=True),
            mo.stat(brief["repondre"], label="Decision", bordered=True),
            mo.stat(brief["confiance"], label="Confiance", bordered=True),
        ],
        gap=1,
    )
    cartes
    return


@app.cell
def _(brief, mo):
    mo.md(
        f"""
        ## Decision strategique

        - **Cible** : {brief["cible_narrative"]}
        - **Posture** : {brief["posture"]}
        - **Timing** : {brief["timing"]}
        - **Escalade humaine** : {brief["escalade_humaine"]}

        > {brief["justification"]}
        """
    )
    return


@app.cell
def _(mo):
    mo.md("## Narratifs detectes")
    return


@app.cell
def _(analyse, mo, pd):
    narratifs = pd.DataFrame(analyse["narratifs"])
    narratifs["mots_cles"] = narratifs["mots_cles"].apply(lambda mots: ", ".join(mots))
    mo.ui.table(narratifs, selection=None)
    return


@app.cell
def _(mo):
    mo.md("## Acteurs cles")
    return


@app.cell
def _(analyse, mo, pd):
    acteurs = pd.DataFrame(analyse["acteurs_cles"])
    mo.ui.table(acteurs, selection=None)
    return


@app.cell
def _(mo):
    mo.md("## Messages de riposte (a valider par un humain)")
    return


@app.cell
def _(mo, riposte):
    blocs = [
        mo.callout(mo.md(f"**Proposition {i}**\n\n{message}"), kind="info")
        for i, message in enumerate(riposte["messages"], 1)
    ]
    mo.vstack(blocs)
    return


@app.cell
def _(mo, riposte):
    mo.md(
        f"**Canal** : {riposte['canal']} — "
        f"**A valider humainement** : {riposte['a_valider_humainement']}"
    )
    return


@app.cell
def _():
    # Tarifs DeepSeek V4 Flash, en dollars par million de tokens.
    PRIX_INPUT = 0.14
    PRIX_OUTPUT = 0.28

    def cout_agent(m):
        """Cout en dollars d'un agent a partir de ses tokens."""
        entree = m.get("input_tokens", 0) / 1e6 * PRIX_INPUT
        sortie = m.get("output_tokens", 0) / 1e6 * PRIX_OUTPUT
        return entree + sortie

    return (cout_agent,)


@app.cell
def _(mo):
    mo.md("## Performance (temps + tokens + cout)")
    return


@app.cell
def _(cout_agent, metriques, mo):
    temps = round(sum(m.get("duree_s", 0) for m in metriques.values()), 1)
    tokens = sum(m.get("total_tokens", 0) for m in metriques.values())
    cout = sum(cout_agent(m) for m in metriques.values())
    mo.hstack(
        [
            mo.stat(f"{temps} s", label="Temps total", bordered=True),
            mo.stat(tokens, label="Tokens total", bordered=True),
            mo.stat(f"${cout:.4f}", label="Cout total", bordered=True),
            mo.stat(f"${cout * 1000:.2f}", label="Cout x1000 crises", bordered=True),
        ],
        gap=1,
    )
    return


@app.cell
def _(cout_agent, metriques, mo, pd):
    lignes = [
        {
            "agent": nom,
            "duree_s": m.get("duree_s"),
            "appels": m.get("appels"),
            "tokens_in": m.get("input_tokens"),
            "tokens_out": m.get("output_tokens"),
            "tokens_total": m.get("total_tokens"),
            "cout_usd": round(cout_agent(m), 5),
        }
        for nom, m in metriques.items()
    ]
    perf = pd.DataFrame(lignes)
    total = {
        "agent": "TOTAL",
        "duree_s": round(perf["duree_s"].sum(), 2),
        "appels": perf["appels"].sum(),
        "tokens_in": perf["tokens_in"].sum(),
        "tokens_out": perf["tokens_out"].sum(),
        "tokens_total": perf["tokens_total"].sum(),
        "cout_usd": round(perf["cout_usd"].sum(), 5),
    }
    perf = pd.concat([perf, pd.DataFrame([total])], ignore_index=True)
    mo.ui.table(perf, selection=None)
    return


if __name__ == "__main__":
    app.run()


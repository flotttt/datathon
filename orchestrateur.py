"""
orchestrateur.py — LE CHEF D'ORCHESTRE (poste de Mekk)
C'est lui qui transforme 3 agents isolés en UN produit.

Pipeline : Corpus -> Analyste -> Stratège -> Rédacteur -> Riposte

Lancement :
    python orchestrateur.py
"""
import json
from common import charger_cle, charger_corpus, echantillon, corpus_en_texte
from contracts import valider_sortie
from templates.agents import stratege
from templates.agents import analyste, redacteur


def lancer_pipeline(corpus_texte: str, verbose: bool = True) -> dict:
    if verbose: print("\n=== 1/3  ANALYSTE ===")
    analyse = analyste.run(corpus_texte)
    valider_sortie("analyste", analyse)
    if verbose: print(json.dumps(analyse, ensure_ascii=False, indent=2))

    if verbose: print("\n=== 2/3  STRATÈGE ===")
    brief = stratege.run(analyse)
    valider_sortie("stratege", brief)
    if verbose: print(json.dumps(brief, ensure_ascii=False, indent=2))

    if verbose: print("\n=== 3/3  RÉDACTEUR ===")
    riposte = redacteur.run(brief)
    valider_sortie("redacteur", riposte)
    if verbose: print(json.dumps(riposte, ensure_ascii=False, indent=2))

    return {"analyse": analyse, "brief": brief, "riposte": riposte}


if __name__ == "__main__":
    charger_cle()
    df = charger_corpus("data.xlsx")
    ech = echantillon(df, n=40, fenetre_pic=True)
    texte = corpus_en_texte(ech, max_msg=40)

    print(f"Échantillon : {len(ech)} messages de la fenêtre de pic.")
    resultat = lancer_pipeline(texte)

    print("\n" + "=" * 50)
    print("PRODUIT FINAL — riposte prête à valider :")
    print("=" * 50)
    for i, m in enumerate(resultat["riposte"]["messages"], 1):
        print(f"\n  Proposition {i} :\n  {m}")
    print(f"\n  Canal : {resultat['riposte']['canal']}")
    print(f"  À valider par un humain : {resultat['riposte']['a_valider_humainement']}")

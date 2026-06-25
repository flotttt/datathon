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
    # --- Charte visuelle : un seul bloc CSS, injecte le style "produit" ---
    CSS = """
    <style>
    .pyr-wrap { font-family: ui-sans-serif, system-ui, sans-serif; max-width: 980px; }
    .pyr-ctx {
        display:flex; gap:24px; align-items:center; padding:10px 18px;
        background:#F4F2FA; border-radius:10px; font-size:14px; color:#4B4666;
        margin-bottom:18px;
    }
    .pyr-ctx b { color:#211B38; }
    .pyr-ctx .dot { width:8px; height:8px; border-radius:50%; background:#9A92B8; }

    /* 1 - DECISION (le bloc roi) */
    .deci { border-radius:16px; padding:26px 30px; margin-bottom:16px; color:#fff; }
    .deci.oui        { background:#0F6E56; }
    .deci.temporiser { background:#9A5B0B; }
    .deci.non        { background:#8A2222; }
    .deci .verdict { font-size:40px; font-weight:800; letter-spacing:-1px; line-height:1.05; }
    .deci .meta { display:flex; gap:30px; margin-top:14px; flex-wrap:wrap; }
    .deci .meta div { font-size:14px; opacity:.92; }
    .deci .meta b { display:block; font-size:11px; text-transform:uppercase; letter-spacing:1.5px; opacity:.7; margin-bottom:3px; }
    .deci .why { margin-top:18px; padding-top:16px; border-top:1px solid rgba(255,255,255,.25);
                 font-size:14.5px; line-height:1.55; opacity:.95; }
    .deci .badges { display:flex; gap:10px; margin-top:16px; }
    .deci .badge { font-size:12px; font-weight:600; padding:5px 12px; border-radius:20px;
                   background:rgba(255,255,255,.18); }

    /* 2 - RIPOSTE */
    .sec-h { font-size:13px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;
             color:#5B21B6; margin:24px 0 12px; }
    .msg { background:#fff; border:1px solid #E2DEEE; border-left:4px solid #5B21B6;
           border-radius:0 12px 12px 0; padding:16px 20px; margin-bottom:12px; }
    .msg .lab { font-size:12px; font-weight:700; color:#5B21B6; margin-bottom:6px; }
    .msg .txt { font-size:15px; line-height:1.55; color:#211B38; }
    .valid { display:inline-flex; align-items:center; gap:8px; background:#FEF3E2;
             color:#9A5B0B; font-size:13px; font-weight:600; padding:8px 16px;
             border-radius:20px; margin-top:4px; }

    /* 3 - ANALYSE (preuve, discret) */
    .narr { display:flex; flex-wrap:wrap; gap:10px; }
    .narr .n { border-radius:10px; padding:12px 16px; max-width:320px; }
    .narr .n.dominant   { background:#EEEDFE; border:1px solid #AFA9EC; }
    .narr .n.secondaire { background:#F4F2FA; border:1px solid #D8D3E6; }
    .narr .n.marginal   { background:#F7F6FB; border:1px solid #E6E2F0; }
    .narr .n .nom { font-size:14px; font-weight:700; color:#26215C; }
    .narr .n.secondaire .nom, .narr .n.marginal .nom { font-weight:600; color:#534AB7; }
    .narr .n .poids { font-size:10px; text-transform:uppercase; letter-spacing:1px;
                      color:#7F77DD; font-weight:700; margin-bottom:4px; }
    .narr .n .mc { font-size:12px; color:#6B6480; margin-top:6px; line-height:1.4; }

    .act { display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }
    .act .a { display:flex; align-items:center; gap:8px; background:#fff;
              border:1px solid #E2DEEE; border-radius:20px; padding:6px 14px; font-size:13px; }
    .act .a .pseudo { font-weight:600; color:#211B38; }
    .act .a .cert { font-size:11px; color:#0F6E56; }
    .act .a .ncert { font-size:11px; color:#888780; }

    /* 4 - PERF (pied technique) */
    .perf { display:flex; gap:14px; flex-wrap:wrap; margin-top:6px; }
    .perf .p { background:#F4F2FA; border-radius:10px; padding:12px 18px; }
    .perf .p .v { font-size:22px; font-weight:700; color:#211B38; }
    .perf .p .l { font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#888780; }
    </style>
    """
    mo.md(CSS)
    return (CSS,)


@app.cell
def _(analyse, brief, mo):
    # --- BANDEAU CONTEXTE ---
    nb_acteurs = len(analyse.get("acteurs_cles", []))
    nb_narr = len(analyse.get("narratifs", []))
    ctx = mo.md(f"""
    <div class="pyr-ctx">
      <span><b>Cellule de crise — CNC</b></span><span class="dot"></span>
      <span>État : <b>{analyse['etat_propagation']}</b></span><span class="dot"></span>
      <span>Sentiment : <b>{analyse['ton']['sentiment_global']}</b> · agressivité <b>{analyse['ton']['niveau_agressivite']}</b></span><span class="dot"></span>
      <span><b>{nb_narr}</b> narratifs · <b>{nb_acteurs}</b> acteurs clés</span>
    </div>
    """)
    ctx
    return


@app.cell
def _(brief, mo):
    # --- 1. LA DECISION (bloc roi, couleur semantique) ---
    rep = brief["repondre"]
    verdict_txt = {"oui": "RÉPONDRE", "temporiser": "TEMPORISER", "non": "NE PAS RÉPONDRE"}.get(rep, rep.upper())
    esc = "Oui — validation humaine requise" if brief.get("escalade_humaine") else "Non"

    deci = mo.md(f"""
    <div class="deci {rep}">
      <div class="verdict">{verdict_txt}</div>
      <div class="meta">
        <div><b>Cible narrative</b>{brief['cible_narrative']}</div>
        <div><b>Posture</b>{brief['posture']}</div>
        <div><b>Timing</b>{brief['timing']}</div>
      </div>
      <div class="why">{brief['justification']}</div>
      <div class="badges">
        <span class="badge">Confiance : {brief['confiance']}</span>
        <span class="badge">Escalade humaine : {esc}</span>
      </div>
    </div>
    """)
    deci
    return


@app.cell
def _(mo, riposte):
    # --- 2. LA RIPOSTE (le livrable) ---
    blocs = ""
    for i, m in enumerate(riposte["messages"], 1):
        blocs += f'<div class="msg"><div class="lab">Proposition {i}</div><div class="txt">{m}</div></div>'

    rip = mo.md(f"""
    <div class="sec-h">Riposte proposée — canal : {riposte['canal']}</div>
    {blocs}
    <div class="valid">⚠ À valider par un humain avant publication</div>
    """)
    rip
    return


@app.cell
def _(analyse, mo):
    # --- 3a. ANALYSE : narratifs (badges colores par poids) ---
    cartes = ""
    for n in analyse["narratifs"]:
        poids = n.get("poids", "secondaire")
        mc = ", ".join(n.get("mots_cles", [])[:6])
        cartes += f"""<div class="n {poids}">
          <div class="poids">{poids}</div>
          <div class="nom">{n['nom']}</div>
          <div class="mc">{mc}</div>
        </div>"""

    narr = mo.md(f"""
    <div class="sec-h">Narratifs détectés</div>
    <div class="narr">{cartes}</div>
    """)
    narr
    return


@app.cell
def _(analyse, mo):
    # --- 3b. ANALYSE : acteurs (pills) ---
    pills = ""
    for a in analyse["acteurs_cles"]:
        cert = a.get("type") == "certifie"
        tag = '<span class="cert">✓ certifié</span>' if cert else '<span class="ncert">non certifié</span>'
        pills += f'<div class="a"><span class="pseudo">@{a["pseudo"]}</span>{tag}</div>'

    act = mo.md(f"""
    <div class="sec-h">Acteurs clés (les plus amplifiés)</div>
    <div class="act">{pills}</div>
    """)
    act
    return


@app.cell
def _():
    # Tarifs DeepSeek, en dollars par million de tokens.
    PRIX_INPUT = 0.14
    PRIX_OUTPUT = 0.28

    def cout_agent(m):
        entree = m.get("input_tokens", 0) / 1e6 * PRIX_INPUT
        sortie = m.get("output_tokens", 0) / 1e6 * PRIX_OUTPUT
        return entree + sortie

    return (cout_agent,)


@app.cell
def _(cout_agent, metriques, mo):
    # --- 4. PERFORMANCE (pied technique, discret) ---
    temps = round(sum(m.get("duree_s", 0) for m in metriques.values()), 1)
    tokens = sum(m.get("total_tokens", 0) for m in metriques.values())
    cout = sum(cout_agent(m) for m in metriques.values())

    perf = mo.md(f"""
    <div class="sec-h">Performance — léger et traçable</div>
    <div class="perf">
      <div class="p"><div class="v">{temps} s</div><div class="l">Temps total</div></div>
      <div class="p"><div class="v">{tokens}</div><div class="l">Tokens</div></div>
      <div class="p"><div class="v">${cout:.4f}</div><div class="l">Coût / crise</div></div>
      <div class="p"><div class="v">${cout*1000:.2f}</div><div class="l">Coût / 1000 crises</div></div>
    </div>
    """)
    perf
    return


if __name__ == "__main__":
    app.run()

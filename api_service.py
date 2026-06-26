"""
api_service.py — Micro-service HTTP qui expose l'orchestrateur au dashboard React.

Lance le pipeline (Analyste -> Stratege -> Redacteur) a la demande et renvoie
le meme JSON que riposte.json, directement consommable par adapt-pipeline.ts.

Lancement :
    ./run.sh --api
    # ou :
    uvicorn api_service:app --port 8000
    # ou :
    python api_service.py
"""
import os
import socket
import subprocess
import time
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import data_loading
from common import charger_cle
from orchestrateur import lancer_pipeline

RACINE = Path(__file__).resolve().parent
MARIMO_DIR = RACINE / "datathon-viz"
MARIMO_PORT = int(os.environ.get("MARIMO_PORT", "2718"))
MARIMO_URL = f"http://localhost:{MARIMO_PORT}"

app = FastAPI(title="Orchestrateur de crise — API")

# CORS large : le dashboard Next passe normalement par son proxy /api/run,
# mais on autorise aussi un appel direct depuis le navigateur en dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_cle_chargee = False


def _assurer_cle() -> None:
    """Charge la cle API une seule fois (au premier /run)."""
    global _cle_chargee
    if not _cle_chargee:
        charger_cle()
        _cle_chargee = True


@app.get("/health")
def health() -> dict:
    """Sonde de disponibilite pour le proxy Next."""
    return {"status": "ok"}


_marimo_proc = None


def _marimo_exe() -> list[str]:
    """Prefere le marimo du venv de datathon-viz, sinon `python -m marimo`."""
    cand = MARIMO_DIR / ".venv" / "bin" / "marimo"
    if cand.exists():
        return [str(cand)]
    return [sys.executable, "-m", "marimo"]


def _port_ouvert(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


@app.post("/marimo")
def marimo() -> JSONResponse:
    """Lance le notebook marimo (datathon-viz) s'il ne tourne pas deja."""
    global _marimo_proc

    deja_lance = _port_ouvert(MARIMO_PORT) or (
        _marimo_proc is not None and _marimo_proc.poll() is None
    )

    if not deja_lance:
        env = dict(os.environ)
        env["DATATHON_DATA"] = str(RACINE / "Dataset" / "data.xlsx")
        _marimo_proc = subprocess.Popen(
            [
                *_marimo_exe(), "run", "app.py",
                "--headless", "--host", "127.0.0.1",
                "--port", str(MARIMO_PORT), "--no-token",
            ],
            cwd=str(MARIMO_DIR),
            env=env,
        )
        # Attendre que le serveur reponde avant de renvoyer l'URL.
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < 20 and not _port_ouvert(MARIMO_PORT):
            time.sleep(0.4)

    if not _port_ouvert(MARIMO_PORT):
        return JSONResponse(
            status_code=500,
            content={"erreur": "Marimo n'a pas demarre a temps."},
        )

    return JSONResponse(content={"url": MARIMO_URL})


@app.post("/run")
def run() -> JSONResponse:
    """Charge le corpus, execute le pipeline complet et renvoie la riposte."""
    _assurer_cle()
    chemin = os.environ.get("DATATHON_DATA", "Dataset/data.xlsx")

    try:
        df = data_loading.load_corpus(chemin)
    except FileNotFoundError:
        return JSONResponse(
            status_code=400,
            content={"erreur": f"Corpus introuvable : {chemin}"},
        )

    t0 = time.perf_counter()
    resultat = lancer_pipeline(df, verbose=False)
    resultat["contexte"] = {
        "entite": "Cellule de crise — CNC",
        "messages": len(df),
    }
    resultat["duree_totale_s"] = round(time.perf_counter() - t0, 2)

    if resultat.get("erreur"):
        return JSONResponse(status_code=500, content=resultat)

    return JSONResponse(content=resultat)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8077")))

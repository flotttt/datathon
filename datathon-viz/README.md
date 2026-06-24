# Datathon - Visualisations (marimo)

Analyse descriptive du corpus de l'affaire Ultia x CNC.
Notebook reactif marimo + modules pandas separes.

## Structure

| Fichier            | Role                                                        |
| ------------------ | ----------------------------------------------------------- |
| `app.py`           | Notebook marimo : importe les modules et trace les graphes  |
| `data_loading.py`  | Chargement et nettoyage du fichier Excel                    |
| `metrics.py`       | Agregations pandas (timeline, top comptes, sentiment, etc.) |
| `requirements.txt` | Dependances                                                 |

Le notebook ne contient aucune logique de calcul : tout est dans
`data_loading.py` et `metrics.py`, qui sont importables et testables seuls.

## Prerequis

- Python 3.10 ou plus

## Installation

```bash
cd datathon-viz
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Donnees

Le notebook cherche `data.xlsx` dans le dossier courant. Deux options :

```bash
# Option 1 : copier le fichier dans le dossier
cp /chemin/vers/data.xlsx .

# Option 2 : pointer vers le fichier via une variable d'environnement
export DATATHON_DATA=/chemin/vers/data.xlsx
```

## Lancer

```bash
# Mode application (lecture seule, pour la demo)
marimo run app.py

# Mode edition (pour modifier les cellules)
marimo edit app.py
```

marimo ouvre l'interface dans le navigateur.

## Ajouter une visualisation

1. Ajouter la fonction d'agregation dans `metrics.py` (renvoie un DataFrame).
2. Ajouter une cellule dans `app.py` qui appelle la fonction et trace le graphe.

Exemple minimal de cellule :

```python
@app.cell
def _(alt, corpus, metrics):
    donnees = metrics.ma_nouvelle_metrique(corpus)
    graphe = alt.Chart(donnees).mark_bar().encode(x="count:Q", y="label:N")
    graphe
    return
```

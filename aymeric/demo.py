"""
Script de démo du pipeline d'agents d'analyse de crise.
Usage :
    cp .env.example .env
    # éditer .env avec MISTRAL_API_KEY=...
    python demo.py
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from data_utils import load_corpus, build_context, context_to_markdown
from agents.orchestrator import CrisisOrchestrator


def main():
    load_dotenv()

    focus = os.getenv("CRISIS_FOCUS", "ultia")
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Datathon CNC × Ultia — Pipeline d'agents IA")
    print("=" * 60)

    print("\n1. Chargement du corpus...")
    df = load_corpus()
    print(f"   {len(df):,} posts chargés.")

    print(f"\n2. Construction du contexte (focus : '{focus}')...")
    context = build_context(df, focus_keyword=focus)
    print(
        f"   {context['basic_stats']['total_posts']:,} posts liés au focus, "
        f"du {context['basic_stats']['date_min']} au {context['basic_stats']['date_max']}"
    )
    context["markdown"] = context_to_markdown(context)

    # Sauvegarde du contexte pour inspection/debug
    context_path = output_dir / f"context_{focus}_{datetime.now():%Y%m%d_%H%M%S}.md"
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(context["markdown"])
    print(f"   Contexte sauvegardé : {context_path}")

    print("\n3. Lancement de l'orchestrateur multi-agents...")
    orchestrator = CrisisOrchestrator()
    report = orchestrator.run(context)

    print("\n4. Rapport généré. Extraits :")
    print("-" * 60)
    print("Synthèse :")
    print(json.dumps(report["synthesis"], indent=2, ensure_ascii=False))
    strategy = report.get("strategy")
    if strategy and hasattr(strategy, "summary"):
        print("\nRecommandation stratégique :")
        print(strategy.summary)
    print("-" * 60)

    report_path = output_dir / f"report_{focus}_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n5. Rapport complet sauvegardé : {report_path}")

    # Version markdown du rapport
    md_path = report_path.with_suffix(".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Rapport d'analyse de crise\n\n")
        f.write(f"**Focus :** {focus}\n\n")
        f.write("## Synthèse\n\n")
        f.write(json.dumps(report["synthesis"], indent=2, ensure_ascii=False))
        f.write("\n\n## Données brutes par agent\n\n")
        f.write("```json\n")
        f.write(json.dumps(report, indent=2, ensure_ascii=False, default=str))
        f.write("\n```\n")
    print(f"   Rapport markdown : {md_path}")


if __name__ == "__main__":
    main()

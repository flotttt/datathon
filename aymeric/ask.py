"""
Script interactif de Q&R (RAG) sur le corpus Twitter/X via Chroma DB.

Usage :
    python ask.py "Quel est le compte qui a lancé la crise ?"
    python ask.py                          # mode interactif
"""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from agents.qa_agent import QAAgent
from chroma_store import is_indexed
from data_utils import build_context, load_corpus


def answer_question(question: str) -> None:
    load_dotenv()

    if not is_indexed():
        print("❌ Chroma DB n'est pas indexé.")
        print("   Lancez d'abord : python chroma_store.py")
        sys.exit(1)

    # On construit un contexte minimal (les tweets pertinents seront récupérés par Chroma)
    df = load_corpus()
    focus = os.getenv("CRISIS_FOCUS", "ultia")
    context = build_context(df, focus_keyword=focus)
    context["question"] = question
    context["markdown"] = ""

    print(f"\n🔍 Question : {question}\n")
    print("Récupération des tweets pertinents via Chroma...")

    agent = QAAgent(n_results=8)
    result = agent.run(context)

    print("\n📝 Réponse :")
    print(result.answer)
    print(f"\nConfiance : {result.confidence}")
    print("\nSources :")
    for src in result.sources:
        print(f"  {src.rank}. @{src.author} ({src.date}) — pertinence {src.relevance}")
        print(f"     {src.text[:150]}...")


def interactive_mode() -> None:
    print("Mode interactif. Tapez 'quit' pour sortir.")
    while True:
        question = input("\n❓ Question : ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        answer_question(question)


def main():
    parser = argparse.ArgumentParser(description="Q&R RAG sur le corpus Ultia × CNC")
    parser.add_argument("question", nargs="?", help="Question à poser")
    args = parser.parse_args()

    if args.question:
        answer_question(args.question)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()

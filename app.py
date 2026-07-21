"""Clinical Jargon Explainer — Cross Clinical educational Space."""

from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

from input_guard import DISCLAIMER, guard_input

GLOSSARY = json.loads((Path(__file__).parent / "data" / "glossary.json").read_text())
DISCIPLINES = sorted({g["discipline"] for g in GLOSSARY})


def lookup(term: str, discipline: str) -> str:
    blocked = guard_input(term)
    if blocked:
        return blocked
    q = (term or "").strip().lower()
    if not q:
        return "Enter a term (e.g. dyspnea, SBAR, NWB, contraindication)."
    hits = []
    for g in GLOSSARY:
        if discipline != "all" and g["discipline"] != discipline:
            continue
        if q == g["term"].lower() or q in g["term"].lower() or q in g["plain_english"].lower():
            hits.append(g)
    if not hits:
        return (
            "No glossary match. Try another spelling, or browse by discipline. "
            "Always verify with your course materials."
        )
    parts = []
    for g in hits[:12]:
        parts.append(
            f"### {g['term']} (`{g['discipline']}`)\n"
            f"**Plain English:** {g['plain_english']}\n\n"
            f"**Context note:** {g['note']}\n\n"
            f"*{g['source']}*\n\n"
            f"_Study tip: restate this in your own words and check your textbook._"
        )
    return "\n\n---\n\n".join(parts)


def list_discipline(discipline: str) -> str:
    rows = [g for g in GLOSSARY if discipline == "all" or g["discipline"] == discipline]
    rows = sorted(rows, key=lambda x: x["term"].lower())
    lines = [f"- **{g['term']}** — {g['plain_english']}" for g in rows]
    return f"## {len(rows)} terms\n\n" + "\n".join(lines)


with gr.Blocks(title="Clinical Jargon Explainer") as demo:
    gr.Markdown(
        f"# Clinical Jargon Explainer\n\n**{DISCLAIMER}**\n\n"
        f"[Cross Clinical OSS](https://github.com/Cross-Clinical/awesome) · "
        f"[ProMedNet](https://crossclinical.com)"
    )
    with gr.Row():
        term = gr.Textbox(label="Term")
        disc = gr.Dropdown(["all", *DISCIPLINES], value="all", label="Discipline filter")
    out = gr.Markdown()
    gr.Button("Explain").click(lookup, [term, disc], out)
    term.submit(lookup, [term, disc], out)
    with gr.Accordion("Browse glossary", open=False):
        d2 = gr.Dropdown(["all", *DISCIPLINES], value="nursing", label="Discipline")
        browse = gr.Markdown()
        d2.change(list_discipline, d2, browse)
        demo.load(list_discipline, d2, browse)

if __name__ == "__main__":
    demo.launch()

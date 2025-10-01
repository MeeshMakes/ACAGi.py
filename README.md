# ACAGi.py

ACAGi: single-script, local-first AGI shell. Embedded virtual desktop + terminal, task buckets, Sentinel self-healing, voice I/O, dual-pass OCR, 3D brain map. Offline by default; GitHub optional.

## Repository Governance Skeleton
This repository now ships with an explicit Codex governance scaffold:
- `AGENT.md` — Operating manual describing workflows, verbose coding mandates, and PR expectations.
- `memory/` — Durable knowledge base (`codex_memory.json`) and actionable instruction queue (`logic_inbox.jsonl`).
- `logs/` — Daily session journals capturing objectives, context review, and follow-up prompts.
- `Dev_Logic/` — Workspace for active design documents, plus `Implemented_logic/` for ratified decisions.
- `Archived Conversation/` — Historical reference for superseded content and discussions.
- `.github/workflows/codex-pr-sentinel.yml` — GitHub Actions workflow running Codex PR Sentinel checks.
- `tools/` — Automation scripts powering sentinel validation and logic inbox maintenance.

Refer to `CHANGELOG.md` for versioned history of repository governance updates.

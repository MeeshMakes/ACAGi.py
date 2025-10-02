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

# ACAGi.py

Welcome to **ACAGi.py** — a project maintained by MeeshMakes.

## Overview

ACAGi.py is a Python-based repository focused on [insert brief description of project purpose or functionality here].
It leverages Python’s flexibility and simplicity to achieve [insert one or two goals or key features].

### Voice pipeline highlights

- **Local ASR + TTS adapters** – `ACAGi.py` now bundles on-device speech-to-text
  and text-to-speech adapters that stream partial transcripts to
  `speech.partial` while supporting barge-in (pausing narration when a human
  starts speaking).
- **Speech orchestrator** – the shared orchestrator exposes a
  `speech.request` topic so docks, macros, or automation can enqueue narration
  requests, and publishes telemetry on `speech.tts` for UI widgets.
- **Amygdala salience** – diarization metadata (speaker labels, priorities,
  barge-in flags) feeds the Amygdala component, which republishes weighted
  scores on `system.salience` for downstream attention dashboards.

## Language Composition

- **Python**: The primary language used throughout the repository.

## Getting Started

To get started, clone the repository and install any necessary dependencies listed in `requirements.txt` (if available):

```bash
git clone https://github.com/MeeshMakes/ACAGi.py.git
cd ACAGi.py
pip install -r requirements.txt
```

## Usage

[Provide basic usage instructions or code examples here.]

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.  
Be sure to follow the coding standards and review guidelines.

## License

[Specify the project license here.]

---

## Future Note

This repository is actively maintained with the intent to expand its capabilities and improve usability. Future work may include:

- Adding more detailed documentation and tutorials.
- Expanding test coverage and introducing CI/CD workflows.
- Refactoring to support additional languages or frameworks if needed.
- Streamlining onboarding for new contributors.

**If you’re reading this in the future:**  
Please check the open issues and pull requests for current development priorities. Keep communication open via issues and discussions.  
Feel free to suggest new directions or enhancements as the project evolves!

---

_Maintained by MeeshMakes_

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

### Self-Implementation Mode

The status bar now exposes a **Self-Implementation Mode** toggle that enables
ACAGi to autonomously survey durable memory, dataset anchors, and the logic
inbox. When active, the controller dispatches Rationalizer intent segmentation
jobs, spawns exploratory task buckets, and appends a session note summarising
every cycle.

Sentinel policies remain in control of energy quotas and loop detection:

- `policies.json` defines a `self_impl` operation with a single concurrent slot,
  a 900 s watchdog, and denied network access.
- The controller emits `autonomy.energy_quota` and `autonomy.loop_detected`
  sentinel events whenever quotas or digest repeats trigger a pause.
- The status bar button is disabled automatically when Sentinel blocks further
  cycles.

#### Manual Observation Steps

1. Launch ACAGi and open the **Log Observatory** dock to tail the shared log.
2. Toggle **Self-Implementation** on from the status bar telemetry panel.
3. Monitor the log for `autonomy.self_impl` events that describe survey inputs,
   generated bucket IDs, and associated task anchors. Expect additional
   sub-events (`energy_violation`, `loop_violation`, `sentinel_blocked`) when
   the controller pauses itself.
4. Inspect the **system.sentinel** feed (Log Observatory or chat stream) for
   `autonomy.energy_quota` or `autonomy.loop_detected` warnings. The status bar
   button will pause automatically and surface the sentinel reason when a
   violation fires.
5. Review `logs/session_<date>.md` for the appended session note summarising
   each Self-Implementation cycle and sentinel pause.

Disable the toggle to return to manual control or investigate sentinel
warnings before re-enabling autonomous cycles.

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

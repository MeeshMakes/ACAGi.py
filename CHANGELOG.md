# Changelog
## [0.1.16] - 2025-10-06
### Added
- Extended the main window status bar with a telemetry panel that surfaces
  remote fan-out toggles, sandbox posture, CPU/RAM meters, attention mix, and
  OCR duty cycle readouts.
- Subscribed the telemetry panel to Gate/Scheduler updates on the Thalamus
  `system.metrics` topic and documented remote pause/resume handling.

### Validation
- Validated syntax with `python -m compileall ACAGi.py` and recorded telemetry
  smoke checks in `logs/session_2025-10-06.md`.

## [0.1.15] - 2025-10-05
### Added
- Added a Ctrl+K command palette overlay that lists policy-reviewed commands and persisted playbook macros while dispatching selections through the event bus.
- Introduced Dev Space playbook management with JSONL-backed promotion flows and manual macro execution note tracking.

### Changed
- Extended safety policies with action-level enforcement for palette triggers and seeded macro defaults in the policy bundle.

## [0.1.14] - 2025-10-05
### Added
- Introduced a Brain Map dock that lazily initialises a graphics scene to render
  Hippocampus nodes and typed edges with energy/salience overlays and Dev Space
  activation callbacks.
- Added energy heatmap, queue depth, and error ray toggles so operators can
  spotlight different operational metrics while reviewing the graph.

### Changed
- Linked the Brain Map dock with the Virtual Desktop focus helper to jump into
  Dev Space diagnostics whenever a node is selected.
- Ensured theme/settings reloads refresh the Brain Map registry reference and
  exposed a View menu toggle alongside other investigative docks.

## [0.1.13] - 2025-10-05
### Added
- Introduced a Log Observatory dock that tails the shared system log, scans
  process/session streams, and surfaces filter/search controls while live
  streaming Thalamus bus events.

### Changed
- Tabified the Log Observatory with the error console and exposed a view menu
  toggle so operators can quickly switch between diagnostics surfaces.

## [0.1.12] - 2025-10-05
### Added
- Introduced a Virtual Desktop dock that lazily initializes consoles, Dev Space
  tabs, and OCR overlays while streaming event bus updates into the UI.

### Changed
- Replaced the standalone TerminalDesktop central widget with the new dock,
  wiring live task/log/dataset refreshes and view menu toggles for operators.

## [0.1.11] - 2025-10-05
### Added
- Enabled transcript bubble taps to push Hippocampus-backed memory entries and
  append corresponding session JSONL notices with dataset anchors for reruns.

### Changed
- Wrapped the Codex bridge LED in a dedicated health state machine that
  synchronizes tooltips, interpreter toggle availability, and ready-banner
  acknowledgements.
- Wired approval prompt responses and ready detections through the new state
  handling so busy/error transitions surface consistent system notices.

## [0.1.10] - 2025-10-04
### Added
- Introduced a sentinel monitor hub that subscribes to task/status topics, detects loops/regressions/stalls, and publishes immune responses with rationale on the `system.immune` stream.
- Added a versioned `policies.json` template and settings loader support that materializes coder/test allowlists, denylists, sandbox requirements, and approval rules for SafetyManager.

### Changed
- Extended SafetyManager and command helpers to enforce operation policies, surface sandbox mismatches, and expose manual immune response triggering utilities.

## [0.1.9] - 2025-10-02
### Added
- Added a Hippocampus-backed dataset manager dock that lets operators ingest
  tagged files or directories from the UI while kicking off OCR, embedding, and
  summarisation workflows.

### Changed
- Registered ingestion outputs with a persistent brain map registry so new
  nodes and edges surface in the 3D visualisation after Hippocampus processes
  them.

## [0.1.8] - 2025-10-02
### Added
- Embedded a `MemoryServices` stack that loads durable lessons, instruction inbox items, and session JSONL tails during boot and exposes CRUD helpers for each store.
- Introduced `DatasetNodePersistence` to split dataset entries into Git-friendly JSONL cores with vector/thumbnail sidecars and enforced metadata anchors.

### Changed
- Updated the dataset manager to rely on the new persistence helpers, automatically generating thumbnails and storing embeddings in sidecars while keeping JSONL entries lightweight.

## [0.1.7] - 2025-10-05
### Added
- Introduced a topic-aware event dispatcher with bounded subscriber queues so observation, note, task, and system streams share a consistent pub/sub surface.

### Changed
- Routed dispatcher telemetry into the shared `vd_system.log` sink and added informational logs to trace publish/drop flows.

## [0.1.6] - 2025-10-05
### Changed
- Consolidated safety guardrails, prompt loader, image pipeline, and repository indexing code directly into `ACAGi.py`, replacing sibling module imports with scoped sections referencing the Dev_Logic assets.
- Embedded the token budget helpers into the monolithic module so runtime budget calculations no longer depend on external imports.

# [0.1.5] - 2025-10-04
### Added
- Added a structured runtime settings loader (`acagi.ini`) that materializes defaults, documents config sections, and persists boolean/limit flags for offline, sandbox, and remote integrations.

### Changed
- Routed runtime feature flags into the event bus metadata, remote throttling, safety sentinel, and UI status bar so operators immediately see offline/sandbox context and configured rate limits.

## [0.1.4] - 2025-10-03
### Added
- Introduced a Boot & Environment bootstrap in `ACAGi.py` that centralizes DPI policy, workspace/transit resolution, shared logging (`vd_system.log`), and the BrainShell crash dialog.

### Changed
- Refreshed path helper functions and the CLI entrypoint to rely on the new boot manager, preserving compatibility with existing callers while supporting workspace overrides.

## [0.1.3] - 2025-10-03
### Changed
- Inlined task persistence, event bus, UI, error console, background engines, and repository reference helper directly into `ACAGi.py`, preserving existing behavior with new section headers for maintainability.
- Updated governance utilities by validating the logic inbox and ensuring dependency-aware multimedia and OpenGL guards live within the monolithic file.

## [0.1.2] - 2025-10-02
### Changed
- Refactored optional dependency handling so `requests` and Pillow are imported normally while runtime capability checks manage warnings and graceful degradation.

## [0.1.1] - 2025-10-02
### Changed
- Clarified ACAGi's single-file positioning in the module docstring and refreshed status/error messaging to use the ACAGi name.

## [0.1.0] - 2025-10-01
### Added
- Initial governance scaffold including `AGENT.md`, memory structures, and session logging template.
- Codex PR Sentinel workflow and supporting automation scripts.
- Dev Logic and Archived Conversation directories with usage guidance.
- Logic inbox seeded with governance follow-up tasks.

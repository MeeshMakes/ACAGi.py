# Changelog
## [0.1.38] - 2025-10-18
### Added
- Introduced a Windows elevation helper that relaunches ACAGi with the
  ``runas`` verb when administrative privileges are missing, guarding against
  infinite recursion with the ``ACAGI_ELEVATED`` environment flag and logging
  bootstrap decisions for operators.

### Validation
- `python -m compileall ACAGi.py`

## [0.1.37] - 2025-10-18
### Fixed
- Reused ACAGi's guarded DPI helper inside `Codex_Terminal.py` so both
  entrypoints share the same idempotent Qt bootstrap and avoid import-time
  configuration.
- Moved the helper invocation to the QApplication construction path to prevent
  late calls after Qt has already been initialised by an embedding host.
- Marked the logic inbox task for factoring the Qt bootstrap helper as
  completed now that the entrypoints share the guard.

### Validation
- `python -m compileall Codex_Terminal.py`
- `python -m compileall ACAGi.py/Codex_Terminal.py`

## [0.1.36] - 2025-10-18
### Fixed
- Removed the module-level DPI policy invocation and now invoke the guard only
  immediately before `QApplication` creation so embedded hosts can opt out while
  standalone launches still configure Qt as early as possible.
- Ensured the high-DPI helper records `_HIGH_DPI_POLICY_APPLIED` for skip
  branches and after execution, preventing redundant retries when multiple
  entrypoints attempt to configure Qt within the same process.
- Added an early-return path in `main()` when a `QApplication` already exists
  so ACAGi avoids constructing duplicate application instances.

### Validation
- `python -m compileall ACAGi.py`

## [0.1.35] - 2025-10-17
### Fixed
- Hardened the high-DPI rounding helper to bail out when a Qt core application
  already exists, preventing Qt's fatal "must be called before creating the
  QGuiApplication" shutdown during ACAGi startup.

### Validation
- `python -m compileall ACAGi.py`

## [0.1.34] - 2025-10-17
### Fixed
- Updated the ACAGi main window to embed the chat view inside the draggable
  Terminal Desktop canvas when running standalone so startup mirrors the
  Codex Terminal experience instead of displaying a bare chat pane.

### Validation
- `python -m py_compile ACAGi.py`

## [0.1.33] - 2025-10-17
### Fixed
- Added a boot-time PySide6 availability guard that logs installation guidance
  instead of throwing `ModuleNotFoundError`, allowing headless workflows to
  continue running automation helpers.

### Validation
- `python ACAGi.py` *(logs missing PySide6 guidance; exits with code 1)*
- `python -m py_compile ACAGi.py`

## [0.1.32] - 2025-10-16
### Fixed
- Hardened the high-DPI rounding policy guard so embedded Qt hosts log and skip
  the setter instead of crashing when a `QGuiApplication` already exists.

### Validation
- `python -m py_compile ACAGi.py`

## [0.1.31] - 2025-10-15
### Fixed
- Deferred the `flush_pending_sentinel_events()` invocation until after its
  definition so sentinel history replay no longer raises a module-import
  `NameError`.

### Validation
- `python ACAGi.py` *(fails: missing `PySide6`; import still exercises sentinel
  flush without raising `NameError`)*
- `python -m py_compile ACAGi.py`

## [0.1.30] - 2025-10-15
### Fixed
- Relocated the `EVENT_DISPATCHER` singleton above the remote access guard so
  module import no longer risks a `NameError` before the dispatcher exists.
- Repositioned the remote access helpers to follow the dispatcher utilities,
  keeping inline documentation accurate about boot ordering expectations.

### Validation
- `python ACAGi.py` *(fails: missing `PySide6` in container; dispatcher ordering validated up to import stage)*

## [0.1.29] - 2025-10-14
### Fixed
- Reordered `RemoteAccessController` initialisation to occur after the event
  dispatcher is created so ACAGi boots without raising `NameError` and the
  Codex Terminal / Virtual Desktop wiring stays intact.
- Logged session context in `logs/session_2025-10-14.md` to document the
  remediation path and uphold archival policy.

### Validation
- `python -m py_compile ACAGi.py`

## [0.1.28] - 2025-10-13
### Changed
- Hoisted `APP_NAME`, `VD_LOGGER_NAME`, and log sink constants to the top of
  `ACAGi.py` so `SafetyManager` and other boot-time subsystems can initialise
  loggers without encountering `NameError` exceptions during module import.
- Recorded the associated session plan in `logs/session_2025-10-13.md` for
  traceability per governance requirements.

### Validation
- `python -m compileall ACAGi.py`

## [0.1.27] - 2025-10-12
### Added
- Introduced a status bar **Self-Implementation Mode** toggle that wires a new
  autonomy controller into the Rationalizer, task bucket pipeline, and sentinel
  event streams.
- Added telemetry publishing on `autonomy.self_impl` and appended session notes
  for every autonomous cycle so operators can audit generated tasks.

### Changed
- Updated `policies.json` with a dedicated `self_impl` operation enforcing
  serialized execution, 900 s watchdogs, and network denial; sentinel events now
  pause the mode on quota or loop violations.
- Documented the new workflow and manual observation steps in `README.md` and
  refreshed status panel UX to surface the toggle state.
- Emitted explicit `autonomy.self_impl` sub-events when sentinel policies pause
  the controller so observers can correlate cycle history with energy or loop
  enforcement in real time.

### Validation
- `python -m compileall ACAGi.py`
- Manual: enable Self-Implementation Mode, observe `autonomy.self_impl` and
  sentinel events in the Log Observatory, and confirm the status bar pauses when
  energy or loop policies trigger.

## [0.1.26] - 2025-10-12
### Added
- Introduced reusable helpers to load and persist `policies.json`, regenerating
  defaults when missing and writing sorted, indented JSON for review-friendly
  diffs.

### Changed
- Updated coder/test/macro policy defaults with explicit duration caps,
  parallel slot limits, and a shared network command blocklist consumed by the
  safety manager and sentinel monitors.
- Enhanced `SafetyManager` and `run_checked` so operation policies now acquire
  parallel slots, clamp timeouts, strip network proxies, and emit sentinel
  events when bans or timeouts trigger.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.
- Logged planned policy override tests in `logs/session_2025-10-02.md`.

## [0.1.25] - 2025-10-11
### Added
- Automated startup processing of `memory/logic_inbox.jsonl`, publishing events or scheduling task buckets for actionable inbox entries while preserving deferred instructions on disk.

### Changed
- Extended the shutdown coordinator to write success/failure/anchor summaries into both durable session notes and the dated session log, capturing logic inbox dispatch outcomes for follow-up reviews.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.
- Manual verification: review `vd_system.log` for the "Logic inbox startup processing" summary and confirm `logs/session_<date>.md` receives the shutdown section with anchors.

## [0.1.24] - 2025-10-10
### Added
- Emitted structured `system.sentinel` events for Codex bridge loss, sandbox
  corruption repairs, and repeated task regressions with UI dialogs that meet
  high-contrast requirements and surface recovery guidance.
- Created `Dev_Logic/Implemented_logic/2025-10-10-sentinel-failure-injection.md`
  documenting manual failure injection steps for each new sentinel pathway.

### Changed
- Extended the sentinel monitor with regression counters that escalate after
  successive rollbacks and wired the terminal to subscribe to sentinel history
  so startup alerts replay into the chat log.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.
- Logged failure simulation procedures in
  `Dev_Logic/Implemented_logic/2025-10-10-sentinel-failure-injection.md`.

## [0.1.23] - 2025-10-10
### Added
- Introduced a coordinated shutdown pipeline that flushes event dispatcher queues,
  syncs log handlers, persists durable memory stores, and appends a structured
  session note via the new `ShutdownCoordinator` helper.
- Captured crash stack traces to timestamped files under the agent `crashes/`
  directory and enhanced the BrainShell crash dialog with report metadata plus a
  high-contrast terminal fallback banner when Qt is unavailable.

### Changed
- Routed the global exception hook through the shutdown coordinator so crash
  handling triggers the same flush/persist workflow used during graceful exits.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.
- Logged manual crash simulation steps in `logs/session_2025-10-02.md`.

## [0.1.22] - 2025-10-09
### Added
- Added local GitHub Desktop and GitHub CLI detection with status badges in the
  status bar telemetry panel and Settings dialog, avoiding any outbound network
  probes.
- Introduced a `RemoteAccessController` that gates remote fan-out behind an
  explicit toggle, syncs safety policy notices, and emits ScriptSpeak
  `TOGGLE_REMOTE` events with rich metadata.

### Changed
- Extended the status bar summary with remote tooling availability indicators
  alongside remote link posture.
- Updated the Settings dialog to surface remote toggle state and detection
  tooltips inside a dedicated "Remote Access" section.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.
- Documented manual remote toggle verification in
  `logs/session_2025-10-02.md`.

## [0.1.21] - 2025-10-09
### Added
- Introduced a ScriptSpeak parser that normalises verbs, arguments, and flags
  into structured payloads and publishes them on a dedicated `script.command`
  event stream with session log journaling.
- Wired macro playbooks and ad-hoc macro events through the parser so queued
  automation steps emit auditable ScriptSpeak instructions.
- Extended the Rationalizer manager to forward ScriptSpeak guidance emitted in
  job results onto the event bus with per-job metadata, enabling automated
  follow-ups to appear in session transcripts.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.

## [0.1.20] - 2025-10-08
### Added
- Implemented coder/test/verifier lifecycle handlers that capture anchored patches
  with rationales, execute configured validations, and publish bucket telemetry
  for UI consumers.

### Changed
- Routed task bucket failures through the Rationalizer loop and persisted the
  latest failure snapshot in durable memory so operators retain actionable
  learnings alongside telemetry events.

## [0.1.19] - 2025-10-08
### Added
- Added task bucket lifecycle data classes and orchestration helpers that drive
  capture→note→bucketize→assemble→apply→test→verify→promote transitions while
  emitting stage telemetry on new event topics.
- Exposed a bucket stage context/result API so handlers can enrich metadata,
  touched files, and notes for downstream observers.

### Changed
- Introduced a serialization manager that leases Apply/Test/Verify stages when
  buckets touch overlapping files, maintaining parallelism for upstream
  assembly work while preventing conflicting writes.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.

## [0.1.18] - 2025-10-07
### Added
- Introduced a Cerebellum scheduler and Rationalizer manager that spin up
  short-lived workers for intent segmentation and reference resolution while
  enforcing Gate quotas.
- Published cortex rationalizer results on new `cortex.intent` and
  `cortex.reference` event topics alongside telemetry on `system.metrics`.

### Changed
- Extended default settings with Cerebellum quota controls and wired the chat
  workflow to queue Rationalizer jobs whenever a user message is recorded.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.

## [0.1.17] - 2025-10-07
### Added
- Embedded local-first ASR and TTS adapters inside `ACAGi.py` with streaming
  partial transcripts on the `speech.partial` bus topic and barge-in support
  that pauses synthesis while the operator speaks.
- Introduced a shared `SpeechOrchestrator` entry point plus a `speech.request`
  event interface so UI or automation layers can enqueue narration safely.
- Connected a new Amygdala salience pipeline that weights diarization and
  speaker-priority metadata, publishing aggregated scores on `system.salience`.

### Changed
- Extended default settings to include a `voice` section with ASR/TTS tunables
  and propagated configuration reloads through the orchestrator.
- Expanded event dispatcher topics for speech activity, TTS telemetry, and
  salience scoring so downstream docks can subscribe without manual wiring.

### Validation
- Ran `python -m compileall ACAGi.py` to confirm syntax integrity.
- Performed manual audio checks by capturing microphone input to verify
  partial transcript streaming, triggering TTS narration, and speaking over it
  to confirm barge-in pauses/resumes playback while logs reflected the state.

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

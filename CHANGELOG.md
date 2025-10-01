# Changelog

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

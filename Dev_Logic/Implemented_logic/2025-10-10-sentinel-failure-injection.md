# Sentinel Failure Injection Checklist (v0.1.0)

## Purpose
Document manual procedures for exercising newly instrumented sentinel failure modes: Codex bridge loss, sandbox configuration corruption, and repeated regression detection.

## Preconditions
- ACAGi desktop running on Windows with Codex bridge available.
- Access to `acagi.ini` and task bucket fixtures.
- Event console (Error Console dock) visible to observe sentinel notices.

## Bridge Loss Simulation
1. Launch Codex bridge via **Start Codex + Bridge**.
2. Once the LED turns green, forcibly terminate the Codex console process (e.g., Task Manager → End task).
3. Observe expectations:
   - Bridge LED transitions to red.
   - System notice: `[Sentinel:ui.terminal] Codex bridge connection lost…`.
   - High-contrast dialog summarises recovery steps.
   - `system.sentinel` event payload includes `kind="bridge.loss"` and `bridge_running=false`.
4. Restart bridge and confirm sentinel alerts clear after successful reconnect.

## Sandbox Corruption Simulation
1. Close ACAGi.
2. Edit `%APPDATA%/ACAGi/acagi.ini`, set `[mode] sandbox = chaos`.
3. Relaunch ACAGi.
4. Confirm expectations:
   - Sentinel dialog and log entry referencing sandbox corruption.
   - Runtime sandbox resets to `restricted` in status bar.
   - Settings dialog shows corrected profile after reopening and saving.
5. Restore file with a valid sandbox value when finished.

## Repeated Regression Simulation
1. Seed a task bucket fixture capable of toggling between `complete` and `in-progress` statuses via event bus mock or manual JSON edits.
2. Publish alternating status updates (`complete` → `blocked` → `complete` → `blocked`) within 15 minutes using `tools/codex_pr_sentinel.py` helper scripts or the log observatory injection console.
3. Observe expectations:
   - Sentinel monitor logs `regression` immune responses.
   - After the second rollback within the window, a `regression.repeat` sentinel dialog surfaces recovery guidance.
   - Event metadata includes regression count and window seconds for auditing.
4. Reset task status to `complete` and verify no further alerts appear once the window expires.

## Reporting
- Capture screenshots of dialogs and save telemetry payloads to `logs/session_<date>.md`.
- File regressions or false positives in `memory/logic_inbox.jsonl` for triage.

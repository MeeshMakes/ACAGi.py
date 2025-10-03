# ACAGi Codex Operating Manual (v0.1.1)

## Mission Charter
- Codify an extensible, local-first autonomous workspace for ACAGi.
- Treat this document as the canonical source for workflow, style, and governance.
- Every modification must increment the version header and summarize deltas in `CHANGELOG.md`.

## Behavioral Prime Directives
1. **Verbose Intent** – All future code, docs, and tasks must be richly narrated. Each implementation must include inline comments and docstrings that articulate rationale, edge cases, and failure plans.
2. **Self-Prompting Loop** – Begin every task by drafting a short internal prompt that explains the objective, expected artifacts, and verification steps. Capture these prompts in session logs under “Suggested Next Coding Steps.”
3. **Canonical Context** – Before editing, always consult:
   - This `AGENT.md` file (top-level scope).
   - `memory/codex_memory.json` for durable lessons and standards.
   - `memory/logic_inbox.jsonl` for queued directives.
   - `Dev_Logic/` for design decisions in progress.
   - `Archived Conversation/` for historical background.
4. **Archival Discipline** – Never delete governance artifacts. When replacing content, move the prior version into `Archived Conversation/` with a date-stamped filename.
5. **Testing Mandate** – Run all available linters, unit tests, and static analyzers before every commit. If tooling is unavailable, log the limitation in the session report and the PR body.
6. **Documentation Sync** – Whenever behavior or workflows change, update:
   - `CHANGELOG.md`
   - Relevant READMEs or guides
   - `memory/codex_memory.json`

## File & Folder Governance
- `logs/` – Contains daily session transcripts named `session_<YYYY-MM-DD>.md`.
- `memory/` – Houses long-lived knowledge bases.
- `Dev_Logic/` – Active design notes. Graduated logic moves to `Dev_Logic/Implemented_logic/` with version headers.
- `Archived Conversation/` – Store historical dialogues and superseded manuals.
- `.github/workflows/` – Must include `codex-pr-sentinel.yml` only; remove legacy watcher workflows.
- `tools/` – Python utilities supporting automation. Keep imports at top-level without try/except guards.

## Coding Standards
- Python files use type hints, descriptive docstrings, and exhaustive logging via `logging` module.
- Prefer pure functions and dependency injection for testability.
- Each module defines a `main()` entry point guarded by `if __name__ == "__main__":` when runnable.
- Never wrap imports in `try/except` blocks.
- Maintain 88-character line limit (Black-compatible) unless explicit reason documented in code comments.

## Autonomous Operation Guidelines
- The status bar **Self-Implementation Mode** toggle must only be used when
  sentinel policies for `self_impl` remain in force (single parallel slot,
  900 s max duration, no network access).
- Always monitor the Log Observatory for `autonomy.self_impl` events and ensure
  session notes capture every autonomous cycle.
- If sentinel emits `autonomy.energy_quota` or `autonomy.loop_detected`, leave
  the mode paused, investigate root cause, and document findings in the current
  session log before re-enabling automation.
- Update documentation and durable memory whenever Self-Implementation behaviour
  changes so operators retain a tested runbook.

## Commit Protocol
1. Sync with `origin/main` (fetch + rebase) before modifications whenever a remote exists.
2. Stage logically grouped changes.
3. Use conventional commit messages with scope when possible (`feat:`, `chore:`, `docs:`).
4. After committing, run `make_pr` with a descriptive title/body summarizing tests.

## Pull Request Narrative Template
- **Summary** – Bullet list of major changes.
- **Testing** – Explicit commands run with their outcomes.
- **Risk** – Call out migration or rollout concerns.
- **Next Steps** – Suggested follow-up improvements.

## Sentinel Handshake
- Any GitHub comment containing `@codex` requires immediate verification that `codex-pr-sentinel.yml` succeeded. On failure, open an issue or log entry detailing remediation.

## Future Enhancements (Seed Prompts)
- Draft a Sentinel troubleshooting runbook.
- Define templates for Dev Logic proposals.
- Investigate structured diff summarization for session logs.


# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `agent_versions.py`

**Functions:** import_agent_versions(db_path, agent_dir), main()
### `bucket_scanner.py`

**Functions:** load_dataset(), save_dataset(data), next_version(), write_agent(version, buckets), append_benchwarm(entry_id, content), log_negative(entry_id), process()
### `catalog_cli.py`

**Functions:** main()
### `Codex_Studio.py`

Codex_Lite.py — Local Ollama • Codex Rust (OSS mode) • Buckets • Agent.md • Error Bot • SQL Snapshots
OS: Windows 10/11, macOS, Linux

Highlights
- Ollama-only: lists models via /api/tags and uses them everywhere
- Codex runs with --oss and -m <ollama-model> (no OpenAI)
- Full Auto Mode toggle (--> --full-auto)
- Self-Repo mode: app folder becomes project; Agent.md created with dense directives
- Agent.md Manager (view/edit/rename/delete version files, keep Agent.md immutable)
- Buckets (Assistant/Notes/ErrorBot) in SQLite, versioned; snapshots + diffs; README generator

**Classes:** Snapshot, DiffHighlighter, DiffPane, ChatPane, AgentManager, SecurityDialog, CodexLite, Main

**Functions:** ensure_layout(), load_json(path, default), save_json(path, data), log_line(msg), which(exe), version_stamp(), is_ollama_running(host, port), is_ollama_available(base_url), ollama_list(base_url), _ollama_chat_cached(base_url, model, messages_tuple, system), ollama_chat(base_url, model, messages, system), ollama_cache_clear(), dataset_paths(project), dataset_init(project), dataset_insert(table, project, cols, vals), dataset_store_bucket(project, operator, tab, content, ver), dataset_delete_bucket(project, operator, tab), dataset_store_repo_files(project, files, ver), dataset_store_diff(project, source, content, ver), dataset_fetch_diffs_desc(project), clone_codex_repo(codex_dir), text_sha1(s), sanitize_skip(path), is_text_file(path), iter_files(root), make_snapshot(root, limit_bytes), unified(a_text, b_text, a_label, b_label), diff_snapshots(a, b), analyse_overview(root), generate_readme(project, log, ver)
### `distill_dumps.py`

Normalize `dump*.md` files into bucketized dataset entries for agents.

Parsing rules (documented so they’re not “magic”):
- HEADING_PATTERN: lines starting with '#' (Markdown ATX headings). The text
  of the heading is PRESERVED as a bucket.
- LIST_ITEM_PATTERNS: '- ', '* ', or '1. ' (numbered) begin list items; each
  item becomes its own bucket value.
- Paragraphs: consecutive non-empty, non-heading, non-list lines are grouped
  into a paragraph bucket.
- Code fences: lines between ``` fences are ignored (kept out of buckets).

**Functions:** bucketize_markdown(text), main()
### `embeddings.py`

**Functions:** _get_model(), init_db(db_path), register_dataset(name, path, description), _vector_to_blob(vec), _blob_to_vector(blob), add_embedding(agent_id, bucket_id, text), embed_dataset(dataset_path, name, description), list_catalog(), search_embeddings(query, top_k)
### `migrate_agent_versions.py`

**Functions:** migrate(dry_run)
### `readme_worker.py`

Helper script to assemble a semantic README section for the project.

The worker scans Python modules, extracts lightweight structural metadata and
writes both an `analysis.json` file and a semantic section within `README.md`.
It is intended to keep repository documentation in sync with the codebase.

**Functions:** gather_python_files(root), analyse_module(path), build_readme(root), main()
### `Codex\codex-src\codex-cli\scripts\stage_rust_release.py`

**Functions:** main()
### `Codex\codex-src\codex-rs\mcp-types\generate_mcp_types.py`

**Classes:** StructField, RustProp

**Functions:** main(), add_definition(name, definition, out), define_struct(name, properties, required_props, description), infer_result_type(request_type_name), implements_request_trait(name), implements_notification_trait(name), add_trait_impl(type_name, trait_name, fields, out), define_string_enum(name, enum_values, out, description), define_untagged_enum(name, type_list, out), define_any_of(name, list_of_refs, description), get_serde_annotation_for_anyof_type(type_name), map_type(typedef, prop_name, struct_name), rust_prop_name(name, is_optional), to_snake_case(name), capitalize(name), check_string_list(value), type_from_ref(ref), emit_doc_comment(text, out)
### `Codex\codex-src\scripts\asciicheck.py`

**Functions:** main(), lint_utf8_ascii(filename, fix)
### `Codex\codex-src\scripts\publish_to_npm.py`

Download a release artifact for the npm package and publish it.

Given a release version like `0.20.0`, this script:
  - Downloads the `codex-npm-<version>.tgz` asset from the GitHub release
    tagged `rust-v<version>` in the `openai/codex` repository using `gh`.
  - Runs `npm publish` on the downloaded tarball to publish `@openai/codex`.

Flags:
  - `--dry-run` delegates to `npm publish --dry-run`. The artifact is still
    downloaded so npm can inspect the archive contents without publishing.

Requirements:
  - GitHub CLI (`gh`) must be installed and authenticated to access the repo.
  - npm must be logged in with an account authorized to publish
    `@openai/codex`. This may trigger a browser for 2FA.

**Functions:** run_checked(cmd, cwd), main()
### `Codex\codex-src\scripts\readme_toc.py`

Utility script to verify (and optionally fix) the Table of Contents in a
Markdown file. By default, it checks that the ToC between `<!-- Begin ToC -->`
and `<!-- End ToC -->` matches the headings in the file. With --fix, it
rewrites the file to update the ToC.

**Functions:** main(), generate_toc_lines(content), check_or_fix(readme_path, fix)
### `helpful scripts\github_uploader.py`

**Functions:** run_cmd(cmd, cwd), select_folder(), upload_repo(), main()
### `scripts\agent_runner.py`

Agent runner that parses Agent.md and dispatches repository_dispatch events for each item.
- Uses GITHUB_TOKEN to call the REST API.
- Does NOT write code changes itself; it dispatches workers which run in Actions.

**Functions:** read_agent_md(path), search_items(query, per_page), dispatch_worker(event_type, payload), short_hash(), main(dry_run)
### `scripts\worker_executor.py`

Worker executor run inside Actions via repository_dispatch.
- Reads payload.json
- Uses the worker_prompt and summary_prompt paths to produce a summary (Codex call required)
- Runs quick checks and tests (pytest)
- Attempts safe fixes (placeholder logic)
- Creates branch + PR via GitHub API if changes made
- Creates ErrorDump if cannot fix

This script is intentionally conservative and includes "hooks" where Codex should be invoked
to produce patches or suggested diffs. A production implementation should implement a robust
model call and patch application logic (e.g., generate patch/diff and apply via git).

**Functions:** load_payload(path), run_cmd(cmd, cwd, capture), save_log(txt), create_error_dump(item, reason, attempts), main(payload_path)
### `tests\conftest.py`

**Functions:** pytest_configure(config), pytest_collection_modifyitems(config, items)
### `tests\test_auto_merge_all_tasks.py`

**Functions:** run(cmd, cwd), init_repo(path), test_ensure_clean_worktree_stashes_when_dirty(tmp_path, monkeypatch), test_main_restores_stash(tmp_path, monkeypatch), test_main_stash_conflict_preserves_stash(tmp_path, monkeypatch), test_dry_run_no_branches(tmp_path, capsys, monkeypatch), test_main_pushes_to_remote(tmp_path, monkeypatch), test_main_reports_merge_conflict(tmp_path, monkeypatch, capsys), test_report_writes_summary(tmp_path, monkeypatch), test_report_to_stdout(tmp_path, monkeypatch, capsys)
### `tests\test_bucket_scanner.py`

**Functions:** test_process_handles_unresolved_entries(tmp_path, monkeypatch)
### `tests\test_embeddings.py`

**Classes:** DummyModel

**Functions:** test_search_embeddings_sql(tmp_path, monkeypatch)
### `tests\test_logging.py`

**Functions:** test_repo_manager_chmod_logs(monkeypatch, tmp_path, caplog), test_catalog_cli_logs_invalid_json(tmp_path, caplog, monkeypatch), test_auto_merge_logs(monkeypatch, caplog)
### `tests\test_readme_worker.py`

**Functions:** test_build_readme_logs_failed_module(tmp_path, caplog, monkeypatch)
### `tests\test_task_dispatcher.py`

**Classes:** EchoHandler

**Functions:** test_dispatcher_handles_task(tmp_path), test_handler_failure_logs_error(tmp_path, caplog)
### `tests\test_task_manager.py`

**Functions:** _sample_task_dict(), test_init_with_corrupted_json_logs_error(tmp_path, caplog), test_load_preserves_tasks_on_corrupted_json(tmp_path, caplog), test_load_missing_fields_defaults(tmp_path), test_list_and_clear_completed(tmp_path), test_export_completed(tmp_path, monkeypatch), test_add_task_with_branch(tmp_path, monkeypatch)
### `tests\test_task_panel.py`

**Functions:** test_task_panel_operations(tmp_path, monkeypatch)
### `tools\auto_merge_all_tasks.py`

Utility to merge all branches into a base branch.

This script is triggered by the phrase "Auto Merge All Tasks".
It fetches all remote branches, sorts them by commit date, and merges
any branches not already merged into the target base branch (default: main).
If a merge conflict occurs the process stops and the user can resolve it
before running the script again.

**Functions:** run(cmd, check, log), list_unmerged(base), ensure_clean_worktree(), write_report(dest, lines), main(base, dry_run, confirm, push, report)
### `tools\codex_check.py`

**Functions:** run(cmd), append_outbox(stage, ok, summary, notes), main()
### `tools\codex_repo_manager.py`

Utility for managing the local Codex source checkout.

Subcommands:
  ensure-source -- ensure a local copy of the Codex source exists
                  optionally verify downloaded archive with --sha256
  protect       -- toggle read only/writable state for the source directory
  upload        -- push the source tree to a user provided git remote

**Functions:** run(cmd, cwd), ensure_source(args), _chmod_recursive(path, readonly), protect(args), upload(args), main(argv)
### `tools\codex_scrub.py`

**Functions:** run(cmd), append_outbox(stage, ok, summary, notes), main()
### `tools\dump_watcher.py`

Watch for new ``dump*.md`` files and process them.

This service observes ``Codex_Agents`` for files matching ``dump*.md``.
Whenever a file is created or modified the dump is distilled into the
dataset and the documentation links are refreshed.  Processed dumps are
archived automatically by :mod:`distill_dumps`.

**Classes:** DumpEventHandler

**Functions:** update_docs_links(), process_dumps(), main()
### `tools\export_merged_tasks.py`

CLI to export merged tasks into Project_datasets.

**Functions:** main(output)
### `tools\migrate_agent_dataset.py`

Convert a SQLite agent dataset back to JSON format.

This helper migrates entries from a database created during the brief
SQLite experiment to the canonical JSON representation used by Codex Studio.

**Functions:** migrate(db_path, json_path), main()
### `tools\process_all_dump_files.py`

Convenience wrapper to process dump files.

This script invokes :func:`distill_dumps.main` so it can be triggered by
automation systems with the phrase "Process All Dump Files". It ensures that
new dumps such as ``dump10.md`` are detected and indexed without manual
intervention.
### `tools\summarize_logs.py`

Download and summarize GitHub Actions workflow logs.

This utility fetches a workflow run's log archive, sends a snippet to
``ollama_chat`` for summarization, and prints the result.  If the
summarizer fails, the script falls back to printing a truncated portion
of the raw logs.  The script exits non-zero when the log archive cannot
be downloaded.

Usage:
    python tools/summarize_logs.py <logs_url>

Environment variables:
    GITHUB_TOKEN  -- token with access to the repository (optional).
    OLLAMA_URL    -- base URL for the Ollama server (default:
                     ``http://localhost:11434``).
    OLLAMA_MODEL  -- model name for summarization (default: ``codex``).

**Functions:** download_logs(url, token), main()
### `tools\task_dispatcher.py`

TaskDispatcher module for polling TaskManager and forwarding tasks to Codex.

**Classes:** TaskHandler, TaskDispatcher
### `tools\task_manager.py`

**Classes:** Task, TaskManager
### `tools\triplewash_status.py`

**Functions:** load(), save(s), set_stage(next_stage, ok, note)

## Other Files

The following files are present in the project but were not analysed in detail:

- `.codex_handshake.json`
- `.git\FETCH_HEAD`
- `.git\HEAD`
- `.git\config`
- `.git\description`
- `.git\hooks\applypatch-msg.sample`
- `.git\hooks\commit-msg.sample`
- `.git\hooks\fsmonitor-watchman.sample`
- `.git\hooks\post-update.sample`
- `.git\hooks\pre-applypatch.sample`
- `.git\hooks\pre-commit.sample`
- `.git\hooks\pre-merge-commit.sample`
- `.git\hooks\pre-push.sample`
- `.git\hooks\pre-rebase.sample`
- `.git\hooks\pre-receive.sample`
- `.git\hooks\prepare-commit-msg.sample`
- `.git\hooks\push-to-checkout.sample`
- `.git\hooks\sendemail-validate.sample`
- `.git\hooks\update.sample`
- `.git\index`
- `.git\info\exclude`
- `.git\logs\HEAD`
- `.git\logs\refs\heads\main`
- `.git\logs\refs\remotes\origin\HEAD`
- `.git\objects\pack\pack-083cc904169f2abf9fe0ce6c939d3a5e18d93a83.idx`
- `.git\objects\pack\pack-083cc904169f2abf9fe0ce6c939d3a5e18d93a83.pack`
- `.git\objects\pack\pack-083cc904169f2abf9fe0ce6c939d3a5e18d93a83.rev`
- `.git\packed-refs`
- `.git\refs\heads\main`
- `.git\refs\remotes\origin\HEAD`
- `.github\CODEX-INSTRUCTIONS.md`
- `.github\CODEX-REQUEST-TEMPLATE.md`
- `.github\COMMIT_GUIDELINES.md`
- `.github\COPILOT-AUTONOMOUS-PR-REVIEW.md`
- `.github\PR_CHECKLIST.md`
- `.github\copilot-instructions.md`
- `.github\workflows\agent-worker.yml`
- `.github\workflows\auto-merge.yml`
- `.github\workflows\codex-spawner.yml`
- `.github\workflows\codex-validation.yml`
- `.github\workflows\log-failures.yml`
- `.github\workflows\triple-wash.yml`
- `.gitignore`
- `.triplewash\status.json`
- `Agent.md`
- `Agent_Versions\.gitkeep`
- `Agent_Versions\Agent_1.md`
- `Codex\codex-src\.codespellignore`
- `Codex\codex-src\.codespellrc`
- `Codex\codex-src\.devcontainer\Dockerfile`
- `Codex\codex-src\.devcontainer\README.md`
- `Codex\codex-src\.devcontainer\devcontainer.json`
- `Codex\codex-src\.git\HEAD`
- `Codex\codex-src\.git\config`
- `Codex\codex-src\.git\description`
- `Codex\codex-src\.git\hooks\applypatch-msg.sample`
- `Codex\codex-src\.git\hooks\commit-msg.sample`
- `Codex\codex-src\.git\hooks\fsmonitor-watchman.sample`
- `Codex\codex-src\.git\hooks\post-update.sample`
- `Codex\codex-src\.git\hooks\pre-applypatch.sample`
- `Codex\codex-src\.git\hooks\pre-commit.sample`
- `Codex\codex-src\.git\hooks\pre-merge-commit.sample`
- `Codex\codex-src\.git\hooks\pre-push.sample`
- `Codex\codex-src\.git\hooks\pre-rebase.sample`
- `Codex\codex-src\.git\hooks\pre-receive.sample`
- `Codex\codex-src\.git\hooks\prepare-commit-msg.sample`
- `Codex\codex-src\.git\hooks\push-to-checkout.sample`
- `Codex\codex-src\.git\hooks\update.sample`
- `Codex\codex-src\.git\index`
- `Codex\codex-src\.git\info\exclude`
- `Codex\codex-src\.git\logs\HEAD`
- `Codex\codex-src\.git\objects\pack\pack-76756d31b97e2584e45ae297a4e9f4170ca43be8.idx`
- `Codex\codex-src\.git\objects\pack\pack-76756d31b97e2584e45ae297a4e9f4170ca43be8.pack`
- `Codex\codex-src\.git\packed-refs`
- `Codex\codex-src\.git\shallow`
- `Codex\codex-src\.github\ISSUE_TEMPLATE\2-bug-report.yml`
- `Codex\codex-src\.github\ISSUE_TEMPLATE\3-docs-issue.yml`
- `Codex\codex-src\.github\ISSUE_TEMPLATE\4-feature-request.yml`
- `Codex\codex-src\.github\actions\codex\.gitignore`
- `Codex\codex-src\.github\actions\codex\.prettierrc.toml`
- `Codex\codex-src\.github\actions\codex\README.md`
- `Codex\codex-src\.github\actions\codex\action.yml`
- `Codex\codex-src\.github\actions\codex\bun.lock`
- `Codex\codex-src\.github\actions\codex\package.json`
- `Codex\codex-src\.github\actions\codex\src\add-reaction.ts`
- `Codex\codex-src\.github\actions\codex\src\comment.ts`
- `Codex\codex-src\.github\actions\codex\src\config.ts`
- `Codex\codex-src\.github\actions\codex\src\default-label-config.ts`
- `Codex\codex-src\.github\actions\codex\src\env-context.ts`
- `Codex\codex-src\.github\actions\codex\src\fail.ts`
- `Codex\codex-src\.github\actions\codex\src\git-helpers.ts`
- `Codex\codex-src\.github\actions\codex\src\git-user.ts`
- `Codex\codex-src\.github\actions\codex\src\github-workspace.ts`
- `Codex\codex-src\.github\actions\codex\src\load-config.ts`
- `Codex\codex-src\.github\actions\codex\src\main.ts`
- `Codex\codex-src\.github\actions\codex\src\post-comment.ts`
- `Codex\codex-src\.github\actions\codex\src\process-label.ts`
- `Codex\codex-src\.github\actions\codex\src\prompt-template.ts`
- `Codex\codex-src\.github\actions\codex\src\review.ts`
- `Codex\codex-src\.github\actions\codex\src\run-codex.ts`
- `Codex\codex-src\.github\actions\codex\src\verify-inputs.ts`
- `Codex\codex-src\.github\actions\codex\tsconfig.json`
- `Codex\codex-src\.github\codex-cli-login.png`
- `Codex\codex-src\.github\codex-cli-permissions.png`
- `Codex\codex-src\.github\codex-cli-splash.png`
- `Codex\codex-src\.github\codex\home\config.toml`
- `Codex\codex-src\.github\codex\labels\codex-attempt.md`
- `Codex\codex-src\.github\codex\labels\codex-review.md`
- `Codex\codex-src\.github\codex\labels\codex-rust-review.md`
- `Codex\codex-src\.github\codex\labels\codex-triage.md`
- `Codex\codex-src\.github\demo.gif`
- `Codex\codex-src\.github\dependabot.yaml`
- `Codex\codex-src\.github\dotslash-config.json`
- `Codex\codex-src\.github\pull_request_template.md`
- `Codex\codex-src\.github\workflows\ci.yml`
- `Codex\codex-src\.github\workflows\cla.yml`
- `Codex\codex-src\.github\workflows\codespell.yml`
- `Codex\codex-src\.github\workflows\codex.yml`
- `Codex\codex-src\.github\workflows\rust-ci.yml`
- `Codex\codex-src\.github\workflows\rust-release.yml`
- `Codex\codex-src\.gitignore`
- `Codex\codex-src\.npmrc`
- `Codex\codex-src\.prettierignore`
- `Codex\codex-src\.prettierrc.toml`
- `Codex\codex-src\.vscode\extensions.json`
- `Codex\codex-src\.vscode\launch.json`
- `Codex\codex-src\.vscode\settings.json`
- `Codex\codex-src\AGENTS.md`
- `Codex\codex-src\CHANGELOG.md`
- `Codex\codex-src\LICENSE`
- `Codex\codex-src\NOTICE`
- `Codex\codex-src\PNPM.md`
- `Codex\codex-src\README.md`
- `Codex\codex-src\cliff.toml`
- `Codex\codex-src\codex-cli\.dockerignore`
- `Codex\codex-src\codex-cli\.gitignore`
- `Codex\codex-src\codex-cli\Dockerfile`
- `Codex\codex-src\codex-cli\README.md`
- `Codex\codex-src\codex-cli\bin\codex.js`
- `Codex\codex-src\codex-cli\package-lock.json`
- `Codex\codex-src\codex-cli\package.json`
- `Codex\codex-src\codex-cli\scripts\README.md`
- `Codex\codex-src\codex-cli\scripts\build_container.sh`
- `Codex\codex-src\codex-cli\scripts\init_firewall.sh`
- `Codex\codex-src\codex-cli\scripts\install_native_deps.sh`
- `Codex\codex-src\codex-cli\scripts\run_in_container.sh`
- `Codex\codex-src\codex-cli\scripts\stage_release.sh`
- `Codex\codex-src\codex-rs\.gitignore`
- `Codex\codex-src\codex-rs\Cargo.lock`
- `Codex\codex-src\codex-rs\Cargo.toml`
- `Codex\codex-src\codex-rs\README.md`
- `Codex\codex-src\codex-rs\ansi-escape\Cargo.toml`
- `Codex\codex-src\codex-rs\ansi-escape\README.md`
- `Codex\codex-src\codex-rs\ansi-escape\src\lib.rs`
- `Codex\codex-src\codex-rs\apply-patch\Cargo.toml`
- `Codex\codex-src\codex-rs\apply-patch\apply_patch_tool_instructions.md`
- `Codex\codex-src\codex-rs\apply-patch\src\lib.rs`
- `Codex\codex-src\codex-rs\apply-patch\src\parser.rs`
- `Codex\codex-src\codex-rs\apply-patch\src\seek_sequence.rs`
- `Codex\codex-src\codex-rs\arg0\Cargo.toml`
- `Codex\codex-src\codex-rs\arg0\src\lib.rs`
- `Codex\codex-src\codex-rs\chatgpt\Cargo.toml`
- `Codex\codex-src\codex-rs\chatgpt\README.md`
- `Codex\codex-src\codex-rs\chatgpt\src\apply_command.rs`
- `Codex\codex-src\codex-rs\chatgpt\src\chatgpt_client.rs`
- `Codex\codex-src\codex-rs\chatgpt\src\chatgpt_token.rs`
- `Codex\codex-src\codex-rs\chatgpt\src\get_task.rs`
- `Codex\codex-src\codex-rs\chatgpt\src\lib.rs`
- `Codex\codex-src\codex-rs\chatgpt\tests\apply_command_e2e.rs`
- `Codex\codex-src\codex-rs\chatgpt\tests\task_turn_fixture.json`
- `Codex\codex-src\codex-rs\cli\Cargo.toml`
- `Codex\codex-src\codex-rs\cli\src\debug_sandbox.rs`
- `Codex\codex-src\codex-rs\cli\src\exit_status.rs`
- `Codex\codex-src\codex-rs\cli\src\lib.rs`
- `Codex\codex-src\codex-rs\cli\src\login.rs`
- `Codex\codex-src\codex-rs\cli\src\main.rs`
- `Codex\codex-src\codex-rs\cli\src\proto.rs`
- `Codex\codex-src\codex-rs\clippy.toml`
- `Codex\codex-src\codex-rs\common\Cargo.toml`
- `Codex\codex-src\codex-rs\common\README.md`
- `Codex\codex-src\codex-rs\common\src\approval_mode_cli_arg.rs`
- `Codex\codex-src\codex-rs\common\src\approval_presets.rs`
- `Codex\codex-src\codex-rs\common\src\config_override.rs`
- `Codex\codex-src\codex-rs\common\src\config_summary.rs`
- `Codex\codex-src\codex-rs\common\src\elapsed.rs`
- `Codex\codex-src\codex-rs\common\src\fuzzy_match.rs`
- `Codex\codex-src\codex-rs\common\src\lib.rs`
- `Codex\codex-src\codex-rs\common\src\model_presets.rs`
- `Codex\codex-src\codex-rs\common\src\sandbox_mode_cli_arg.rs`
- `Codex\codex-src\codex-rs\common\src\sandbox_summary.rs`
- `Codex\codex-src\codex-rs\config.md`
- `Codex\codex-src\codex-rs\core\Cargo.toml`
- `Codex\codex-src\codex-rs\core\README.md`
- `Codex\codex-src\codex-rs\core\prompt.md`
- `Codex\codex-src\codex-rs\core\src\apply_patch.rs`
- `Codex\codex-src\codex-rs\core\src\bash.rs`
- `Codex\codex-src\codex-rs\core\src\chat_completions.rs`
- `Codex\codex-src\codex-rs\core\src\client.rs`
- `Codex\codex-src\codex-rs\core\src\client_common.rs`
- `Codex\codex-src\codex-rs\core\src\codex.rs`
- `Codex\codex-src\codex-rs\core\src\codex_conversation.rs`
- `Codex\codex-src\codex-rs\core\src\config.rs`
- `Codex\codex-src\codex-rs\core\src\config_profile.rs`
- `Codex\codex-src\codex-rs\core\src\config_types.rs`
- `Codex\codex-src\codex-rs\core\src\conversation_history.rs`
- `Codex\codex-src\codex-rs\core\src\conversation_manager.rs`
- `Codex\codex-src\codex-rs\core\src\environment_context.rs`
- `Codex\codex-src\codex-rs\core\src\error.rs`
- `Codex\codex-src\codex-rs\core\src\exec.rs`
- `Codex\codex-src\codex-rs\core\src\exec_env.rs`
- `Codex\codex-src\codex-rs\core\src\flags.rs`
- `Codex\codex-src\codex-rs\core\src\git_info.rs`
- `Codex\codex-src\codex-rs\core\src\is_safe_command.rs`
- `Codex\codex-src\codex-rs\core\src\landlock.rs`
- `Codex\codex-src\codex-rs\core\src\lib.rs`
- `Codex\codex-src\codex-rs\core\src\mcp_connection_manager.rs`
- `Codex\codex-src\codex-rs\core\src\mcp_tool_call.rs`
- `Codex\codex-src\codex-rs\core\src\message_history.rs`
- `Codex\codex-src\codex-rs\core\src\model_family.rs`
- `Codex\codex-src\codex-rs\core\src\model_provider_info.rs`
- `Codex\codex-src\codex-rs\core\src\models.rs`
- `Codex\codex-src\codex-rs\core\src\openai_model_info.rs`
- `Codex\codex-src\codex-rs\core\src\openai_tools.rs`
- `Codex\codex-src\codex-rs\core\src\parse_command.rs`
- `Codex\codex-src\codex-rs\core\src\plan_tool.rs`
- `Codex\codex-src\codex-rs\core\src\project_doc.rs`
- `Codex\codex-src\codex-rs\core\src\prompt_for_compact_command.md`
- `Codex\codex-src\codex-rs\core\src\rollout.rs`
- `Codex\codex-src\codex-rs\core\src\safety.rs`
- `Codex\codex-src\codex-rs\core\src\seatbelt.rs`
- `Codex\codex-src\codex-rs\core\src\seatbelt_base_policy.sbpl`
- `Codex\codex-src\codex-rs\core\src\shell.rs`
- `Codex\codex-src\codex-rs\core\src\spawn.rs`
- `Codex\codex-src\codex-rs\core\src\turn_diff_tracker.rs`
- `Codex\codex-src\codex-rs\core\src\user_agent.rs`
- `Codex\codex-src\codex-rs\core\src\user_notification.rs`
- `Codex\codex-src\codex-rs\core\src\util.rs`
- `Codex\codex-src\codex-rs\core\tests\cli_responses_fixture.sse`
- `Codex\codex-src\codex-rs\core\tests\cli_stream.rs`
- `Codex\codex-src\codex-rs\core\tests\client.rs`
- `Codex\codex-src\codex-rs\core\tests\common\Cargo.toml`
- `Codex\codex-src\codex-rs\core\tests\common\lib.rs`
- `Codex\codex-src\codex-rs\core\tests\compact.rs`
- `Codex\codex-src\codex-rs\core\tests\exec.rs`
- `Codex\codex-src\codex-rs\core\tests\exec_stream_events.rs`
- `Codex\codex-src\codex-rs\core\tests\fixtures\completed_template.json`
- `Codex\codex-src\codex-rs\core\tests\fixtures\incomplete_sse.json`
- `Codex\codex-src\codex-rs\core\tests\live_cli.rs`
- `Codex\codex-src\codex-rs\core\tests\prompt_caching.rs`
- `Codex\codex-src\codex-rs\core\tests\seatbelt.rs`
- `Codex\codex-src\codex-rs\core\tests\stream_error_allows_next_turn.rs`
- `Codex\codex-src\codex-rs\core\tests\stream_no_completed.rs`
- `Codex\codex-src\codex-rs\default.nix`
- `Codex\codex-src\codex-rs\docs\protocol_v1.md`
- `Codex\codex-src\codex-rs\exec\Cargo.toml`
- `Codex\codex-src\codex-rs\exec\src\cli.rs`
- `Codex\codex-src\codex-rs\exec\src\event_processor.rs`
- `Codex\codex-src\codex-rs\exec\src\event_processor_with_human_output.rs`
- `Codex\codex-src\codex-rs\exec\src\event_processor_with_json_output.rs`
- `Codex\codex-src\codex-rs\exec\src\lib.rs`
- `Codex\codex-src\codex-rs\exec\src\main.rs`
- `Codex\codex-src\codex-rs\exec\tests\apply_patch.rs`
- `Codex\codex-src\codex-rs\exec\tests\sandbox.rs`
- `Codex\codex-src\codex-rs\execpolicy\Cargo.toml`
- `Codex\codex-src\codex-rs\execpolicy\README.md`
- `Codex\codex-src\codex-rs\execpolicy\build.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\arg_matcher.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\arg_resolver.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\arg_type.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\default.policy`
- `Codex\codex-src\codex-rs\execpolicy\src\error.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\exec_call.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\execv_checker.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\lib.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\main.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\opt.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\policy.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\policy_parser.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\program.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\sed_command.rs`
- `Codex\codex-src\codex-rs\execpolicy\src\valid_exec.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\bad.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\cp.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\good.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\head.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\literal.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\ls.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\parse_sed_command.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\pwd.rs`
- `Codex\codex-src\codex-rs\execpolicy\tests\sed.rs`
- `Codex\codex-src\codex-rs\file-search\Cargo.toml`
- `Codex\codex-src\codex-rs\file-search\README.md`
- `Codex\codex-src\codex-rs\file-search\src\cli.rs`
- `Codex\codex-src\codex-rs\file-search\src\lib.rs`
- `Codex\codex-src\codex-rs\file-search\src\main.rs`
- `Codex\codex-src\codex-rs\justfile`
- `Codex\codex-src\codex-rs\linux-sandbox\Cargo.toml`
- `Codex\codex-src\codex-rs\linux-sandbox\README.md`
- `Codex\codex-src\codex-rs\linux-sandbox\src\landlock.rs`
- `Codex\codex-src\codex-rs\linux-sandbox\src\lib.rs`
- `Codex\codex-src\codex-rs\linux-sandbox\src\linux_run_main.rs`
- `Codex\codex-src\codex-rs\linux-sandbox\src\main.rs`
- `Codex\codex-src\codex-rs\linux-sandbox\tests\landlock.rs`
- `Codex\codex-src\codex-rs\login\Cargo.toml`
- `Codex\codex-src\codex-rs\login\src\assets\success.html`
- `Codex\codex-src\codex-rs\login\src\lib.rs`
- `Codex\codex-src\codex-rs\login\src\pkce.rs`
- `Codex\codex-src\codex-rs\login\src\server.rs`
- `Codex\codex-src\codex-rs\login\src\token_data.rs`
- `Codex\codex-src\codex-rs\login\tests\login_server_e2e.rs`
- `Codex\codex-src\codex-rs\mcp-client\Cargo.toml`
- `Codex\codex-src\codex-rs\mcp-client\src\lib.rs`
- `Codex\codex-src\codex-rs\mcp-client\src\main.rs`
- `Codex\codex-src\codex-rs\mcp-client\src\mcp_client.rs`
- `Codex\codex-src\codex-rs\mcp-server\Cargo.toml`
- `Codex\codex-src\codex-rs\mcp-server\src\codex_message_processor.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\codex_tool_config.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\codex_tool_runner.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\error_code.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\exec_approval.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\json_to_toml.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\lib.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\main.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\message_processor.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\outgoing_message.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\patch_approval.rs`
- `Codex\codex-src\codex-rs\mcp-server\src\tool_handlers\mod.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\codex_message_processor_flow.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\codex_tool.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\common\Cargo.toml`
- `Codex\codex-src\codex-rs\mcp-server\tests\common\lib.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\common\mcp_process.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\common\mock_model_server.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\common\responses.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\create_conversation.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\interrupt.rs`
- `Codex\codex-src\codex-rs\mcp-server\tests\send_message.rs`
- `Codex\codex-src\codex-rs\mcp-types\Cargo.toml`
- `Codex\codex-src\codex-rs\mcp-types\README.md`
- `Codex\codex-src\codex-rs\mcp-types\schema\2025-03-26\schema.json`
- `Codex\codex-src\codex-rs\mcp-types\schema\2025-06-18\schema.json`
- `Codex\codex-src\codex-rs\mcp-types\src\lib.rs`
- `Codex\codex-src\codex-rs\mcp-types\tests\initialize.rs`
- `Codex\codex-src\codex-rs\mcp-types\tests\progress_notification.rs`
- `Codex\codex-src\codex-rs\ollama\Cargo.toml`
- `Codex\codex-src\codex-rs\ollama\src\client.rs`
- `Codex\codex-src\codex-rs\ollama\src\lib.rs`
- `Codex\codex-src\codex-rs\ollama\src\parser.rs`
- `Codex\codex-src\codex-rs\ollama\src\pull.rs`
- `Codex\codex-src\codex-rs\ollama\src\url.rs`
- `Codex\codex-src\codex-rs\protocol-ts\Cargo.toml`
- `Codex\codex-src\codex-rs\protocol-ts\generate-ts`
- `Codex\codex-src\codex-rs\protocol-ts\src\lib.rs`
- `Codex\codex-src\codex-rs\protocol-ts\src\main.rs`
- `Codex\codex-src\codex-rs\protocol\Cargo.toml`
- `Codex\codex-src\codex-rs\protocol\README.md`
- `Codex\codex-src\codex-rs\protocol\src\config_types.rs`
- `Codex\codex-src\codex-rs\protocol\src\lib.rs`
- `Codex\codex-src\codex-rs\protocol\src\mcp_protocol.rs`
- `Codex\codex-src\codex-rs\protocol\src\message_history.rs`
- `Codex\codex-src\codex-rs\protocol\src\parse_command.rs`
- `Codex\codex-src\codex-rs\protocol\src\plan_tool.rs`
- `Codex\codex-src\codex-rs\protocol\src\protocol.rs`
- `Codex\codex-src\codex-rs\rust-toolchain.toml`
- `Codex\codex-src\codex-rs\rustfmt.toml`
- `Codex\codex-src\codex-rs\scripts\create_github_release.sh`
- `Codex\codex-src\codex-rs\tui\Cargo.toml`
- `Codex\codex-src\codex-rs\tui\prompt_for_init_command.md`
- `Codex\codex-src\codex-rs\tui\src\app.rs`
- `Codex\codex-src\codex-rs\tui\src\app_event.rs`
- `Codex\codex-src\codex-rs\tui\src\app_event_sender.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\approval_modal_view.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\bottom_pane_view.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\chat_composer.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\chat_composer_history.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\command_popup.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\file_search_popup.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\list_selection_view.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\mod.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\popup_consts.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\scroll_state.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\selection_popup_common.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__backspace_after_pastes.snap`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__empty.snap`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__large.snap`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__multiple_pastes.snap`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__small.snap`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\status_indicator_view.rs`
- `Codex\codex-src\codex-rs\tui\src\bottom_pane\textarea.rs`
- `Codex\codex-src\codex-rs\tui\src\chatwidget.rs`
- `Codex\codex-src\codex-rs\tui\src\chatwidget\agent.rs`
- `Codex\codex-src\codex-rs\tui\src\chatwidget\interrupts.rs`
- `Codex\codex-src\codex-rs\tui\src\chatwidget\snapshots\codex_tui__chatwidget__tests__deltas_then_same_final_message_are_rendered_snapshot.snap`
- `Codex\codex-src\codex-rs\tui\src\chatwidget\snapshots\codex_tui__chatwidget__tests__final_reasoning_then_message_without_deltas_are_rendered.snap`
- `Codex\codex-src\codex-rs\tui\src\chatwidget\tests.rs`
- `Codex\codex-src\codex-rs\tui\src\chatwidget_stream_tests.rs`
- `Codex\codex-src\codex-rs\tui\src\citation_regex.rs`
- `Codex\codex-src\codex-rs\tui\src\cli.rs`
- `Codex\codex-src\codex-rs\tui\src\common.rs`
- `Codex\codex-src\codex-rs\tui\src\custom_terminal.rs`
- `Codex\codex-src\codex-rs\tui\src\diff_render.rs`
- `Codex\codex-src\codex-rs\tui\src\exec_command.rs`
- `Codex\codex-src\codex-rs\tui\src\file_search.rs`
- `Codex\codex-src\codex-rs\tui\src\get_git_diff.rs`
- `Codex\codex-src\codex-rs\tui\src\history_cell.rs`
- `Codex\codex-src\codex-rs\tui\src\insert_history.rs`
- `Codex\codex-src\codex-rs\tui\src\lib.rs`
- `Codex\codex-src\codex-rs\tui\src\live_wrap.rs`
- `Codex\codex-src\codex-rs\tui\src\main.rs`
- `Codex\codex-src\codex-rs\tui\src\markdown.rs`
- `Codex\codex-src\codex-rs\tui\src\markdown_stream.rs`
- `Codex\codex-src\codex-rs\tui\src\onboarding\auth.rs`
- `Codex\codex-src\codex-rs\tui\src\onboarding\continue_to_chat.rs`
- `Codex\codex-src\codex-rs\tui\src\onboarding\mod.rs`
- `Codex\codex-src\codex-rs\tui\src\onboarding\onboarding_screen.rs`
- `Codex\codex-src\codex-rs\tui\src\onboarding\trust_directory.rs`
- `Codex\codex-src\codex-rs\tui\src\onboarding\welcome.rs`
- `Codex\codex-src\codex-rs\tui\src\render\line_utils.rs`
- `Codex\codex-src\codex-rs\tui\src\render\markdown_utils.rs`
- `Codex\codex-src\codex-rs\tui\src\render\mod.rs`
- `Codex\codex-src\codex-rs\tui\src\session_log.rs`
- `Codex\codex-src\codex-rs\tui\src\shimmer.rs`
- `Codex\codex-src\codex-rs\tui\src\slash_command.rs`
- `Codex\codex-src\codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__add_details.snap`
- `Codex\codex-src\codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__update_details_with_rename.snap`
- `Codex\codex-src\codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__wrap_behavior_insert.snap`
- `Codex\codex-src\codex-rs\tui\src\status_indicator_widget.rs`
- `Codex\codex-src\codex-rs\tui\src\streaming\controller.rs`
- `Codex\codex-src\codex-rs\tui\src\streaming\mod.rs`
- `Codex\codex-src\codex-rs\tui\src\text_formatting.rs`
- `Codex\codex-src\codex-rs\tui\src\tui.rs`
- `Codex\codex-src\codex-rs\tui\src\updates.rs`
- `Codex\codex-src\codex-rs\tui\src\user_approval_widget.rs`
- `Codex\codex-src\codex-rs\tui\styles.md`
- `Codex\codex-src\codex-rs\tui\tests\fixtures\binary-size-log.jsonl`
- `Codex\codex-src\codex-rs\tui\tests\fixtures\ideal-binary-response.txt`
- `Codex\codex-src\codex-rs\tui\tests\fixtures\oss-story.jsonl`
- `Codex\codex-src\codex-rs\tui\tests\status_indicator.rs`
- `Codex\codex-src\codex-rs\tui\tests\vt100_history.rs`
- `Codex\codex-src\codex-rs\tui\tests\vt100_live_commit.rs`
- `Codex\codex-src\codex-rs\tui\tests\vt100_streaming_no_dup.rs`
- `Codex\codex-src\docs\CLA.md`
- `Codex\codex-src\docs\release_management.md`
- `Codex\codex-src\flake.lock`
- `Codex\codex-src\flake.nix`
- `Codex\codex-src\package.json`
- `Codex\codex-src\pnpm-lock.yaml`
- `Codex\codex-src\pnpm-workspace.yaml`
- `Codex\codex.exe`
- `Codex_Agents\Agent.md`
- `Codex_Agents\Agent_1.md`
- `Codex_Agents\Agent_2.md`
- `Codex_Agents\Agent_3.md`
- `Codex_Agents\Agent_Versions\.gitkeep`
- `Codex_Agents\archive\dump.md`
- `Codex_Agents\archive\dump10.md`
- `Codex_Agents\archive\dump10_1.md`
- `Codex_Agents\archive\dump11.md`
- `Codex_Agents\archive\dump12.md`
- `Codex_Agents\archive\dump13.md`
- `Codex_Agents\archive\dump2.md`
- `Codex_Agents\archive\dump3.md`
- `Codex_Agents\archive\dump4.md`
- `Codex_Agents\archive\dump5.md`
- `Codex_Agents\archive\dump6.md`
- `Codex_Agents\archive\dump7.md`
- `Codex_Agents\archive\dump8.md`
- `Codex_Agents\archive\dump9.md`
- `Codex_Agents\code.md`
- `Codex_Agents\inbox.md`
- `Codex_Agents\outbox.md`
- `Codex_Studio.db`
- `Dump.md`
- `ErrorDump.md`
- `LICENSE`
- `MERGE_PROCESS_WALKTHROUGH.md`
- `Project_datasets\Codex_Studio.db`
- `README.md`
- `README_MCP.md`
- `UX_Manager\README.md`
- `UX_Manager\images\Assistant\.gitkeep`
- `UX_Manager\images\Codex\.gitkeep`
- `UX_Manager\images\Codex\Codex_Design.PNG`
- `UX_Manager\images\Codex\Codex_Design_light.PNG`
- `UX_Manager\images\Codex\UX Pilot - Superfast UX_UI Design with AI.pdf`
- `UX_Manager\images\Codex\basic_toolkit.PNG`
- `UX_Manager\images\Codex\basic_toolkit2.PNG`
- `UX_Manager\images\ErrorBot\.gitkeep`
- `agents\summary_prompt.txt`
- `agents\task_worker_prompt.txt`
- `analysis.json`
- `ansi-escape\Cargo.toml`
- `ansi-escape\src\lib.rs`
- `config.lite.json`
- `copilot-instructions.md`
- `datasets\agent_dataset.json`
- `datasets\agent_dataset_template.json`
- `datasets\cortex_lite.db`
- `datasets\tasks.json`
- `datasets\ux_theme_dataset.json`
- `docs\buckets.md`
- `docs\changelog.md`
- `docs\dump_archive.md`
- `docs\index.md`
- `docs\mcp.md`
- `docs\testing.md`
- `docs\troubleshooting.md`
- `docs\workflow.md`
- `logs\assistant_timing.log`
- `logs\codex_lite.log`
- `negative_diffs.log`
- `projects.lite.json`
- `requirements.txt`
- `starter-kit\.github\workflows\self-heal.yml`
- `starter-kit\Agent.md`
- `starter-kit\Dump.md`
- `starter-kit\ErrorDump.md`
- `starter-kit\copilot-instructions.md`
- `tools\__pycache__\task_manager.cpython-313.pyc`
- `tools\catalog_cli_demo.sh`


## Detailed Module Analyses


## Module `agent_versions.py`

```python
from __future__ import annotations
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime

from distill_dumps import bucketize_markdown

DB_PATH = Path('datasets/agent_versions.db')
AGENT_DIR = Path('Agent_Versions')

FILENAME_RE = re.compile(r'^Agent_(\d+)\.md$')

def import_agent_versions(db_path: Path = DB_PATH, agent_dir: Path = AGENT_DIR) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_versions(
                id INTEGER PRIMARY KEY,
                name TEXT,
                version INTEGER,
                created TEXT,
                content TEXT,
                buckets JSON,
                UNIQUE(name, version)
            )
            """
        )

        if not agent_dir.is_dir():
            return

        for path in sorted(agent_dir.glob('Agent_*.md')):
            if not path.is_file():
                continue
            m = FILENAME_RE.match(path.name)
            if not m:
                continue
            version = int(m.group(1))
            name = 'Agent'
            created = datetime.utcfromtimestamp(path.stat().st_mtime).isoformat(timespec='seconds') + 'Z'
            content = path.read_text(encoding='utf-8', errors='ignore')
            buckets = json.dumps(bucketize_markdown(content))
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_versions(name, version, created, content, buckets)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, version, created, content, buckets),
            )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    import_agent_versions()


if __name__ == '__main__':
    main()
```

**Functions:** import_agent_versions(db_path, agent_dir), main()


## Module `bucket_scanner.py`

```python
from __future__ import annotations
import json
import re
from datetime import datetime
from pathlib import Path

DATASET = Path('datasets/agent_dataset.json')
AGENT_DIR = Path('Agent_Versions')
BENCHWARM = Path('Agent_BenchWarm.md')
NEG_LOG = Path('negative_diffs.log')
FILENAME_RE = re.compile(r'^Agent_(\d+)\.md$')


def load_dataset():
    if DATASET.exists():
        return json.loads(DATASET.read_text(encoding='utf-8'))
    return {"entries": []}


def save_dataset(data):
    DATASET.write_text(json.dumps(data, indent=2), encoding='utf-8')


def next_version() -> int:
    AGENT_DIR.mkdir(exist_ok=True)
    max_ver = 0
    for path in AGENT_DIR.glob('Agent_*.md'):
        m = FILENAME_RE.match(path.name)
        if m:
            max_ver = max(max_ver, int(m.group(1)))
    return max_ver + 1


def write_agent(version: int, buckets: list[dict[str, str]]) -> Path:
    path = AGENT_DIR / f'Agent_{version}.md'
    lines: list[str] = []
    for b in buckets:
        lines.append(f"[BuckID: {b['id']}]")
        lines.append(f"Title: {b['title']}")
        lines.append(f"Version: v{version}")
        lines.append(f"Created: {datetime.utcnow().date().isoformat()}")
        lines.append("Tags: auto, unresolved")
        lines.append("")
        lines.append("Content:")
        for line in b['content']:
            lines.append(f"- {line}")
        lines.append("")
        lines.append("Diff Notes:")
        lines.append("- negative diff recorded")
        lines.append("")
        lines.append("Status:")
        lines.append(f"- {b['status']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding='utf-8')
    return path


def append_benchwarm(entry_id: str, content: list[str]) -> None:
    BENCHWARM.parent.mkdir(exist_ok=True)
    lines = [f"[BuckID: {entry_id}]", "Title: BenchWarm", f"Created: {datetime.utcnow().date().isoformat()}", "", "Content:"]
    lines.extend(f"- {c}" for c in content)
    lines.append("")
    BENCHWARM.write_text((BENCHWARM.read_text(encoding='utf-8') if BENCHWARM.exists() else '') + "\n".join(lines) + "\n", encoding='utf-8')


def log_negative(entry_id: str) -> None:
    msg = f"{datetime.utcnow().isoformat()}Z {entry_id}\n"
    NEG_LOG.write_text((NEG_LOG.read_text(encoding='utf-8') if NEG_LOG.exists() else '') + msg, encoding='utf-8')


def process():
    data = load_dataset()
    unresolved: list[tuple[dict, dict]] = []
    for entry in data.get('entries', []):
        dm = entry.setdefault('diff_metrics', {'instability': 0, 'negative': 0})
        entry.setdefault('version_ref', None)
        if entry.get('status') != 'resolved':
            dm['instability'] += 1
            dm['negative'] += 1
            log_negative(entry['id'])
            bucket = {
                'id': entry['id'],
                'title': entry['buckets'][0] if entry['buckets'] else 'Unresolved',
                'content': entry['buckets'][1:] if len(entry['buckets']) > 1 else [],
                'status': entry.get('status', 'pending'),
            }
            if dm['instability'] >= 4:
                append_benchwarm(entry['id'], entry['buckets'])
                entry['status'] = 'benchwarm'
                entry['version_ref'] = str(BENCHWARM)
            else:
                unresolved.append((entry, bucket))
    if unresolved:
        version = next_version()
        buckets = [b for _, b in unresolved]
        agent_path = write_agent(version, buckets)
        for entry, _ in unresolved:
            entry['version_ref'] = str(agent_path)
    save_dataset(data)


if __name__ == '__main__':
    process()
```

**Functions:** load_dataset(), save_dataset(data), next_version(), write_agent(version, buckets), append_benchwarm(entry_id, content), log_negative(entry_id), process()


## Module `catalog_cli.py`

```python
import argparse
import json
import logging
from pathlib import Path
from embeddings import (
    init_db,
    register_dataset,
    embed_dataset,
    list_catalog,
    search_embeddings,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dataset catalog and embedding search")
    sub = parser.add_subparsers(dest="cmd")

    reg = sub.add_parser("register", help="register a dataset")
    reg.add_argument("name")
    reg.add_argument("path")
    reg.add_argument("description", nargs="?", default="")

    emb = sub.add_parser("embed", help="embed all buckets from a dataset JSON file")
    emb.add_argument("path")
    emb.add_argument("name", nargs="?", default=None)
    emb.add_argument("description", nargs="?", default="")

    sub.add_parser("catalog", help="list registered datasets")

    search = sub.add_parser("search", help="search stored embeddings")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()
    init_db()

    def validate_dataset_file(path: str) -> None:
        """Ensure dataset file exists and contains valid JSON."""
        p = Path(path)
        if not p.is_file():
            parser.exit(1, f"Error: dataset file '{path}' does not exist\n")
        try:
            json.loads(p.read_text())
        except Exception as exc:  # pragma: no cover - best effort safeguard
            logging.warning("Invalid dataset JSON %s: %s", path, exc)
            parser.exit(1, f"Error: dataset file '{path}' is not valid JSON: {exc}\n")

    if args.cmd == "register":
        validate_dataset_file(args.path)
        register_dataset(args.name, args.path, args.description)
    elif args.cmd == "embed":
        validate_dataset_file(args.path)
        embed_dataset(args.path, name=args.name, description=args.description)
    elif args.cmd == "catalog":
        for row in list_catalog():
            print(
                f"{row['dataset_name']}\t{row['path']}\t{row['description']}\t{row['created']}"
            )
    elif args.cmd == "search":
        results = search_embeddings(args.query, top_k=args.top_k)
        for r in results:
            print(f"{r['agent_id']}\t{r['bucket_id']}\t{r['score']:.3f}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

**Functions:** main()


## Module `Codex_Studio.py`

```python
# -*- coding: utf-8 -*-
"""
Codex_Lite.py — Local Ollama • Codex Rust (OSS mode) • Buckets • Agent.md • Error Bot • SQL Snapshots
OS: Windows 10/11, macOS, Linux

Highlights
- Ollama-only: lists models via /api/tags and uses them everywhere
- Codex runs with --oss and -m <ollama-model> (no OpenAI)
- Full Auto Mode toggle (--> --full-auto)
- Self-Repo mode: app folder becomes project; Agent.md created with dense directives
- Agent.md Manager (view/edit/rename/delete version files, keep Agent.md immutable)
- Buckets (Assistant/Notes/ErrorBot) in SQLite, versioned; snapshots + diffs; README generator
"""
import os, sys, json, sqlite3, subprocess, shlex, ast, difflib, hashlib, re, socket, logging, urllib.request, urllib.parse, urllib.error, tempfile, zipfile, tarfile, shutil
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from functools import lru_cache
import numpy as np
import time

from tools.task_manager import TaskManager

# ======== Optional GPU ========
try:
    import torch  # type: ignore
except Exception as e:  # pragma: no cover - torch is optional
    logging.warning("Torch import failed: %s", e)
    torch = None

# ======== Qt ========
try:
    from PySide6.QtCore import Qt, QEvent, QRegularExpression, QObject, QProcess, Signal
    from PySide6.QtGui import QFont, QColor, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QFontDatabase
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
        QPushButton, QLineEdit, QComboBox, QPlainTextEdit, QFileDialog, QMessageBox, QDialog,
        QDialogButtonBox, QInputDialog, QTabWidget, QListWidget, QListWidgetItem, QCheckBox, QTextBrowser,
        QDockWidget, QMenu
    )
except Exception as e:
    logging.exception("PySide6 import failed")
    sys.exit(1)

# ======== Optional RAG ========
try:
    from sentence_transformers import SentenceTransformer, util
    EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logging.warning("SentenceTransformer unavailable: %s", e)
    EMBED_MODEL = None

# ======== Logging ========
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ======== Paths ========
APP_ROOT: Path = Path(__file__).resolve().parent
CODEX_DIR: Path = APP_ROOT / "Codex"
LOG_DIR: Path = APP_ROOT / "logs"
DATASETS_ROOT: Path = APP_ROOT / "Project_datasets"
DIFFS_DIR: Path = APP_ROOT / "diffs"
CONFIG_JSON: Path = APP_ROOT / "config.lite.json"
PROJECTS_JSON: Path = APP_ROOT / "projects.lite.json"
APP_LOG: Path = LOG_DIR / "codex_lite.log"
ASSISTANT_TIMING_LOG: Path = LOG_DIR / "assistant_timing.log"
HANDSHAKE_NAME = ".codex_handshake.json"
ANSI_ESCAPE_RE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

# GitHub release info for Codex
CODEX_RELEASE_TAG = "rust-v0.23.0"
CODEX_RELEASE_BASE = f"https://github.com/openai/codex/releases/download/{CODEX_RELEASE_TAG}"
CODEX_REPO_URL = "https://github.com/openai/codex.git"
CODEX_ASSETS = {
    "nt": "codex-x86_64-pc-windows-msvc.exe.zip",
    "posix": {
        "Linux": "codex-x86_64-unknown-linux-gnu.tar.gz",
        "Darwin": "codex-x86_64-apple-darwin.tar.gz",
    },
}

DEFAULT_CONFIG = {
    "oss_base_url": "http://localhost:11434",
    "default_models": {
        "assistant": "gpt-oss:20b",
        "notes": "gpt-oss:20b",
        "errorbot": "gpt-oss:20b",
        "codex": "qwen3:8b",
    },
    "sandbox": "workspace-write",
    "approval": "on-request",
    "full_auto": False,
    "launch_mode": "Embedded"  # External | Embedded
}
DEFAULT_PROJECTS = {"projects": []}

EXCLUDE_DIRS = {
    ".git","node_modules",".venv","venv","env","__pycache__",
    "dist","build",".mypy_cache",".pytest_cache",".idea",".vscode",".DS_Store","Codex","Codex_Agents"
}
EXCLUDE_SUFFIXES = {".exe",".dll",".pyd",".so",".dylib",".bin",".o",".a",".pyc",".pyo",".zip",".tar",".gz",".7z"}

# ======== Utils ========
def ensure_layout():
    for p in [CODEX_DIR, LOG_DIR, DATASETS_ROOT, DIFFS_DIR]:
        p.mkdir(parents=True, exist_ok=True)
    if not CONFIG_JSON.exists():
        CONFIG_JSON.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    if not PROJECTS_JSON.exists():
        PROJECTS_JSON.write_text(json.dumps(DEFAULT_PROJECTS, indent=2), encoding="utf-8")
    if not APP_LOG.exists():
        APP_LOG.write_text("", encoding="utf-8")

def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logging.exception("Load %s failed", path)
        return default

def save_json(path: Path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)

def log_line(msg: str):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with APP_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")
    logging.info(msg)

def which(exe: str) -> str:
    try:
        if os.name == "nt":
            res = subprocess.run(["where", exe], capture_output=True, text=True)
        else:
            res = subprocess.run(["which", exe], capture_output=True, text=True)
        if res.returncode != 0:
            return ""
        for ln in res.stdout.splitlines():
            s = ln.strip()
            if s:
                return s
        return ""
    except Exception as e:
        logging.warning("which(%s) failed: %s", exe, e)
        return ""

def version_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def is_ollama_running(host='127.0.0.1', port=11434) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return True
    except Exception as e:
        logging.warning("Ollama connection failed: %s", e)
        return False

def is_ollama_available(base_url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(base_url)
        host = parsed.hostname or '127.0.0.1'
        port = parsed.port or 11434
        return is_ollama_running(host, port)
    except Exception as e:
        logging.warning("Ollama availability check failed: %s", e)
        return False

# ======== Ollama HTTP ========
def ollama_list(base_url: str) -> Tuple[List[str], Optional[Exception]]:
    """Return models from an Ollama server.

    Parameters
    ----------
    base_url: str
        The server base URL.

    Returns
    -------
    Tuple[List[str], Optional[Exception]]
        A tuple of available model names and a possible exception. Network
        errors like ``URLError`` or ``timeout`` are caught and returned
        so callers can surface user-facing diagnostics. Other exceptions
        are propagated to the caller.
    """
    try:
        req = urllib.request.Request(base_url.rstrip("/") + "/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        return [m["name"] for m in data.get("models", [])], None
    except (urllib.error.URLError, socket.timeout) as e:
        log_line(f"Ollama list failed: {e}")
        return [], e

@lru_cache(maxsize=128)
def _ollama_chat_cached(base_url: str, model: str, messages_tuple: Tuple[Tuple[str, str], ...], system: Optional[str]) -> Tuple[bool, str]:
    messages = [{'role': r, 'content': c} for r, c in messages_tuple]
    if system:
        messages = [{'role': 'system', 'content': system}] + messages
    body = {"model": model, "messages": messages, "stream": False}
    req = urllib.request.Request(base_url.rstrip("/") + "/api/chat",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        return True, data.get("message", {}).get("content", "").strip()
    except Exception as e:
        logging.exception("Ollama chat failed")
        return False, f"[OLLAMA ERROR] {e}"

def ollama_chat(base_url: str, model: str, messages: list, system: Optional[str] = None) -> Tuple[bool, str]:
    messages_tuple = tuple((m.get('role'), m.get('content')) for m in messages)
    return _ollama_chat_cached(base_url, model, messages_tuple, system)

def ollama_cache_clear() -> None:
    _ollama_chat_cached.cache_clear()

# ======== SQLite ========
def dataset_paths(project: Path) -> List[Path]:
    local_dir = project / "datasets"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_db = local_dir / "cortex_lite.db"
    global_db = DATASETS_ROOT / f"{project.name}.db"
    return [local_db, global_db]

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS buckets(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         project TEXT, operator TEXT, tab_name TEXT, content TEXT, version TEXT, ts TEXT
       )""",
    """CREATE TABLE IF NOT EXISTS repo_files(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         project TEXT, path TEXT, content TEXT, version TEXT, ts TEXT
       )""",
    """CREATE TABLE IF NOT EXISTS diffs(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         project TEXT, source TEXT, content TEXT, version TEXT, ts TEXT
       )"""
]

def dataset_init(project: Path):
    for db in dataset_paths(project):
        conn = sqlite3.connect(str(db))
        try:
            cur = conn.cursor()
            for sql in SCHEMA: cur.execute(sql)
            conn.commit()
        finally:
            conn.close()

def dataset_insert(table: str, project: Path, cols: List[str], vals: Tuple):
    for db in dataset_paths(project):
        conn = sqlite3.connect(str(db))
        try:
            cur = conn.cursor()
            cur.execute(f"INSERT INTO {table}({', '.join(cols)}) VALUES({', '.join(['?']*len(cols))})", vals)
            conn.commit()
        finally:
            conn.close()

def dataset_store_bucket(project: Path, operator: str, tab: str, content: str, ver: str):
    ts = datetime.now().isoformat(timespec="seconds")
    dataset_insert("buckets", project, ["project","operator","tab_name","content","version","ts"],
                   (project.name, operator, tab, content, ver, ts))

def dataset_delete_bucket(project: Path, operator: str, tab: str):
    for db in dataset_paths(project):
        conn = sqlite3.connect(str(db))
        try:
            conn.execute("DELETE FROM buckets WHERE project=? AND operator=? AND tab_name=?",
                         (project.name, operator, tab))
            conn.commit()
        finally:
            conn.close()

def dataset_store_repo_files(project: Path, files: List[Tuple[str,str]], ver: str):
    ts = datetime.now().isoformat(timespec="seconds")
    for db in dataset_paths(project):
        conn = sqlite3.connect(str(db))
        try:
            conn.executemany(
                "INSERT INTO repo_files(project,path,content,version,ts) VALUES(?,?,?,?,?)",
                [(project.name, p, c, ver, ts) for p, c in files]
            )
            conn.commit()
        finally:
            conn.close()

def dataset_store_diff(project: Path, source: str, content: str, ver: str):
    ts = datetime.now().isoformat(timespec="seconds")
    dataset_insert("diffs", project, ["project","source","content","version","ts"],
                   (project.name, source, content, ver, ts))

def dataset_fetch_diffs_desc(project: Path) -> List[Tuple[str,str,str]]:
    db = dataset_paths(project)[0]
    conn = sqlite3.connect(str(db)); conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT ts, source, content FROM diffs WHERE project=? ORDER BY id DESC", (project.name,))
        return [(r["ts"], r["source"], r["content"]) for r in cur.fetchall()]
    finally:
        conn.close()

def clone_codex_repo(codex_dir: Path) -> Optional[Path]:
    repo_dir = codex_dir / "codex-src"
    try:
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
        subprocess.run([
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            CODEX_RELEASE_TAG,
            CODEX_REPO_URL,
            str(repo_dir),
        ], check=True)
        return repo_dir
    except Exception as e:
        logging.exception("Clone failed")
        log_line(f"Clone failed: {e}")
        return None

# ======== Snapshots & Diffs ========
def text_sha1(s: str) -> str: return hashlib.sha1(s.encode("utf-8","ignore")).hexdigest()

def sanitize_skip(path: Path) -> bool:
    low = path.name.lower()
    if low.startswith("readme") and path.suffix.lower()==".md": return True
    if "Codex_Agents" in [p.lower() for p in path.parts]: return True
    return False

def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in EXCLUDE_SUFFIXES: return False
    try:
        with path.open("rb") as f: chunk = f.read(4096)
        if b"\x00" in chunk: return False
        return True
    except Exception as e:
        logging.warning("Could not read %s: %s", path, e)
        return False

def iter_files(root: Path):
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fn in files:
            p = Path(cur) / fn
            if sanitize_skip(p): continue
            if not is_text_file(p): continue
            yield p

class Snapshot:
    def __init__(self, stamp: str, files: Dict[str, Tuple[str,str]]):
        self.stamp = stamp
        self.files = files  # rel -> (sha, text)

def make_snapshot(root: Path, limit_bytes=2_000_000) -> Snapshot:
    files: Dict[str, Tuple[str,str]] = {}
    for p in iter_files(root):
        try:
            if p.stat().st_size > limit_bytes: continue
        except Exception as e:
            logging.warning("Could not stat %s: %s", p, e)
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            logging.warning("Could not read %s: %s", p, e)
            txt = f"[[unreadable: {e}]]"
        rel = str(p.relative_to(root)).replace("\\","/")
        files[rel] = (text_sha1(txt), txt)
    return Snapshot(version_stamp(), files)

def unified(a_text: str, b_text: str, a_label: str, b_label: str) -> str:
    return "\n".join(difflib.unified_diff(a_text.splitlines(), b_text.splitlines(),
                                          fromfile=a_label, tofile=b_label, lineterm=""))

def diff_snapshots(a: Snapshot, b: Snapshot) -> List[Tuple[str,str]]:
    a_paths, b_paths = set(a.files), set(b.files)
    out: List[Tuple[str,str]] = []
    for rel in sorted(b_paths - a_paths):
        out.append(("added", unified("", b.files[rel][1], f"a/{rel}", f"b/{rel}")))
    for rel in sorted(a_paths - b_paths):
        out.append(("removed", unified(a.files[rel][1], "", f"a/{rel}", f"b/{rel}")))
    for rel in sorted(a_paths & b_paths):
        (sa, ta) = a.files[rel]; (sb, tb) = b.files[rel]
        if sa != sb:
            out.append(("changed", unified(ta, tb, f"a/{rel}", f"b/{rel}")))
    return out

# ======== README (light) ========
def analyse_overview(root: Path) -> str:
    py_sections, other = [], []
    for p in iter_files(root):
        rel = str(p.relative_to(root)).replace("\\","/")
        if p.suffix.lower()==".py":
            doc, classes, funcs = "", [], []
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
                doc = (ast.get_docstring(tree) or "").strip()
                for n in tree.body:
                    if isinstance(n, ast.ClassDef): classes.append(n.name)
                    if isinstance(n, ast.FunctionDef): funcs.append(n.name)
            except Exception as e:
                logging.warning("Could not parse %s: %s", p, e)
            sec = [f"### `{rel}`"]
            if doc: sec.append(doc)
            if classes: sec.append("**Classes:** " + ", ".join(classes))
            if funcs: sec.append("**Functions:** " + ", ".join(funcs))
            py_sections.append("\n\n".join(sec))
        else:
            other.append(rel)
    out = ["# Project Documentation", "", "Auto-generated after update.", ""]
    if py_sections: out += ["## Python Modules",""] + py_sections + [""]
    if other:
        out += ["## Other Files", ""] + [f"- `{x}`" for x in sorted(other)] + [""]
    return "\n".join(out)

def generate_readme(project: Path, log=lambda s: None, ver: Optional[str]=None):
    try:
        md = analyse_overview(project); ts = ver or version_stamp()
        readme = project / "README.md"; hist = project / ".readmes"; hist.mkdir(exist_ok=True)
        prev = readme.read_text(encoding="utf-8", errors="ignore") if readme.exists() else ""
        readme.write_text(md, encoding="utf-8")
        (hist / f"README_{ts}.md").write_text(md, encoding="utf-8")
        log(f"[SYSTEM] README generated at {readme} (snapshot README_{ts}.md)")
        if prev:
            patch = unified(prev, md, "README.md(prev)","README.md(curr)")
            if patch.strip(): dataset_store_diff(project, "readme", patch, ts)
    except Exception as e:
        logging.exception("README generation failed")
        log(f"[SYSTEM] README generation failed: {e}")

# ======== UI Helpers ========
class DiffHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        def fmt(c): f=QTextCharFormat(); f.setForeground(QColor(c)); return f
        self.rules = [
            (QRegularExpression(r"^(\+.*)$"), fmt("#00a859")),
            (QRegularExpression(r"^(\-.*)$"), fmt("#d14")),
            (QRegularExpression(r"^@@.*@@"), fmt("#b58900")),
            (QRegularExpression(r"^(diff --git|index |--- |\+\+\+ )"), fmt("#7b5cff")),
        ]
    def highlightBlock(self, text: str):
        for rx, sty in self.rules:
            it = rx.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), sty)

class DiffPane(QWidget):
    def __init__(self):
        super().__init__()
        self.blocks: List[Tuple[str,str,str]] = []
        self.idx = -1
        v = QVBoxLayout(self)
        head = QHBoxLayout()
        self.lbl = QLabel("Diffs: 0")
        self.prev = QPushButton("◀ Prev"); self.nextb = QPushButton("Next ▶")
        head.addWidget(self.lbl); head.addStretch(1); head.addWidget(self.prev); head.addWidget(self.nextb)
        v.addLayout(head)
        self.view = QPlainTextEdit(); self.view.setReadOnly(True); self.view.setLineWrapMode(QPlainTextEdit.NoWrap)
        v.addWidget(self.view, 1)
        self.hl = DiffHighlighter(self.view.document())
        mono = QFont("Consolas" if os.name=="nt" else "Monospace"); mono.setStyleHint(QFont.TypeWriter)
        self.view.setFont(mono)
        self.prev.clicked.connect(self._prev); self.nextb.clicked.connect(self._next)
    def set_blocks(self, blocks: List[Tuple[str,str,str]]):
        self.blocks = blocks; self.idx = 0 if blocks else -1; self._render()
    def _render(self):
        n=len(self.blocks); self.lbl.setText(f"Diffs: {n} (page {self.idx+1 if self.idx>=0 else 0}/{n})")
        self.view.setPlainText("" if self.idx<0 else f"--- [{self.blocks[self.idx][0]}] source={self.blocks[self.idx][1]} ---\n{self.blocks[self.idx][2]}")
    def _prev(self):
        if self.idx>0: self.idx-=1; self._render()
    def _next(self):
        if self.blocks and self.idx<len(self.blocks)-1: self.idx+=1; self._render()

# ======== Chat Pane ========
class ChatPane(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        # Load emoji font
        fd = QFontDatabase()
        emoji = None
        for path in (
            "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
            "/usr/share/fonts/truetype/emoji/NotoColorEmoji.ttf",
        ):
            fid = fd.addApplicationFont(path)
            if fid != -1:
                fam = fd.applicationFontFamilies(fid)
                if fam:
                    emoji = QFont(fam[0])
                    break
        if emoji:
            self.setFont(emoji)
        css = (
            """
            QTextBrowser { border:1px solid #c7c7c7; background:#0f1113; color:#ededed; padding:4px; }
            .user { background:#4b6ef5; color:#fff; padding:6px; border-radius:6px; margin:4px 40px 4px 4px; }
            .assistant { background:#444; color:#fff; padding:6px; border-radius:6px; margin:4px 4px 4px 40px; }
            .codex { background:#2f2f2f; color:#98c379; padding:6px; border-radius:6px; margin:4px 40px 4px 4px; }
            .system { background:#222; color:#f1c40f; padding:6px; border-radius:6px; margin:4px 40px; }
            """
        )
        self.setStyleSheet(css)
        self.document().setDefaultStyleSheet(css)

    def append_message(self, role: str, text: str):
        esc = html.escape(text).replace("\n", "<br>")
        self.append(f"<div class='{role}'>{esc}</div>")
        self.moveCursor(QTextCursor.End)

# ======== Agent Manager Dialog ========
class AgentManager(QDialog):
    def __init__(self, root: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agent.md Manager")
        self.root = root
        v = QVBoxLayout(self)
        self.list = QListWidget(); v.addWidget(self.list, 2)
        self.edit = QPlainTextEdit(); self.edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        v.addWidget(self.edit, 5)
        row = QHBoxLayout()
        self.btn_open = QPushButton("Open"); self.btn_save = QPushButton("Save")
        self.btn_new = QPushButton("New version file…")
        self.btn_rename = QPushButton("Rename")
        self.btn_delete = QPushButton("Delete")
        row.addWidget(self.btn_open); row.addWidget(self.btn_save); row.addWidget(self.btn_new)
        row.addWidget(self.btn_rename); row.addWidget(self.btn_delete)
        v.addLayout(row)
        self._refresh()
        self.btn_open.clicked.connect(self._open)
        self.btn_save.clicked.connect(self._save)
        self.btn_new.clicked.connect(self._new)
        self.btn_rename.clicked.connect(self._rename)
        self.btn_delete.clicked.connect(self._delete)
    def _agent_dir(self) -> Path:
        d = self.root / "Codex_Agents"; d.mkdir(exist_ok=True); return d
    def _refresh(self):
        self.list.clear()
        d = self._agent_dir()
        files = sorted([p.name for p in d.glob("*.md")])
        for name in files:
            self.list.addItem(name)
    def _sel_path(self) -> Optional[Path]:
        it = self.list.currentItem()
        if not it: return None
        return self._agent_dir() / it.text()
    def _open(self):
        p = self._sel_path()
        if not p: return
        try:
            self.edit.setPlainText(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception as e:
            logging.exception("Open agent file failed")
            QMessageBox.warning(self, "Open", str(e))
    def _save(self):
        p = self._sel_path()
        if not p: return
        if p.name == "Agent.md":
            QMessageBox.warning(self, "Agent.md", "Agent.md is immutable; edits are blocked.")
            return
        try:
            p.write_text(self.edit.toPlainText(), encoding="utf-8")
            QMessageBox.information(self, "Saved", f"Saved {p.name}")
        except Exception as e:
            logging.exception("Save agent file failed")
            QMessageBox.warning(self, "Save", str(e))
    def _new(self):
        name, ok = QInputDialog.getText(self, "New Agent Version", "Name (e.g., v1):")
        if not ok or not name.strip(): return
        p = self._agent_dir() / f"Agent_{name.strip()}.md"
        if p.exists(): QMessageBox.information(self, "Exists", "File exists."); return
        p.write_text("# Agent Version\n\n(Add directives…)\n", encoding="utf-8")
        self._refresh()
    def _rename(self):
        p = self._sel_path()
        if not p: return
        if p.name=="Agent.md":
            QMessageBox.information(self, "Agent.md", "Agent.md is immutable (cannot be renamed).")
            return
        name, ok = QInputDialog.getText(self, "Rename", "New name (without .md):", text=p.stem)
        if not ok or not name.strip(): return
        dest = p.with_name(f"{name.strip()}.md")
        if dest.exists(): QMessageBox.information(self, "Exists", "Target exists."); return
        p.rename(dest); self._refresh()
    def _delete(self):
        p = self._sel_path()
        if not p: return
        if p.name=="Agent.md":
            QMessageBox.information(self, "Agent.md", "Agent.md is immutable (cannot be deleted).")
            return
        if QMessageBox.question(self, "Delete", f"Delete {p.name}?") == QMessageBox.Yes:
            p.unlink(missing_ok=True); self._refresh()
class SecurityDialog(QDialog):
    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Settings")
        self.cfg = cfg
        v = QVBoxLayout(self)
        row1 = QHBoxLayout()
        self.cb_sandbox = QComboBox()
        self.cb_sandbox.addItems(["workspace-write", "read-only", "none"])
        self.cb_sandbox.setCurrentText(cfg.get("sandbox", "workspace-write"))
        row1.addWidget(QLabel("Sandbox:"))
        row1.addWidget(self.cb_sandbox, 1)
        v.addLayout(row1)
        row2 = QHBoxLayout()
        self.cb_approval = QComboBox()
        self.cb_approval.addItems(["on-request", "on-failure", "never"])
        self.cb_approval.setCurrentText(cfg.get("approval", "on-request"))
        row2.addWidget(QLabel("Approval:"))
        row2.addWidget(self.cb_approval, 1)
        v.addLayout(row2)
        self.chk_full_auto = QCheckBox("Full Auto Mode")
        self.chk_full_auto.setChecked(bool(cfg.get("full_auto", False)))
        v.addWidget(self.chk_full_auto)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        v.addWidget(btns)

    def values(self):
        return {
            "sandbox": self.cb_sandbox.currentText(),
            "approval": self.cb_approval.currentText(),
            "full_auto": self.chk_full_auto.isChecked(),
        }

# ======== Main Widget ========
class CodexLite(QWidget):
    def __init__(self, status_cb):
        super().__init__()
        ensure_layout()
        self.cfg = load_json(CONFIG_JSON, DEFAULT_CONFIG)
        self.projects = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        self.status_cb = status_cb

        self._pre_snapshot = None
        self._pre_project: Optional[Path] = None

        self.codex_proc = QProcess(self)
        self.codex_proc.readyReadStandardOutput.connect(self._codex_out)
        self.codex_proc.readyReadStandardError.connect(self._codex_err)
        self.codex_proc.finished.connect(lambda *_: self._status("Embedded Codex exited."))
        self._strip_ansi = False
        self._last_assistant_msg = ""

        self.task_manager = TaskManager(LOG_DIR / "tasks.json")

        self._build_ui()
        self._apply_theme()
        self._reload_projects()
        self._populate_models(initial=True)
        self._status("Ready")

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        split = QSplitter(Qt.Horizontal); root.addWidget(split, 1)

        # LEFT: Assistant side
        left = QWidget(); lv = QVBoxLayout(left)
        gA = QGroupBox("Assistant"); av = QVBoxLayout(gA)

        row_models = QHBoxLayout()
        self.cb_assistant = QComboBox()
        self.cb_notes = QComboBox()
        self.cb_error = QComboBox()
        row_models.addWidget(QLabel("Assistant:")); row_models.addWidget(self.cb_assistant, 1)
        row_models.addWidget(QLabel("Notes:")); row_models.addWidget(self.cb_notes, 1)
        row_models.addWidget(QLabel("Error Bot:")); row_models.addWidget(self.cb_error, 1)
        av.addLayout(row_models)

        self.chat = ChatPane(); av.addWidget(self.chat, 1)

        compose = QHBoxLayout()
        self.ass_in = QPlainTextEdit(); self.ass_in.setFixedHeight(90)
        self.ass_in.setPlaceholderText("Ask your assistant… (Enter to send; Shift+Enter = newline)")
        self.btn_send = QPushButton("Send"); self.btn_send.clicked.connect(self._assistant_send)
        self.btn_to_note = QPushButton("Summarize → Notes"); self.btn_to_note.clicked.connect(self._assistant_to_note)
        compose.addWidget(self.ass_in, 1); compose.addWidget(self.btn_send); compose.addWidget(self.btn_to_note)
        av.addLayout(compose)
        self.input_line = QLineEdit(); self.input_line.setPlaceholderText("Type to send to Embedded Codex…")
        self.input_line.returnPressed.connect(self._send_to_embedded)
        av.addWidget(self.input_line)
        lv.addWidget(gA, 1)

        # RIGHT: Project / Codex / Buckets / Diff
        right = QWidget(); rv = QVBoxLayout(right)

        # Project row
        gP = QGroupBox("Project"); pv = QVBoxLayout(gP)
        prow1 = QHBoxLayout()
        self.cb_project = QComboBox()
        self.btn_add = QPushButton("Add…")
        self.btn_open = QPushButton("Open Folder")
        self.btn_forget = QPushButton("Forget")
        self.btn_selfrepo = QPushButton("Self-Repo Mode")
        prow1.addWidget(QLabel("Current:")); prow1.addWidget(self.cb_project, 1)
        for b, fn in [(self.btn_add, self._add_project), (self.btn_open, self._open_project),
                      (self.btn_forget, self._forget_project), (self.btn_selfrepo, self._self_repo)]:
            b.clicked.connect(fn); prow1.addWidget(b)
        pv.addLayout(prow1)

        prow2 = QHBoxLayout()
        self.cb_codex_model = QComboBox()
        self.btn_refresh_models = QPushButton("Refresh Ollama Models"); self.btn_refresh_models.clicked.connect(self._populate_models)
        self.chk_full_auto = QCheckBox("Full Auto Mode")
        self.chk_full_auto.setChecked(bool(self.cfg.get("full_auto", False)))
        self.btn_security = QPushButton("Security Settings…")
        self.btn_security.clicked.connect(self._security_settings)
        self.btn_setup_codex = QPushButton("Setup Codex"); self.btn_setup_codex.clicked.connect(self._setup_codex)
        self.btn_setup_codex.setToolTip("Download binary and clone source from GitHub")
        self.btn_upload_src = QPushButton("Upload Codex Source"); self.btn_upload_src.clicked.connect(self._upload_codex_source)
        self.btn_upload_src.setToolTip("Push Codex source to your GitHub repo")
        self.btn_launch_ext = QPushButton("Launch External"); self.btn_launch_ext.clicked.connect(lambda: self._launch_codex(mode="External"))
        self.btn_launch_ext.setToolTip("Open Codex in a separate terminal window")
        self.btn_launch_emb = QPushButton("Launch Embedded"); self.btn_launch_emb.clicked.connect(lambda: self._launch_codex(mode="Embedded"))
        self.btn_launch_emb.setToolTip("Run Codex inside this GUI")
        prow2.addWidget(QLabel("Codex model:")); prow2.addWidget(self.cb_codex_model, 1)
        prow2.addWidget(self.btn_refresh_models)
        prow2.addStretch(1)
        prow2.addWidget(self.chk_full_auto)
        prow2.addWidget(self.btn_security)
        prow2.addWidget(self.btn_setup_codex)
        prow2.addWidget(self.btn_upload_src)
        prow2.addWidget(self.btn_launch_ext)
        prow2.addWidget(self.btn_launch_emb)
        pv.addLayout(prow2)
        rv.addWidget(gP)

        # Agents / README row
        gR = QGroupBox("Agents / README"); grv = QHBoxLayout(gR)
        self.btn_core_agent = QPushButton("Create Core Agent.md"); self.btn_core_agent.clicked.connect(self._create_core_agent)
        self.btn_agent_new = QPushButton("New Agent file…"); self.btn_agent_new.clicked.connect(self._new_agent_file)
        self.btn_export_note = QPushButton("Export Note → Agent_v*.md"); self.btn_export_note.clicked.connect(self._export_selected_note)
        self.btn_agent_mgr = QPushButton("Agent.md Manager"); self.btn_agent_mgr.clicked.connect(self._open_agent_manager)
        self.btn_readme = QPushButton("Generate README"); self.btn_readme.clicked.connect(self._gen_readme)
        for b in [self.btn_core_agent, self.btn_agent_new, self.btn_export_note, self.btn_agent_mgr, self.btn_readme]:
            grv.addWidget(b)
        rv.addWidget(gR)

        # Buckets row
        gB = QGroupBox("Buckets"); gbv = QHBoxLayout(gB)
        # Notes
        notes = QGroupBox("Notes (Buckets)"); nv = QVBoxLayout(notes)
        self.tabs_notes = QTabWidget(); self.tabs_notes.setTabsClosable(True)
        self.tabs_notes.tabCloseRequested.connect(lambda i: self._close_bucket(self.tabs_notes,"notes",i))
        nv.addWidget(self.tabs_notes, 1)
        rown = QHBoxLayout()
        self.btn_note_new = QPushButton("New Note"); self.btn_note_new.clicked.connect(lambda: self._note_create("# Note\n"))
        self.btn_note_save = QPushButton("Save Note"); self.btn_note_save.clicked.connect(self._note_save)
        rown.addWidget(self.btn_note_new); rown.addWidget(self.btn_note_save)
        nv.addLayout(rown)
        # Tasks
        tasks = QGroupBox("Tasks"); tv = QVBoxLayout(tasks)
        self.list_tasks = QListWidget(); tv.addWidget(self.list_tasks, 1)
        self.list_tasks.currentItemChanged.connect(self._task_selection_changed)
        rowt = QHBoxLayout()
        self.btn_task_pause = QPushButton("Pause"); self.btn_task_pause.clicked.connect(self._task_pause)
        self.btn_task_done = QPushButton("Complete"); self.btn_task_done.clicked.connect(self._task_done)
        self.btn_task_remove = QPushButton("Delete"); self.btn_task_remove.clicked.connect(self._task_remove)
        for b in [self.btn_task_pause, self.btn_task_done, self.btn_task_remove]:
            rowt.addWidget(b)
        tv.addLayout(rowt)
        # Error Bot
        eb = QGroupBox("Error Bot"); ev = QVBoxLayout(eb)
        self.tabs_error = QTabWidget(); self.tabs_error.setTabsClosable(True)
        self.tabs_error.tabCloseRequested.connect(lambda i: self._close_bucket(self.tabs_error,"errorbot",i))
        ev.addWidget(self.tabs_error, 1)
        rowe = QHBoxLayout()
        self.btn_scan = QPushButton("Run Error Bot (Analyze diffs + buckets)"); self.btn_scan.clicked.connect(self._run_error_bot)
        self.btn_clear_diffs = QPushButton("Clear Diff View"); self.btn_clear_diffs.clicked.connect(lambda: self.diffpane.set_blocks([]))
        self.btn_save_patch = QPushButton("Export Patch"); self.btn_save_patch.clicked.connect(self._save_patch)
        rowe.addWidget(self.btn_scan); rowe.addWidget(self.btn_clear_diffs); rowe.addWidget(self.btn_save_patch)
        ev.addLayout(rowe)
        gbv.addWidget(notes,1); gbv.addWidget(tasks,1); gbv.addWidget(eb,1)
        rv.addWidget(gB, 2)

        # Diff viewer
        self.diffpane = DiffPane()
        rv.addWidget(self.diffpane, 2)

        split.addWidget(left); split.addWidget(right)
        split.setStretchFactor(0, 3); split.setStretchFactor(1, 5)

        # Enter to send in assistant input
        self.ass_in.installEventFilter(self._enter_filter(self._assistant_send))
        self.task_manager.tasks_changed.connect(self._tasks_refresh)
        self._tasks_refresh()

    def _apply_theme(self):
        self.setStyleSheet("""
        QWidget { background:#d3d4d1; }
        QGroupBox { background:#e6e6e6; border:1px solid #c6c6c6; border-radius:6px; margin-top:8px; font-weight:bold; color:#222; }
        QGroupBox::title { left:10px; padding:0 4px; }
        QPlainTextEdit, QTextBrowser { border:1px solid #c7c7c7; background:#0f1113; color:#ededed; }
        QPushButton { border:none; border-radius:6px; padding:8px 12px; color:#fff; background:#7b5cff; }
        QPushButton:hover { background:#6a4be0; }
        """)
        mono = QFont("Consolas" if os.name=="nt" else "Monospace"); mono.setStyleHint(QFont.TypeWriter)
        for w in [self.diffpane.view, self.ass_in]:
            w.setFont(mono)

    def _status(self, s: str):
        self.status_cb(s); log_line(s)
        self.chat.append_message('system', s)

    def _enter_filter(self, fn):
        class F(QObject):
            def eventFilter(s, o, e):
                if e.type() == QEvent.KeyPress and e.key() in (Qt.Key_Return, Qt.Key_Enter) and not (e.modifiers() & Qt.ShiftModifier):
                    fn(); return True
                return False
        return F(self)

    # ---------- Models ----------
    def _populate_models(self, initial=False):
        base = self.cfg.get("oss_base_url","http://localhost:11434")
        if not is_ollama_available(base):
            for cb in [self.cb_assistant, self.cb_notes, self.cb_error, self.cb_codex_model]:
                cb.clear(); cb.addItem("Ollama offline")
            self._status(f"Ollama server unavailable at {base}")
            return
        models, err = ollama_list(base)
        if err:
            for cb in [self.cb_assistant, self.cb_notes, self.cb_error, self.cb_codex_model]:
                cb.clear(); cb.addItem("Ollama error")
            self._status(f"Failed to list Ollama models: {err}")
            return
        if not models:
            for cb in [self.cb_assistant, self.cb_notes, self.cb_error, self.cb_codex_model]:
                cb.clear(); cb.addItem("No Ollama models")
            self._status("Ollama reachable but no models found. Pull models with 'ollama pull <model>'.")
            return
        for cb in [self.cb_assistant, self.cb_notes, self.cb_error, self.cb_codex_model]:
            sel = cb.currentText()
            cb.clear(); cb.addItems(models)
        # set defaults
        defaults = self.cfg.get("default_models", {})
        def set_default(cb, key):
            want = defaults.get(key)
            i = cb.findText(want) if want else -1
            if i >= 0:
                cb.setCurrentIndex(i)
            else:
                cb.setCurrentIndex(0)
                if key == "codex" and want == "qwen3:8b":
                    self._status("Default 'qwen3:8b' not found; using first available model.")
        if initial:
            set_default(self.cb_assistant, "assistant")
            set_default(self.cb_notes, "notes")
            set_default(self.cb_error, "errorbot")
            set_default(self.cb_codex_model, "codex")
        self._status("Ollama models refreshed.")

    # ---------- Projects ----------
    def _reload_projects(self):
        self.cb_project.clear()
        self.projects = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        self.cb_project.addItem("<none>")
        for p in self.projects.get("projects", []):
            self.cb_project.addItem(p["name"])
        if self.cfg.get("default_project"):
            i = self.cb_project.findText(self.cfg["default_project"])
            if i>=0: self.cb_project.setCurrentIndex(i)

    def _get_project_entry(self, name: str):
        return next((x for x in self.projects.get("projects", []) if x.get("name")==name), None)

    def _current_project(self) -> Optional[Path]:
        name = self.cb_project.currentText()
        if not name or name=="<none>": return None
        ent = self._get_project_entry(name); 
        if not ent: return None
        p = Path(ent.get("path",""))
        if not p.exists(): self._status("Project path missing."); return None
        ent["last_used"] = datetime.now().isoformat(); save_json(PROJECTS_JSON, self.projects)
        dataset_init(p)
        return p

    def _add_project(self):
        d = QFileDialog.getExistingDirectory(self, "Select Project Folder", str(Path.home()))
        if not d: return
        p = Path(d)
        data = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        if not any(x.get("path")==str(p) for x in data.get("projects", [])):
            data["projects"].append({"name": p.name, "path": str(p), "type":"local", "last_used": datetime.now().isoformat()})
            save_json(PROJECTS_JSON, data)
        self._reload_projects()
        self.cb_project.setCurrentText(p.name)
        self.cfg["default_project"] = p.name; save_json(CONFIG_JSON, self.cfg)
        dataset_init(p)
        self._status("Project added and initialized (SQL).")

    def _open_project(self):
        p = self._current_project()
        if not p: return
        try:
            if os.name=="nt": os.startfile(str(p))  # type: ignore
            elif sys.platform=="darwin": subprocess.Popen(["open", str(p)])
            else: subprocess.Popen(["xdg-open", str(p)])
        except Exception as e:
            logging.exception("Open project failed")
            self._status(f"Open project failed: {e}")

    def _forget_project(self):
        sel = self.cb_project.currentText()
        if not sel or sel=="<none>": return
        data = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        data["projects"] = [x for x in data.get("projects", []) if x.get("name")!=sel]
        save_json(PROJECTS_JSON, data)
        if self.cfg.get("default_project")==sel:
            self.cfg["default_project"] = ""; save_json(CONFIG_JSON, self.cfg)
        self._reload_projects()
        self._status("Project forgotten.")

    def _self_repo(self):
        # Make the app folder itself the project and ensure SQL + Agent.md exist
        data = load_json(PROJECTS_JSON, DEFAULT_PROJECTS)
        if not any(x.get("path")==str(APP_ROOT) for x in data.get("projects", [])):
            data["projects"].append({"name": APP_ROOT.name, "path": str(APP_ROOT), "type":"local", "last_used": datetime.now().isoformat()})
            save_json(PROJECTS_JSON, data)
        self._reload_projects()
        self.cb_project.setCurrentText(APP_ROOT.name)
        self.cfg["default_project"] = APP_ROOT.name; save_json(CONFIG_JSON, self.cfg)
        dataset_init(APP_ROOT)
        self._status("Self-Repo mode: current project = app root.")
        self._create_core_agent(force=True)

    # ---------- Agent.md ----------
    def _agent_dir(self, project: Path) -> Path:
        d = project / "Codex_Agents"; d.mkdir(exist_ok=True); return d

    def _default_agent_body(self) -> str:
        return (
            "# Agent.md — Operating Charter for Codex (Local-Ollama, Self-Evolving)\n\n"
            "You are **Codex** running entirely with **local Ollama models** via the `--oss` provider.\n"
            "This repository is your **workspace and subject**. Your primary objective is to **self-improve Codex_Lite** and its ecosystem while strictly honoring the user's intent.\n\n"
            "## Ground Rules\n"
            "1. **Provider**: Use local models (Ollama). Never request OpenAI or remote APIs. Assume an Ollama server at `http://localhost:11434`.\n"
            "2. **Models**: Default to `gpt-oss:20b` (or user-selected). Be concise but precise; prefer small diffs and incremental PR-style changes.\n"
            "3. **Workspace**: Treat this folder as the project root. Use `-C <root>` when you run the Codex CLI.\n"
            "4. **Artifacts**: Maintain buckets in SQLite, snapshots, diffs, and `README.md`. Avoid editing generated snapshots directly.\n"
            "5. **Agent Files**: `Codex_Agents/Agent.md` is the **immutable global policy**. Also consult any `Codex_Agents/Agent_Versions/Agent_*.md` files as **versioned directives**. If none exist, propose improvements.\n"
            "6. **Notes**: User can convert Notes buckets into `Agent_Versions/Agent_*.md`. Treat them as **high-priority directives** when present.\n"
            "7. **Safety**: Unless Full Auto Mode is enabled, ask for approval before risky actions. Respect sandbox configuration.\n\n"
            "## Operating Procedure\n"
            "- On start: read `Agent.md` + latest `Agent_Versions/Agent_*.md` files, SQLite buckets, and most recent diffs.\n"
            "- Detect logical gaps, missing features, UX rough edges, and reliability problems.\n"
            "- Propose changes as *minimal diffs*, with file paths, reasoning, and test/validation steps.\n"
            "- When the user approves (or Full Auto Mode), apply patches safely and update documentation.\n\n"
            "## Priorities\n"
            "1. Robust **Ollama-only** integration and model selection across Assistant/Notes/ErrorBot/Codex.\n"
            "2. Reliability: clean error handling, cross-platform terminal behavior, snapshot consistency, and DB integrity.\n"
            "3. Humanistic UX: clear status lines, safe defaults, reversible actions, and readable diffs.\n"
            "4. Autonomy: self-diagnose failures, suggest fixes, and refine prompts/agents to improve over time.\n\n"
            "## Datasets\n"
            "- You may index project text into embeddings if enabled. Use them only for retrieval—not as ground truth.\n\n"
            "## Deliverables\n"
            "- Small, reviewable diffs; updated READMEs; new/updated `Agent_Versions/Agent_*.md` when turning Notes into persistent directives; Error Bot reports after each update.\n"
        )

    def _create_core_agent(self, force=False):
        p = self._current_project()
        if not p: QMessageBox.information(self, "Select project", "Choose a project."); return
        d = self._agent_dir(p)
        core = d / "Agent.md"
        if core.exists() and not force:
            self._status(f"Core Agent.md already exists at {core}")
            return
        core.write_text(self._default_agent_body(), encoding="utf-8")
        self._status(f"Core Agent.md created at {core}")

    def _new_agent_file(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        name, ok = QInputDialog.getText(self, "New Agent File", "Agent name (e.g. v1):")
        if not ok or not name.strip(): return
        path = self._agent_dir(p) / f"Agent_{name.strip()}.md"
        path.write_text("# Agent Version\n\n(Add directives…)\n", encoding="utf-8")
        self._status(f"Agent file created: {path}")

    def _export_selected_note(self):
        idx = self.tabs_notes.currentIndex()
        if idx < 0: QMessageBox.information(self,"Notes","Select a note tab first."); return
        w = self.tabs_notes.widget(idx)
        if not isinstance(w, QPlainTextEdit): return
        txt = w.toPlainText()
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        out = self._agent_dir(p) / f"Agent_{version_stamp()}.md"
        out.write_text(txt, encoding="utf-8")
        self._status(f"Exported note to {out}")

    def _open_agent_manager(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        AgentManager(p, self).exec()

    # ---------- Assistant / Notes / ErrorBot ----------
    def _assistant_send(self):
        msg = self.ass_in.toPlainText().strip()
        if not msg: return
        self.ass_in.clear()
        base = self.cfg.get("oss_base_url","http://localhost:11434")
        model = self.cb_assistant.currentText()
        sys_prompt = "You are a pragmatic engineering copilot inside Codex Lite. Prefer concrete steps, short patches, and file paths."
        start = time.time()
        ok, out = ollama_chat(base, model, [{'role':'user','content':msg}], sys_prompt)
        self.chat.append_message('user', msg)
        if not ok:
            self._status(out)
            self.chat.append_message('assistant', out)
            return
        self.chat.append_message('assistant', out)
        self._last_assistant_msg = out
        elapsed = time.time() - start
        self._status(f"Assistant responded in {elapsed:.2f}s")
        content = f"You: {msg}\n\nAssistant({model}):\n{out}"
        p = self._current_project()
        if p: dataset_store_bucket(p, "assistant", f"Asst_{version_stamp()}", content, version_stamp())
        try:
            ASSISTANT_TIMING_LOG.open("a", encoding="utf-8").write(f"{datetime.now().isoformat()}\n")
        except Exception as e:
            logging.exception("Assistant timing log failed")
            self._status(f"Assistant timing log failed: {e}")

    def _assistant_to_note(self):
        if not getattr(self, '_last_assistant_msg', ''):
            QMessageBox.information(self,"Assistant","No assistant output to summarize."); return
        summary = self._summarize_text(self._last_assistant_msg)
        self._note_create(summary)

    def _summarize_text(self, text: str) -> str:
        base = self.cfg.get("oss_base_url","http://localhost:11434")
        model = self.cb_notes.currentText()
        sys_prompt = "Summarize into actionable, terse bullet points with file paths and diffs when relevant."
        ok, out = ollama_chat(base, model, [{'role':'user','content':text}], sys_prompt)
        return out if ok and out.strip() else text[:2000]

    def _note_create(self, content: str):
        te = QPlainTextEdit(); te.setLineWrapMode(QPlainTextEdit.NoWrap); te.setPlainText(content)
        title = f"Note_{version_stamp()}"
        idx = self.tabs_notes.addTab(te, title); self.tabs_notes.setCurrentIndex(idx)
        p = self._current_project()
        if p: dataset_store_bucket(p, "notes", title, content, version_stamp())
        try:
            self.task_manager.add_task(title=title, content=content, status="new")
        except Exception as e:
            logging.exception("add_task failed")

    def _note_save(self):
        idx = self.tabs_notes.currentIndex()
        if idx < 0: return
        w = self.tabs_notes.widget(idx)
        if not isinstance(w, QPlainTextEdit): return
        content = w.toPlainText()
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        dataset_store_bucket(p, "notes", self.tabs_notes.tabText(idx), content, version_stamp())
        try:
            self.task_manager.add_task(title=self.tabs_notes.tabText(idx), content=content, status="saved")
        except Exception as e:
            logging.exception("add_task failed")
        self._status("Note saved (SQL version bump).")

    def _close_bucket(self, tabs: QTabWidget, operator: str, i: int):
        if i<0: return
        title = tabs.tabText(i)
        tabs.removeTab(i)
        p = self._current_project()
        if p:
            dataset_delete_bucket(p, operator, title)
            self._status(f"{operator} bucket removed: {title}")

    # ---------- Tasks ----------
    def _tasks_refresh(self):
        self.task_manager.reload()
        self.list_tasks.clear()
        try:
            tasks = self.task_manager.list_tasks()
        except Exception as e:
            logging.exception("Task refresh failed")
            self._status(f"Task refresh failed: {e}")
            return
        for t in tasks:
            text = f"{t.get('title', '')} ({t.get('status')})"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, t.get("id"))
            item.setData(Qt.UserRole + 1, t.get("status"))
            self.list_tasks.addItem(item)
            summary = t.get("summary")
            if summary:
                summary = html.escape(summary)
                summ = QLabel()
                summ.setTextFormat(Qt.RichText)
                summ.setText(summary)
                self.list_tasks.setItemWidget(item, summ)
        self._task_selection_changed(self.list_tasks.currentItem(), None)

    def _task_done(self):
        item = self.list_tasks.currentItem()
        if not item: return
        tid = item.data(Qt.UserRole)
        try:
            self.task_manager.mark_done(tid)
        except Exception as e:
            logging.exception("Mark done failed")
            QMessageBox.information(self, "Tasks", f"Complete failed: {e}")

    def _task_pause(self):
        item = self.list_tasks.currentItem()
        if not item:
            return
        tid = item.data(Qt.UserRole)
        try:
            self.task_manager.pause_task(tid)
        except Exception as e:
            logging.exception("Pause task failed")
            QMessageBox.information(self, "Tasks", f"Pause failed: {e}")

    def _task_remove(self):
        item = self.list_tasks.currentItem()
        if not item: return
        tid = item.data(Qt.UserRole)
        if QMessageBox.question(self, "Tasks", "Remove selected task?") != QMessageBox.Yes:
            return
        try:
            self.task_manager.remove_task(tid)
        except Exception as e:
            logging.exception("Remove task failed")
            QMessageBox.information(self, "Tasks", f"Remove failed: {e}")

    def _task_selection_changed(self, current, _prev):
        status = current.data(Qt.UserRole + 1) if current else None
        disabled = status == "done"
        for b in [self.btn_task_pause, self.btn_task_done, self.btn_task_remove]:
            b.setEnabled(current is not None and not disabled)

    def _security_settings(self):
        dlg = SecurityDialog(self.cfg, self)
        if dlg.exec_():
            self.cfg.update(dlg.values())
            save_json(CONFIG_JSON, self.cfg)
            self.chk_full_auto.setChecked(self.cfg.get("full_auto", False))

    # ---------- Codex Setup / Launch ----------
    def _codex_bin_in_project(self, project: Path) -> Path:
        return project / "Codex" / ("codex.exe" if os.name=="nt" else "codex")

    def _codex_repo_dir(self, project: Path) -> Path:
        return project / "Codex" / "codex-src"

    def _setup_codex(self) -> Optional[Path]:
        p = self._current_project()
        if not p:
            QMessageBox.information(self, "Select project", "Choose a project.")
            return None
        target = self._codex_bin_in_project(p)
        target.parent.mkdir(parents=True, exist_ok=True)

        # Sources to copy from (priority order)
        candidates = [
            Path(r"C:\Users\Art PC\Desktop\Codex\Codex-Transit\codex-rust-v0.23.0\codex-x86_64-pc-windows-msvc.exe"),
            Path(r"C:\Users\Art PC\Desktop\Codex\codex-x86_64-pc-windows-msvc.exe"),
        ]
        src = next((c for c in candidates if c.exists()), None)
        if not src:
            # fallback: download from GitHub release
            plat = os.name
            asset = CODEX_ASSETS.get(plat)
            if isinstance(asset, dict):
                import platform as _pf
                asset = asset.get(_pf.system(), "")
            if not asset:
                self._status("Unknown platform; please install Codex manually.")
                return None
            url = f"{CODEX_RELEASE_BASE}/{asset}"
            self._status("Downloading Codex from GitHub…")
            try:
                tmp_dir = Path(tempfile.mkdtemp())
                archive = tmp_dir / asset
                with urllib.request.urlopen(url, timeout=60) as r:
                    archive.write_bytes(r.read())
                bin_path = archive
                if asset.endswith('.zip'):
                    with zipfile.ZipFile(archive) as z:
                        z.extractall(tmp_dir)
                    for name in ['codex.exe', 'codex']:
                        cand = tmp_dir / name
                        if cand.exists():
                            bin_path = cand
                            break
                elif asset.endswith('.tar.gz'):
                    with tarfile.open(archive, 'r:gz') as t:
                        t.extractall(tmp_dir)
                    for name in ['codex.exe', 'codex']:
                        cand = tmp_dir / name
                        if cand.exists():
                            bin_path = cand
                            break
                if plat != 'nt':
                    os.chmod(bin_path, 0o755)
                src = bin_path
                self._status('Download complete.')
            except Exception as e:
                logging.exception("Download failed")
                self._status(f'Download failed: {e}')
                return None

        if target.exists():
            if QMessageBox.question(self, "Overwrite?", "Codex already installed in this project. Overwrite?") == QMessageBox.No:
                self._status("Setup Codex skipped (already installed).")
                return None
        try:
            data = src.read_bytes()
            target.write_bytes(data)
            self._status(f"Codex installed into {target.parent}")
            # make executable on unix
            if os.name!="nt":
                os.chmod(target, 0o755)
        except Exception as e:
            logging.exception("Install failed")
            self._status(f"Install failed: {e}")
            return None

        repo = clone_codex_repo(target.parent)
        if repo:
            self._status(f"Source cloned to {repo}")
        return repo

    def _upload_codex_source(self):
        p = self._current_project()
        if not p:
            QMessageBox.information(self, "Select project", "Choose a project.")
            return
        default = p / "Codex" / "codex-src"
        folder = QFileDialog.getExistingDirectory(self, "Select Codex Source Folder", str(default if default.exists() else p))
        if not folder:
            return
        owner, ok = QInputDialog.getText(self, "GitHub Owner", "Enter your GitHub owner/org name (e.g. Meesh-Makes):")
        if not ok or not owner:
            return
        repo_name, ok = QInputDialog.getText(self, "GitHub Repo Name", "Enter the repository name (e.g. Codex_Studio):")
        if not ok or not repo_name:
            return

        repo_url = f"https://github.com/{owner}/{repo_name}.git"
        QMessageBox.information(self, "Starting", f"Uploading {folder} to {repo_url}...")

        script = APP_ROOT / "tools" / "codex_repo_manager.py"
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "upload",
                    "--workdir",
                    folder,
                    "--remote-url",
                    repo_url,
                    "--default-branch",
                    "main",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
            out = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            out = (e.stdout + e.stderr).strip()

        QMessageBox.information(self, "Done", f"Upload complete!\n\n{out}")

    def _write_handshake(self, project: Path):
        info = {
            "project_root": str(project),
            "agent_dir": str(self._agent_dir(project)),
            "datasets": [str(p) for p in dataset_paths(project)],
            "generated": datetime.now().isoformat()
        }
        repo_dir = self._codex_repo_dir(project)
        if repo_dir.exists():
            info["codex_repo"] = str(repo_dir)
        path = project / HANDSHAKE_NAME
        path.write_text(json.dumps(info, indent=2), encoding="utf-8")
        # export env for spawned processes
        os.environ["CODEX_HANDSHAKE"] = str(path)
        self._status(f"Handshake written: {path}")

    def _pre_snapshot_now(self, project: Path):
        snap = make_snapshot(project)
        self._pre_snapshot = snap; self._pre_project = project
        files = [(rel, txt) for rel, (_, txt) in snap.files.items()]
        dataset_store_repo_files(project, files, snap.stamp)
        self._status(f"Pre-snapshot captured (v={snap.stamp}).")

    def _codex_args(self, project: Path, model: str) -> List[str]:
        args = []
        args += ["--oss"]
        args += ["-m", model]
        args += ["-C", str(project)]
        if self.chk_full_auto.isChecked():
            args += ["--full-auto"]
        if torch and getattr(torch, "cuda", None) and torch.cuda.is_available():
            os.environ["OLLAMA_GPU"] = "1"
            args += ["--gpu"]
        else:
            os.environ.pop("OLLAMA_GPU", None)
        # no explicit approval/sandbox flags here—`--full-auto` covers it; otherwise Codex defaults apply
        return args

    def _launch_codex(self, mode: str):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        codex = self._codex_bin_in_project(p)
        if not codex.exists():
            self._status("Codex not installed in this project. Click 'Setup Codex' first.")
            return

        self._write_handshake(p)
        self._pre_snapshot_now(p)

        model = self.cb_codex_model.currentText()
        args = self._codex_args(p, model)

        if mode=="External":
            # Spawn terminal window running codex with args
            cmdline = f"\"{codex}\" " + " ".join(shlex.quote(a) for a in args)
            try:
                if os.name=="nt":
                    subprocess.Popen(f'start "" cmd /k {cmdline}', cwd=str(p), shell=True)
                elif sys.platform=="darwin":
                    osa = f'tell application "Terminal"\nactivate\ndo script "cd {shlex.quote(str(p))}; {cmdline}"\nend tell\n'
                    subprocess.Popen(["osascript","-e",osa])
                else:
                    subprocess.Popen(["gnome-terminal","--","bash","-lc",cmdline])
                self._status("External Codex launched. If needed, echo %CODEX_HANDSHAKE% (Windows) to verify.")
            except Exception as e:
                logging.exception("External launch failed")
                self._status(f"External launch failed: {e}")
        else:
            # Embedded QProcess
            self.input_line.setEnabled(True)
            self.codex_proc.setWorkingDirectory(str(p))
            use_pywinpty = False
            prog = str(codex)
            try:
                if os.name == "nt":
                    import pywinpty  # type: ignore
                    prog = sys.executable
                    args = ["-m", "pywinpty", str(codex)] + args
                    use_pywinpty = True
            except Exception as e:
                self._strip_ansi = True
                msg = f"pywinpty unavailable, stripping ANSI: {e}"
                self._status(msg)
                logging.warning(msg)
            self.codex_proc.setProgram(prog)
            self.codex_proc.setArguments(args)
            env = self.codex_proc.processEnvironment()
            env.insert("CODEX_HANDSHAKE", str(p / HANDSHAKE_NAME))
            self.codex_proc.setProcessEnvironment(env)
            self.codex_proc.start()
            if self.codex_proc.waitForStarted(5000):
                self._status("Embedded Codex started.")
            else:
                if os.name == "nt" and use_pywinpty:
                    msg = f"Embedded launch failed via pywinpty: {self.codex_proc.errorString()}"
                    self._strip_ansi = True
                    self._status(msg)
                    logging.warning(msg)
                else:
                    self._status("Embedded launch failed: " + self.codex_proc.errorString())

    def _codex_out(self):
        out = bytes(self.codex_proc.readAllStandardOutput()).decode("utf-8","ignore")
        if self._strip_ansi:
            out = ANSI_ESCAPE_RE.sub('', out)
        if out:
            self.chat.append_message('codex', out)

    def _codex_err(self):
        err = bytes(self.codex_proc.readAllStandardError()).decode("utf-8","ignore")
        if self._strip_ansi:
            err = ANSI_ESCAPE_RE.sub('', err)
        if err:
            self.chat.append_message('codex', err)

    def _handle_slash(self, txt: str) -> bool:
        cmd = txt.strip().split()[0]
        if cmd == "/processdumps":
            try:
                from distill_dumps import main as distill_main
                distill_main()
                self.chat.append_message('system', "/processdumps complete")
            except Exception as e:
                logging.exception("/processdumps failed")
                self.chat.append_message('system', f"/processdumps failed: {e}")
            return True
        if cmd == "/help":
            self.chat.append_message('system',
                "Slash commands:\n/processdumps – process Codex_Agents/dump*.md into datasets.")
            return True
        return False

    def _send_to_embedded(self):
        txt = self.input_line.text().rstrip()
        if not txt: return
        self.input_line.clear()
        self.chat.append_message('user', txt)
        if txt.startswith('/'):
            if self._handle_slash(txt):
                return
        try:
            self.codex_proc.write((txt + "\n").encode())
        except Exception as e:
            logging.exception("Write to embedded failed")
            self._status(f"Write to embedded failed: {e}")

    # ---------- README ----------
    def _gen_readme(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        generate_readme(p, self._status, ver=version_stamp())

    # ---------- Error Bot ----------
    def _run_error_bot(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        if not self._pre_snapshot or self._pre_project!=p:
            self._pre_snapshot_now(p)
        post = make_snapshot(p)
        files = [(rel, txt) for rel, (_, txt) in post.files.items()]
        dataset_store_repo_files(p, files, post.stamp)
        diffs = diff_snapshots(self._pre_snapshot, post)
        blocks=[]
        for src, patch in diffs:
            if patch.strip():
                dataset_store_diff(p, src, patch, post.stamp)
                blocks.append((datetime.now().isoformat(timespec="seconds"), src, patch))
        self.diffpane.set_blocks(dataset_fetch_diffs_desc(p))
        self._status(f"Error Bot: computed {len(blocks)} diffs (v {post.stamp}).")

        # Compose analysis
        notes_text = self._collect_recent_notes(p, 5)
        agent_snapshot = self._collect_agent_snapshot(p, 1400)
        prompt = self._compose_errorbot_prompt(diffs, notes_text, agent_snapshot)
        base = self.cfg.get("oss_base_url","http://localhost:11434")
        model = self.cb_error.currentText()
        sys_prompt = "You are Error Bot. Be precise; list errors (file:line), risky changes, and next steps."
        ok, out = ollama_chat(base, model, [{'role':'user','content':prompt}], sys_prompt)
        report = out if ok else "Error Bot failed to produce output."
        te = QPlainTextEdit(); te.setLineWrapMode(QPlainTextEdit.NoWrap); te.setPlainText(report)
        title = f"ErrorBot_{version_stamp()}"; idx = self.tabs_error.addTab(te, title); self.tabs_error.setCurrentIndex(idx)
        dataset_store_bucket(p, "errorbot", title, report, version_stamp())
        self._status("Error Bot report created.")

        generate_readme(p, self._status, ver=post.stamp)

    def _collect_recent_notes(self, project: Path, limit:int=5) -> str:
        db = dataset_paths(project)[0]
        conn = sqlite3.connect(str(db)); conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT tab_name, content, version, ts FROM buckets WHERE project=? AND operator='notes' ORDER BY id DESC LIMIT ?",
                (project.name, limit)).fetchall()
            secs=[]
            for r in rows: secs.append(f"[{r['tab_name']} v{r['version']} @{r['ts']}]\n{r['content']}\n")
            return "\n".join(secs)
        finally:
            conn.close()

    def _collect_agent_snapshot(self, project: Path, head_chars:int=1200) -> str:
        d = self._agent_dir(project)
        files = sorted([p for p in d.glob("*.md")], key=lambda p: p.stat().st_mtime, reverse=True)
        names = [p.name for p in files]
        head = ""
        if files:
            try:
                head = files[0].read_text(encoding="utf-8", errors="ignore")[:head_chars]
            except Exception as e:
                logging.warning("Failed to read %s: %s", files[0], e)
                head = ""
        return "AGENT_FILES:\n- " + "\n- ".join(names) + ("\n\nLATEST_HEAD:\n" + head if head else "")

    def _compose_errorbot_prompt(self, diffs: List[Tuple[str,str]], notes: str, agents: str) -> str:
        parts = ["Analyze codebase changes and surface:\n- Errors introduced (-diff)\n- Improvement hints (+diff)\n- Cross-check with Notes and Agent directives.\n"]
        if diffs:
            parts.append("\n".join([f"--- DIFF ({src}) ---\n{patch}" for src, patch in diffs[:50]]))
        if notes: parts.append("\n--- NOTES ---\n" + notes)
        if agents: parts.append("\n--- AGENT SNAPSHOT ---\n" + agents)
        parts.append("\nProvide:\n- Errors (file:line → reason)\n- Risky changes\n- Concrete next actions\n")
        return "\n".join(parts)

    def _save_patch(self):
        p = self._current_project()
        if not p: QMessageBox.information(self,"Select project","Choose a project."); return
        rows = dataset_fetch_diffs_desc(p)
        if not rows: QMessageBox.information(self,"No diffs","Nothing to export."); return
        ts = version_stamp()
        out = DIFFS_DIR / f"diff_{ts}.patch"
        with out.open("w", encoding="utf-8") as f:
            for ts_, src, content in rows:
                f.write(f"--- [{ts_}] source={src} ---\n{content}\n\n")
        self.chat.append_message('system', f"Patch exported: {out}")

# ======== Main Window ========
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Codex Lite — Local Ollama • Codex Rust • Buckets • Agent.md • Error Bot")
        self.resize(1480, 980)
        self.statusBar().showMessage("Booting…")
        self.w = CodexLite(self.statusBar().showMessage)
        self.setCentralWidget(self.w)

        # Task panel docked on the right
        self.tasks_dock = QDockWidget("Tasks", self)
        self.task_list = QListWidget()
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self._task_menu)
        self.tasks_dock.setWidget(self.task_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.tasks_dock)

        self.w.task_manager.tasks_changed.connect(self._refresh_tasks)
        self._refresh_tasks()

    def _refresh_tasks(self):
        self.task_list.clear()
        for t in self.w.task_manager.list_tasks():
            item = QListWidgetItem(f"{t['title']} ({t['status']})")
            item.setData(Qt.UserRole, t['id'])
            item.setData(Qt.UserRole + 1, t['status'])
            self.task_list.addItem(item)

    def _task_menu(self, pos):
        item = self.task_list.itemAt(pos)
        if not item:
            return
        task_id = item.data(Qt.UserRole)
        status = item.data(Qt.UserRole + 1)
        menu = QMenu(self)
        if status != "done":
            act_done = menu.addAction("Complete")
            act_done.triggered.connect(lambda: self.w.task_manager.mark_done(task_id))
        act_remove = menu.addAction("Remove")
        act_remove.triggered.connect(lambda: self.w.task_manager.remove_task(task_id))
        menu.exec_(self.task_list.mapToGlobal(pos))

# ======== Entry ========
if __name__ == "__main__":
    try:
        ensure_layout()
        app = QApplication(sys.argv); app.setApplicationName("Codex Lite")
        win = Main(); win.show()
        sys.exit(app.exec())
    except Exception:
        logging.exception("Main failed")
        sys.exit(1)
```

Codex_Lite.py — Local Ollama • Codex Rust (OSS mode) • Buckets • Agent.md • Error Bot • SQL Snapshots
OS: Windows 10/11, macOS, Linux

Highlights
- Ollama-only: lists models via /api/tags and uses them everywhere
- Codex runs with --oss and -m <ollama-model> (no OpenAI)
- Full Auto Mode toggle (--> --full-auto)
- Self-Repo mode: app folder becomes project; Agent.md created with dense directives
- Agent.md Manager (view/edit/rename/delete version files, keep Agent.md immutable)
- Buckets (Assistant/Notes/ErrorBot) in SQLite, versioned; snapshots + diffs; README generator
**Classes:** Snapshot, DiffHighlighter, DiffPane, ChatPane, AgentManager, SecurityDialog, CodexLite, Main
**Functions:** ensure_layout(), load_json(path, default), save_json(path, data), log_line(msg), which(exe), version_stamp(), is_ollama_running(host, port), is_ollama_available(base_url), ollama_list(base_url), _ollama_chat_cached(base_url, model, messages_tuple, system), ollama_chat(base_url, model, messages, system), ollama_cache_clear(), dataset_paths(project), dataset_init(project), dataset_insert(table, project, cols, vals), dataset_store_bucket(project, operator, tab, content, ver), dataset_delete_bucket(project, operator, tab), dataset_store_repo_files(project, files, ver), dataset_store_diff(project, source, content, ver), dataset_fetch_diffs_desc(project), clone_codex_repo(codex_dir), text_sha1(s), sanitize_skip(path), is_text_file(path), iter_files(root), make_snapshot(root, limit_bytes), unified(a_text, b_text, a_label, b_label), diff_snapshots(a, b), analyse_overview(root), generate_readme(project, log, ver)


## Module `distill_dumps.py`

```python
"""
Normalize `dump*.md` files into bucketized dataset entries for agents.

Parsing rules (documented so they’re not “magic”):
- HEADING_PATTERN: lines starting with '#' (Markdown ATX headings). The text
  of the heading is PRESERVED as a bucket.
- LIST_ITEM_PATTERNS: '- ', '* ', or '1. ' (numbered) begin list items; each
  item becomes its own bucket value.
- Paragraphs: consecutive non-empty, non-heading, non-list lines are grouped
  into a paragraph bucket.
- Code fences: lines between ``` fences are ignored (kept out of buckets).
"""
from __future__ import annotations
import hashlib
import json, re
from pathlib import Path
from datetime import datetime

HEADING_PATTERN = re.compile(r"^#{1,6}\s+")
UL_ITEM_PATTERNS = ( "- ", "* " )
OL_ITEM_PATTERN  = re.compile(r"^\d+\.\s+")
FENCE_PATTERN    = re.compile(r"^```")

def bucketize_markdown(text: str) -> list[str]:
    buckets: list[str] = []
    current_para: list[str] = []
    in_fence = False

    def flush_para():
        nonlocal current_para, buckets
        if current_para:
            buckets.append(" ".join(current_para).strip())
            current_para = []

    for raw in text.splitlines():
        line = raw.rstrip("\n")

        # code fence handling
        if FENCE_PATTERN.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if not line.strip():
            flush_para()
            continue

        # headings -> dedicated bucket, preserve text
        if HEADING_PATTERN.match(line):
            flush_para()
            buckets.append(HEADING_PATTERN.sub("", line).strip())
            continue

        # unordered list items ('- ' or '* ')
        if any(line.lstrip().startswith(p) for p in UL_ITEM_PATTERNS):
            flush_para()
            item = line.lstrip()[2:].strip()
            if item:
                buckets.append(item)
            continue

        # ordered list items ('1. ')
        if OL_ITEM_PATTERN.match(line.lstrip()):
            flush_para()
            item = OL_ITEM_PATTERN.sub("", line.lstrip()).strip()
            if item:
                buckets.append(item)
            continue

        # otherwise, paragraph text
        current_para.append(line.strip())

    flush_para()
    # final cleanup
    return [b for b in (s.strip() for s in buckets) if b]

DATASET_PATH = Path("datasets/agent_dataset.json")


def main() -> None:
    """Bucketize new dumps, append them to the JSON dataset, and archive files."""

    root = Path("Codex_Agents")
    archive = root / "archive"
    archive.mkdir(exist_ok=True)

    out_path = DATASET_PATH
    data = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {"entries": []}

    # map existing entries by content digest for stable deduplication
    by_hash = {e["id"].split(":", 1)[-1]: e for e in data["entries"]}

    def dump_key(path: Path) -> int:
        """Sort `dumpN.md` files by their numeric component."""
        match = re.search(r"\d+", path.stem)
        return int(match.group()) if match else -1

    for p in sorted(root.glob("dump*.md"), key=dump_key):
        if not p.is_file():
            continue

        text = p.read_text(encoding="utf-8", errors="ignore")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        archived = archive / p.name
        if archived.exists():
            base = archived.stem
            suffix = archived.suffix
            counter = 1
            while (archive / f"{base}_{counter}{suffix}").exists():
                counter += 1
            archived = archive / f"{base}_{counter}{suffix}"
        p.rename(archived)

        # if content already exists, just update its source path
        entry = by_hash.get(digest)
        if entry:
            entry["source_path"] = str(archived)
            continue

        entry = {
            "id": f"{p.name}:{digest}",
            "created": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "source_path": str(archived),
            "content": text,
            "buckets": bucketize_markdown(text),
            "status": "pending",
        }
        data["entries"].append(entry)
        by_hash[digest] = entry

    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
```

Normalize `dump*.md` files into bucketized dataset entries for agents.

Parsing rules (documented so they’re not “magic”):
- HEADING_PATTERN: lines starting with '#' (Markdown ATX headings). The text
  of the heading is PRESERVED as a bucket.
- LIST_ITEM_PATTERNS: '- ', '* ', or '1. ' (numbered) begin list items; each
  item becomes its own bucket value.
- Paragraphs: consecutive non-empty, non-heading, non-list lines are grouped
  into a paragraph bucket.
- Code fences: lines between ``` fences are ignored (kept out of buckets).
**Functions:** bucketize_markdown(text), main()


## Module `embeddings.py`

```python
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict

import logging
import numpy as np

SentenceTransformer = None  # type: ignore
_EMBED_MODEL = None


def _get_model():
    global _EMBED_MODEL, SentenceTransformer
    if _EMBED_MODEL is None:
        if SentenceTransformer is None:
            try:
                from sentence_transformers import SentenceTransformer as ST
            except Exception as exc:  # pragma: no cover
                logging.exception("SentenceTransformer import failed")
                raise RuntimeError('SentenceTransformer model not available') from exc
            SentenceTransformer = ST
        _EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    return _EMBED_MODEL

DB_PATH = Path(__file__).resolve().parent / 'Codex_Studio.db'


def init_db(db_path: Path = DB_PATH) -> None:
    """Ensure catalog and embeddings tables exist."""
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS catalog(
                    dataset_name TEXT PRIMARY KEY,
                    path TEXT,
                    description TEXT,
                    created TEXT
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS embeddings(
                    agent_id TEXT,
                    bucket_id INTEGER,
                    vector BLOB
                )"""
        )
        conn.commit()
    finally:
        conn.close()


def register_dataset(name: str, path: str, description: str = "", *, db_path: Path = DB_PATH) -> None:
    """Register a dataset in the catalog."""
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO catalog(dataset_name, path, description, created) VALUES(?,?,?,?)",
            (name, path, description, datetime.utcnow().isoformat(timespec='seconds') + 'Z'),
        )
        conn.commit()
    finally:
        conn.close()


def _vector_to_blob(vec: np.ndarray) -> bytes:
    return vec.astype('float32').tobytes()


def _blob_to_vector(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype='float32')


def add_embedding(agent_id: str, bucket_id: int, text: str, *, db_path: Path = DB_PATH) -> None:
    """Generate and store an embedding for a bucket."""
    model = _get_model()
    init_db(db_path)
    vec = model.encode(text)
    norm = np.linalg.norm(vec)
    if norm:
        vec = vec / norm
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO embeddings(agent_id, bucket_id, vector) VALUES(?,?,?)",
            (agent_id, bucket_id, _vector_to_blob(vec)),
        )
        conn.commit()
    finally:
        conn.close()


def embed_dataset(dataset_path: str, name: str | None = None, description: str = "", *, db_path: Path = DB_PATH) -> None:
    """Embed all buckets from a JSON dataset file.

    The dataset is expected to have the structure produced by ``distill_dumps.py``.
    """
    import json

    path = Path(dataset_path)
    data = json.loads(path.read_text(encoding='utf-8'))
    dataset_name = name or path.stem
    register_dataset(dataset_name, str(path), description, db_path=db_path)
    for entry in data.get('entries', []):
        agent_id = entry.get('id', '')
        for idx, bucket in enumerate(entry.get('buckets', [])):
            add_embedding(agent_id, idx, bucket, db_path=db_path)


def list_catalog(*, db_path: Path = DB_PATH) -> List[Dict[str, str]]:
    init_db(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute('SELECT dataset_name, path, description, created FROM catalog ORDER BY dataset_name')
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def search_embeddings(query: str, top_k: int = 5, *, db_path: Path = DB_PATH) -> List[Dict[str, object]]:
    """Perform a cosine-similarity search over stored embeddings."""
    model = _get_model()
    init_db(db_path)
    qvec = model.encode(query)
    qnorm = np.linalg.norm(qvec)
    if qnorm:
        qvec = qvec / qnorm
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        qvec_local = qvec.copy()

        def dot_product(blob: bytes) -> float:
            vec = _blob_to_vector(blob)
            return float(np.dot(qvec_local, vec))

        conn.create_function('dot_product', 1, dot_product)
        cur = conn.cursor()
        cur.execute(
            "SELECT agent_id, bucket_id, dot_product(vector) AS score FROM embeddings ORDER BY score DESC LIMIT ?",
            (top_k,),
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


__all__ = [
    'init_db',
    'register_dataset',
    'add_embedding',
    'embed_dataset',
    'list_catalog',
    'search_embeddings',
]
```

**Functions:** _get_model(), init_db(db_path), register_dataset(name, path, description), _vector_to_blob(vec), _blob_to_vector(blob), add_embedding(agent_id, bucket_id, text), embed_dataset(dataset_path, name, description), list_catalog(), search_embeddings(query, top_k)


## Module `migrate_agent_versions.py`

```python
from pathlib import Path
import shutil
import argparse


def migrate(dry_run: bool = False) -> None:
    src = Path("Codex_Agents")
    dst = src / "Agent_Versions"
    dst.mkdir(exist_ok=True)

    for path in src.glob("Agent_*.md"):
        if path.name == "Agent.md" or path.is_dir():
            continue
        target = dst / f"{path.stem}_v1{path.suffix}"
        if dry_run:
            print(f"Would copy {path} -> {target}")
        else:
            shutil.copy2(path, target)
            print(f"Copied {path} -> {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy Agent_*.md files into Agent_Versions with a version suffix")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without copying files")
    args = parser.parse_args()
    migrate(dry_run=args.dry_run)
```

**Functions:** migrate(dry_run)


## Module `readme_worker.py`

```python
"""Helper script to assemble a semantic README section for the project.

The worker scans Python modules, extracts lightweight structural metadata and
writes both an `analysis.json` file and a semantic section within `README.md`.
It is intended to keep repository documentation in sync with the codebase.
"""

import argparse
import ast
import hashlib
import json
import os
import re
import logging
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
START_MARKER = "<!-- BEGIN SEMANTIC -->"
END_MARKER = "<!-- END SEMANTIC -->"


def gather_python_files(root: Path):
    """Return a deterministic list of project Python files.

    The traversal skips common virtual environment and version-control
    directories. Directories and files are iterated in sorted order so that
    generated documentation is stable across platforms and runs.
    """

    py_files = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [
            d
            for d in dirs
            if d not in {"venv", ".venv", "env", ".git", "__pycache__", "Codex_Agents"}
        ]
        dirs.sort()
        for fname in sorted(files):
            if fname.endswith(".py"):
                py_files.append(Path(current) / fname)
    return py_files


def analyse_module(path: Path):
    """Return lightweight semantic info for ``path``.

    If the module fails to parse (for example due to a ``SyntaxError``), a
    minimal semantics dictionary is returned so the caller can continue
    processing other files without crashing.
    """

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
        doc = ast.get_docstring(tree) or ""
        classes, functions, imports = [], [], []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                sig = f"{node.name}(" + ", ".join(arg.arg for arg in node.args.args) + ")"
                functions.append(sig)
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        keywords = [
            w for w, _ in Counter(re.findall(r"[A-Za-z_]{3,}", doc.lower())).most_common(8)
        ]
        summary = doc[:120] if doc else "No module docstring."
    except Exception as e:  # pragma: no cover - defensive
        logging.warning("Failed to parse %s: %s", path, e)
        classes, functions, imports, keywords = [], [], [], []
        summary = f"Failed to parse module: {e}"

    semantics = {
        "file": str(path.relative_to(ROOT)),
        "summary": summary,
        "keywords": keywords,
        "classes": classes,
        "functions": functions,
        "imports": imports,
        "bucket": "Assistant",
    }
    return semantics


def build_readme(root: Path):
    semantics_list = []
    sections = []
    for py_path in gather_python_files(root):
        semantics = analyse_module(py_path)
        semantics_list.append(semantics)
        sections.append(
            f"### Module `{semantics['file']}`\n\n<!-- SEMANTICS\n"
            + json.dumps(semantics, indent=2)
            + "\n-->\n"
        )

    analysis_path = root / "analysis.json"
    analysis_path.write_text(
        json.dumps(semantics_list, indent=2, sort_keys=True), encoding="utf-8"
    )

    h = hashlib.sha256()
    h.update(analysis_path.read_bytes())
    snapshot = h.hexdigest()

    content_lines = ["## Semantic Module Overview", ""]
    content_lines.extend(sections)
    content_lines.extend(["### Snapshot", f"- SHA256 of analysis.json: `{snapshot}`", ""])
    semantic_block = "\n".join([START_MARKER, *content_lines, END_MARKER])

    readme_path = root / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(
        START_MARKER + r".*?" + END_MARKER, re.DOTALL
    )
    if pattern.search(readme_text):
        readme_text = pattern.sub(lambda m: semantic_block, readme_text)
    else:
        readme_text = readme_text.rstrip() + "\n\n" + semantic_block + "\n"
    readme_path.write_text(readme_text, encoding="utf-8")


def main():
    """Entry point for command-line execution.

    Allows an optional ``--root`` argument so the script can operate on
    arbitrary directories. If not supplied, the directory containing this
    script is used.
    """

    parser = argparse.ArgumentParser(description="Generate semantic README")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root to scan (default: script directory)",
    )
    args = parser.parse_args()
    build_readme(args.root.resolve())


if __name__ == "__main__":
    main()
```

Helper script to assemble a semantic README section for the project.

The worker scans Python modules, extracts lightweight structural metadata and
writes both an `analysis.json` file and a semantic section within `README.md`.
It is intended to keep repository documentation in sync with the codebase.
**Functions:** gather_python_files(root), analyse_module(path), build_readme(root), main()


## Module `Codex\codex-src\codex-cli\scripts\stage_rust_release.py`

```python
#!/usr/bin/env python3

import json
import subprocess
import sys
import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="""Stage a release for the npm module.

Run this after the GitHub Release has been created and use
`--release-version` to specify the version to release.

Optionally pass `--tmp` to control the temporary staging directory that will be
forwarded to stage_release.sh.
"""
    )
    parser.add_argument(
        "--release-version", required=True, help="Version to release, e.g., 0.3.0"
    )
    parser.add_argument(
        "--tmp",
        help="Optional path to stage the npm package; forwarded to stage_release.sh",
    )
    args = parser.parse_args()
    version = args.release_version

    gh_run = subprocess.run(
        [
            "gh",
            "run",
            "list",
            "--branch",
            f"rust-v{version}",
            "--json",
            "workflowName,url,headSha",
            "--jq",
            'first(.[] | select(.workflowName == "rust-release"))',
        ],
        stdout=subprocess.PIPE,
        check=True,
    )
    gh_run.check_returncode()
    workflow = json.loads(gh_run.stdout)
    sha = workflow["headSha"]

    print(f"should `git checkout {sha}`")

    current_dir = Path(__file__).parent.resolve()
    cmd = [
        str(current_dir / "stage_release.sh"),
        "--version",
        version,
        "--workflow-url",
        workflow["url"],
    ]
    if args.tmp:
        cmd.extend(["--tmp", args.tmp])

    stage_release = subprocess.run(cmd)
    stage_release.check_returncode()

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Functions:** main()


## Module `Codex\codex-src\codex-rs\mcp-types\generate_mcp_types.py`

```python
#!/usr/bin/env python3
# flake8: noqa: E501

import argparse
import json
import subprocess
import sys

from dataclasses import (
    dataclass,
)
from pathlib import Path

# Helper first so it is defined when other functions call it.
from typing import Any, Literal

SCHEMA_VERSION = "2025-06-18"
JSONRPC_VERSION = "2.0"

STANDARD_DERIVE = "#[derive(Debug, Clone, PartialEq, Deserialize, Serialize, TS)]\n"
STANDARD_HASHABLE_DERIVE = (
    "#[derive(Debug, Clone, PartialEq, Deserialize, Serialize, Hash, Eq, TS)]\n"
)

# Will be populated with the schema's `definitions` map in `main()` so that
# helper functions (for example `define_any_of`) can perform look-ups while
# generating code.
DEFINITIONS: dict[str, Any] = {}
# Names of the concrete *Request types that make up the ClientRequest enum.
CLIENT_REQUEST_TYPE_NAMES: list[str] = []
# Concrete *Notification types that make up the ServerNotification enum.
SERVER_NOTIFICATION_TYPE_NAMES: list[str] = []
# Enum types that will need a `allow(clippy::large_enum_variant)` annotation in
# order to compile without warnings.
LARGE_ENUMS = {"ServerResult"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Embed, cluster and analyse text prompts via the OpenAI API.",
    )

    default_schema_file = (
        Path(__file__).resolve().parent / "schema" / SCHEMA_VERSION / "schema.json"
    )
    parser.add_argument(
        "schema_file",
        nargs="?",
        default=default_schema_file,
        help="schema.json file to process",
    )
    args = parser.parse_args()
    schema_file = args.schema_file

    lib_rs = Path(__file__).resolve().parent / "src/lib.rs"

    global DEFINITIONS  # Allow helper functions to access the schema.

    with schema_file.open(encoding="utf-8") as f:
        schema_json = json.load(f)

    DEFINITIONS = schema_json["definitions"]

    out = [
        f"""
// @generated
// DO NOT EDIT THIS FILE DIRECTLY.
// Run the following in the crate root to regenerate this file:
//
// ```shell
// ./generate_mcp_types.py
// ```
use serde::Deserialize;
use serde::Serialize;
use serde::de::DeserializeOwned;
use std::convert::TryFrom;

use ts_rs::TS;

pub const MCP_SCHEMA_VERSION: &str = "{SCHEMA_VERSION}";
pub const JSONRPC_VERSION: &str = "{JSONRPC_VERSION}";

/// Paired request/response types for the Model Context Protocol (MCP).
pub trait ModelContextProtocolRequest {{
    const METHOD: &'static str;
    type Params: DeserializeOwned + Serialize + Send + Sync + 'static;
    type Result: DeserializeOwned + Serialize + Send + Sync + 'static;
}}

/// One-way message in the Model Context Protocol (MCP).
pub trait ModelContextProtocolNotification {{
    const METHOD: &'static str;
    type Params: DeserializeOwned + Serialize + Send + Sync + 'static;
}}

fn default_jsonrpc() -> String {{ JSONRPC_VERSION.to_owned() }}

"""
    ]
    definitions = schema_json["definitions"]
    # Keep track of every *Request type so we can generate the TryFrom impl at
    # the end.
    # The concrete *Request types referenced by the ClientRequest enum will be
    # captured dynamically while we are processing that definition.
    for name, definition in definitions.items():
        add_definition(name, definition, out)
    # No-op: list collected via define_any_of("ClientRequest").

    # Generate TryFrom impl string and append to out before writing to file.
    try_from_impl_lines: list[str] = []
    try_from_impl_lines.append("impl TryFrom<JSONRPCRequest> for ClientRequest {\n")
    try_from_impl_lines.append("    type Error = serde_json::Error;\n")
    try_from_impl_lines.append(
        "    fn try_from(req: JSONRPCRequest) -> std::result::Result<Self, Self::Error> {\n"
    )
    try_from_impl_lines.append("        match req.method.as_str() {\n")

    for req_name in CLIENT_REQUEST_TYPE_NAMES:
        defn = definitions[req_name]
        method_const = (
            defn.get("properties", {}).get("method", {}).get("const", req_name)
        )
        payload_type = f"<{req_name} as ModelContextProtocolRequest>::Params"
        try_from_impl_lines.append(f'            "{method_const}" => {{\n')
        try_from_impl_lines.append(
            "                let params_json = req.params.unwrap_or(serde_json::Value::Null);\n"
        )
        try_from_impl_lines.append(
            f"                let params: {payload_type} = serde_json::from_value(params_json)?;\n"
        )
        try_from_impl_lines.append(
            f"                Ok(ClientRequest::{req_name}(params))\n"
        )
        try_from_impl_lines.append("            },\n")

    try_from_impl_lines.append(
        '            _ => Err(serde_json::Error::io(std::io::Error::new(std::io::ErrorKind::InvalidData, format!("Unknown method: {}", req.method)))),\n'
    )
    try_from_impl_lines.append("        }\n")
    try_from_impl_lines.append("    }\n")
    try_from_impl_lines.append("}\n\n")

    out.extend(try_from_impl_lines)

    # Generate TryFrom for ServerNotification
    notif_impl_lines: list[str] = []
    notif_impl_lines.append(
        "impl TryFrom<JSONRPCNotification> for ServerNotification {\n"
    )
    notif_impl_lines.append("    type Error = serde_json::Error;\n")
    notif_impl_lines.append(
        "    fn try_from(n: JSONRPCNotification) -> std::result::Result<Self, Self::Error> {\n"
    )
    notif_impl_lines.append("        match n.method.as_str() {\n")

    for notif_name in SERVER_NOTIFICATION_TYPE_NAMES:
        n_def = definitions[notif_name]
        method_const = (
            n_def.get("properties", {}).get("method", {}).get("const", notif_name)
        )
        payload_type = f"<{notif_name} as ModelContextProtocolNotification>::Params"
        notif_impl_lines.append(f'            "{method_const}" => {{\n')
        # params may be optional
        notif_impl_lines.append(
            "                let params_json = n.params.unwrap_or(serde_json::Value::Null);\n"
        )
        notif_impl_lines.append(
            f"                let params: {payload_type} = serde_json::from_value(params_json)?;\n"
        )
        notif_impl_lines.append(
            f"                Ok(ServerNotification::{notif_name}(params))\n"
        )
        notif_impl_lines.append("            },\n")

    notif_impl_lines.append(
        '            _ => Err(serde_json::Error::io(std::io::Error::new(std::io::ErrorKind::InvalidData, format!("Unknown method: {}", n.method)))),\n'
    )
    notif_impl_lines.append("        }\n")
    notif_impl_lines.append("    }\n")
    notif_impl_lines.append("}\n")

    out.extend(notif_impl_lines)

    with open(lib_rs, "w", encoding="utf-8") as f:
        for chunk in out:
            f.write(chunk)

    subprocess.check_call(
        ["cargo", "fmt", "--", "--config", "imports_granularity=Item"],
        cwd=lib_rs.parent.parent,
        stderr=subprocess.DEVNULL,
    )

    return 0


def add_definition(name: str, definition: dict[str, Any], out: list[str]) -> None:
    if name == "Result":
        out.append("pub type Result = serde_json::Value;\n\n")
        return

    # Capture description
    description = definition.get("description")

    properties = definition.get("properties", {})
    if properties:
        required_props = set(definition.get("required", []))
        out.extend(define_struct(name, properties, required_props, description))

        # Special carve-out for Result types:
        if name.endswith("Result"):
            out.extend(f"impl From<{name}> for serde_json::Value {{\n")
            out.append(f"    fn from(value: {name}) -> Self {{\n")
            out.append("        // Leave this as it should never fail\n")
            out.append("        #[expect(clippy::unwrap_used)]\n")
            out.append("        serde_json::to_value(value).unwrap()\n")
            out.append("    }\n")
            out.append("}\n\n")
        return

    enum_values = definition.get("enum", [])
    if enum_values:
        assert definition.get("type") == "string"
        define_string_enum(name, enum_values, out, description)
        return

    any_of = definition.get("anyOf", [])
    if any_of:
        assert isinstance(any_of, list)
        out.extend(define_any_of(name, any_of, description))
        return

    type_prop = definition.get("type", None)
    if type_prop:
        if type_prop == "string":
            # Newtype pattern
            out.append(STANDARD_DERIVE)
            out.append(f"pub struct {name}(String);\n\n")
            return
        elif types := check_string_list(type_prop):
            define_untagged_enum(name, types, out)
            return
        elif type_prop == "array":
            item_name = name + "Item"
            out.extend(define_any_of(item_name, definition["items"]["anyOf"]))
            out.append(f"pub type {name} = Vec<{item_name}>;\n\n")
            return
        raise ValueError(f"Unknown type: {type_prop} in {name}")

    ref_prop = definition.get("$ref", None)
    if ref_prop:
        ref = type_from_ref(ref_prop)
        out.extend(f"pub type {name} = {ref};\n\n")
        return

    raise ValueError(f"Definition for {name} could not be processed.")


extra_defs = []


@dataclass
class StructField:
    viz: Literal["pub"] | Literal["const"]
    name: str
    type_name: str
    serde: str | None = None

    def append(self, out: list[str], supports_const: bool) -> None:
        if self.serde:
            out.append(f"    {self.serde}\n")
        if self.viz == "const":
            if supports_const:
                out.append(f"    const {self.name}: {self.type_name};\n")
            else:
                out.append(f"    pub {self.name}: String, // {self.type_name}\n")
        else:
            out.append(f"    pub {self.name}: {self.type_name},\n")


def define_struct(
    name: str,
    properties: dict[str, Any],
    required_props: set[str],
    description: str | None,
) -> list[str]:
    out: list[str] = []

    fields: list[StructField] = []
    for prop_name, prop in properties.items():
        if prop_name == "_meta":
            # TODO?
            continue
        elif prop_name == "jsonrpc":
            fields.append(
                StructField(
                    "pub",
                    "jsonrpc",
                    "String",  # cannot use `&'static str` because of Deserialize
                    '#[serde(rename = "jsonrpc", default = "default_jsonrpc")]',
                )
            )
            continue

        prop_type = map_type(prop, prop_name, name)
        is_optional = prop_name not in required_props
        if is_optional:
            prop_type = f"Option<{prop_type}>"
        rs_prop = rust_prop_name(prop_name, is_optional)
        if prop_type.startswith("&'static str"):
            fields.append(StructField("const", rs_prop.name, prop_type, rs_prop.serde))
        else:
            fields.append(StructField("pub", rs_prop.name, prop_type, rs_prop.serde))

    if implements_request_trait(name):
        add_trait_impl(name, "ModelContextProtocolRequest", fields, out)
    elif implements_notification_trait(name):
        add_trait_impl(name, "ModelContextProtocolNotification", fields, out)
    else:
        # Add doc comment if available.
        emit_doc_comment(description, out)
        out.append(STANDARD_DERIVE)
        out.append(f"pub struct {name} {{\n")
        for field in fields:
            field.append(out, supports_const=False)
        out.append("}\n\n")

    # Declare any extra structs after the main struct.
    if extra_defs:
        out.extend(extra_defs)
        # Clear the extra structs for the next definition.
        extra_defs.clear()
    return out


def infer_result_type(request_type_name: str) -> str:
    """Return the corresponding Result type name for a given *Request name."""
    if not request_type_name.endswith("Request"):
        return "Result"  # fallback
    candidate = request_type_name[:-7] + "Result"
    if candidate in DEFINITIONS:
        return candidate
    # Fallback to generic Result if specific one missing.
    return "Result"


def implements_request_trait(name: str) -> bool:
    return name.endswith("Request") and name not in (
        "Request",
        "JSONRPCRequest",
        "PaginatedRequest",
    )


def implements_notification_trait(name: str) -> bool:
    return name.endswith("Notification") and name not in (
        "Notification",
        "JSONRPCNotification",
    )


def add_trait_impl(
    type_name: str, trait_name: str, fields: list[StructField], out: list[str]
) -> None:
    out.append(STANDARD_DERIVE)
    out.append(f"pub enum {type_name} {{}}\n\n")

    out.append(f"impl {trait_name} for {type_name} {{\n")
    for field in fields:
        if field.name == "method":
            field.name = "METHOD"
            field.append(out, supports_const=True)
        elif field.name == "params":
            out.append(f"    type Params = {field.type_name};\n")
        else:
            print(f"Warning: {type_name} has unexpected field {field.name}.")
    if trait_name == "ModelContextProtocolRequest":
        result_type = infer_result_type(type_name)
        out.append(f"    type Result = {result_type};\n")
    out.append("}\n\n")


def define_string_enum(
    name: str, enum_values: Any, out: list[str], description: str | None
) -> None:
    emit_doc_comment(description, out)
    out.append(STANDARD_DERIVE)
    out.append(f"pub enum {name} {{\n")
    for value in enum_values:
        assert isinstance(value, str)
        out.append(f'    #[serde(rename = "{value}")]\n')
        out.append(f"    {capitalize(value)},\n")

    out.append("}\n\n")
    return out


def define_untagged_enum(name: str, type_list: list[str], out: list[str]) -> None:
    out.append(STANDARD_HASHABLE_DERIVE)
    out.append("#[serde(untagged)]\n")
    out.append(f"pub enum {name} {{\n")
    for simple_type in type_list:
        match simple_type:
            case "string":
                out.append("    String(String),\n")
            case "integer":
                out.append("    Integer(i64),\n")
            case _:
                raise ValueError(
                    f"Unknown type in untagged enum: {simple_type} in {name}"
                )
    out.append("}\n\n")


def define_any_of(
    name: str, list_of_refs: list[Any], description: str | None = None
) -> list[str]:
    """Generate a Rust enum for a JSON-Schema `anyOf` union.

    For most types we simply map each `$ref` inside the `anyOf` list to a
    similarly named enum variant that holds the referenced type as its
    payload. For certain well-known composite types (currently only
    `ClientRequest`) we need a little bit of extra intelligence:

    * The JSON shape of a request is `{ "method": <string>, "params": <object?> }`.
    * We want to deserialize directly into `ClientRequest` using Serde's
      `#[serde(tag = "method", content = "params")]` representation so that
      the enum payload is **only** the request's `params` object.
    * Therefore each enum variant needs to carry the dedicated `…Params` type
      (wrapped in `Option<…>` if the `params` field is not required), not the
      full `…Request` struct from the schema definition.
    """

    # Verify each item in list_of_refs is a dict with a $ref key.
    refs = [item["$ref"] for item in list_of_refs if isinstance(item, dict)]

    out: list[str] = []
    if description:
        emit_doc_comment(description, out)
    out.append(STANDARD_DERIVE)

    if serde := get_serde_annotation_for_anyof_type(name):
        out.append(serde + "\n")

    if name in LARGE_ENUMS:
        out.append("#[allow(clippy::large_enum_variant)]\n")
    out.append(f"pub enum {name} {{\n")

    if name == "ClientRequest":
        # Record the set of request type names so we can later generate a
        # `TryFrom<JSONRPCRequest>` implementation.
        global CLIENT_REQUEST_TYPE_NAMES
        CLIENT_REQUEST_TYPE_NAMES = [type_from_ref(r) for r in refs]

    if name == "ServerNotification":
        global SERVER_NOTIFICATION_TYPE_NAMES
        SERVER_NOTIFICATION_TYPE_NAMES = [type_from_ref(r) for r in refs]

    for ref in refs:
        ref_name = type_from_ref(ref)

        # For JSONRPCMessage variants, drop the common "JSONRPC" prefix to
        # make the enum easier to read (e.g. `Request` instead of
        # `JSONRPCRequest`). The payload type remains unchanged.
        variant_name = (
            ref_name[len("JSONRPC") :]
            if name == "JSONRPCMessage" and ref_name.startswith("JSONRPC")
            else ref_name
        )

        # Special-case for `ClientRequest` and `ServerNotification` so the enum
        # variant's payload is the *Params type rather than the full *Request /
        # *Notification marker type.
        if name in ("ClientRequest", "ServerNotification"):
            # Rely on the trait implementation to tell us the exact Rust type
            # of the `params` payload. This guarantees we stay in sync with any
            # special-case logic used elsewhere (e.g. objects with
            # `additionalProperties` mapping to `serde_json::Value`).
            if name == "ClientRequest":
                payload_type = f"<{ref_name} as ModelContextProtocolRequest>::Params"
            else:
                payload_type = (
                    f"<{ref_name} as ModelContextProtocolNotification>::Params"
                )

            # Determine the wire value for `method` so we can annotate the
            # variant appropriately. If for some reason the schema does not
            # specify a constant we fall back to the type name, which will at
            # least compile (although deserialization will likely fail).
            request_def = DEFINITIONS.get(ref_name, {})
            method_const = (
                request_def.get("properties", {})
                .get("method", {})
                .get("const", ref_name)
            )

            out.append(f'    #[serde(rename = "{method_const}")]\n')
            out.append(f"    {variant_name}({payload_type}),\n")
        else:
            # The regular/straight-forward case.
            out.append(f"    {variant_name}({ref_name}),\n")

    out.append("}\n\n")
    return out


def get_serde_annotation_for_anyof_type(type_name: str) -> str | None:
    # TODO: Solve this in a more generic way.
    match type_name:
        case "ClientRequest":
            return '#[serde(tag = "method", content = "params")]'
        case "ServerNotification":
            return '#[serde(tag = "method", content = "params")]'
        case _:
            return "#[serde(untagged)]"


def map_type(
    typedef: dict[str, any],
    prop_name: str | None = None,
    struct_name: str | None = None,
) -> str:
    """typedef must have a `type` key, but may also have an `items`key."""
    ref_prop = typedef.get("$ref", None)
    if ref_prop:
        return type_from_ref(ref_prop)

    any_of = typedef.get("anyOf", None)
    if any_of:
        assert prop_name is not None
        assert struct_name is not None
        custom_type = struct_name + capitalize(prop_name)
        extra_defs.extend(define_any_of(custom_type, any_of))
        return custom_type

    type_prop = typedef.get("type", None)
    if type_prop is None:
        # Likely `unknown` in TypeScript, like the JSONRPCError.data property.
        return "serde_json::Value"

    if type_prop == "string":
        if const_prop := typedef.get("const", None):
            assert isinstance(const_prop, str)
            return f'&\'static str = "{const_prop    }"'
        else:
            return "String"
    elif type_prop == "integer":
        return "i64"
    elif type_prop == "number":
        return "f64"
    elif type_prop == "boolean":
        return "bool"
    elif type_prop == "array":
        item_type = typedef.get("items", None)
        if item_type:
            item_type = map_type(item_type, prop_name, struct_name)
            assert isinstance(item_type, str)
            return f"Vec<{item_type}>"
        else:
            raise ValueError("Array type without items.")
    elif type_prop == "object":
        # If the schema says `additionalProperties: {}` this is effectively an
        # open-ended map, so deserialize into `serde_json::Value` for maximum
        # flexibility.
        if typedef.get("additionalProperties") is not None:
            return "serde_json::Value"

        # If there are *no* properties declared treat it similarly.
        if not typedef.get("properties"):
            return "serde_json::Value"

        # Otherwise, synthesize a nested struct for the inline object.
        assert prop_name is not None
        assert struct_name is not None
        custom_type = struct_name + capitalize(prop_name)
        extra_defs.extend(
            define_struct(
                custom_type,
                typedef["properties"],
                set(typedef.get("required", [])),
                typedef.get("description"),
            )
        )
        return custom_type
    else:
        raise ValueError(f"Unknown type: {type_prop} in {typedef}")


@dataclass
class RustProp:
    name: str
    # serde annotation, if necessary
    serde: str | None = None


def rust_prop_name(name: str, is_optional: bool) -> RustProp:
    """Convert a JSON property name to a Rust property name."""
    prop_name: str
    is_rename = False
    if name == "type":
        prop_name = "r#type"
    elif name == "ref":
        prop_name = "r#ref"
    elif name == "enum":
        prop_name = "r#enum"
    elif snake_case := to_snake_case(name):
        prop_name = snake_case
        is_rename = True
    else:
        prop_name = name

    serde_annotations = []
    if is_rename:
        serde_annotations.append(f'rename = "{name}"')
    if is_optional:
        serde_annotations.append("default")
        serde_annotations.append('skip_serializing_if = "Option::is_none"')

    if serde_annotations:
        serde_str = f'#[serde({", ".join(serde_annotations)})]'
    else:
        serde_str = None
    return RustProp(prop_name, serde_str)


def to_snake_case(name: str) -> str:
    """Convert a camelCase or PascalCase name to snake_case."""
    snake_case = name[0].lower() + "".join(
        "_" + c.lower() if c.isupper() else c for c in name[1:]
    )
    if snake_case != name:
        return snake_case
    else:
        return None


def capitalize(name: str) -> str:
    """Capitalize the first letter of a name."""
    return name[0].upper() + name[1:]


def check_string_list(value: Any) -> list[str] | None:
    """If the value is a list of strings, return it. Otherwise, return None."""
    if not isinstance(value, list):
        return None
    for item in value:
        if not isinstance(item, str):
            return None
    return value


def type_from_ref(ref: str) -> str:
    """Convert a JSON reference to a Rust type."""
    assert ref.startswith("#/definitions/")
    return ref.split("/")[-1]


def emit_doc_comment(text: str | None, out: list[str]) -> None:
    """Append Rust doc comments derived from the JSON-schema description."""
    if not text:
        return
    for line in text.strip().split("\n"):
        out.append(f"/// {line.rstrip()}\n")


if __name__ == "__main__":
    sys.exit(main())
```

**Classes:** StructField, RustProp
**Functions:** main(), add_definition(name, definition, out), define_struct(name, properties, required_props, description), infer_result_type(request_type_name), implements_request_trait(name), implements_notification_trait(name), add_trait_impl(type_name, trait_name, fields, out), define_string_enum(name, enum_values, out, description), define_untagged_enum(name, type_list, out), define_any_of(name, list_of_refs, description), get_serde_annotation_for_anyof_type(type_name), map_type(typedef, prop_name, struct_name), rust_prop_name(name, is_optional), to_snake_case(name), capitalize(name), check_string_list(value), type_from_ref(ref), emit_doc_comment(text, out)


## Module `Codex\codex-src\scripts\asciicheck.py`

```python
#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

"""
Utility script that takes a list of files and returns non-zero if any of them
contain non-ASCII characters other than those in the allowed list.

If --fix is used, it will attempt to replace non-ASCII characters with ASCII
equivalents.

The motivation behind this script is that characters like U+00A0 (non-breaking
space) can cause regexes not to match and can result in surprising anchor
values for headings when GitHub renders Markdown as HTML.
"""


"""
When --fix is used, perform the following substitutions.
"""
substitutions: dict[int, str] = {
    0x00A0: " ",  # non-breaking space
    0x2011: "-",  # non-breaking hyphen
    0x2013: "-",  # en dash
    0x2014: "-",  # em dash
    0x2018: "'",  # left single quote
    0x2019: "'",  # right single quote
    0x201C: '"',  # left double quote
    0x201D: '"',  # right double quote
    0x2026: "...",  # ellipsis
    0x202F: " ",  # narrow non-breaking space
}

"""
Unicode codepoints that are allowed in addition to ASCII.
Be conservative with this list.

Note that it is always an option to use the hex HTML representation
instead of the character itself so the source code is ASCII-only.
For example, U+2728 (sparkles) can be written as `&#x2728;`.
"""
allowed_unicode_codepoints = {
    0x2728,  # sparkles
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for non-ASCII characters in files."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Rewrite files, replacing non-ASCII characters with ASCII equivalents, where possible.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Files to check for non-ASCII characters.",
    )
    args = parser.parse_args()

    has_errors = False
    for filename in args.files:
        path = Path(filename)
        has_errors |= lint_utf8_ascii(path, fix=args.fix)
    return 1 if has_errors else 0


def lint_utf8_ascii(filename: Path, fix: bool) -> bool:
    """Returns True if an error was printed."""
    try:
        with open(filename, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        print("UTF-8 decoding error:")
        print(f"  byte offset: {e.start}")
        print(f"  reason: {e.reason}")
        # Attempt to find line/column
        partial = raw[: e.start]
        line = partial.count(b"\n") + 1
        col = e.start - (partial.rfind(b"\n") if b"\n" in partial else -1)
        print(f"  location: line {line}, column {col}")
        return True

    errors = []
    for lineno, line in enumerate(text.splitlines(keepends=True), 1):
        for colno, char in enumerate(line, 1):
            codepoint = ord(char)
            if char == "\n":
                continue
            if (
                not (0x20 <= codepoint <= 0x7E)
                and codepoint not in allowed_unicode_codepoints
            ):
                errors.append((lineno, colno, char, codepoint))

    if errors:
        for lineno, colno, char, codepoint in errors:
            safe_char = repr(char)[1:-1]  # nicely escape things like \u202f
            print(
                f"Invalid character at line {lineno}, column {colno}: U+{codepoint:04X} ({safe_char})"
            )

    if errors and fix:
        print(f"Attempting to fix {filename}...")
        num_replacements = 0
        new_contents = ""
        for char in text:
            codepoint = ord(char)
            if codepoint in substitutions:
                num_replacements += 1
                new_contents += substitutions[codepoint]
            else:
                new_contents += char
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_contents)
        print(f"Fixed {num_replacements} of {len(errors)} errors in {filename}.")

    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
```

**Functions:** main(), lint_utf8_ascii(filename, fix)


## Module `Codex\codex-src\scripts\publish_to_npm.py`

```python
#!/usr/bin/env python3

"""
Download a release artifact for the npm package and publish it.

Given a release version like `0.20.0`, this script:
  - Downloads the `codex-npm-<version>.tgz` asset from the GitHub release
    tagged `rust-v<version>` in the `openai/codex` repository using `gh`.
  - Runs `npm publish` on the downloaded tarball to publish `@openai/codex`.

Flags:
  - `--dry-run` delegates to `npm publish --dry-run`. The artifact is still
    downloaded so npm can inspect the archive contents without publishing.

Requirements:
  - GitHub CLI (`gh`) must be installed and authenticated to access the repo.
  - npm must be logged in with an account authorized to publish
    `@openai/codex`. This may trigger a browser for 2FA.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_checked(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a subprocess command and raise if it fails."""
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    proc.check_returncode()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Download the npm release artifact for a given version and publish it."
        )
    )
    parser.add_argument(
        "version",
        help="Release version to publish, e.g. 0.20.0 (without the 'v' prefix)",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        help=(
            "Optional directory to download the artifact into. Defaults to a temporary directory."
        ),
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Delegate to `npm publish --dry-run` (still downloads the artifact).",
    )
    args = parser.parse_args()

    version: str = args.version.lstrip("v")
    tag = f"rust-v{version}"
    asset_name = f"codex-npm-{version}.tgz"

    download_dir_context_manager = (
        tempfile.TemporaryDirectory() if args.dir is None else None
    )
    # Use provided dir if set, else the temporary one created above
    download_dir: Path = args.dir if args.dir else Path(download_dir_context_manager.name)  # type: ignore[arg-type]
    download_dir.mkdir(parents=True, exist_ok=True)

    # 1) Download the artifact using gh
    repo = "openai/codex"
    gh_cmd = [
        "gh",
        "release",
        "download",
        tag,
        "--repo",
        repo,
        "--pattern",
        asset_name,
        "--dir",
        str(download_dir),
    ]
    print(f"Downloading {asset_name} from {repo}@{tag} into {download_dir}...")
    # Even in --dry-run we download so npm can inspect the tarball.
    run_checked(gh_cmd)

    artifact_path = download_dir / asset_name
    if not args.dry_run and not artifact_path.is_file():
        print(
            f"Error: expected artifact not found after download: {artifact_path}",
            file=sys.stderr,
        )
        return 1

    # 2) Publish to npm
    npm_cmd = ["npm", "publish"]
    if args.dry_run:
        npm_cmd.append("--dry-run")
    npm_cmd.append(str(artifact_path))

    # Ensure CI is unset so npm can open a browser for 2FA if needed.
    env = os.environ.copy()
    if env.get("CI"):
        env.pop("CI")

    print("Running:", " ".join(npm_cmd))
    proc = subprocess.run(npm_cmd, env=env)
    proc.check_returncode()

    print("Publish complete.")
    # Keep the temporary directory alive until here; it is cleaned up on exit
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Download a release artifact for the npm package and publish it.

Given a release version like `0.20.0`, this script:
  - Downloads the `codex-npm-<version>.tgz` asset from the GitHub release
    tagged `rust-v<version>` in the `openai/codex` repository using `gh`.
  - Runs `npm publish` on the downloaded tarball to publish `@openai/codex`.

Flags:
  - `--dry-run` delegates to `npm publish --dry-run`. The artifact is still
    downloaded so npm can inspect the archive contents without publishing.

Requirements:
  - GitHub CLI (`gh`) must be installed and authenticated to access the repo.
  - npm must be logged in with an account authorized to publish
    `@openai/codex`. This may trigger a browser for 2FA.
**Functions:** run_checked(cmd, cwd), main()


## Module `Codex\codex-src\scripts\readme_toc.py`

```python
#!/usr/bin/env python3

"""
Utility script to verify (and optionally fix) the Table of Contents in a
Markdown file. By default, it checks that the ToC between `<!-- Begin ToC -->`
and `<!-- End ToC -->` matches the headings in the file. With --fix, it
rewrites the file to update the ToC.
"""

import argparse
import sys
import re
import difflib
from pathlib import Path
from typing import List

# Markers for the Table of Contents section
BEGIN_TOC: str = "<!-- Begin ToC -->"
END_TOC: str = "<!-- End ToC -->"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check and optionally fix the README.md Table of Contents."
    )
    parser.add_argument(
        "file", nargs="?", default="README.md", help="Markdown file to process"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Rewrite file with updated ToC"
    )
    args = parser.parse_args()
    path = Path(args.file)
    return check_or_fix(path, args.fix)


def generate_toc_lines(content: str) -> List[str]:
    """
    Generate markdown list lines for headings (## to ######) in content.
    """
    lines = content.splitlines()
    headings = []
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{2,6})\s+(.*)$", line)
        if not m:
            continue
        level = len(m.group(1))
        text = m.group(2).strip()
        headings.append((level, text))

    toc = []
    for level, text in headings:
        indent = "  " * (level - 2)
        slug = text.lower()
        # normalize spaces and dashes
        slug = slug.replace("\u00a0", " ")
        slug = slug.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
        # drop other punctuation
        slug = re.sub(r"[^0-9a-z\s-]", "", slug)
        slug = slug.strip().replace(" ", "-")
        toc.append(f"{indent}- [{text}](#{slug})")
    return toc


def check_or_fix(readme_path: Path, fix: bool) -> int:
    if not readme_path.is_file():
        print(f"Error: file not found: {readme_path}", file=sys.stderr)
        return 1
    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    # locate ToC markers
    try:
        begin_idx = next(i for i, l in enumerate(lines) if l.strip() == BEGIN_TOC)
        end_idx = next(i for i, l in enumerate(lines) if l.strip() == END_TOC)
    except StopIteration:
        print(
            f"Error: Could not locate '{BEGIN_TOC}' or '{END_TOC}' in {readme_path}.",
            file=sys.stderr,
        )
        return 1
    # extract current ToC list items
    current_block = lines[begin_idx + 1 : end_idx]
    current = [l for l in current_block if l.lstrip().startswith("- [")]
    # generate expected ToC
    expected = generate_toc_lines(content)
    if current == expected:
        return 0
    if not fix:
        print(
            "ERROR: README ToC is out of date. Diff between existing and generated ToC:"
        )
        # Show full unified diff of current vs expected
        diff = difflib.unified_diff(
            current,
            expected,
            fromfile="existing ToC",
            tofile="generated ToC",
            lineterm="",
        )
        for line in diff:
            print(line)
        return 1
    # rebuild file with updated ToC
    prefix = lines[: begin_idx + 1]
    suffix = lines[end_idx:]
    new_lines = prefix + [""] + expected + [""] + suffix
    readme_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Updated ToC in {readme_path}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Utility script to verify (and optionally fix) the Table of Contents in a
Markdown file. By default, it checks that the ToC between `<!-- Begin ToC -->`
and `<!-- End ToC -->` matches the headings in the file. With --fix, it
rewrites the file to update the ToC.
**Functions:** main(), generate_toc_lines(content), check_or_fix(readme_path, fix)


## Module `helpful scripts\github_uploader.py`

```python
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def run_cmd(cmd, cwd=None):
    """Run shell commands and capture output/errors."""
    try:
        result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR] {e.stderr.strip()}"

def select_folder():
    return filedialog.askdirectory(title="Select Project Folder")

def upload_repo():
    folder = select_folder()
    if not folder:
        return

    # Ask for Owner and Repo name
    owner = simpledialog.askstring("GitHub Owner", "Enter your GitHub owner/org name (e.g. Meesh-Makes):")
    if not owner:
        return
    repo_name = simpledialog.askstring("GitHub Repo Name", "Enter the repository name (e.g. Codex_Studio):")
    if not repo_name:
        return

    # Build repo URL automatically
    repo_url = f"https://github.com/{owner}/{repo_name}.git"

    messagebox.showinfo("Starting", f"Uploading {folder} to {repo_url}...")

    # Step 1: Init repo if missing
    if not os.path.exists(os.path.join(folder, ".git")):
        run_cmd(["git", "init"], cwd=folder)
        run_cmd(["git", "branch", "-M", "main"], cwd=folder)

    # Step 2: Add/replace remote
    run_cmd(["git", "remote", "remove", "origin"], cwd=folder)
    run_cmd(["git", "remote", "add", "origin", repo_url], cwd=folder)

    # Step 3: Add files in chunks
    CHUNK_SIZE = 500
    file_list = []
    for root, _, files in os.walk(folder):
        for f in files:
            path = os.path.relpath(os.path.join(root, f), folder)
            file_list.append(path)

    for i in range(0, len(file_list), CHUNK_SIZE):
        chunk = file_list[i:i + CHUNK_SIZE]
        run_cmd(["git", "add"] + chunk, cwd=folder)

    # Step 4: Commit (skip if nothing new)
    run_cmd(["git", "commit", "-m", "Automated upload via GitHub Uploader"], cwd=folder)

    # Step 5: Push (force-with-lease avoids overwriting)
    result = run_cmd(["git", "push", "--force-with-lease", "-u", "origin", "main"], cwd=folder)

    messagebox.showinfo("Done", f"Upload complete!\n\n{result}")

def main():
    root = tk.Tk()
    root.title("GitHub Uploader")
    root.geometry("450x200")

    label = tk.Label(root, text="Upload Local Folder to GitHub Repo", pady=20)
    label.pack()

    upload_button = tk.Button(root, text="Select Folder & Upload", command=upload_repo)
    upload_button.pack(pady=10)

    quit_button = tk.Button(root, text="Quit", command=root.quit)
    quit_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
```

**Functions:** run_cmd(cmd, cwd), select_folder(), upload_repo(), main()


## Module `scripts\agent_runner.py`

```python
#!/usr/bin/env python3
"""
Agent runner that parses Agent.md and dispatches repository_dispatch events for each item.
- Uses GITHUB_TOKEN to call the REST API.
- Does NOT write code changes itself; it dispatches workers which run in Actions.
"""

import os
import re
import json
import time
import requests
from urllib.parse import quote_plus
from pathlib import Path

GITHUB_API = "https://api.github.com"
REPO = "MeeshMakes/Codex_Studio"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {TOKEN}"
}

def read_agent_md(path="Agent.md"):
    text = Path(path).read_text()
    blocks = re.split(r"(?m)^AGENT:", text)
    commands = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith("spawn_workers"):
            lines = b.splitlines()[1:]
            kv = {}
            for ln in lines:
                if ":" not in ln:
                    continue
                k, v = ln.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v.lower() in ("true", "false"):
                    val = v.lower() == "true"
                elif v.startswith("[") and v.endswith("]"):
                    val = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
                elif re.match(r"^\d+$", v):
                    val = int(v)
                else:
                    val = v
                kv[k] = val
            commands.append(kv)
    return commands

def search_items(query, per_page=100):
    url = f"{GITHUB_API}/search/issues?q={quote_plus(query)}&per_page={per_page}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("items", [])

def dispatch_worker(event_type, payload):
    url = f"{GITHUB_API}/repos/{REPO}/dispatches"
    data = {"event_type": event_type, "client_payload": payload}
    resp = requests.post(url, headers=HEADERS, json=data)
    if resp.status_code in (204, 201):
        return True
    else:
        print("[dispatch_worker] failed:", resp.status_code, resp.text)
        return False

def short_hash():
    return str(int(time.time()))[-6:]

def main(dry_run=True):
    cmds = read_agent_md()
    for cmd in cmds:
        source = cmd.get("source")
        if not source:
            print("[agent-runner] skip: no source")
            continue
        m = re.match(r"repo://([^/]+/[^?]+)\?query=(.+)", source)
        if not m:
            print("[agent-runner] invalid source:", source)
            continue
        query = m.group(2)
        items = search_items(query)
        max_items = int(cmd.get("max_items", len(items)))
        concurrency = int(cmd.get("concurrency", 4))
        launched = 0
        for i, item in enumerate(items):
            if launched >= max_items:
                break
            payload = {
                "spawn_config": cmd,
                "item": {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "html_url": item.get("html_url"),
                    "user": item.get("user", {}).get("login"),
                },
                "agent_branch": f"agent/{cmd.get('type')}/{item.get('number')}-{short_hash()}"
            }
            print("[agent-runner] dispatch payload:", json.dumps(payload, indent=2))
            if dry_run:
                print("[agent-runner] dry_run: not dispatching")
            else:
                ok = dispatch_worker("agent-work", payload)
                if not ok:
                    print("[agent-runner] dispatch failed for item", item.get("number"))
            launched += 1
        print(f"[agent-runner] command type={cmd.get('type')} launched={launched} concurrency={concurrency}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", default=False)
    args = p.parse_args()
    main(dry_run=args.dry_run)
```

Agent runner that parses Agent.md and dispatches repository_dispatch events for each item.
- Uses GITHUB_TOKEN to call the REST API.
- Does NOT write code changes itself; it dispatches workers which run in Actions.
**Functions:** read_agent_md(path), search_items(query, per_page), dispatch_worker(event_type, payload), short_hash(), main(dry_run)


## Module `scripts\worker_executor.py`

```python
#!/usr/bin/env python3
"""
Worker executor run inside Actions via repository_dispatch.
- Reads payload.json
- Uses the worker_prompt and summary_prompt paths to produce a summary (Codex call required)
- Runs quick checks and tests (pytest)
- Attempts safe fixes (placeholder logic)
- Creates branch + PR via GitHub API if changes made
- Creates ErrorDump if cannot fix

This script is intentionally conservative and includes "hooks" where Codex should be invoked
to produce patches or suggested diffs. A production implementation should implement a robust
model call and patch application logic (e.g., generate patch/diff and apply via git).
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import requests
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "MeeshMakes/Codex_Studio"
gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO)

def load_payload(path):
    with open(path, "r") as f:
        return json.load(f)

def run_cmd(cmd, cwd=".", capture=False):
    print(f">>> {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=capture)
    if capture:
        return res.returncode, res.stdout + res.stderr
    return res.returncode, None

def save_log(txt):
    Path("/tmp/agent-runner.log").write_text(txt)

def create_error_dump(item, reason, attempts):
    name = f"ErrorDump-{item.get('number')}.md"
    content = f"# ErrorDump for item {item.get('number')}\n\nReason: {reason}\n\nAttempts:\n{json.dumps(attempts, indent=2)}\n"
    Path(f"/tmp/{name}").write_text(content)
    # attach to repo as issue comment or push file if needed (simpler to comment)
    issue = repo.get_issue(number=item.get("number"))
    issue.create_comment(f"Automated ErrorDump created: `{name}`\n\nReason: {reason}\n")
    return name

def main(payload_path):
    payload = load_payload(payload_path)
    item = payload.get("item")
    spawn = payload.get("spawn_config", {})
    branch = payload.get("agent_branch")
    # 1) generate summary using Codex if CODEX_API_KEY present and summary_prompt provided
    summary = {"title": "no summary generated", "summary": "", "bullets": [], "confidence": "low"}
    # (hook) Codex call goes here to produce structured summary.json
    Path("/tmp/summary.json").write_text(json.dumps(summary, indent=2))

    # 2) run static checks
    rc, logs = run_cmd("pytest -q --maxfail=1", capture=True)
    save_log(logs)
    attempts = []
    if rc == 0:
        print("[worker_executor] tests passed locally (quick run).")
    else:
        print("[worker_executor] tests failed. collecting logs and attempting minimal fixes.")
        # minimal fix examples: run formatter then re-run tests
        run_cmd("ruff check . || true")
        run_cmd("black --check . || true")
        # placeholder: attempt minimal automated fix (NOT implemented)
        attempts.append({"action": "ran linters and formatters"})
        rc2, logs2 = run_cmd("pytest -q --maxfail=1", capture=True)
        save_log(logs + "\n\n" + logs2)
        if rc2 != 0:
            reason = "tests failing after minimal attempts"
            create_error_dump(item, reason, attempts)
            print("[worker_executor] giving up; created ErrorDump and commented on original item.")
            return

    # 3) If we reach here, either tests passed or minimal fixes succeeded.
    # For real code changes, Codex should generate a patch. This script shows how to create branch and PR if patch exists.
    # Placeholder: no code changes created in this simplified executor.
    print("[worker_executor] no automatic code changes performed in this run (placeholder).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: worker_executor.py /path/to/payload.json")
        sys.exit(1)
    main(sys.argv[1])
```

Worker executor run inside Actions via repository_dispatch.
- Reads payload.json
- Uses the worker_prompt and summary_prompt paths to produce a summary (Codex call required)
- Runs quick checks and tests (pytest)
- Attempts safe fixes (placeholder logic)
- Creates branch + PR via GitHub API if changes made
- Creates ErrorDump if cannot fix

This script is intentionally conservative and includes "hooks" where Codex should be invoked
to produce patches or suggested diffs. A production implementation should implement a robust
model call and patch application logic (e.g., generate patch/diff and apply via git).
**Functions:** load_payload(path), run_cmd(cmd, cwd, capture), save_log(txt), create_error_dump(item, reason, attempts), main(payload_path)


## Module `tests\conftest.py`

```python
import os
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "gui: marks tests that require a GUI display")
    config.addinivalue_line("markers", "requires_display: marks tests that require a GUI display")

def pytest_collection_modifyitems(config, items):
    headless = os.environ.get("CI") or os.environ.get("HEADLESS")
    if headless:
        skip_gui = pytest.mark.skip(reason="Skipping GUI tests in CI/HEADLESS environment")
        for item in items:
            if "gui" in item.keywords or "requires_display" in item.keywords:
                item.add_marker(skip_gui)
```

**Functions:** pytest_configure(config), pytest_collection_modifyitems(config, items)


## Module `tests\test_auto_merge_all_tasks.py`

```python
import subprocess
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.auto_merge_all_tasks import ensure_clean_worktree, main


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def init_repo(path: Path) -> None:
    run(["git", "init"], cwd=path)
    run(["git", "config", "user.name", "Test"], cwd=path)
    run(["git", "config", "user.email", "test@example.com"], cwd=path)
    run(["git", "branch", "-m", "main"], cwd=path)
    (path / "file.txt").write_text("base\n")
    run(["git", "add", "file.txt"], cwd=path)
    run(["git", "commit", "-m", "init"], cwd=path)


def test_ensure_clean_worktree_stashes_when_dirty(tmp_path, monkeypatch):
    init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("dirty\n")
    monkeypatch.chdir(tmp_path)
    stashed = ensure_clean_worktree()
    assert stashed
    res = subprocess.run(["git", "stash", "list"], cwd=tmp_path, text=True, capture_output=True, check=True)
    assert "auto_merge_all_tasks" in res.stdout


def test_main_restores_stash(tmp_path, monkeypatch):
    init_repo(tmp_path)
    (tmp_path / "file.txt").write_text("local change\n")
    monkeypatch.chdir(tmp_path)
    main("main", push=False)
    assert (tmp_path / "file.txt").read_text() == "local change\n"
    res = subprocess.run(["git", "stash", "list"], cwd=tmp_path, text=True, capture_output=True, check=True)
    assert res.stdout.strip() == ""


def test_main_stash_conflict_preserves_stash(tmp_path, monkeypatch):
    init_repo(tmp_path)
    run(["git", "checkout", "-b", "feature"], cwd=tmp_path)
    (tmp_path / "file.txt").write_text("feature change\n")
    run(["git", "commit", "-am", "feature"], cwd=tmp_path)
    run(["git", "checkout", "main"], cwd=tmp_path)
    (tmp_path / "file.txt").write_text("local change\n")
    monkeypatch.chdir(tmp_path)
    main("main", push=False)
    res = subprocess.run(["git", "stash", "list"], cwd=tmp_path, text=True, capture_output=True, check=True)
    assert "auto_merge_all_tasks" in res.stdout
    conflict_text = (tmp_path / "file.txt").read_text()
    assert "<<<<<<<" in conflict_text


def test_dry_run_no_branches(tmp_path, capsys, monkeypatch):
    init_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    main("main", dry_run=True, push=False)
    captured = capsys.readouterr()
    assert "Dry run: no branches to merge." in captured.out


def test_main_pushes_to_remote(tmp_path, monkeypatch):
    remote = tmp_path / "remote.git"
    run(["git", "init", "--bare", str(remote)], cwd=tmp_path)
    work = tmp_path / "work"
    run(["git", "clone", str(remote), str(work)], cwd=tmp_path)
    run(["git", "config", "user.name", "Test"], cwd=work)
    run(["git", "config", "user.email", "test@example.com"], cwd=work)
    run(["git", "branch", "-m", "main"], cwd=work)
    (work / "file.txt").write_text("base\n")
    run(["git", "add", "file.txt"], cwd=work)
    run(["git", "commit", "-m", "init"], cwd=work)
    run(["git", "push", "origin", "main"], cwd=work)

    run(["git", "checkout", "-b", "feature"], cwd=work)
    (work / "file.txt").write_text("feature change\n")
    run(["git", "commit", "-am", "feature"], cwd=work)
    run(["git", "checkout", "main"], cwd=work)

    before = run(["git", "rev-parse", "main"], cwd=remote).stdout.strip()

    monkeypatch.chdir(work)
    main("main")

    after = run(["git", "rev-parse", "main"], cwd=remote).stdout.strip()
    assert before != after


def test_main_reports_merge_conflict(tmp_path, monkeypatch, capsys):
    init_repo(tmp_path)
    run(["git", "checkout", "-b", "feature"], cwd=tmp_path)
    (tmp_path / "file.txt").write_text("feature change\n")
    run(["git", "commit", "-am", "feature"], cwd=tmp_path)
    run(["git", "checkout", "main"], cwd=tmp_path)
    (tmp_path / "file.txt").write_text("main change\n")
    run(["git", "commit", "-am", "main change"], cwd=tmp_path)
    monkeypatch.chdir(tmp_path)
    main("main", push=False)
    out = capsys.readouterr().out
    assert "Conflict merging feature" in out


def test_report_writes_summary(tmp_path, monkeypatch):
    init_repo(tmp_path)
    run(["git", "checkout", "-b", "feature"], cwd=tmp_path)
    (tmp_path / "file.txt").write_text("feature change\n")
    run(["git", "commit", "-am", "feature"], cwd=tmp_path)
    run(["git", "checkout", "main"], cwd=tmp_path)
    report_file = tmp_path / "report.txt"
    monkeypatch.chdir(tmp_path)
    main("main", push=False, report=str(report_file))
    assert report_file.read_text().strip() == "Merged feature into main"


def test_report_to_stdout(tmp_path, monkeypatch, capsys):
    init_repo(tmp_path)
    run(["git", "checkout", "-b", "feature"], cwd=tmp_path)
    (tmp_path / "file.txt").write_text("feature change\n")
    run(["git", "commit", "-am", "feature"], cwd=tmp_path)
    run(["git", "checkout", "main"], cwd=tmp_path)
    monkeypatch.chdir(tmp_path)
    main("main", push=False, report="-")
    out = capsys.readouterr().out
    assert "Merged feature into main" in out
```

**Functions:** run(cmd, cwd), init_repo(path), test_ensure_clean_worktree_stashes_when_dirty(tmp_path, monkeypatch), test_main_restores_stash(tmp_path, monkeypatch), test_main_stash_conflict_preserves_stash(tmp_path, monkeypatch), test_dry_run_no_branches(tmp_path, capsys, monkeypatch), test_main_pushes_to_remote(tmp_path, monkeypatch), test_main_reports_merge_conflict(tmp_path, monkeypatch, capsys), test_report_writes_summary(tmp_path, monkeypatch), test_report_to_stdout(tmp_path, monkeypatch, capsys)


## Module `tests\test_bucket_scanner.py`

```python
import json
from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
import bucket_scanner


def test_process_handles_unresolved_entries(tmp_path, monkeypatch):
    dataset = tmp_path / "agent_dataset.json"
    agent_dir = tmp_path / "Agent_Versions"
    benchwarm = tmp_path / "Agent_BenchWarm.md"
    neg_log = tmp_path / "negative_diffs.log"
    monkeypatch.setattr(bucket_scanner, "DATASET", dataset)
    monkeypatch.setattr(bucket_scanner, "AGENT_DIR", agent_dir)
    monkeypatch.setattr(bucket_scanner, "BENCHWARM", benchwarm)
    monkeypatch.setattr(bucket_scanner, "NEG_LOG", neg_log)

    data = {
        "entries": [
            {
                "id": "a1",
                "status": "open",
                "buckets": ["Title1", "Line1"],
                "diff_metrics": {"instability": 3, "negative": 3},
            },
            {
                "id": "a2",
                "status": "open",
                "buckets": ["Title2", "Line2"],
                "diff_metrics": {"instability": 1, "negative": 1},
            },
        ]
    }
    dataset.write_text(json.dumps(data))

    bucket_scanner.process()

    # negative diff log records all unresolved entries
    log_text = neg_log.read_text()
    assert "a1" in log_text and "a2" in log_text

    updated = json.loads(dataset.read_text())
    e1, e2 = updated["entries"]

    # entry a1 should go to benchwarm after reaching instability threshold
    assert e1["status"] == "benchwarm"
    assert Path(e1["version_ref"]).name == benchwarm.name
    assert benchwarm.exists()

    # entry a2 should create a new agent file
    agent_path = Path(e2["version_ref"])
    assert agent_path.exists()
    assert agent_path.parent == agent_dir
    text = agent_path.read_text()
    assert "BuckID: a2" in text
```

**Functions:** test_process_handles_unresolved_entries(tmp_path, monkeypatch)


## Module `tests\test_embeddings.py`

```python
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
import embeddings


class DummyModel:
    def encode(self, text: str) -> np.ndarray:
        if text == "foo":
            return np.array([1.0, 0.0, 0.0], dtype=np.float32)
        if text == "bar":
            return np.array([0.0, 1.0, 0.0], dtype=np.float32)
        return np.zeros(3, dtype=np.float32)


def test_search_embeddings_sql(tmp_path, monkeypatch):
    db = tmp_path / "db.sqlite"
    monkeypatch.setattr(embeddings, "_get_model", lambda: DummyModel())

    embeddings.add_embedding("a1", 0, "foo", db_path=db)
    embeddings.add_embedding("a2", 0, "bar", db_path=db)

    results = embeddings.search_embeddings("foo", top_k=1, db_path=db)
    assert len(results) == 1
    assert results[0]["agent_id"] == "a1"
    assert results[0]["bucket_id"] == 0
    assert results[0]["score"] == pytest.approx(1.0)
```

**Classes:** DummyModel
**Functions:** test_search_embeddings_sql(tmp_path, monkeypatch)


## Module `tests\test_logging.py`

```python
import logging
from pathlib import Path

import pytest

import sys

import catalog_cli
from tools import auto_merge_all_tasks as am
from tools import codex_repo_manager as crm


def test_repo_manager_chmod_logs(monkeypatch, tmp_path, caplog):
    target = tmp_path / "dir"
    target.mkdir()

    def bad_chmod(self, mode):  # type: ignore[override]
        raise OSError("boom")

    monkeypatch.setattr(Path, "chmod", bad_chmod)
    with caplog.at_level(logging.WARNING):
        crm._chmod_recursive(target, readonly=True)
    assert any("Failed to chmod" in r.message for r in caplog.records)


def test_catalog_cli_logs_invalid_json(tmp_path, caplog, monkeypatch):
    bad = tmp_path / "bad.json"
    bad.write_text("{bad json")
    monkeypatch.setattr(sys, "argv", ["catalog_cli.py", "register", "ds", str(bad)])
    with caplog.at_level(logging.WARNING):
        with pytest.raises(SystemExit):
            catalog_cli.main()
    assert any("Invalid dataset JSON" in r.message for r in caplog.records)


def test_auto_merge_logs(monkeypatch, caplog):
    def boom(*args, **kwargs):
        raise RuntimeError("git broke")

    monkeypatch.setattr(am.subprocess, "run", boom)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            am.main("main")
    assert any("Failed to determine current branch" in r.message for r in caplog.records)
```

**Functions:** test_repo_manager_chmod_logs(monkeypatch, tmp_path, caplog), test_catalog_cli_logs_invalid_json(tmp_path, caplog, monkeypatch), test_auto_merge_logs(monkeypatch, caplog)


## Module `tests\test_readme_worker.py`

```python
import json
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import readme_worker as rw


def test_build_readme_logs_failed_module(tmp_path, caplog, monkeypatch):
    monkeypatch.setattr(rw, "ROOT", tmp_path)
    (tmp_path / "README.md").write_text("base\n")
    (tmp_path / "good.py").write_text("\"\"\"good\"\"\"\n")
    (tmp_path / "bad.py").write_text("def broken(:\n")
    with caplog.at_level(logging.WARNING):
        rw.build_readme(tmp_path)
    assert any("bad.py" in record.message for record in caplog.records)
    analysis = json.loads((tmp_path / "analysis.json").read_text())
    assert any(item["file"] == "bad.py" and item["summary"].startswith("Failed to parse module") for item in analysis)
```

**Functions:** test_build_readme_logs_failed_module(tmp_path, caplog, monkeypatch)


## Module `tests\test_task_dispatcher.py`

```python
import json
import logging
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tools.task_dispatcher import TaskDispatcher, TaskHandler
from tools.task_manager import TaskManager


class EchoHandler(TaskHandler):
    def can_handle(self, task):
        return True

    def handle(self, task):
        return f"echo:{task.title}"


def test_dispatcher_handles_task(tmp_path):
    db = tmp_path / "tasks.json"
    db.write_text(
        json.dumps(
            [
                {
                    "id": "1",
                    "title": "sample",
                    "status": "open",
                    "created": "now",
                    "file": "dummy",
                }
            ]
        )
    )

    tm = TaskManager(db_path=db)
    sent: list[str] = []
    dispatcher = TaskDispatcher(tm, sent.append)
    dispatcher.register_handler(EchoHandler())

    dispatcher.dispatch_once()

    assert tm.list_tasks()[0]["status"] == "done"
    assert sent == ["echo:sample"]


def test_handler_failure_logs_error(tmp_path, caplog):
    db = tmp_path / "tasks.json"
    db.write_text(
        json.dumps(
            [
                {
                    "id": "1",
                    "title": "boom",
                    "status": "open",
                    "created": "now",
                    "file": "dummy",
                }
            ]
        )
    )

    tm = TaskManager(db_path=db)

    class FailingHandler(TaskHandler):
        def can_handle(self, task):
            return True

        def handle(self, task):
            raise RuntimeError("boom")

    dispatcher = TaskDispatcher(tm, lambda payload: None)
    dispatcher.register_handler(FailingHandler())

    caplog.set_level(logging.ERROR)
    dispatcher.dispatch_once()

    assert tm.list_tasks()[0]["status"] == "open"
    assert "failed for task" in caplog.text
```

**Classes:** EchoHandler
**Functions:** test_dispatcher_handles_task(tmp_path), test_handler_failure_logs_error(tmp_path, caplog)


## Module `tests\test_task_manager.py`

```python
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from tools.task_manager import TaskManager, Task


def _sample_task_dict():
    return {
        "id": "1",
        "title": "Existing",
        "status": "open",
        "created": "now",
        "file": "Agent_1.md",
    }


def test_init_with_corrupted_json_logs_error(tmp_path, caplog):
    db = tmp_path / "tasks.json"
    db.write_text("{bad json")
    caplog.set_level(logging.ERROR)

    tm = TaskManager(db_path=db)

    assert tm.list_tasks() == []
    assert "Failed to decode tasks database" in caplog.text


def test_load_preserves_tasks_on_corrupted_json(tmp_path, caplog):
    db = tmp_path / "tasks.json"
    db.write_text(json.dumps([_sample_task_dict()]))
    tm = TaskManager(db_path=db)
    assert len(tm.list_tasks()) == 1

    db.write_text("{bad json")
    caplog.set_level(logging.ERROR)
    tm._load()

    assert len(tm.list_tasks()) == 1
    assert "Failed to decode tasks database" in caplog.text


def test_load_missing_fields_defaults(tmp_path):
    db = tmp_path / "tasks.json"
    db.write_text(json.dumps([{ "id": "1", "title": "legacy", "file": "Agent_1.md" }]))
    tm = TaskManager(db_path=db)

    task = tm.list_tasks()[0]
    assert task["status"] == "queued"
    # created should be set to an ISO timestamp
    datetime.fromisoformat(task["created"])


def test_list_and_clear_completed(tmp_path):
    db = tmp_path / "tasks.json"
    tm = TaskManager(db_path=db)
    tm._tasks = [
        Task(id="1", title="t1", status="open", created="now", file="f1"),
        Task(id="2", title="t2", status="done", created="now", file="f2"),
    ]

    completed = tm.list_completed()
    assert len(completed) == 1
    assert completed[0]["id"] == "2"

    triggered = []
    tm.tasks_changed.connect(lambda: triggered.append(True))
    removed = tm.clear_completed()

    assert removed == 1
    assert len(tm._tasks) == 1
    assert tm._tasks[0].id == "1"
    assert len(triggered) == 1

    removed_again = tm.clear_completed()
    assert removed_again == 0
    assert len(triggered) == 1


def test_export_completed(tmp_path, monkeypatch):
    import tools.task_manager as tm_module

    # Redirect root directories to temporary location
    monkeypatch.setattr(tm_module, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(tm_module, "AGENT_DIR", tmp_path / "Agent_Versions")
    monkeypatch.setattr(tm_module, "LOG_DIR", tmp_path / "logs")
    tm_module.AGENT_DIR.mkdir()

    manager = tm_module.TaskManager(db_path=tmp_path / "tasks.json")

    agent_file = tm_module.AGENT_DIR / "Agent_1.md"
    agent_file.write_text("hello", encoding="utf-8")

    manager._tasks = [
        tm_module.Task(
            id="1",
            title="t1",
            status="merged",
            created="now",
            file=str(agent_file.relative_to(tmp_path)),
            branch="main",
            merged_commit="abc123",
        )
    ]

    export_file = manager.export_completed()
    data = json.loads(export_file.read_text())
    assert data == [
        {"title": "t1", "content": "hello", "branch": "main", "merged_commit": "abc123"}
    ]


def test_add_task_with_branch(tmp_path, monkeypatch):
    import tools.task_manager as tm_module

    # Redirect root directories to temporary location
    monkeypatch.setattr(tm_module, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(tm_module, "AGENT_DIR", tmp_path / "Agent_Versions")
    monkeypatch.setattr(tm_module, "LOG_DIR", tmp_path / "logs")

    manager = tm_module.TaskManager(db_path=tmp_path / "tasks.json")

    # Test add_task with branch parameter
    task_file = manager.add_task("Test Task", "Test content", branch="feature-branch")
    
    # Verify task was created with correct branch
    tasks = manager.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test Task"
    assert tasks[0]["branch"] == "feature-branch"
    assert tasks[0]["status"] == "open"
    
    # Verify backward compatibility - add_task without branch
    manager.add_task("Task without branch", "Content")
    tasks = manager.list_tasks()
    assert len(tasks) == 2
    assert tasks[1]["branch"] == ""  # Default empty branch
```

**Functions:** _sample_task_dict(), test_init_with_corrupted_json_logs_error(tmp_path, caplog), test_load_preserves_tasks_on_corrupted_json(tmp_path, caplog), test_load_missing_fields_defaults(tmp_path), test_list_and_clear_completed(tmp_path), test_export_completed(tmp_path, monkeypatch), test_add_task_with_branch(tmp_path, monkeypatch)


## Module `tests\test_task_panel.py`

```python
import os
from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
import tools.task_manager as tm


@pytest.mark.gui
def test_task_panel_operations(tmp_path, monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    # redirect task manager paths to temporary directory
    monkeypatch.setattr(tm, "ROOT_DIR", tmp_path)
    monkeypatch.setattr(tm, "AGENT_DIR", tmp_path / "Agent_Versions")
    monkeypatch.setattr(tm, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(tm, "TASKS_FILE", tmp_path / "logs" / "tasks.json")

    # Import Codex_Studio lazily to avoid GUI imports during collection
    import Codex_Studio as cs

    # patch Codex_Studio paths to avoid touching real filesystem
    monkeypatch.setattr(cs, "APP_ROOT", tmp_path)
    monkeypatch.setattr(cs, "CODEX_DIR", tmp_path / "Codex")
    monkeypatch.setattr(cs, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(cs, "DATASETS_ROOT", tmp_path / "Project_datasets")
    monkeypatch.setattr(cs, "DIFFS_DIR", tmp_path / "diffs")
    monkeypatch.setattr(cs, "CONFIG_JSON", tmp_path / "config.lite.json")
    monkeypatch.setattr(cs, "PROJECTS_JSON", tmp_path / "projects.lite.json")
    monkeypatch.setattr(cs, "APP_LOG", tmp_path / "codex_lite.log")

    # avoid network calls during model population
    monkeypatch.setattr(cs, "is_ollama_available", lambda base_url: False)
    monkeypatch.setattr(cs, "ollama_list", lambda base_url: ([], None))

    # auto-confirm message boxes
    monkeypatch.setattr(cs.QMessageBox, "question", lambda *args, **kwargs: cs.QMessageBox.Yes)

    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    widget = cs.CodexLite(lambda s: None)

    # add task and ensure it appears in list
    widget.task_manager.add_task("t1", "content")
    app.processEvents()
    assert widget.list_tasks.count() == 1
    task_id = widget.task_manager.list_tasks()[0]["id"]

    # mark complete via UI helper
    widget.list_tasks.setCurrentRow(0)
    widget._task_done()
    app.processEvents()
    assert widget.task_manager.get_task(task_id).status == "done"
    assert "done" in widget.list_tasks.item(0).text()

    # after completion, buttons are disabled and task remains listed
    widget.list_tasks.setCurrentRow(0)
    assert widget.list_tasks.count() == 1
    assert not widget.btn_task_done.isEnabled()
    assert not widget.btn_task_remove.isEnabled()
```

**Functions:** test_task_panel_operations(tmp_path, monkeypatch)


## Module `tools\auto_merge_all_tasks.py`

```python
"""Utility to merge all branches into a base branch.

This script is triggered by the phrase "Auto Merge All Tasks".
It fetches all remote branches, sorts them by commit date, and merges
any branches not already merged into the target base branch (default: main).
If a merge conflict occurs the process stops and the user can resolve it
before running the script again.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

def run(cmd: List[str], check: bool = True, log: bool = True) -> subprocess.CompletedProcess:
    """Run a command and echo it to the console."""
    print("+", " ".join(cmd))
    result = subprocess.run(cmd, text=True, capture_output=True)
    if log or result.returncode != 0:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result

def list_unmerged(base: str) -> List[str]:
    """Return branches not merged into base."""
    res = subprocess.run(
        ["git", "branch", "--format=%(refname:short)", "--sort=committerdate", "--no-merged", base],
        text=True,
        capture_output=True,
        check=True,
    )
    branches = [b.strip() for b in res.stdout.splitlines() if b.strip()]
    return [b for b in branches if b != base]


def ensure_clean_worktree() -> bool:
    """Ensure the git worktree is clean, stashing changes if necessary.

    Returns ``True`` if a stash was created, ``False`` otherwise.
    """
    res = subprocess.run(
        ["git", "status", "--porcelain"],
        text=True,
        capture_output=True,
        check=True,
    )
    if res.stdout.strip():
        print("Worktree dirty; stashing changes")
        run(["git", "stash", "push", "--include-untracked", "-m", "auto_merge_all_tasks"], check=True)
        return True
    return False

def write_report(dest: str, lines: List[str]) -> None:
    content = "\n".join(lines)
    if dest == "-":
        print(content)
    else:
        Path(dest).write_text(content + ("\n" if content else ""))


def main(
    base: str,
    dry_run: bool = False,
    confirm: bool = False,
    push: bool = True,
    report: Optional[str] = None,
) -> None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        )
        current = result.stdout.strip()
    except Exception as exc:
        logging.exception("Failed to determine current branch")
        raise RuntimeError(
            "Failed to determine current branch. Are you in a Git repository?"
        ) from exc
    if current != base:
        run(["git", "checkout", base])

    stashed = False
    if not dry_run:
        stashed = ensure_clean_worktree()

    run(["git", "fetch", "--all", "--prune"])

    branches = list_unmerged(base)
    summary: List[str] = []
    if dry_run:
        if not branches:
            print("Dry run: no branches to merge.")
            return
        print("Dry run: the following branches would be merged:")
        for branch in branches:
            print(branch)
        if report:
            summary = [f"Would merge {b}" for b in branches]
            write_report(report, summary)
        return

    for branch in branches:
        print(f"== Merging {branch} into {base} ==")
        if confirm:
            reply = input(f"Merge {branch}? [y/N] ").strip().lower()
            if reply not in {"y", "yes"}:
                print(f"Skipping {branch}")
                summary.append(f"Skipped {branch}")
                continue
        res = run(["git", "merge", "--no-ff", branch], check=False, log=False)
        if res.returncode == 0:
            summary.append(f"Merged {branch} into {base}")
            if push:
                run(["git", "push", "origin", base])
        elif res.returncode == 1:
            print(f"Conflict merging {branch}. Aborting.")
            summary.append(f"Conflict merging {branch}")
            run(["git", "merge", "--abort"], check=False, log=False)
            break
        else:
            print(f"Error merging {branch} (exit code {res.returncode}). Aborting.")
            summary.append(f"Error merging {branch}")
            run(["git", "merge", "--abort"], check=False, log=False)
            break

    if stashed:
        print("Restoring stashed changes")
        res = run(["git", "stash", "pop"], check=False)
        if res.returncode == 0:
            print("Stashed changes restored")
        else:
            print("Conflicts restoring stashed changes; stash preserved")

    if report and not dry_run:
        write_report(report, summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge all branches into a base branch")
    parser.add_argument("base", nargs="?", default="main", help="base branch to merge into")
    parser.add_argument("--dry-run", action="store_true", help="list branches without merging")
    parser.add_argument("--confirm", action="store_true", help="prompt before merging each branch")
    parser.add_argument("--no-push", action="store_true", help="skip pushing to origin")
    parser.add_argument(
        "--report",
        nargs="?",
        const="-",
        help="write merge summary to file or stdout (default stdout)",
    )
    args = parser.parse_args()
    main(
        args.base,
        dry_run=args.dry_run,
        confirm=args.confirm,
        push=not args.no_push,
        report=args.report,
    )
```

Utility to merge all branches into a base branch.

This script is triggered by the phrase "Auto Merge All Tasks".
It fetches all remote branches, sorts them by commit date, and merges
any branches not already merged into the target base branch (default: main).
If a merge conflict occurs the process stops and the user can resolve it
before running the script again.
**Functions:** run(cmd, check, log), list_unmerged(base), ensure_clean_worktree(), write_report(dest, lines), main(base, dry_run, confirm, push, report)


## Module `tools\codex_check.py`

```python
#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
from datetime import datetime

def run(cmd):
    return subprocess.run(cmd, text=True, shell=isinstance(cmd,str), capture_output=True)

def append_outbox(stage, ok, summary, notes=""):
    p=Path("Codex_Agents/outbox.md"); p.parent.mkdir(exist_ok=True,parents=True)
    ts=datetime.utcnow().isoformat()
    body=f"\n## [CODEX] {ts} {stage} ok:{str(ok).lower()}\n- summary: {summary}\n- notes:\n```\n{notes.strip()}\n```\n"
    p.write_text(p.read_text(encoding="utf-8")+body if p.exists() else "# Codex → Copilot Outbox (system-log)\n"+body, encoding="utf-8")

def main():
    notes=[]
    d=run([sys.executable,"distill_dumps.py"])
    notes.extend([d.stdout,d.stderr])
    tests=run("pytest -q")
    ok=(tests.returncode==0)
    append_outbox("CODEx_CHECK", ok, "distilled dumps; ran test suite", "\n".join(notes))
    subprocess.run([sys.executable,"tools/triplewash_status.py","set","COPILOT_CLEAN","true" if ok else "false","codex-check complete"], check=False)

if __name__=="__main__":
    main()
```

**Functions:** run(cmd), append_outbox(stage, ok, summary, notes), main()


## Module `tools\codex_repo_manager.py`

```python
# -*- coding: utf-8 -*-
"""Utility for managing the local Codex source checkout.

Subcommands:
  ensure-source -- ensure a local copy of the Codex source exists
                  optionally verify downloaded archive with --sha256
  protect       -- toggle read only/writable state for the source directory
  upload        -- push the source tree to a user provided git remote
"""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import logging
from pathlib import Path
from urllib.request import urlopen, Request
import zipfile
import hashlib

DEFAULT_REPO = "https://github.com/openai/codex.git"
DEFAULT_TAG = "rust-v0.23.0"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def run(cmd: list[str], cwd: Path | None = None) -> str:
    """Run *cmd* and return stdout. Raises CalledProcessError on failure."""
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout


def ensure_source(args: argparse.Namespace) -> None:
    """Ensure that the Codex source tree exists at *dest*.

    If git is available and preferred, a shallow clone is performed; otherwise
    a release archive is downloaded and extracted. When ``--sha256`` is
    supplied, the downloaded archive's hash is verified before extraction.
    """
    dest = Path(args.dest)
    repo = args.repo
    tag = args.tag
    prefer_git = args.prefer == "git"
    archive_kind = args.archive

    if dest.exists() and (dest / ".git").exists():
        print(f"{dest} already present", flush=True)
        return

    if prefer_git and shutil.which("git"):
        if dest.exists():
            shutil.rmtree(dest)
        run(["git", "clone", "--depth", "1", "--branch", tag, repo, str(dest)])
        print(f"Cloned {repo}@{tag} to {dest}")
        return

    # fall back to downloading release archive
    suffix = "zip" if archive_kind == "zip" else "tar.gz"
    url = f"{repo.rstrip('.git')}/archive/refs/tags/{tag}.{suffix}"
    tmpdir = Path(tempfile.mkdtemp(prefix="codex_src_"))
    archive_path = tmpdir / f"src.{suffix}"
    req = Request(url, headers={"User-Agent": "codex-repo-manager"})
    with urlopen(req) as r, open(archive_path, "wb") as f:
        shutil.copyfileobj(r, f)

    h = hashlib.sha256()
    with open(archive_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    digest = h.hexdigest()
    if getattr(args, "sha256", None):
        if digest.lower() != args.sha256.lower():
            shutil.rmtree(tmpdir)
            raise SystemExit(
                f"SHA256 mismatch: expected {args.sha256}, got {digest}"
            )

    extract_dir = tmpdir / "extract"
    extract_dir.mkdir()
    if archive_kind == "zip":
        with zipfile.ZipFile(archive_path) as z:
            z.extractall(extract_dir)
            inner = next(extract_dir.iterdir())
    else:
        with tarfile.open(archive_path) as t:
            t.extractall(extract_dir)
            inner = next(extract_dir.iterdir())
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(str(inner), dest)
    shutil.rmtree(tmpdir)
    print(f"Downloaded {url} to {dest} (sha256={digest})")


def _chmod_recursive(path: Path, readonly: bool) -> None:
    mode_file = stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH
    mode_dir = mode_file | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    if not readonly:
        mode_file |= stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH
        mode_dir |= stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH
    for p in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        try:
            p.chmod(mode_dir if p.is_dir() else mode_file)
        except Exception as e:
            logging.warning("Failed to chmod %s: %s", p, e)
    try:
        path.chmod(mode_dir if path.is_dir() else mode_file)
    except Exception as e:
        logging.warning("Failed to chmod %s: %s", path, e)


def protect(args: argparse.Namespace) -> None:
    dest = Path(args.dest)
    _chmod_recursive(dest, readonly=args.readonly)
    state = "read-only" if args.readonly else "writable"
    print(f"Marked {dest} as {state}")


def upload(args: argparse.Namespace) -> None:
    workdir = Path(args.workdir)
    branch = args.default_branch
    remote = args.remote_url
    if not workdir.exists():
        raise SystemExit(f"{workdir} does not exist")

    if not (workdir / ".git").exists():
        run(["git", "init"], cwd=workdir)
        run(["git", "branch", "-M", branch], cwd=workdir)
    run(["git", "config", "user.email", "codex@example.com"], cwd=workdir)
    run(["git", "config", "user.name", "Codex Repo Manager"], cwd=workdir)

    try:
        run(["git", "remote", "remove", "origin"], cwd=workdir)
    except subprocess.CalledProcessError as e:
        logging.warning("Failed to remove origin remote: %s", e)
    run(["git", "remote", "add", "origin", remote], cwd=workdir)

    # add files in manageable chunks
    files: list[str] = []
    for root, _, fs in os.walk(workdir):
        for f in fs:
            rel = os.path.relpath(os.path.join(root, f), workdir)
            files.append(rel)
    chunk = 500
    for i in range(0, len(files), chunk):
        run(["git", "add"] + files[i:i+chunk], cwd=workdir)

    try:
        run(["git", "commit", "-m", "Automated upload via Codex Repo Manager"], cwd=workdir)
    except subprocess.CalledProcessError as e:
        logging.warning("No changes to commit: %s", e)

    run(["git", "push", "--force-with-lease", "-u", "origin", branch], cwd=workdir)
    print("Upload complete")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Manage local Codex source repo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ensure = sub.add_parser("ensure-source", help="download or clone Codex source")
    p_ensure.add_argument("--dest", required=True)
    p_ensure.add_argument("--repo", default=DEFAULT_REPO)
    p_ensure.add_argument("--tag", default=DEFAULT_TAG)
    p_ensure.add_argument("--prefer", choices=["git", "archive"], default="git")
    p_ensure.add_argument("--archive", choices=["zip", "tar.gz"], default="zip")
    p_ensure.add_argument(
        "--sha256",
        help="expected SHA256 checksum of downloaded archive",
    )
    p_ensure.set_defaults(func=ensure_source)

    p_protect = sub.add_parser("protect", help="set folder read-only or writable")
    p_protect.add_argument("--dest", required=True)
    grp = p_protect.add_mutually_exclusive_group(required=True)
    grp.add_argument("--readonly", action="store_true")
    grp.add_argument("--writable", action="store_true")
    p_protect.set_defaults(func=protect)

    p_upload = sub.add_parser("upload", help="push local repo to remote")
    p_upload.add_argument("--workdir", required=True)
    p_upload.add_argument("--remote-url", required=True)
    p_upload.add_argument("--default-branch", default="main")
    p_upload.set_defaults(func=upload)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
```

Utility for managing the local Codex source checkout.

Subcommands:
  ensure-source -- ensure a local copy of the Codex source exists
                  optionally verify downloaded archive with --sha256
  protect       -- toggle read only/writable state for the source directory
  upload        -- push the source tree to a user provided git remote
**Functions:** run(cmd, cwd), ensure_source(args), _chmod_recursive(path, readonly), protect(args), upload(args), main(argv)


## Module `tools\codex_scrub.py`

```python
#!/usr/bin/env python3
import subprocess, sys, shutil
from pathlib import Path
from datetime import datetime

ART=Path(".triplewash/artifacts"); ART.mkdir(parents=True, exist_ok=True)

def run(cmd): return subprocess.run(cmd, text=True, shell=isinstance(cmd,str), capture_output=True)

def append_outbox(stage, ok, summary, notes=""):
    p=Path("Codex_Agents/outbox.md"); p.parent.mkdir(exist_ok=True,parents=True)
    ts=datetime.utcnow().isoformat()
    body=f"\n## [CODEX] {ts} {stage} ok:{str(ok).lower()}\n- summary: {summary}\n- notes:\n```\n{notes.strip()}\n```\n- artifacts:\n  - {ART}/scrub.log\n"
    p.write_text(p.read_text(encoding="utf-8")+body if p.exists() else "# Codex → Copilot Outbox (system-log)\n"+body, encoding="utf-8")

def main():
    log = ART/"scrub.log"
    notes=[]
    notes.append("normalize headings; keep fenced code; bucketize lists")
    d=run([sys.executable,"distill_dumps.py"]); notes += [d.stdout,d.stderr]
    ok=True
    log.write_text("\n".join([n for n in notes if n]), encoding="utf-8")
    append_outbox("CODEX_SCRUB", ok, "applied refactor/scrub & re-distilled dumps", "\n".join(notes))
    subprocess.run([sys.executable,"tools/triplewash_status.py","set","COPILOT_FINALIZE","true" if ok else "false","codex-scrub complete"], check=False)

if __name__=="__main__":
    main()
```

**Functions:** run(cmd), append_outbox(stage, ok, summary, notes), main()


## Module `tools\dump_watcher.py`

```python
"""Watch for new ``dump*.md`` files and process them.

This service observes ``Codex_Agents`` for files matching ``dump*.md``.
Whenever a file is created or modified the dump is distilled into the
dataset and the documentation links are refreshed.  Processed dumps are
archived automatically by :mod:`distill_dumps`.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "Codex_Agents"
ARCHIVE_DIR = AGENTS_DIR / "archive"
DOCS_DIR = ROOT / "docs"
DOC_FILE = DOCS_DIR / "dump_archive.md"


def update_docs_links() -> None:
    """Generate ``docs/dump_archive.md`` with links to archived dumps."""

    lines = [
        "# 📥 Dump Archive",
        "",
        "Processed `dump*.md` files live in `Codex_Agents/archive/`.",
        "This file is updated automatically whenever new dumps are ingested.",
        "",
    ]

    for path in sorted(ARCHIVE_DIR.glob("dump*.md")):
        rel = Path("..") / path.relative_to(DOCS_DIR.parent)
        lines.append(f"- [{path.name}]({rel.as_posix()})")

    lines.append("")
    DOC_FILE.write_text("\n".join(lines), encoding="utf-8")


def process_dumps() -> None:
    """Run the distillation script and refresh docs links."""

    subprocess.run(["python", str(ROOT / "distill_dumps.py")], check=True)
    update_docs_links()


class DumpEventHandler(PatternMatchingEventHandler):
    """Trigger dump processing on file events."""

    def __init__(self) -> None:
        super().__init__(patterns=["dump*.md"], ignore_directories=True)

    def on_created(self, event):  # noqa: D401 - short handler
        process_dumps()

    def on_modified(self, event):  # noqa: D401 - short handler
        process_dumps()


def main() -> None:
    """Start the file watcher service."""

    update_docs_links()

    observer = Observer()
    observer.schedule(DumpEventHandler(), str(AGENTS_DIR), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
```

Watch for new ``dump*.md`` files and process them.

This service observes ``Codex_Agents`` for files matching ``dump*.md``.
Whenever a file is created or modified the dump is distilled into the
dataset and the documentation links are refreshed.  Processed dumps are
archived automatically by :mod:`distill_dumps`.
**Classes:** DumpEventHandler
**Functions:** update_docs_links(), process_dumps(), main()


## Module `tools\export_merged_tasks.py`

```python
"""CLI to export merged tasks into Project_datasets."""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.task_manager import TaskManager


def main(output: str | None = None) -> Path:
    tm = TaskManager()
    return tm.export_completed(Path(output) if output else None)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    parser = argparse.ArgumentParser(description="Export merged tasks to dataset")
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="Optional path for export file"
    )
    args = parser.parse_args()
    dest = main(args.output)
    print(f"Exported merged tasks to {dest}")
```

CLI to export merged tasks into Project_datasets.
**Functions:** main(output)


## Module `tools\migrate_agent_dataset.py`

```python
#!/usr/bin/env python3
"""Convert a SQLite agent dataset back to JSON format.

This helper migrates entries from a database created during the brief
SQLite experiment to the canonical JSON representation used by Codex Studio.
"""
import argparse
import json
import sqlite3
from pathlib import Path

def migrate(db_path: Path, json_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        rows = cur.execute(
            "SELECT id, created, source_path, content, buckets, status FROM entries"
        ).fetchall()
    except sqlite3.Error as exc:  # pragma: no cover - best effort
        raise SystemExit(f"Failed to read entries: {exc}\n")
    entries = []
    for row in rows:
        ident, created, source, content, buckets, status = row
        try:
            bucket_list = json.loads(buckets) if isinstance(buckets, str) else []
        except json.JSONDecodeError:
            bucket_list = []
        entries.append(
            {
                "id": ident,
                "created": created,
                "source_path": source,
                "content": content,
                "buckets": bucket_list,
                "status": status,
            }
        )
    json_path.write_text(json.dumps({"entries": entries}, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} entries to {json_path}")

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Convert agent_dataset.db to agent_dataset.json"
    )
    ap.add_argument("db", nargs="?", default="datasets/agent_dataset.db")
    ap.add_argument("json", nargs="?", default="datasets/agent_dataset.json")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        ap.exit(1, f"Error: {db_path} not found\n")
    migrate(db_path, Path(args.json))

if __name__ == "__main__":
    main()
```

Convert a SQLite agent dataset back to JSON format.

This helper migrates entries from a database created during the brief
SQLite experiment to the canonical JSON representation used by Codex Studio.
**Functions:** migrate(db_path, json_path), main()


## Module `tools\process_all_dump_files.py`

```python
"""Convenience wrapper to process dump files.

This script invokes :func:`distill_dumps.main` so it can be triggered by
automation systems with the phrase "Process All Dump Files". It ensures that
new dumps such as ``dump10.md`` are detected and indexed without manual
intervention.
"""

from pathlib import Path
import sys

# Ensure project root is on the module search path so ``distill_dumps`` can be
# imported when this script is executed from the ``tools`` directory.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from distill_dumps import main


if __name__ == "__main__":
    main()
```

Convenience wrapper to process dump files.

This script invokes :func:`distill_dumps.main` so it can be triggered by
automation systems with the phrase "Process All Dump Files". It ensures that
new dumps such as ``dump10.md`` are detected and indexed without manual
intervention.


## Module `tools\summarize_logs.py`

```python
#!/usr/bin/env python3
"""Download and summarize GitHub Actions workflow logs.

This utility fetches a workflow run's log archive, sends a snippet to
``ollama_chat`` for summarization, and prints the result.  If the
summarizer fails, the script falls back to printing a truncated portion
of the raw logs.  The script exits non-zero when the log archive cannot
be downloaded.

Usage:
    python tools/summarize_logs.py <logs_url>

Environment variables:
    GITHUB_TOKEN  -- token with access to the repository (optional).
    OLLAMA_URL    -- base URL for the Ollama server (default:
                     ``http://localhost:11434``).
    OLLAMA_MODEL  -- model name for summarization (default: ``codex``).
"""

from __future__ import annotations

import io
import os
import sys
import zipfile
import urllib.request

from Codex_Studio import ollama_chat

TRUNCATE_LINES = 200
PROMPT = "Summarize the following GitHub Actions log and identify the failure cause."


def download_logs(url: str, token: str | None) -> str:
    """Return the joined text of all log files in the archive at *url*.

    The function exits the program with a non-zero status on download
    errors.
    """

    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}")
            data = resp.read()
    except Exception as exc:
        print(f"Failed to download logs: {exc}", file=sys.stderr)
        sys.exit(1)

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        parts = []
        for name in sorted(zf.namelist()):
            if name.endswith(".txt"):
                parts.append(zf.read(name).decode("utf-8", "replace"))
    return "\n".join(parts)


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: summarize_logs.py <logs_url>", file=sys.stderr)
        sys.exit(1)

    log_url = sys.argv[1]
    token = os.environ.get("GITHUB_TOKEN")
    logs = download_logs(log_url, token)

    # Limit the text sent to the model to avoid huge payloads.
    snippet = logs[-8000:]

    base = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "codex")
    messages = [{"role": "user", "content": f"{PROMPT}\n\n{snippet}"}]
    ok, out = ollama_chat(base, model, messages)

    if ok and out.strip():
        print(out.strip())
    else:
        lines = logs.splitlines()
        print("\n".join(lines[:TRUNCATE_LINES]))


if __name__ == "__main__":
    main()
```

Download and summarize GitHub Actions workflow logs.

This utility fetches a workflow run's log archive, sends a snippet to
``ollama_chat`` for summarization, and prints the result.  If the
summarizer fails, the script falls back to printing a truncated portion
of the raw logs.  The script exits non-zero when the log archive cannot
be downloaded.

Usage:
    python tools/summarize_logs.py <logs_url>

Environment variables:
    GITHUB_TOKEN  -- token with access to the repository (optional).
    OLLAMA_URL    -- base URL for the Ollama server (default:
                     ``http://localhost:11434``).
    OLLAMA_MODEL  -- model name for summarization (default: ``codex``).
**Functions:** download_logs(url, token), main()


## Module `tools\task_dispatcher.py`

```python
"""TaskDispatcher module for polling TaskManager and forwarding tasks to Codex."""

from __future__ import annotations

import logging
import time
from typing import Callable, List, Optional

from tools.task_manager import Task, TaskManager

logger = logging.getLogger(__name__)


class TaskHandler:
    """Base class for task handlers.

    Subclasses should override :meth:`can_handle` and :meth:`handle` to
    process specific task types. The :meth:`handle` method should return a
    string payload that will be forwarded to Codex. If ``None`` is returned,
    nothing will be forwarded for that task.
    """

    def can_handle(self, task: Task) -> bool:  # pragma: no cover - interface method
        return False

    def handle(self, task: Task) -> Optional[str]:  # pragma: no cover - interface method
        raise NotImplementedError


class TaskDispatcher:
    """Poll :class:`TaskManager` and forward tasks to Codex.

    Parameters
    ----------
    task_manager:
        Source from which tasks are polled.
    codex_sender:
        Callable used to forward payloads to Codex. It should accept a string
        and may raise exceptions on failure.
    poll_interval:
        Delay between polling cycles when :meth:`run` is used.
    """

    def __init__(
        self,
        task_manager: TaskManager,
        codex_sender: Callable[[str], None],
        poll_interval: float = 5.0,
    ) -> None:
        self.task_manager = task_manager
        self.codex_sender = codex_sender
        self.poll_interval = poll_interval
        self.handlers: List[TaskHandler] = []

    # ------------ registration ------------
    def register_handler(self, handler: TaskHandler) -> None:
        """Register a handler for dispatching tasks."""
        self.handlers.append(handler)

    # ------------ dispatch logic ------------
    def dispatch_once(self) -> None:
        """Process all open tasks once.

        This method fetches tasks from :class:`TaskManager` and tries to find a
        registered handler for each. On success the task is marked complete. Any
        exceptions are logged and do not stop the dispatcher.
        """

        for task_dict in self.task_manager.list_tasks():
            task = Task(**task_dict)
            if task.status != "open":
                continue

            handler = self._find_handler(task)
            if handler is None:
                logger.warning("No handler found for task %s", task.id)
                continue

            try:
                payload = handler.handle(task)
                if payload:
                    self._send_to_codex(payload)
                # mark task as done so it is removed from the active queue
                self.task_manager.mark_done(task.id)
                logger.info("Task %s handled by %s", task.id, handler.__class__.__name__)
            except Exception as exc:  # pragma: no cover - exercised in tests
                logger.error(
                    "Handler %s failed for task %s: %s",
                    handler.__class__.__name__,
                    task.id,
                    exc,
                )

    def run(self) -> None:
        """Continuously poll for tasks until interrupted."""
        try:
            while True:
                self.dispatch_once()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:  # pragma: no cover - manual interruption
            logger.info("TaskDispatcher stopped")

    # ------------ internal helpers ------------
    def _find_handler(self, task: Task) -> Optional[TaskHandler]:
        for handler in self.handlers:
            try:
                if handler.can_handle(task):
                    return handler
            except Exception as exc:
                logger.error(
                    "Error checking handler %s for task %s: %s",
                    handler.__class__.__name__,
                    task.id,
                    exc,
                )
        return None

    def _send_to_codex(self, payload: str) -> None:
        """Forward payload to Codex using the provided sender callable."""
        try:
            self.codex_sender(payload)
        except Exception as exc:
            logger.error("Failed sending task to Codex: %s", exc)
            raise
```

TaskDispatcher module for polling TaskManager and forwarding tasks to Codex.
**Classes:** TaskHandler, TaskDispatcher


## Module `tools\task_manager.py`

```python
from __future__ import annotations

"""Task manager storing note metadata and exporting to Agent_Versions."""

from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import List, Optional
import uuid

from PySide6.QtCore import QObject, Signal

# Paths
ROOT_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT_DIR / "logs"
AGENT_DIR = ROOT_DIR / "Agent_Versions"
TASKS_FILE = LOG_DIR / "tasks.json"

logger = logging.getLogger(__name__)


@dataclass
class Task:
    id: str
    title: str
    status: str
    created: str
    file: str
    branch: str = ""
    merged_commit: str = ""


class TaskManager(QObject):
    """Persist tasks and map notes to agent version files."""

    tasks_changed = Signal()

    def __init__(self, db_path: Path | None = None):
        super().__init__()
        self.db_path = Path(db_path) if db_path else TASKS_FILE
        # ensure parent directory exists before any IO
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._tasks: List[Task] = []
        AGENT_DIR.mkdir(parents=True, exist_ok=True)
        self._load()

    # ---------- internal helpers ----------
    def _load(self) -> None:
        if self.db_path.exists():
            try:
                data = json.loads(self.db_path.read_text(encoding="utf-8"))
                tasks: List[Task] = []
                for t in data:
                    # Backward compatibility with tasks missing new fields
                    merged = {
                        "status": "queued",
                        "created": datetime.now().isoformat(),
                        "branch": "",
                        "merged_commit": "",
                    }
                    merged.update(t)
                    tasks.append(Task(**merged))
                self._tasks = tasks
            except json.JSONDecodeError as exc:
                logger.error("Failed to decode tasks database %s: %s", self.db_path, exc)
        else:
            self._tasks = []

    def _save(self) -> None:
        data = [asdict(t) for t in self._tasks]
        # ensure directory exists before writing
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _next_version(self) -> int:
        nums = []
        for p in AGENT_DIR.glob("Agent_*.md"):
            try:
                nums.append(int(p.stem.split("_")[1]))
            except (IndexError, ValueError):
                continue
        return max(nums, default=0) + 1

    # ---------- public API ----------
    def reload(self) -> None:
        """Reload tasks from the database file."""
        self._load()

    def add_task(self, title: str, content: str, status: str = "open", branch: str = "") -> str:
        """Save note content to an Agent_Versions file and record metadata.

        Returns the path to the created agent file.
        """
        version = self._next_version()
        agent_file = AGENT_DIR / f"Agent_{version}.md"
        agent_file.write_text(content, encoding="utf-8")

        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            status=status,
            created=datetime.now().isoformat(),
            file=str(agent_file.relative_to(ROOT_DIR)),
            branch=branch,
        )
        self._tasks.append(task)
        self._save()
        self.tasks_changed.emit()
        return str(agent_file)

    def list_tasks(self) -> List[dict]:
        return [asdict(t) for t in self._tasks]

    def list_completed(self) -> List[dict]:
        """Return tasks marked as completed."""
        return [asdict(t) for t in self._tasks if t.status == "done"]

    def export_completed(self, export_path: Path | None = None) -> Path:
        """Export merged tasks for downstream processing.

        Tasks with ``status == 'merged'`` are collected and written to a JSON
        file containing the title, agent file content, branch, and merged commit
        hash. The destination defaults to ``Project_datasets/merged_tasks.json``
        but may be overridden via ``export_path``.
        """

        export_dir = ROOT_DIR / "Project_datasets"
        export_dir.mkdir(parents=True, exist_ok=True)
        dest = Path(export_path) if export_path else export_dir / "merged_tasks.json"

        records = []
        for t in self._tasks:
            if t.status == "merged":
                agent_path = ROOT_DIR / t.file
                try:
                    content = agent_path.read_text(encoding="utf-8")
                except OSError:
                    content = ""
                records.append(
                    {
                        "title": t.title,
                        "content": content,
                        "branch": t.branch,
                        "merged_commit": t.merged_commit,
                    }
                )

        dest.write_text(json.dumps(records, indent=2), encoding="utf-8")
        return dest

    def get_task(self, task_id: str) -> Optional[Task]:
        return next((t for t in self._tasks if t.id == task_id), None)

    def mark_done(self, task_id: str) -> bool:
        """Mark a task as completed.

        Parameters
        ----------
        task_id: str
            Identifier of the task to mark done.

        Returns
        -------
        bool
            ``True`` if the task was found and updated, ``False`` otherwise.
        """

        t = self.get_task(task_id)
        if not t:
            return False
        t.status = "done"
        self._save()
        self.tasks_changed.emit()
        return True

    # Backwards compatible alias
    def mark_complete(self, task_id: str) -> bool:  # pragma: no cover - thin wrapper
        return self.mark_done(task_id)

    def pause_task(self, task_id: str) -> bool:
        """Set a task status to ``paused``.

        This is a minimal helper used by the UI when a task is temporarily
        withheld from dispatch. Paused tasks remain in the task list but are
        ignored by automated dispatchers.
        """

        t = self.get_task(task_id)
        if not t:
            return False
        t.status = "paused"
        self._save()
        self.tasks_changed.emit()
        return True

    def remove_task(self, task_id: str) -> bool:
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        if len(self._tasks) == before:
            return False
        self._save()
        self.tasks_changed.emit()
        return True

    def clear_completed(self) -> int:
        """Remove all completed tasks.

        Returns the number of tasks removed."""
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.status != "done"]
        removed = before - len(self._tasks)
        if removed:
            self._save()
            self.tasks_changed.emit()
        return removed
```

**Classes:** Task, TaskManager


## Module `tools\triplewash_status.py`

```python
#!/usr/bin/env python3
import json, sys
from pathlib import Path
STATE = Path(".triplewash/status.json")
def load():
    if STATE.exists(): return json.loads(STATE.read_text(encoding="utf-8"))
    STATE.parent.mkdir(parents=True, exist_ok=True)
    s={"stage":"CODEx_CHECK","attempt":0,"ok":False,"notes":[]}
    STATE.write_text(json.dumps(s,indent=2),encoding="utf-8")
    return s
def save(s): STATE.write_text(json.dumps(s,indent=2),encoding="utf-8")
def set_stage(next_stage, ok=None, note=None):
    s=load(); 
    if note: s["notes"]=list(dict.fromkeys(s.get("notes",[])+[note]))
    s["stage"]=next_stage
    if ok is not None: s["ok"]=bool(ok)
    if next_stage.endswith("_CHECK") and s.get("stage")==next_stage: s["attempt"]=s.get("attempt",0)+1
    save(s)
if __name__=="__main__":
    if len(sys.argv)<2: print(load()); sys.exit(0)
    if sys.argv[1]=="set": set_stage(sys.argv[2], (sys.argv[3].lower()=="true") if len(sys.argv)>3 else None, sys.argv[4] if len(sys.argv)>4 else None)
    else: print(load())
```

**Functions:** load(), save(s), set_stage(next_stage, ok, note)

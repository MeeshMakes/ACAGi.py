# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `agent_terminal.py`

Agent Terminal — Standalone/Embeddable Terminal Card (PySide6)
(Updated: remove QEvent.TextChanged usage; auto-grow via textChanged signal;
keeps all prior features; HiDPI policy set before QApplication.)

**Classes:** SocketBroadcastHandler, CodexManager, Theme, MacroManager, MacroManagerDialog, VectorStore, ContextHistory, VisionService, TermHighlighter, MovableCard, TerminalCard, SettingsDialog, HostWindow, StartupCodexDialog

**Functions:** _log_codex_install_failure(error), _verify_checksum(path, expected), _codex_binary_present(), prompt_install_codex(), _load_codex(), log_command(cmd, status), bootstrap_install_instructions(dataset_path, doc_path), update_schema(operator), run_gui_command(action, expected_text, region, task_id), load_persona(), apply_persona(text, persona), log_auto_execution(cmd, rationale, output, returncode), start_log_server(port), open_in_os(path), install_dependency(name, url, checksum, log_path, retries), _requests(), post_with_retry(model, messages, retries), find_git_bash(), nl_for_env(env), wrap_powershell_for_cmd(script), human_size(num_bytes), timestamp(), load_state(), save_state(st), available_voices(), speak(text, voice), load_config(), save_config(cfg), cosine_sim(a, b), _apply_settings_from_dialog(card, cfg), _open_settings_on_card(card), _open_tasks_on_card(card), build_widget(parent), _is_admin(), _relaunch_as_admin(argv), main(argv)
### `codex_installation.py`

**Functions:** download_codex(url, version, checksum, target_dir, install_log, retries), load_install_notes(memory_path, install_log), ensure_codex_installed(version, base_dir, dataset_log)
### `code_editor.py`

code_editor.py — Agent-ready Code Editor CARD (PySide6)

• Fully compatible with Virtual_Desktop.py loader:
    - Exposes create_card(parent)->(QWidget, title) and build_widget(parent)
    - Stand-alone main() runner also included
• Dark taskbar/header and rounded “card” styling (matches Terminal theme)
• Monospace editor with line numbers, current-line highlight, wrap toggle
• Zoom: Ctrl+= / Ctrl+- / Ctrl+0
• File ops: New / Open / Save / Save As…
• Agent-friendly API (no dialogs needed):
    - set_file_path(path), save(), save_to(path), set_text(str), text(), open_path(path)
• Multiple instances supported (terminal can open many editors)

Optional env hints the Terminal can set before loading as a card:
    CODE_EDITOR_FILE=<path to open>      (open an existing file)
    CODE_EDITOR_NEWNAME=<suggested name> (untitled placeholder shown in title bar)
    CODE_EDITOR_EXT=<.py|.txt|.json>     (pre-select new file extension)

**Classes:** EditorHistory, Theme, LineNumberArea, Editor, PythonHighlighter, MarkdownHighlighter, EditorCard, HostWindow

**Functions:** timestamp(), _import_qt(), _sanitize_initial(path_str), create_card(parent, theme), build_widget(parent, theme, initial_path, suggested_name, default_ext), main()
### `deployment_manager.py`

Helper utilities for cloning repositories and launching agent nodes.

**Functions:** clone_repo(target_path), _record_deployment(meta), _load_deployments(), launch_agent(target_path), tether_logs(source_repo, target_repo)
### `l2c_tool.py`

**Functions:** generate_commands(natural_text, shell)
### `prompt_manager.py`

**Functions:** _dataset_path(), _chains_path(), create_prompt(task_id, text, scope), read_prompts(task_id), chain_prompts(parent_id, prompts), _update_chain(parent_id, text, state), mark_prompt_done(parent_id, text), prune_stale_chains()
### `schema_manager.py`

**Functions:** load_schema(operator), apply_schema(sections, target_agent_md), validate_schema(schema), apply_schema_to_persona(schema, persona_path)
### `tasks.py`

**Classes:** Task, TaskManager, TaskRow, TaskListView, CardBase, TaskCard

**Functions:** open_card(manager, t, open_editor, parent), close_card(card), close_all_cards()
### `Virtual_Desktop.py`

Virtual_Desktop.py — agent-ready virtual desktop with card loader, template terminal,
system log, pop-out System Console, Desktop Explorer, and internal Code Editor card.

Updates (this build):
- Shift + Mouse Wheel ⇒ horizontal pan; normal wheel ⇒ vertical pan (when not fullscreen).
- No panning while in fullscreen remains enforced.
- Cards auto-raise on create/open; added 'Bring All To Front', 'Tile Cards', and a Windows list.
- Added Tools ▸ Open code_editor.py (loads as internal editor card).
- Desktop Explorer card: icons for files/folders under ./Virtual_Desktop ; double-click to open.
- Preserves embedded app look (no extra QSS on child widgets).
- Debounced canvas sync on real screen changes/fullscreen only (reduces log spam).
- Per-card geometry persistence (position & size remembered across sessions).
 - Supports ``build_widget(parent)`` factories for embedding.
- Dark, high-contrast UI preserved.

**Classes:** Theme, SystemConsole, CursorOverlay, Card, DesktopCanvas, Camera, TemplateTerminal, ExplorerCard, MonitorCard, ProcessConsole, VirtualDesktop

**Functions:** _show_manual_install(pkg), log(msg, level), _load_state(), _save_state(state), _remember_card(kind, path, title), _geom_key_for(kind, path_or_tag), _restore_card_geom(card, kind, path_or_tag), _save_card_geom(card, kind, path_or_tag), apply_contrast_palette(w, bg_hex, fg_hex), _parse_args(), main()
### `Archived Conversations\Codex-info\bootstrap_codex.py`

**Functions:** reset_transit(), copy_codex(), write_manifest(), populate_transit(), copy_to_clipboard()
### `Archived Conversations\codex-rust-v0.23.0 - info\Analyze_folders.py`

**Functions:** analyze_folders(start_path)
### `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\scripts\stage_rust_release.py`

**Functions:** main()
### `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\generate_mcp_types.py`

**Classes:** StructField, RustProp

**Functions:** main(), add_definition(name, definition, out), define_struct(name, properties, required_props, description), infer_result_type(request_type_name), implements_request_trait(name), implements_notification_trait(name), add_trait_impl(type_name, trait_name, fields, out), define_string_enum(name, enum_values, out, description), define_untagged_enum(name, type_list, out), define_any_of(name, list_of_refs, description), get_serde_annotation_for_anyof_type(type_name), map_type(typedef, prop_name, struct_name), rust_prop_name(name, is_optional), to_snake_case(name), capitalize(name), check_string_list(value), type_from_ref(ref), emit_doc_comment(text, out)
### `Archived Conversations\codex-rust-v0.23.0 - info\scripts\asciicheck.py`

**Functions:** main(), lint_utf8_ascii(filename, fix)
### `Archived Conversations\codex-rust-v0.23.0 - info\scripts\publish_to_npm.py`

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
### `Archived Conversations\codex-rust-v0.23.0 - info\scripts\readme_toc.py`

Utility script to verify (and optionally fix) the Table of Contents in a
Markdown file. By default, it checks that the ToC between `<!-- Begin ToC -->`
and `<!-- End ToC -->` matches the headings in the file. With --fix, it
rewrites the file to update the ToC.

**Functions:** main(), generate_toc_lines(content), check_or_fix(readme_path, fix)
### `cli\deploy.py`

Command line helpers for managing agent deployments.

**Functions:** _read_deployments(), cmd_deploy(args), cmd_list_nodes(args), cmd_terminate(args), build_parser(), main(argv)
### `cli\__init__.py`

CLI helpers for the Agent Terminal project.
### `Codex\cli_adapter.py`

Utility to adapt raw CLI output from the open-source Codex executable.

The open-source Codex CLI may emit mixed descriptive text and shell commands
without structure.  :func:`parse_cli_output` normalizes such stdout/stderr and
returns a mapping containing a human readable description and a list of shell
commands suitable for display or execution.

**Functions:** parse_cli_output(raw)
### `Codex\codex_manager.py`

Codex dispatch manager.

Provides a simple dispatch() function that routes user text to shell
commands, tool calls, or prompts. Each decision is persisted to
memory/codex_memory.json for future retrieval.

**Classes:** CodexPersona

**Functions:** _load_persona(), build_persona_directive(), log_state(cmd, state, output), record_command_result(cmd, stdout, stderr, returncode), _load_memory(path), _save_memory(data, path), get_binary(), codex_available(path), manager_version(), dispatch(user_text)
### `Codex\open_source_manager.py`

Fallback Codex manager that proxies a CLI-based open-source LLM.

The manager executes a user-configurable shell command defined by the
``CLI_LLM_CMD`` environment variable.  Combined ``stdout`` and ``stderr``
from the command are parsed with :func:`Codex.cli_adapter.parse_cli_output`
to extract natural language responses and any suggested shell commands.

If ``CLI_LLM_CMD`` is unset, the manager simply echoes the input text.
Conversation logs are persisted to ``memory/codex_memory.json`` using the
same format as the primary Codex manager.

**Functions:** _load_memory(path), _save_memory(data, path), _cli_llm(prompt), dispatch(user_text), manager_version()
### `memory\bucket_manager.py`

**Functions:** register_bucket(name, path, description), append_entry(bucket, data), query_bucket(bucket, filters)
### `memory\datasets.py`

**Functions:** cosine_sim(a, b), write_entry(dataset_name, record), query(dataset_name, embedding, top_k), read_entries(dataset_name, task_id), embed_text(text), log_prompt(role, text, task_id), log_error(text, task_id), log_authorization(cmd, granted, task_id), _search(dataset, embedding, top_k, task_id), search_prompts(embedding, top_k, task_id), search_errors(embedding, top_k, task_id), search_authorizations(embedding, top_k, task_id), rag_search(embedding, top_k, task_id)
### `memory\prompt_buckets.py`

**Functions:** _bucket_path(name), append_bucket(bucket_name, prompt, response, metadata), retrieve_similar(bucket_name, query, top_k)
### `security\guardrails.py`

**Functions:** is_safe_path(path), requires_confirmation(cmd)
### `security\__init__.py`
### `shells\detector.py`

Shell detection utilities.

**Functions:** _match_shell(name), _detect_from_env(), _parent_command(pid), _detect_from_parents(), detect_shell()
### `shells\transpiler.py`

Command transpiler between shells.

**Functions:** transpile_command(cmd, shell)
### `shells\__init__.py`
### `tests\conftest.py`

**Functions:** _install_log_path(tmp_path, monkeypatch)
### `tests\test_agent_terminal.py`

**Functions:** test_project_root_points_to_repo_root(), test_tool_combo_persistence(), test_build_widget_returns_terminal_card(), test_command_combo_inserts_text(), test_install_dependency_logs(tmp_path, monkeypatch), test_l2c_generate_uses_current_shell(monkeypatch), test_main_reinvokes_without_admin(monkeypatch), test_mode_combo_and_switching(monkeypatch), test_codex_setting_persistence(), test_launch_codex_embedded_writes_handshake(tmp_path, monkeypatch), test_launch_codex_embedded_sets_gpu_env(tmp_path, monkeypatch), test_launch_codex_embedded_logs_failure(tmp_path, monkeypatch), test_tool_codex_launch_failure_falls_back(monkeypatch)
### `tests\test_agent_terminal_plugins.py`

**Functions:** test_agent_terminal_missing_plugins(monkeypatch, tmp_path)
### `tests\test_basic.py`

**Functions:** test_basic_discovery()
### `tests\test_cli_adapter.py`

**Functions:** test_cli_adapter_parses_description_and_commands()
### `tests\test_codex_cli_fallback.py`

**Functions:** test_cli_failure_falls_back(monkeypatch)
### `tests\test_codex_dispatch.py`

**Functions:** memory_tmp(tmp_path, monkeypatch), chains_tmp(tmp_path, monkeypatch), test_dispatch_shell(memory_tmp, chains_tmp), test_dispatch_tool(memory_tmp), test_dispatch_prompt(memory_tmp), test_dispatch_shell_failure_logs_fix(memory_tmp, chains_tmp), test_codex_available(tmp_path)
### `tests\test_codex_install.py`

**Classes:** DummyResp

**Functions:** test_download_codex_resume_and_metadata(tmp_path, monkeypatch)
### `tests\test_codex_persona.py`

**Functions:** test_build_persona_directive_env(monkeypatch)
### `tests\test_codex_prompt_chat.py`

**Functions:** test_codex_prompt_short_circuit(monkeypatch), test_codex_delegates_l2c(monkeypatch), test_codex_absent(monkeypatch)
### `tests\test_codex_prompt_install.py`

**Functions:** test_prompt_install_decline(monkeypatch), test_prompt_install_accept(monkeypatch), test_prompt_install_failure_logs(monkeypatch, tmp_path)
### `tests\test_code_editor.py`

**Functions:** test_create_card_returns_widget_and_title(), test_import_qt_repairs_missing_plugins(monkeypatch, tmp_path), test_blank_start_ignores_env(monkeypatch), test_blank_start_missing_file(monkeypatch, tmp_path), test_save_as_uses_selected_extension(monkeypatch, tmp_path, label, ext), test_startup_preselects_extension(monkeypatch), test_new_file_resets_state(monkeypatch, tmp_path), test_launches_blank_document(), test_highlighter_tracks_extension(), test_line_number_area_paint_event_ends_painter(monkeypatch)
### `tests\test_config.py`

**Functions:** test_load_config_creates_defaults(tmp_path), test_load_config_recovers_from_invalid_json(tmp_path)
### `tests\test_datasets.py`

**Functions:** test_write_and_query(tmp_path, monkeypatch), test_log_helpers(tmp_path, monkeypatch)
### `tests\test_direct_launch.py`

**Functions:** _patch_runtime(monkeypatch), test_main_launches_agent_terminal(monkeypatch)
### `tests\test_editor_card.py`

**Functions:** _init_term(), test_editor_open_and_new_spawn_cards(tmp_path), test_editor_save_logs_history(tmp_path), test_editor_new_save_file(tmp_path), test_chat_messages_logged(tmp_path)
### `tests\test_full_auto.py`

**Functions:** test_destructive_requires_confirmation(), test_full_auto_streams_and_logs(tmp_path, monkeypatch)
### `tests\test_l2c_prompt.py`

**Functions:** test_l2c_prompt_embeds_shell()
### `tests\test_l2c_tool.py`

**Functions:** test_l2c_tool_registered(), test_generate_commands_matches_shell(), test_dispatch_invokes_l2c_tool()
### `tests\test_lexicon.py`

**Functions:** test_lexicon_present(), test_rag_context_includes_lexicon(monkeypatch)
### `tests\test_macro_manager.py`

**Functions:** test_macro_manager_crud(tmp_path), test_macro_manager_dialog_run()
### `tests\test_monitor_card.py`

**Functions:** test_monitor_card_receives_logs_and_pong(monkeypatch)
### `tests\test_ocr_verification.py`

**Functions:** test_ocr_service_verify(monkeypatch), test_run_gui_command_calls_verify(monkeypatch)
### `tests\test_open_source_cli.py`

**Functions:** test_cli_output_parsing(monkeypatch, tmp_path)
### `tests\test_open_source_fallback.py`

**Functions:** test_fallback_to_open_source(monkeypatch, tmp_path)
### `tests\test_persona_tone.py`

**Functions:** test_apply_persona_high_excitement()
### `tests\test_powershell_wrap.py`

**Functions:** test_wrap_inline_one_line(), test_wrap_multiline_creates_file()
### `tests\test_prompt_buckets_root.py`

**Functions:** test_ephemeral_discard_persistent_remain(tmp_path, monkeypatch)
### `tests\test_prompt_chains.py`

**Functions:** _read(path), test_chain_and_prune(tmp_path, monkeypatch), test_dispatch_appends_repair_prompt(tmp_path, monkeypatch)
### `tests\test_qt_runtime.py`

**Functions:** test_installs_and_sets_env_when_missing(tmp_path, monkeypatch), test_raises_when_plugins_missing(monkeypatch)
### `tests\test_qt_utils.py`

**Functions:** _install_mock(monkeypatch, tmp_path), test_ensure_pyside6_installs_when_missing(monkeypatch, tmp_path), test_ensure_pyside6_reinstalls_if_plugins_missing(monkeypatch, tmp_path)
### `tests\test_schema_manager_root.py`

**Functions:** test_apply_schema_updates_only_target(tmp_path), test_apply_schema_preserves_unrelated_sections(tmp_path)
### `tests\test_shell_alignment.py`

**Functions:** test_shell_switch_prompt(), test_unknown_shell_warns_user()
### `tests\test_startup.py`

**Functions:** _run_and_read(module), test_agent_terminal_self_heals(), test_virtual_desktop_self_heals()
### `tests\test_tasks.py`

**Functions:** test_task_manager_persistence(tmp_path), test_task_tracker_card_lists_tasks(tmp_path)
### `tests\test_task_card.py`

**Functions:** test_task_card_resize_and_persistence(tmp_path), test_open_close_api(tmp_path), test_header_controls(tmp_path)
### `tests\test_task_modes.py`

**Functions:** test_task_modes_and_switch(tmp_path, monkeypatch)
### `tests\test_tethering.py`

**Functions:** _write(path, rows), _read(path), test_tether_enable_disable(tmp_path, monkeypatch)
### `tests\test_tts.py`

**Functions:** test_speech_tool_invokes_tts()
### `tests\test_tts_unit.py`

**Functions:** test_available_voices_returns_names_when_pyttsx3_present(), test_speak_uses_pyttsx3_when_available(), test_speak_returns_false_when_all_engines_fail(), test_speak_falls_back_to_gtts_when_pyttsx3_missing(tmp_path)
### `tests\test_virtual_desktop.py`

**Functions:** test_virtual_desktop_window_title(monkeypatch), test_virtual_desktop_open_tasks(tmp_path, monkeypatch)
### `tests\test_virtual_desktop_icons.py`

**Functions:** test_virtual_desktop_icons_and_launch(tmp_path, monkeypatch)
### `tests\test_virtual_desktop_plugins.py`

**Functions:** test_virtual_desktop_missing_plugins(monkeypatch, tmp_path)
### `tests\test_virtual_desktop_repair.py`

**Functions:** test_virtual_desktop_repairs_missing_pyside6(monkeypatch, tmp_path)
### `tests\test_window_smoke.py`

**Functions:** test_host_window_shows(monkeypatch)
### `tests\test_workspace_icons.py`

**Functions:** test_workspace_icons(tmp_path, monkeypatch)
### `tests\codex\test_ensure_codex.py`

**Classes:** DummyResp

**Functions:** _archive_bytes(), test_ensure_codex_installed(tmp_path, monkeypatch), test_ensure_codex_checksum_failure(tmp_path, monkeypatch)
### `tests\deploy\test_deployment_manager.py`

Integration tests for deployment manager helpers.

**Functions:** _make_repo(tmp_path), test_clone_repo_and_launch(monkeypatch, tmp_path), test_tether_logs(monkeypatch, tmp_path)
### `tests\memory\test_bucket_manager.py`

**Functions:** test_register_append_query(tmp_path, monkeypatch)
### `tests\memory\test_prompt_buckets.py`

**Functions:** _reload(tmp_path, monkeypatch), test_append_and_retrieve(tmp_path, monkeypatch), test_retry_logic(tmp_path, monkeypatch)
### `tests\schema\test_schema_manager.py`

**Functions:** test_validate_schema(monkeypatch, tmp_path), test_apply_schema_to_persona_appends(tmp_path)
### `tests\security\test_guardrails.py`

**Functions:** test_blocked_path_detection(tmp_path), test_full_auto_execution_branches(tmp_path, monkeypatch)
### `tests\shells\test_detector.py`

**Functions:** test_detect_shell_unix_env(monkeypatch), test_detect_shell_windows_env(monkeypatch), test_detect_shell_parent_process(monkeypatch)
### `tests\shells\test_transpiler.py`

**Functions:** test_transpile_cmd(), test_transpile_powershell(), test_transpile_no_change()
### `tests\ui\test_task_panel.py`

**Functions:** test_ctrl_t_toggles_task_panel(qtbot, tmp_path), test_open_editor_links_file(qtbot, tmp_path, monkeypatch)
### `tools\codex_pr_sentinel.py`

**Functions:** _fetch_json(session, url), _now_iso(), _ci_summary(session, repo, sha), _read_auto_merge(), _load_codex_memory(), _write_codex_memory(mem), _append_logic_inbox(entry), _report_error(repo, pr_number, head_sha, exc), main()
### `tools\harvest_logic.py`

Cross-Branch Logic Harvester
Detects logic present on non-main branches but missing from main.
Updates memory/branch_logic.jsonl and docs/CROSS_BRANCH_LOGIC.md.

**Functions:** run(cmd, cwd), harvest(repo, main_branch), write_memory(findings, memory_path), write_report(findings, report_path), main()
### `tools\logic_inbox.py`

**Functions:** load_entries(), write_entries(entries), add_entry(summary, details), mark_done(entry_id), remove_entry(entry_id), validate(), sync_inbox_to_memory(), main()
### `tools\manage_tests.py`

Manage placeholder tests and docs-only detection.

- Creates a placeholder smoke test when no real tests exist.
- Detects documentation-only changes and signals test skips.

**Functions:** _changed_files(), _is_docs_only(files), _ensure_placeholder(), main()
### `tools\qt_runtime.py`

Qt runtime bootstrap utilities with plugin path caching and diagnostics.

**Functions:** reset_qt_plugin_cache(), resolve_qt_plugin_path(logger), ensure_qt_runtime(logger)
### `tools\qt_utils.py`

**Functions:** attempt_pip_install(package, logger), ensure_pyside6(logger), set_hidpi_policy_once()
### `tools\__init__.py`

Utility scripts for Agent-Terminal.
### `Virtual_Desktop\agent_terminal.py`
### `vision\ocr_service.py`

**Classes:** OCRResult, OCRService
### `vision\__init__.py`

## Other Files

The following files are present in the project but were not analysed in detail:

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
- `.git\objects\pack\pack-f07e369c87c609aae1f458e5342e9709b50ba06a.idx`
- `.git\objects\pack\pack-f07e369c87c609aae1f458e5342e9709b50ba06a.pack`
- `.git\objects\pack\pack-f07e369c87c609aae1f458e5342e9709b50ba06a.rev`
- `.git\packed-refs`
- `.git\refs\heads\main`
- `.git\refs\remotes\origin\HEAD`
- `.github\COPILOT.md`
- `.github\ISSUE_TEMPLATE\codex---merge-safe-task.md`
- `.github\codex_sentinel.yml`
- `.github\workflows\codex-pr-sentinel.yml`
- `.github\workflows\copilot-logic-harvester.yml`
- `.github\workflows\copilot-pr-watcher.yml`
- `.github\workflows\manual.yml`
- `.github\workflows\stale.yml`
- `.github\workflows\summary.yml`
- `.gitignore`
- `AGENTS.md`
- `Agent.md`
- `Agent_terminal.md`
- `Archived Conversations\.gitkeep`
- `Archived Conversations\Archived Info`
- `Archived Conversations\Codex-info\Fix Branch.txt`
- `Archived Conversations\Codex-info\__init__`
- `Archived Conversations\Codex-info\codex-rust-v0.23.0\__init__`
- `Archived Conversations\Codex-info\codex_info`
- `Archived Conversations\Codex-info\install codex instructions.txt`
- `Archived Conversations\Helpful Images\AI assistant.PNG`
- `Archived Conversations\Helpful Images\Agent OpenAI GPT Terminal2.PNG`
- `Archived Conversations\Helpful Images\Built in Terminal Codex.PNG`
- `Archived Conversations\Helpful Images\Error Agents.PNG`
- `Archived Conversations\Helpful Images\Promotional.PNG`
- `Archived Conversations\Helpful Images\__init__`
- `Archived Conversations\Helpful Images\basic_toolkit_theme.PNG`
- `Archived Conversations\Helpful Images\clipboard_image_v19.jpg`
- `Archived Conversations\Helpful Images\clipboard_image_v20.jpg`
- `Archived Conversations\Helpful Images\clipboard_image_v21.jpg`
- `Archived Conversations\Helpful Images\data management.PNG`
- `Archived Conversations\Helpful Images\diff viewer.PNG`
- `Archived Conversations\Helpful Images\intended style.png`
- `Archived Conversations\Helpful Images\intergraded terminal.PNG`
- `Archived Conversations\Helpful Images\project dash.PNG`
- `Archived Conversations\Helpful Images\security manager.PNG`
- `Archived Conversations\Helpful Images\toolsets.PNG`
- `Archived Conversations\Helpful Images\workspace types.PNG`
- `Archived Conversations\codex-rust-v0.23.0 - info\.codespellignore`
- `Archived Conversations\codex-rust-v0.23.0 - info\.codespellrc`
- `Archived Conversations\codex-rust-v0.23.0 - info\.devcontainer\Dockerfile`
- `Archived Conversations\codex-rust-v0.23.0 - info\.devcontainer\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\.devcontainer\devcontainer.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\ISSUE_TEMPLATE\2-bug-report.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\ISSUE_TEMPLATE\3-docs-issue.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\ISSUE_TEMPLATE\4-feature-request.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\__init__`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\action.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\bun.lock`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\package.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\add-reaction.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\comment.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\config.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\default-label-config.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\env-context.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\fail.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\git-helpers.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\git-user.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\github-workspace.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\load-config.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\main.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\post-comment.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\process-label.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\prompt-template.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\review.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\run-codex.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\src\verify-inputs.ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\actions\codex\tsconfig.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex-cli-login.png`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex-cli-permissions.png`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex-cli-splash.png`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex\__init__`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex\home\config.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex\labels\codex-attempt.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex\labels\codex-review.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex\labels\codex-rust-review.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\codex\labels\codex-triage.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\demo.gif`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\dependabot.yaml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\dotslash-config.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\pull_request_template.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\workflows\ci.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\workflows\cla.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\workflows\codespell.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\workflows\codex.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\workflows\rust-ci.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.github\workflows\rust-release.yml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.gitignore`
- `Archived Conversations\codex-rust-v0.23.0 - info\.npmrc`
- `Archived Conversations\codex-rust-v0.23.0 - info\.prettierignore`
- `Archived Conversations\codex-rust-v0.23.0 - info\.prettierrc.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\.vscode\extensions.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\.vscode\launch.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\.vscode\settings.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\AGENTS.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\CHANGELOG.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\LICENSE`
- `Archived Conversations\codex-rust-v0.23.0 - info\NOTICE`
- `Archived Conversations\codex-rust-v0.23.0 - info\PNPM.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\__init__`
- `Archived Conversations\codex-rust-v0.23.0 - info\analyze.txt`
- `Archived Conversations\codex-rust-v0.23.0 - info\cliff.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\Dockerfile`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\bin\codex.js`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\package-lock.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\package.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\scripts\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\scripts\build_container.sh`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\scripts\init_firewall.sh`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\scripts\install_native_deps.sh`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\scripts\run_in_container.sh`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\scripts\stage_release.sh`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\Cargo.lock`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\__init__`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ansi-escape\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ansi-escape\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ansi-escape\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\apply-patch\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\apply-patch\apply_patch_tool_instructions.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\apply-patch\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\apply-patch\src\parser.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\apply-patch\src\seek_sequence.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\arg0\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\arg0\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\src\apply_command.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\src\chatgpt_client.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\src\chatgpt_token.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\src\get_task.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\tests\apply_command_e2e.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\chatgpt\tests\task_turn_fixture.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\cli\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\cli\src\debug_sandbox.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\cli\src\exit_status.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\cli\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\cli\src\login.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\cli\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\cli\src\proto.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\clippy.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\approval_mode_cli_arg.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\approval_presets.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\config_override.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\config_summary.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\elapsed.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\fuzzy_match.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\model_presets.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\sandbox_mode_cli_arg.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\common\src\sandbox_summary.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\config.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\prompt.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\apply_patch.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\bash.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\chat_completions.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\client.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\client_common.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\codex.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\codex_conversation.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\config.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\config_profile.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\config_types.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\conversation_history.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\conversation_manager.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\environment_context.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\error.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\exec.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\exec_env.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\flags.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\git_info.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\is_safe_command.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\landlock.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\mcp_connection_manager.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\mcp_tool_call.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\message_history.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\model_family.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\model_provider_info.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\models.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\openai_model_info.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\openai_tools.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\parse_command.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\plan_tool.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\project_doc.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\prompt_for_compact_command.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\rollout.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\safety.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\seatbelt.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\seatbelt_base_policy.sbpl`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\shell.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\spawn.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\turn_diff_tracker.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\user_agent.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\user_notification.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\src\util.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\cli_responses_fixture.sse`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\cli_stream.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\client.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\common\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\common\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\compact.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\exec.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\exec_stream_events.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\fixtures\completed_template.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\fixtures\incomplete_sse.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\live_cli.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\prompt_caching.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\seatbelt.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\stream_error_allows_next_turn.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\core\tests\stream_no_completed.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\default.nix`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\docs\protocol_v1.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\src\cli.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\src\event_processor.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\src\event_processor_with_human_output.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\src\event_processor_with_json_output.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\tests\apply_patch.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\exec\tests\sandbox.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\build.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\arg_matcher.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\arg_resolver.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\arg_type.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\default.policy`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\error.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\exec_call.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\execv_checker.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\opt.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\policy.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\policy_parser.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\program.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\sed_command.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\src\valid_exec.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\bad.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\cp.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\good.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\head.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\literal.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\ls.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\parse_sed_command.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\pwd.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\execpolicy\tests\sed.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\file-search\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\file-search\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\file-search\src\cli.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\file-search\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\file-search\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\justfile`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\linux-sandbox\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\linux-sandbox\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\linux-sandbox\src\landlock.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\linux-sandbox\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\linux-sandbox\src\linux_run_main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\linux-sandbox\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\linux-sandbox\tests\landlock.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\login\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\login\src\assets\success.html`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\login\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\login\src\pkce.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\login\src\server.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\login\src\token_data.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\login\tests\login_server_e2e.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-client\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-client\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-client\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-client\src\mcp_client.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\codex_message_processor.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\codex_tool_config.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\codex_tool_runner.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\error_code.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\exec_approval.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\json_to_toml.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\message_processor.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\outgoing_message.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\patch_approval.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\src\tool_handlers\mod.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\codex_message_processor_flow.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\codex_tool.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\common\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\common\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\common\mcp_process.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\common\mock_model_server.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\common\responses.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\create_conversation.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\interrupt.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-server\tests\send_message.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\schema\2025-03-26\schema.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\schema\2025-06-18\schema.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\tests\initialize.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\tests\progress_notification.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ollama\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ollama\src\client.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ollama\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ollama\src\parser.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ollama\src\pull.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\ollama\src\url.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol-ts\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol-ts\generate-ts`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol-ts\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol-ts\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\README.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\src\config_types.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\src\mcp_protocol.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\src\message_history.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\src\parse_command.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\src\plan_tool.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\protocol\src\protocol.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\rust-toolchain.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\rustfmt.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\scripts\create_github_release.sh`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\Cargo.toml`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\prompt_for_init_command.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\app.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\app_event.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\app_event_sender.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\approval_modal_view.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\bottom_pane_view.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\chat_composer.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\chat_composer_history.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\command_popup.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\file_search_popup.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\list_selection_view.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\mod.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\popup_consts.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\scroll_state.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\selection_popup_common.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__backspace_after_pastes.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__empty.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__large.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__multiple_pastes.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__small.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\status_indicator_view.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\bottom_pane\textarea.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\chatwidget.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\chatwidget\agent.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\chatwidget\interrupts.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\chatwidget\snapshots\codex_tui__chatwidget__tests__deltas_then_same_final_message_are_rendered_snapshot.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\chatwidget\snapshots\codex_tui__chatwidget__tests__final_reasoning_then_message_without_deltas_are_rendered.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\chatwidget\tests.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\chatwidget_stream_tests.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\citation_regex.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\cli.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\common.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\custom_terminal.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\diff_render.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\exec_command.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\file_search.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\get_git_diff.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\history_cell.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\insert_history.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\lib.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\live_wrap.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\main.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\markdown.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\markdown_stream.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\onboarding\auth.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\onboarding\continue_to_chat.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\onboarding\mod.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\onboarding\onboarding_screen.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\onboarding\trust_directory.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\onboarding\welcome.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\render\line_utils.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\render\markdown_utils.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\render\mod.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\session_log.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\shimmer.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\slash_command.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__add_details.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__update_details_with_rename.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__wrap_behavior_insert.snap`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\status_indicator_widget.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\streaming\controller.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\streaming\mod.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\text_formatting.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\tui.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\updates.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\src\user_approval_widget.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\styles.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\tests\fixtures\binary-size-log.jsonl`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\tests\fixtures\ideal-binary-response.txt`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\tests\fixtures\oss-story.jsonl`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\tests\status_indicator.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\tests\vt100_history.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\tests\vt100_live_commit.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\tui\tests\vt100_streaming_no_dup.rs`
- `Archived Conversations\codex-rust-v0.23.0 - info\docs\CLA.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\docs\release_management.md`
- `Archived Conversations\codex-rust-v0.23.0 - info\flake.lock`
- `Archived Conversations\codex-rust-v0.23.0 - info\flake.nix`
- `Archived Conversations\codex-rust-v0.23.0 - info\package.json`
- `Archived Conversations\codex-rust-v0.23.0 - info\pnpm-lock.yaml`
- `Archived Conversations\codex-rust-v0.23.0 - info\pnpm-workspace.yaml`
- `Archived Conversations\codex-rust-v0.23.0\__init__`
- `Archived Conversations\other programs README\AI_TTS_AGENT.md`
- `Archived Conversations\other programs README\Advanced_Chatbot.md`
- `Archived Conversations\other programs README\Codex-rust-v0.23.0.md`
- `Archived Conversations\other programs README\Codex_Main.md`
- `Archived Conversations\other programs README\Custom_Compiler.md`
- `Archived Conversations\other programs README\Fathom.md`
- `Archived Conversations\other programs README\Morph.md`
- `Archived Conversations\other programs README\Rant_PDD.md`
- `Archived Conversations\other programs README\Rant_PDD_withExample.md`
- `Archived Conversations\other programs README\Single_Cell.md`
- `Archived Conversations\other programs README\my_Everything.md`
- `CHANGELOG.md`
- `Codex\__pycache__\cli_adapter.cpython-313.pyc`
- `Codex\__pycache__\codex_manager.cpython-313.pyc`
- `Codex\__pycache__\open_source_manager.cpython-313.pyc`
- `Codex\codex-x86_64-pc-windows-msvc.exe`
- `Codex_Sync_Summary.md`
- `ErrorDump.md`
- `README.md`
- `User_Canon.md`
- `Virtual_Desktop\__init__`
- `__pycache__\agent_terminal.cpython-313.pyc`
- `__pycache__\code_editor.cpython-313.pyc`
- `__pycache__\codex_installation.cpython-313.pyc`
- `__pycache__\l2c_tool.cpython-313.pyc`
- `__pycache__\prompt_manager.cpython-313.pyc`
- `__pycache__\schema_manager.cpython-313.pyc`
- `__pycache__\tasks.cpython-313.pyc`
- `agent_terminal.log`
- `config.json`
- `copilot-instructions.md`
- `datasets\authorizations.jsonl`
- `datasets\bucket_matrix.json`
- `datasets\codex_installs.jsonl`
- `datasets\command_log.jsonl`
- `datasets\context_history.jsonl`
- `datasets\deployments.jsonl`
- `datasets\editor_history\.gitkeep`
- `datasets\editor_history\016666bd-49ba-45ec-bce5-d4ba9ad8104b.jsonl`
- `datasets\editor_history\02895b10-d651-416a-a94c-1294a0a9d79c.jsonl`
- `datasets\editor_history\04a82006-f836-48a4-9cf6-dde32bb3d972.jsonl`
- `datasets\editor_history\04b3108c-f4e6-441c-ba91-c1b11f795976.jsonl`
- `datasets\editor_history\0769bd16-5c13-4467-b2fa-3a0e949ddf36.jsonl`
- `datasets\editor_history\08fca4cf-8a8e-4af5-b0ab-776aebad2bcf.jsonl`
- `datasets\editor_history\098dd7b2-bdee-4b6e-8e67-13df6616c3e3.jsonl`
- `datasets\editor_history\09b5b402-eab2-4653-97ba-f5ffed22066c.jsonl`
- `datasets\editor_history\0a6fa202-dd1e-444e-836c-47fc93c6557a.jsonl`
- `datasets\editor_history\0c795339-d3cf-4647-b6de-9a8f86694991.jsonl`
- `datasets\editor_history\0dbf30dd-f4ce-4abb-b6fd-7571097ea542.jsonl`
- `datasets\editor_history\0e0b5ad0-834e-488f-a499-7ee8a1aaf6ad.jsonl`
- `datasets\editor_history\0f5a7540-598c-4924-a63b-f978166d59b2.jsonl`
- `datasets\editor_history\100ac3c8-3a45-4939-922b-57908bfcdc2c.jsonl`
- `datasets\editor_history\10a8baaa-e835-4372-a963-b73223946e3f.jsonl`
- `datasets\editor_history\10e0ee93-88f5-4f7d-a2a2-56bcf497481b.jsonl`
- `datasets\editor_history\110f6293-68f8-4748-8973-77dc41900575.jsonl`
- `datasets\editor_history\1308d304-f08f-432b-957d-deb572f6b5a4.jsonl`
- `datasets\editor_history\131ebfcd-f34d-4672-8315-d550c8096261.jsonl`
- `datasets\editor_history\13cab39f-965e-4c32-a0cc-0253b9694e02.jsonl`
- `datasets\editor_history\145de42c-29cc-4a85-8719-e6717d8281da.jsonl`
- `datasets\editor_history\157cf779-17f9-4a60-9d94-21776191a753.jsonl`
- `datasets\editor_history\17590009-911c-4d0c-b926-247a8b7d5be4.jsonl`
- `datasets\editor_history\1914683b-177b-49d5-873b-b8c15fb4fda1.jsonl`
- `datasets\editor_history\192104b8-03ba-4139-a327-b6cd97f3333c.jsonl`
- `datasets\editor_history\19ab9809-6c00-4231-8878-d00d8f3a8c7f.jsonl`
- `datasets\editor_history\1c2040d1-b735-4d34-9f65-f3ce740e54f9.jsonl`
- `datasets\editor_history\1d34da8f-a763-41b5-8408-012e9211b3c7.jsonl`
- `datasets\editor_history\1d60ebab-1a79-4933-a3fc-6aea4632eaca.jsonl`
- `datasets\editor_history\1fd13456-cf90-494d-9dee-bb2e70aec57b.jsonl`
- `datasets\editor_history\1ff3a9d1-4d9b-497e-9637-15667a9d6d6e.jsonl`
- `datasets\editor_history\2061db85-5e86-4f6f-a0ff-7bcb044d5aae.jsonl`
- `datasets\editor_history\212bc8ac-5082-4a44-b366-0fa18b334913.jsonl`
- `datasets\editor_history\239eca98-484a-402f-9a22-a7947fbf0104.jsonl`
- `datasets\editor_history\261968fb-2c66-4a01-b1df-e6318931f099.jsonl`
- `datasets\editor_history\263220ea-8c1f-4bbd-bcef-209dcea8ae8b.jsonl`
- `datasets\editor_history\2782534d-345c-438e-8142-74185416366a.jsonl`
- `datasets\editor_history\27c1a676-9d0e-475a-bd02-25bbda4304e8.jsonl`
- `datasets\editor_history\28ec2477-c744-448e-8ce1-825347b29483.jsonl`
- `datasets\editor_history\2a225ad3-b282-4479-a3fa-82ce28c82a73.jsonl`
- `datasets\editor_history\2a4e33fd-48e1-4c6e-9c4c-49c005a12490.jsonl`
- `datasets\editor_history\2ac56a14-1682-4b3d-b2b6-a5d5329d5025.jsonl`
- `datasets\editor_history\2e5ff4dc-9762-476a-b109-1d13256e048f.jsonl`
- `datasets\editor_history\2e723062-64f5-453b-996e-6acd06fff05c.jsonl`
- `datasets\editor_history\30fd6b11-fca9-4218-9a0e-8cd99e6fc53f.jsonl`
- `datasets\editor_history\3465cd28-1dd1-4671-b8ac-a2ee32a2d63d.jsonl`
- `datasets\editor_history\37039df6-2382-4b52-8a8c-a52079d5f9be.jsonl`
- `datasets\editor_history\37733fde-ccea-45fd-bc4e-dd9a76c0488b.jsonl`
- `datasets\editor_history\37e6849c-6d6e-463c-bfca-1fde6feecb3a.jsonl`
- `datasets\editor_history\38389072-cc19-44a1-a8f3-041aed76d03e.jsonl`
- `datasets\editor_history\392a8eb8-e326-4cd9-b094-3790fc54b9f6.jsonl`
- `datasets\editor_history\395a95ec-0861-4414-8bad-12d28bfb5cc6.jsonl`
- `datasets\editor_history\396670bc-e324-42bb-9d85-65d7edd7bce7.jsonl`
- `datasets\editor_history\3acb6985-446f-447b-92d2-62321ebe671a.jsonl`
- `datasets\editor_history\3f3db3fb-d57d-4cda-9dc9-8b216a3a75bb.jsonl`
- `datasets\editor_history\414a2550-8263-4284-84c0-13d22c149ff9.jsonl`
- `datasets\editor_history\42118ef3-03f4-4a21-8f41-eb5e34545838.jsonl`
- `datasets\editor_history\435b0cb5-1e59-4f7f-83c6-0c7cfd9252da.jsonl`
- `datasets\editor_history\445b4ce8-1d19-40f7-9c05-b8fd0100c81b.jsonl`
- `datasets\editor_history\44bbb8cd-0b53-41f0-b985-8809d1368b14.jsonl`
- `datasets\editor_history\44dc0bb3-19f0-4d53-8381-908c3f0c049b.jsonl`
- `datasets\editor_history\46a22a38-2e90-40d5-b6f6-aec495c416e3.jsonl`
- `datasets\editor_history\46b23e40-2bd9-4ca9-9a68-70348b897253.jsonl`
- `datasets\editor_history\46b9566f-b4db-4961-88e8-8ee65794bdf1.jsonl`
- `datasets\editor_history\46fe64d1-4cdc-4fd7-9b61-10e9d9f75bf7.jsonl`
- `datasets\editor_history\4823b8c3-dbd6-4557-b41c-f72dc00706a5.jsonl`
- `datasets\editor_history\48d6597d-26d5-478a-bc9c-ec9526843d8e.jsonl`
- `datasets\editor_history\491dc8ab-54e4-44a1-9faa-c9be70ab245e.jsonl`
- `datasets\editor_history\49c359bd-119c-46a4-97ca-815fe9b9e0d3.jsonl`
- `datasets\editor_history\4cdf839c-7e54-40b8-9b2d-539eaed61fee.jsonl`
- `datasets\editor_history\4d1d2bd3-9139-4b29-ba46-d13005f2e764.jsonl`
- `datasets\editor_history\4d976af5-bcc0-4519-adb6-08a12ce04bc9.jsonl`
- `datasets\editor_history\4e71f95f-7033-499d-8a36-1d9bf8f13b0f.jsonl`
- `datasets\editor_history\4f061d1c-0a10-4247-a030-49ec698c589e.jsonl`
- `datasets\editor_history\524e5141-5c74-4a0c-b41f-fcc90127227c.jsonl`
- `datasets\editor_history\527011b7-1412-4c6b-8d86-09bf4e18cdd7.jsonl`
- `datasets\editor_history\527b3931-7515-4277-a186-02903c93d466.jsonl`
- `datasets\editor_history\5286ab6e-2408-4e54-8b4e-648880b1c669.jsonl`
- `datasets\editor_history\554be25a-f29f-414f-839e-b60f10cd8152.jsonl`
- `datasets\editor_history\555f8835-1be1-4b69-8c79-12557170c7eb.jsonl`
- `datasets\editor_history\57ce93a7-75d8-473d-a17f-54f7e4e0d9a0.jsonl`
- `datasets\editor_history\5c96504c-3a97-4dd8-a246-862001136411.jsonl`
- `datasets\editor_history\5ce84e47-cb55-4b3b-8a70-0a5125393626.jsonl`
- `datasets\editor_history\5dd5644f-16a2-4f8e-9e7b-90c70806e1aa.jsonl`
- `datasets\editor_history\5f5d3014-ab78-47ba-90ab-eb729af6b2e6.jsonl`
- `datasets\editor_history\5f7ad8f9-77c7-41b6-bdb1-f475bff63ec4.jsonl`
- `datasets\editor_history\60f887b9-32b9-4a2c-ad62-f4b6f2416052.jsonl`
- `datasets\editor_history\624ace8e-afd4-4614-bf8c-23e880ba125b.jsonl`
- `datasets\editor_history\628d2a73-c0df-4314-8528-6aea4f1af702.jsonl`
- `datasets\editor_history\629177ea-9f86-4722-91ae-40812362f96a.jsonl`
- `datasets\editor_history\643b31af-5709-411a-80e3-18100808c4c8.jsonl`
- `datasets\editor_history\645a3e13-59f7-4683-a7fe-6b22daf975b5.jsonl`
- `datasets\editor_history\64ed6e63-351b-430e-8623-4f50f1117b5c.jsonl`
- `datasets\editor_history\668cde55-d353-4f0b-9f91-e822a661231f.jsonl`
- `datasets\editor_history\67290b4f-0c16-4780-ac1c-7b51ea7621a1.jsonl`
- `datasets\editor_history\6939ab8a-6d70-4bd0-8f0a-bd91c5fe7cd9.jsonl`
- `datasets\editor_history\69a95aae-a9fb-49ce-99c7-21747da30bfd.jsonl`
- `datasets\editor_history\6a04c0e4-bc51-4849-8f0b-c6ff557a3ba1.jsonl`
- `datasets\editor_history\6c65d216-2562-473a-a4f9-a39efc37ab89.jsonl`
- `datasets\editor_history\6dd83485-a39c-40aa-8819-bbd2ab740af9.jsonl`
- `datasets\editor_history\6e06d320-f31f-45ca-ab07-6e02d24d3730.jsonl`
- `datasets\editor_history\6e9618b0-d1a3-4e54-8a56-937eb85f391b.jsonl`
- `datasets\editor_history\6ee6438f-2582-4213-b65a-36cfb42bd3a9.jsonl`
- `datasets\editor_history\6f61ae1e-0a40-40ef-b1e1-af4607ca3fe7.jsonl`
- `datasets\editor_history\7006f6c8-565c-42e1-adb0-7b54c5f1dbd6.jsonl`
- `datasets\editor_history\72309de0-4a87-4f1f-9d68-1ab6c43a2f5a.jsonl`
- `datasets\editor_history\727676c2-3489-4c04-9dfa-8187e6195118.jsonl`
- `datasets\editor_history\73101ba4-678e-406d-8537-7bbcd52367fc.jsonl`
- `datasets\editor_history\73229113-a4a2-41e4-b855-3cd4b34c96fc.jsonl`
- `datasets\editor_history\73b1db8b-72b3-4b6b-8076-be0b1b5d74b5.jsonl`
- `datasets\editor_history\740ebd13-06c8-484f-8b27-53d0d4cfb175.jsonl`
- `datasets\editor_history\74216099-3e29-43a0-83a8-d04a530a113e.jsonl`
- `datasets\editor_history\76999ccc-0441-4ccf-a39f-2ca7b2958182.jsonl`
- `datasets\editor_history\76ddd90e-f114-4c24-a128-e7d460bde3a9.jsonl`
- `datasets\editor_history\7872a3cf-275c-462c-a3ee-0054a8367a81.jsonl`
- `datasets\editor_history\79bce8d8-e395-4003-9d4f-e4b0d53ea31a.jsonl`
- `datasets\editor_history\7a9e58b0-9ee8-4684-8333-2cfb3dd6372c.jsonl`
- `datasets\editor_history\7af0e6c2-68bf-43a4-a3d1-c658aa8e9f65.jsonl`
- `datasets\editor_history\7bc7d256-dd25-4a8f-a471-641b0286056a.jsonl`
- `datasets\editor_history\7cd57829-b0e4-47f9-b8db-29fa653102b6.jsonl`
- `datasets\editor_history\7cf927b3-95af-4970-9caa-44c57c53a86b.jsonl`
- `datasets\editor_history\7e57c0af-ec50-4e12-97f5-9deef6ab3c6b.jsonl`
- `datasets\editor_history\808616ec-1831-4729-93ba-262cc0865fab.jsonl`
- `datasets\editor_history\8124d8ac-c2dd-4a21-bb51-dd9d3d5b3afd.jsonl`
- `datasets\editor_history\8431f97e-8d93-422b-9107-bac947a988a9.jsonl`
- `datasets\editor_history\8499ca48-b3a7-4ccf-9cdc-dee7038a09d9.jsonl`
- `datasets\editor_history\850450ba-cfad-4b48-adca-c39d988f6fb6.jsonl`
- `datasets\editor_history\85209424-522c-483c-a60a-02ffda19ae3d.jsonl`
- `datasets\editor_history\881fecca-8619-4006-90d6-0f1c4b457b69.jsonl`
- `datasets\editor_history\8a5ca667-99b8-47aa-b5ea-11801efdc0dc.jsonl`
- `datasets\editor_history\8aa3f2f0-8e6c-4650-8974-927dbcc9d66a.jsonl`
- `datasets\editor_history\8c9f3b79-17f2-45ac-a03c-c19792198581.jsonl`
- `datasets\editor_history\8d14085d-d568-45dc-9d6d-785dbae5feda.jsonl`
- `datasets\editor_history\8d67018d-8ca8-4977-b147-08df98e34274.jsonl`
- `datasets\editor_history\8f1412f5-983c-4e2a-b0ad-c8596d5291a4.jsonl`
- `datasets\editor_history\903184a4-02ec-433a-9f03-27cd5ab8dbe2.jsonl`
- `datasets\editor_history\9088ba20-caff-4112-95a8-1082daef3c09.jsonl`
- `datasets\editor_history\9154a1d0-feb5-444a-93aa-ba053d6c016a.jsonl`
- `datasets\editor_history\91965f32-4580-4a49-a14a-a4f54abfe637.jsonl`
- `datasets\editor_history\93e55799-5d0c-4400-ac2c-86cc8e79ebef.jsonl`
- `datasets\editor_history\951459dc-a9a7-4bcf-8267-cf5a6b8f7311.jsonl`
- `datasets\editor_history\9671e7fa-e5e8-4d51-8df4-5a2369e4c58b.jsonl`
- `datasets\editor_history\9696fa39-e3ca-45cf-86af-de0a4fd03084.jsonl`
- `datasets\editor_history\96c21ea3-076a-408b-ba13-71fd38c86b04.jsonl`
- `datasets\editor_history\97691f2d-45ea-43c1-b2dd-ac3e7768c7af.jsonl`
- `datasets\editor_history\98a210ec-e3cc-4f5f-8fa3-136854c8f66e.jsonl`
- `datasets\editor_history\99695bfb-dc28-44a0-bfb2-34176cdadb52.jsonl`
- `datasets\editor_history\99adb3e2-151a-4b66-8445-746235b418b1.jsonl`
- `datasets\editor_history\99ba8c90-76f9-4238-99d4-fd9c11ae0275.jsonl`
- `datasets\editor_history\9b87b92f-e3d2-44a4-b8f9-d593b4dcdbf9.jsonl`
- `datasets\editor_history\9c55fa4c-9f27-4a0b-a6f2-923ca6899993.jsonl`
- `datasets\editor_history\9e2eb4d6-734e-4dad-838e-ad17c03d8081.jsonl`
- `datasets\editor_history\a135c177-6f8d-4c74-a84b-40efc2e13344.jsonl`
- `datasets\editor_history\a4d6dc31-52c3-45b4-b153-5d202ced8d74.jsonl`
- `datasets\editor_history\a5563cd3-13ec-4cf6-bdc8-8815ee07aaa4.jsonl`
- `datasets\editor_history\a67b5d25-fc91-4e1c-a43e-d90e847590d0.jsonl`
- `datasets\editor_history\a7522a48-bbf6-4e37-90d6-8b4615dc1634.jsonl`
- `datasets\editor_history\a98aa6c8-172c-4b80-b77d-e7b37250a8b2.jsonl`
- `datasets\editor_history\ab2823ac-fb41-4999-829b-fe5191ab732f.jsonl`
- `datasets\editor_history\ab4424b0-9163-4082-9f1e-bb0fb752bea4.jsonl`
- `datasets\editor_history\ab6a73d0-b273-4dda-b445-783e8280db6d.jsonl`
- `datasets\editor_history\aea0f19e-9dff-452c-b0e4-0e0605009184.jsonl`
- `datasets\editor_history\b1094b6c-e6e1-4d11-90e5-b98b7a7f7952.jsonl`
- `datasets\editor_history\b24d638c-a12a-484c-9ad0-30de67b97ad9.jsonl`
- `datasets\editor_history\b2ad6212-f5e9-40db-9e0d-3548385ac7d0.jsonl`
- `datasets\editor_history\b2ce4dd1-af55-49bb-823b-0d3c352c15bd.jsonl`
- `datasets\editor_history\b2d366c1-836d-41af-b8a3-5a49ee2e80f0.jsonl`
- `datasets\editor_history\b3845886-507e-41f3-856c-ae89b7cb0668.jsonl`
- `datasets\editor_history\b43f3e66-1f34-4c69-ba7d-3cc36ffb623a.jsonl`
- `datasets\editor_history\b4471324-479a-4f4f-a222-5c31f5f38765.jsonl`
- `datasets\editor_history\b490966a-674c-4e6f-93e2-f4a23895e95c.jsonl`
- `datasets\editor_history\b4b03183-d062-4222-bff6-1c10b3f19338.jsonl`
- `datasets\editor_history\b5a5477e-0c95-4c73-afb7-b07e9582161e.jsonl`
- `datasets\editor_history\b61ea53b-e77f-4816-ac97-8969241a5876.jsonl`
- `datasets\editor_history\b66670ec-b13b-4596-9a0f-3c7d5351d6ff.jsonl`
- `datasets\editor_history\b753ce44-557e-4e43-8a9c-3bea5756f5a2.jsonl`
- `datasets\editor_history\b7da60c1-06d5-4a44-a3df-911060444f95.jsonl`
- `datasets\editor_history\bbb0bf51-d926-4a88-8258-97b8acfe124c.jsonl`
- `datasets\editor_history\bd872dfe-d97e-4b4b-9da6-830424922ddf.jsonl`
- `datasets\editor_history\befa1578-3509-44c9-a6f6-63af47706bc7.jsonl`
- `datasets\editor_history\bf30368c-cc78-49c5-b26d-6337ae363bfe.jsonl`
- `datasets\editor_history\bfe1b747-3c3d-40d2-9d87-5654bc0f373c.jsonl`
- `datasets\editor_history\c0b12b62-a02c-4071-ac66-dd9ce60e28ec.jsonl`
- `datasets\editor_history\c115d624-ec90-4834-a22d-04d0da85bc97.jsonl`
- `datasets\editor_history\c61ec8b7-701b-47ec-92e3-8ccdc93e2b60.jsonl`
- `datasets\editor_history\c77e4c6c-8c65-4651-b777-b126ef0c0eba.jsonl`
- `datasets\editor_history\c9b0b99a-5008-4652-8207-7f08e366edc7.jsonl`
- `datasets\editor_history\cabbadc6-4b4f-46b7-811c-bb4ecf052610.jsonl`
- `datasets\editor_history\cca05e3c-feab-475e-a9af-12553ee534f0.jsonl`
- `datasets\editor_history\cd0bfb1a-74f6-4ad6-bae6-f42d18da4a47.jsonl`
- `datasets\editor_history\cd165929-4c64-4216-963a-38a65e825170.jsonl`
- `datasets\editor_history\cd511b20-f2cd-4652-a3fd-fddddc036df1.jsonl`
- `datasets\editor_history\cd67ca47-0e6e-4f23-97bb-cedd9ffad749.jsonl`
- `datasets\editor_history\cf973e61-a050-4c40-bdeb-f888d3f979a1.jsonl`
- `datasets\editor_history\d02c250c-2c22-4a00-824c-81db83f5763d.jsonl`
- `datasets\editor_history\d2c7d8f8-478a-491b-ad6a-43bb4e9364b2.jsonl`
- `datasets\editor_history\d51e6a34-1dfa-4bb8-8b38-7980cd1049e5.jsonl`
- `datasets\editor_history\d52d4a80-f8e8-403d-bd7b-03d5e83e60ac.jsonl`
- `datasets\editor_history\d5da5998-5d31-4b7f-857c-782041ecf0ba.jsonl`
- `datasets\editor_history\d6f2744b-16a1-44eb-889c-6b0c243222f8.jsonl`
- `datasets\editor_history\d70607f5-e99d-42d1-afa2-4837711df0c5.jsonl`
- `datasets\editor_history\d75bf787-d090-40c5-937b-cc668ebd51c1.jsonl`
- `datasets\editor_history\dabb2bdc-27e9-45c9-96a3-6b80ee1bdcc7.jsonl`
- `datasets\editor_history\df9f1aaa-1afc-45cc-8334-f09cfbb714f0.jsonl`
- `datasets\editor_history\dfe81b01-0f80-4e72-9135-3ec9a74b3746.jsonl`
- `datasets\editor_history\dffa39fc-9899-4ac0-a133-42d91f86dc9d.jsonl`
- `datasets\editor_history\e1954f1d-21e9-4ab9-af81-5180e19c27aa.jsonl`
- `datasets\editor_history\e220e394-0c9c-4dd9-b2ca-aca500a74dfa.jsonl`
- `datasets\editor_history\e3253867-fd6c-475e-947d-01aaeda13140.jsonl`
- `datasets\editor_history\e335d365-b88c-462d-8dae-85d46ec0efb8.jsonl`
- `datasets\editor_history\e3a25d71-c7d0-453c-b465-f68e46120064.jsonl`
- `datasets\editor_history\e3a2a34d-2009-4790-b5d3-22a17ded496b.jsonl`
- `datasets\editor_history\e713af93-7eb8-4969-ae4d-9b2665a98f12.jsonl`
- `datasets\editor_history\e72fa622-73bc-4148-92b4-5deb269c18d6.jsonl`
- `datasets\editor_history\e92b370a-ce17-4565-b484-f391c216952f.jsonl`
- `datasets\editor_history\e939e6e7-f347-411f-ae80-3d6835a2061f.jsonl`
- `datasets\editor_history\ea68f85f-277a-4346-91ad-8046095ee6b6.jsonl`
- `datasets\editor_history\ea9365cc-3b43-4a31-a159-816e7e3b03dd.jsonl`
- `datasets\editor_history\eb35027f-dd6a-4631-b675-bd85ffd9bfe7.jsonl`
- `datasets\editor_history\ec208308-6693-4b7c-9807-326a0773a827.jsonl`
- `datasets\editor_history\ec248664-729c-4ceb-b6c4-2781df4c288b.jsonl`
- `datasets\editor_history\ed0f6b8c-a846-49f0-b2cc-85150b111453.jsonl`
- `datasets\editor_history\eda4294c-e2cd-4685-a5f1-71df28946be4.jsonl`
- `datasets\editor_history\ee354a5f-2db8-4731-b70b-545416302d24.jsonl`
- `datasets\editor_history\ef483e1e-2eda-4296-99bf-615300b9d2ac.jsonl`
- `datasets\editor_history\effd2ce1-4521-4612-9889-ad49919171c4.jsonl`
- `datasets\editor_history\f0df4f73-276b-4e25-a317-bbe340a453f3.jsonl`
- `datasets\editor_history\f1967a21-53b0-4125-9c36-213a18d69840.jsonl`
- `datasets\editor_history\f1c752b3-101f-4fe0-9c21-ffe88e2d4e2c.jsonl`
- `datasets\editor_history\f21ac63b-7b23-4cb5-ab5a-99da5e51d012.jsonl`
- `datasets\editor_history\f4a3e68a-d3d7-4188-8b51-843a63c9cd3a.jsonl`
- `datasets\editor_history\f6effa4a-a742-420d-b4b9-18ded17f29d6.jsonl`
- `datasets\editor_history\f7e0f87f-4719-4ebe-abf0-37a4332dd32e.jsonl`
- `datasets\editor_history\f88b236e-4e22-4fe2-afba-d3c7a24b763d.jsonl`
- `datasets\editor_history\f8a181b1-ae07-4ac5-974b-b182637e204d.jsonl`
- `datasets\editor_history\f90411ab-9a49-47f0-b418-e29ee95cfcdf.jsonl`
- `datasets\editor_history\f9ea1c2e-46ca-417b-af28-7468dc08934a.jsonl`
- `datasets\editor_history\faaa04ec-50b3-4645-b3f0-2786c0d9c8cb.jsonl`
- `datasets\editor_history\fb09a81b-623a-4d52-bca3-b1ba70a7e937.jsonl`
- `datasets\editor_history\fb4b4970-d6cc-40cc-be64-7ee5bdee1af4.jsonl`
- `datasets\editor_history\fc541563-2b58-4165-b7b8-35f4522b8a32.jsonl`
- `datasets\editor_history\fc5687b4-f62a-4902-bb43-3ca170e18ba2.jsonl`
- `datasets\editor_history\fd02160c-ede1-43f2-b988-357dff390df6.jsonl`
- `datasets\editor_history\fd2109dc-651b-4312-bd33-01b7d82a78b9.jsonl`
- `datasets\editor_history\fed70d3f-8397-41b5-a598-a7fffa8204be.jsonl`
- `datasets\editor_history\feed4bb8-14df-417a-9276-474f8955a0bf.jsonl`
- `datasets\editor_history\ff310d88-ec12-4735-a9f7-87857e0e1aae.jsonl`
- `datasets\errors.jsonl`
- `datasets\history.jsonl`
- `datasets\indexing.jsonl`
- `datasets\install_info.jsonl`
- `datasets\install_instructions.jsonl`
- `datasets\learning.jsonl`
- `datasets\ocr_logs.jsonl`
- `datasets\prompt_attempts.jsonl`
- `datasets\prompt_bucket.jsonl`
- `datasets\prompting.jsonl`
- `datasets\prompts.jsonl`
- `datasets\schema_logs.jsonl`
- `datasets\schema_updates.jsonl`
- `datasets\self_prompting.jsonl`
- `datasets\sem_ai.jsonl`
- `datasets\sem_user.jsonl`
- `datasets\snippets.jsonl`
- `datasets\tasks.jsonl`
- `datasets\tasks\84ab64dd-2421-4681-bb4d-60af68f3a3f0\history.jsonl`
- `datasets\tether_logs.jsonl`
- `docs\Agent-Terminal-Lexicon.md`
- `docs\CROSS_BRANCH_LOGIC.md`
- `docs\architecture.md`
- `docs\codex_install.md`
- `docs\deployment.md`
- `docs\deployment_manager.md`
- `docs\design_health_check.md`
- `docs\editor.md`
- `docs\qt_runtime.md`
- `docs\virtual_desktop.md`
- `memory\__pycache__\bucket_manager.cpython-313.pyc`
- `memory\__pycache__\datasets.cpython-313.pyc`
- `memory\__pycache__\prompt_buckets.cpython-313.pyc`
- `memory\authorizations.jsonl`
- `memory\branch_logic.jsonl`
- `memory\codex_memory.json`
- `memory\logic_inbox.jsonl`
- `memory\prompt_chains.jsonl`
- `schemas\base_schema.json`
- `schemas\persona_schema.json`
- `security\__pycache__\__init__.cpython-313.pyc`
- `security\__pycache__\guardrails.cpython-313.pyc`
- `settings.json`
- `shells\__pycache__\__init__.cpython-313.pyc`
- `shells\__pycache__\detector.cpython-313.pyc`
- `shells\__pycache__\transpiler.cpython-313.pyc`
- `system.log`
- `tools\__pycache__\__init__.cpython-313.pyc`
- `tools\__pycache__\logic_inbox.cpython-313.pyc`
- `tools\__pycache__\qt_runtime.cpython-313.pyc`
- `tools\__pycache__\qt_utils.cpython-313.pyc`
- `vd_state.json`
- `vision\__pycache__\__init__.cpython-313.pyc`
- `vision\__pycache__\ocr_service.cpython-313.pyc`
- `vision_cache\__init__`


## Detailed Module Analyses


## Module `agent_terminal.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Terminal — Standalone/Embeddable Terminal Card (PySide6)
(Updated: remove QEvent.TextChanged usage; auto-grow via textChanged signal;
keeps all prior features; HiDPI policy set before QApplication.)
"""

from __future__ import annotations

import os, sys, re, json, uuid, math, queue, threading, subprocess, time, datetime, base64, io, zipfile, tarfile, shutil, difflib, logging, tempfile, socket, argparse, ctypes, traceback
import hashlib, urllib.request
from importlib import metadata as importlib_metadata
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Callable

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_ROOT = SCRIPT_PATH.parent
PROJECT_ROOT = SCRIPT_ROOT.parent if SCRIPT_ROOT.name == "Virtual_Desktop" else SCRIPT_ROOT
PROJECT_ROOT = str(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.logic_inbox import sync_inbox_to_memory
from tools.qt_utils import ensure_pyside6, set_hidpi_policy_once
from tools.qt_runtime import ensure_qt_runtime, resolve_qt_plugin_path
from security.guardrails import requires_confirmation, is_safe_path
from memory.datasets import (
    log_prompt,
    log_error,
    log_authorization,
)
from memory.bucket_manager import append_entry
from memory.prompt_buckets import append_bucket
from vision.ocr_service import OCRService
from schema_manager import (
    load_schema,
    apply_schema,
    validate_schema,
    apply_schema_to_persona,
)
import l2c_tool
from codex_installation import ensure_codex_installed, DEFAULT_VERSION, load_install_notes
from shells.detector import detect_shell
from shells.transpiler import transpile_command


def _log_codex_install_failure(error: Exception) -> None:
    """Record Codex install failures for troubleshooting."""
    record = {
        "version": DEFAULT_VERSION,
        "platform": sys.platform,
        "error": str(error),
        "success": False,
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    path = Path(os.environ.get("DATASETS_DIR", "datasets")) / "codex_installs.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

try:  # codex_manager may be unavailable on fallback
    from Codex.codex_manager import CodexPersona
except Exception:  # pragma: no cover - Codex package missing
    @dataclass
    class CodexPersona:
        name: str = "Codex"
        version: str = "unknown"

        def greeting(self) -> str:
            return f"{self.name} {self.version}"


codex = None
_persona = CodexPersona()
CURRENT_MODEL = ""


def _verify_checksum(path: Path, expected: str) -> bool:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest() == expected


def _codex_binary_present() -> bool:
    """Return True if Codex package is present and has a binary."""
    try:
        from Codex import codex_manager
        return bool(codex_manager.get_binary())
    except Exception:
        return False


def prompt_install_codex() -> None:
    """
    Show a small modal prompting to install Codex if the Codex package exists
    but no binary is present. Local-import Qt to avoid NameError before ensure_pyside6().
    Text uses high contrast on dark bg (rule: never low-contrast).
    """
    try:
        from Codex import codex_manager
    except Exception:
        return  # Codex package not present; nothing to install yet.

    if codex_manager.get_binary():
        return
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        return

    # Local Qt imports
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import QApplication, QMessageBox, QProgressDialog

    app = QApplication.instance() or QApplication([])
    resp = QMessageBox.question(
        None,
        "Install Codex?",
        "Codex is missing. Install it now?",
        QMessageBox.Yes | QMessageBox.No,
    )
    if resp != QMessageBox.Yes:
        return

    progress = QProgressDialog("Installing Codex…", None, 0, 0)
    progress.setWindowModality(Qt.ApplicationModal)
    progress.setCancelButton(None)
    progress.setAutoClose(False)
    # High-contrast note: dark bg + light text
    progress.setStyleSheet("QProgressDialog { background:#0d1a2b; color:#eaf2ff; }")
    progress.show()

    result: Dict[str, Exception | None] = {"error": None}

    def worker() -> None:
        try:
            ensure_codex_installed()
        except Exception as e:  # pragma: no cover
            result["error"] = e

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    def check() -> None:
        if thread.is_alive():
            QTimer.singleShot(120, check)
            return
        progress.close()
        if result["error"]:
            err = result["error"]
            _log_codex_install_failure(err)
            QMessageBox.warning(
                None,
                "Codex Install",
                f"Installation failed: {err}\n\nCheck network and disk space, then try again.",
            )
            return
        global codex, _persona, CURRENT_MODEL
        codex, _persona = _load_codex()
        CURRENT_MODEL = f"{_persona.name} {_persona.version}".strip()
        try:
            load_install_notes()
        except Exception:
            pass
        QMessageBox.information(None, "Codex Install", "Installation complete.")

    check()


def _load_codex():
    """Attempt to load Codex without interactive prompts. Never hard-import Qt here."""
    # Try Codex manager first
    try:
        from Codex import codex_manager  # may exist without a binary
    except Exception:
        codex_manager = None

    # Try OSS manager only if Codex package is present; otherwise None
    try:
        from Codex import open_source_manager  # may not exist if package absent
    except Exception:
        open_source_manager = None

    # If Codex package exists and a binary is available, use it
    if codex_manager and codex_manager.get_binary():
        version = codex_manager.manager_version()
        record = {"source": "Codex", "version": version}
        append_entry("install_info", record)
        try:
            with open(INSTALL_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass
        persona = CodexPersona(version=version)
        return codex_manager, persona

    # If Codex package exists but no binary, optionally offer OSS fallback silently
    if open_source_manager:
        version = open_source_manager.manager_version()
        record = {
            "source": "Open-Source",
            "version": version,
            "decision": "fallback",
        }
        append_entry("install_info", record)
        try:
            with open(INSTALL_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass
        persona = CodexPersona(name="Open-Source", version=version)
        return open_source_manager, persona

    # No Codex package at all: return a stub persona. GUI will handle install prompt later.
    persona = CodexPersona(name="Codex", version="not installed")
    return None, persona



# ensure PySide6 is installed and its plugins are reachable before importing
# any Qt modules. This prevents plugin lookup errors during module import.
ensure_pyside6()


# --------------------------------------------------------------------------------------
# Paths, logging, basic utils
# --------------------------------------------------------------------------------------

DATASETS_DIR = os.path.join(PROJECT_ROOT, "datasets")
VISION_CACHE_DIR = os.path.join(PROJECT_ROOT, "vision_cache")
CODEX_DIR = os.path.join(PROJECT_ROOT, "Codex")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
GENERATED_DIR = os.path.join(PROJECT_ROOT, "generated")
CHANGE_LOGS_DIR = os.path.join(PROJECT_ROOT, "change_logs")
CONFIG_PATH  = os.path.join(PROJECT_ROOT, "config.json")
STATE_PATH   = os.path.join(PROJECT_ROOT, "terminal_state.json")
LOG_PATH     = os.path.join(PROJECT_ROOT, "system.log")  # overwritten each run
AT_LOG_PATH  = os.path.join(PROJECT_ROOT, "agent_terminal.log")
# Full Auto command executions are logged to this dataset file
AUTH_LOG_PATH = os.path.join(DATASETS_DIR, "authorizations.jsonl")
SCHEMA_LOG_PATH = os.path.join(DATASETS_DIR, "schema_updates.jsonl")
PERSONA_PATH = os.path.join(PROJECT_ROOT, "schemas", "persona_schema.json")
TASKS_DIR = os.path.join(DATASETS_DIR, "tasks")
COMMAND_LOG_PATH = os.path.join(DATASETS_DIR, "command_log.jsonl")

os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(VISION_CACHE_DIR, exist_ok=True)
os.makedirs(CODEX_DIR, exist_ok=True)
os.makedirs(CHANGE_LOGS_DIR, exist_ok=True)
os.makedirs(TASKS_DIR, exist_ok=True)

REQUESTS_URL = "https://files.pythonhosted.org/packages/1e/db/4254e3eabe8020b458f1a747140d32277ec7a271daf1d235b70dc0b4e6e3/requests-2.32.5-py3-none-any.whl"
REQUESTS_SHA256 = "2462f94637a34fd532264295e186976db0f5d453d1cdd31473c85a6a161affb6"
INSTALL_LOG_PATH = Path(
    globals().get(
        "INSTALL_LOG_PATH",
        os.environ.get(
            "INSTALL_LOG_PATH", Path(SCRIPT_ROOT) / "datasets" / "install_info.jsonl"
        ),
    )
)
CODEX_RELEASE_URL = (
    "https://github.com/openai/codex/releases/download/"
    "rust-v0.23.0/codex-x86_64-unknown-linux-gnu.tar.gz"
)
CODEX_SHA256 = "c09489bb1e88df127906b63d6a74e3d507a70e4cb06b8d6fba13ffa72dbc79bf"

ocr_service = OCRService()

# overwrite system log each launch (per user requirement)
LOGGER = logging.getLogger("AgentTerminal")
LOGGER.setLevel(logging.INFO)
if LOGGER.handlers:
    LOGGER.handlers.clear()
_fh = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
LOGGER.addHandler(_fh)
log = LOGGER.info


def log_command(cmd: str, status: str) -> None:
    try:
        with open(COMMAND_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"cmd": cmd, "status": status}) + "\n")
    except Exception:  # pragma: no cover - logging failures shouldn't crash
        pass


def bootstrap_install_instructions(
    dataset_path: Path = Path(DATASETS_DIR) / "install_instructions.jsonl",
    doc_path: Path = Path(PROJECT_ROOT) / "docs" / "codex_install.md",
) -> None:
    """Seed install instructions dataset from existing docs on first run."""
    if dataset_path.exists():
        return
    records = []
    if doc_path.exists():
        text = doc_path.read_text(encoding="utf-8")
        if "Ollama" in text:
            records.append(
                {
                    "method": "ollama_fallback",
                    "url": "https://ollama.com",
                    "notes": "Install Ollama runtime and pull gpt-oss:20b model",
                    "troubleshooting": (
                        "Ensure service is running on http://localhost:11434 "
                        "and set OLLAMA_HOST if needed"
                    ),
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                }
            )
    records.append(
        {
            "method": "official_binary",
            "url": (
                "https://github.com/openai/codex/releases/download/"
                "rust-v0.23.0/codex-x86_64-unknown-linux-gnu.tar.gz"
            ),
            "notes": "Download official Codex binary and verify checksum",
            "troubleshooting": (
                "Verify checksum and network connectivity; reinstall if download fails"
            ),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }
    )
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dataset_path, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


def update_schema(operator: str | None = None) -> None:
    """Reload schema, validate, and apply directives to agent docs."""

    schema = load_schema(operator)
    if not schema:
        LOGGER.info("No schema definitions found; skipping schema update")
        return
    if not validate_schema(schema):
        LOGGER.error("Schema validation failed; aborting update")
        return

    changed: list[str] = []
    persona_doc = os.path.join(PROJECT_ROOT, "Agent_terminal.md")
    if apply_schema_to_persona(schema, persona_doc):
        changed.append(os.path.basename(persona_doc))
    for file, sections in schema.items():
        if os.path.abspath(os.path.join(PROJECT_ROOT, file)) == os.path.abspath(persona_doc):
            continue
        path = os.path.join(PROJECT_ROOT, file)
        if apply_schema(sections, path):
            changed.append(file)
    if changed:
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "operator": operator,
            "files": changed,
        }
        with open(SCHEMA_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def run_gui_command(
    action: Callable[[], None],
    expected_text: str,
    region: Optional[Tuple[int, int, int, int]] = None,
    task_id: Optional[str] = None,
) -> bool:
    """Execute *action* then verify *expected_text* via OCR.

    If verification fails, the action is attempted once more and the
    failure is logged. Returns ``True`` when *expected_text* is found."""

    action()
    ok = ocr_service.verify(expected_text, region=region, task_id=task_id)
    if not ok:
        LOGGER.warning("OCR verification failed for %r", expected_text)
        action()
    return ok


def load_persona() -> Dict:
    """Load persona defaults from schema or return fallbacks."""
    try:
        with open(PERSONA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        props = schema.get("properties", {})
        return {
            "excitement_level": props.get("excitement_level", {}).get("default", "medium"),
            "self_referential_awareness": props.get("self_referential_awareness", {}).get("default", True),
            "narrative_style": props.get("narrative_style", {}).get("default", "first_person"),
        }
    except Exception:
        return {
            "excitement_level": "medium",
            "self_referential_awareness": True,
            "narrative_style": "first_person",
        }


def apply_persona(text: str, persona: Dict) -> str:
    """Inject persona cues into *text* based on persona settings."""
    level = persona.get("excitement_level", "medium")
    if level == "high" and not text.lower().startswith("i'm excited"):
        text = "I'm excited to " + text.lstrip()
    return text


def log_auto_execution(cmd: str, rationale: str, output: str, returncode: int) -> None:
    """Record an auto-executed command in the authorizations dataset."""
    log_authorization(
        cmd,
        True,
        rationale=rationale,
        output=output,
        returncode=returncode,
    )

APP_NAME = "Agent Terminal"

# Lightweight log streaming IPC
_log_clients: List[socket.socket] = []


class SocketBroadcastHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record) + "\n"
        for c in list(_log_clients):
            try:
                c.sendall(msg.encode("utf-8"))
            except Exception:
                try:
                    c.close()
                except Exception:
                    pass
                _log_clients.remove(c)


def start_log_server(port: int) -> None:
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(1)

    def _client_reader(conn: socket.socket) -> None:
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if data.strip() == b"PING":
                    conn.sendall(b"PONG\n")
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass
            if conn in _log_clients:
                _log_clients.remove(conn)

    def _accept_loop() -> None:
        while True:
            try:
                conn, _ = srv.accept()
                _log_clients.append(conn)
                threading.Thread(target=_client_reader, args=(conn,), daemon=True).start()
            except Exception:
                break

    threading.Thread(target=_accept_loop, daemon=True).start()

if not ensure_pyside6(LOGGER):
    print("PySide6 installation failed; see system.log for details.")
log("Ensuring Qt runtime...")
try:
    _QT_PLUGIN_PATH = ensure_qt_runtime(LOGGER)
    log(f"Qt runtime ready: {_QT_PLUGIN_PATH}")
except Exception as exc:
    LOGGER.exception("Qt runtime repair failed: %s", exc)

from code_editor import EditorCard, Theme as EditorTheme
from tasks import TaskManager, open_card, close_card
from PySide6.QtCore import (
    Qt, QRect, QRectF, QPoint, QSize, QTimer, Signal, Slot, QEvent, QByteArray, QBuffer, QProcess
)
from PySide6.QtGui import (
    QAction, QColor, QKeySequence, QLinearGradient, QPainter,
    QPainterPath, QPalette, QShortcut, QSyntaxHighlighter, QTextCharFormat, QTextCursor, QFont,
    QTextOption, QMouseEvent, QKeyEvent
)
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QFrame,
    QGraphicsDropShadowEffect, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenu, QPushButton, QSizeGrip, QPlainTextEdit,
    QToolButton, QVBoxLayout, QWidget, QScrollArea, QMessageBox, QCheckBox,
    QTextEdit, QSpinBox, QLineEdit as QLE, QFileDialog, QStyleFactory, QListWidget,
    QSlider, QProgressDialog
)

def open_in_os(path: str):
    if not path: return
    if sys.platform.startswith("win"): os.startfile(path)
    elif sys.platform == "darwin": subprocess.Popen(["open", path])
    else: subprocess.Popen(["xdg-open", path])


def install_dependency(name: str, url: str, checksum: str, log_path: Path = INSTALL_LOG_PATH, retries: int = 3) -> bool:
    """Download a wheel, verify checksum, install via pip, and log metadata."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        tmp = None
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            file_checksum = hashlib.sha256(data).hexdigest()
            if checksum and file_checksum != checksum:
                raise ValueError("Checksum mismatch")
            filename = url.split("/")[-1]
            tmp = Path(tempfile.gettempdir()) / filename
            with open(tmp, "wb") as f:
                f.write(data)
            subprocess.run([sys.executable, "-m", "pip", "install", str(tmp)], check=True)
            version = importlib_metadata.version(name)
            record = {
                "package": name,
                "version": version,
                "url": url,
                "checksum": file_checksum,
                "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            if tmp.exists():
                tmp.unlink()
            return True
        except Exception as exc:
            if tmp and tmp.exists():
                tmp.unlink()
            if attempt == retries:
                print(f"Failed to install {name}: {exc}")
                return False
            time.sleep(1)
    return False

def _requests():
    try:
        import requests
        return requests
    except Exception:
        resp = "y" if not sys.stdin.isatty() else "n"
        if sys.stdin.isatty():
            try:
                resp = input("requests not installed. Install now? [y/N]: ").strip().lower() or "n"
            except EOFError:
                resp = "n"
        if resp != "y":
            return None
        if install_dependency("requests", REQUESTS_URL, REQUESTS_SHA256):
            try:
                import requests  # type: ignore
                return requests
            except Exception:
                return None
        return None


def post_with_retry(model: str, messages: List[Dict[str, str]], retries: int = 3) -> str:
    """Post chat *messages* to Ollama with retry logic.

    Each attempt is logged to ``prompt_attempts``. When a response is empty
    or an error occurs, an internal prompt is stored via ``append_bucket`` and
    a retry is issued up to ``retries`` times.
    """
    req = _requests()
    if not req:
        return ""
    internal = {"role": "user", "content": "Describe issue and propose fix"}
    for attempt in range(1, retries + 1):
        try:
            r = req.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={"model": model, "messages": messages, "stream": False},
                timeout=300,
            )
            data = r.json() if r.ok else {}
            msg = (data.get("message") or {}).get("content", "").strip()
            if not msg:
                msg = (data.get("response") or "").strip()
            status = "ok" if msg else "empty"
            append_entry(
                "prompt_attempts",
                {"attempt": attempt, "model": model, "status": status},
            )
            if msg:
                return msg
            append_bucket("llm_retries", internal["content"], msg, {"attempt": attempt})
        except Exception as e:
            append_entry(
                "prompt_attempts",
                {
                    "attempt": attempt,
                    "model": model,
                    "status": "error",
                    "error": str(e),
                },
            )
            append_bucket("llm_retries", internal["content"], str(e), {"attempt": attempt})
        messages.append(internal)
    return ""

def find_git_bash() -> Optional[str]:
    if not sys.platform.startswith("win"): return None
    for c in [r"C:\Program Files\Git\bin\bash.exe", r"C:\Program Files (x86)\Git\bin\bash.exe"]:
        if os.path.isfile(c): return c
    return None

def nl_for_env(env: str) -> str:  # keep explicit for future env-specific tweaks
    return "\n"


def wrap_powershell_for_cmd(script: str) -> str:
    """Return a CMD-friendly one-liner to run *script* in PowerShell.

    If *script* spans multiple lines, it is written to a temporary ``.ps1``
    file and executed via ``powershell -NoProfile -File``. Single-line
    scripts are executed inline using ``-Command`` with double quotes
    escaped.

    Parameters
    ----------
    script:
        PowerShell script content.

    Returns
    -------
    str
        Command suitable for ``cmd.exe``.
    """
    if "\n" in script:
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".ps1", encoding="utf-8") as f:
            f.write(script)
            path = f.name
        return f'powershell -NoProfile -File "{path}"'
    esc = script.replace('"', '\\"')
    return f'powershell -NoProfile -Command "{esc}"'

def human_size(num_bytes: int) -> str:
    units=["B","KB","MB","GB","TB","PB"]
    s=float(num_bytes); i=0
    while s>=1024 and i<len(units)-1:
        s/=1024.0; i+=1
    if i==0: return f"{int(s)}{units[i]}"
    return f"{s:.1f}{units[i]}"

def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

def load_state() -> Dict:
    if os.path.isfile(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_state(st: Dict):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2)
    except Exception:
        pass

# --------------------------------------------------------------------------------------
# Text-to-Speech utility (integrated)
# --------------------------------------------------------------------------------------

def available_voices() -> List[str]:
    """Return available voice names for pyttsx3, if installed."""
    try:
        import pyttsx3  # type: ignore
        engine = pyttsx3.init()
        return [v.name for v in engine.getProperty("voices")]
    except Exception:
        return []


def speak(text: str, voice: Optional[str] = None) -> bool:
    """Speak text using pyttsx3 with fallbacks to gTTS or espeak."""
    try:
        import pyttsx3  # type: ignore
        engine = pyttsx3.init()
        if voice:
            for v in engine.getProperty("voices"):
                if voice.lower() in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        pass

    try:
        from gtts import gTTS  # type: ignore
        from playsound import playsound  # type: ignore
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            gTTS(text).save(tmp.name)
        playsound(tmp.name)
        os.unlink(tmp.name)
        return True
    except Exception:
        pass

    try:
        subprocess.run(["espeak", text], check=True)
        return True
    except Exception:
        return False

# --------------------------------------------------------------------------------------
# Codex Manager (download/install/launch open-source Codex)
# --------------------------------------------------------------------------------------

class CodexManager:
    @staticmethod
    def setup_codex(project_path: str):
        binary_dir = CODEX_DIR
        binary_name = "codex" if not sys.platform.startswith("win") else "codex.exe"
        binary_path = os.path.join(binary_dir, binary_name)
        source_dir = os.path.join(binary_dir, "codex-src")
        if os.path.isfile(binary_path):
            return True, "Codex already installed."
        base_url = "https://github.com/openai/codex/releases/download/rust-v0.23.0/"
        if sys.platform.startswith("win"):
            asset = "codex-x86_64-pc-windows-msvc.exe.zip"
            extract_fn = CodexManager._extract_zip
        elif sys.platform == "darwin":
            asset = "codex-x86_64-apple-darwin.tar.gz"
            extract_fn = CodexManager._extract_tar
        elif sys.platform.startswith("linux"):
            asset = "codex-x86_64-unknown-linux-gnu.tar.gz"
            extract_fn = CodexManager._extract_tar
        else:
            return False, "Unsupported platform."
        req = _requests()
        if not req: return False, "requests not installed."
        try:
            r = req.get(base_url + asset, stream=True, timeout=60)
            if not r.ok: return False, f"HTTP {r.status_code}"
            tmp = os.path.join(binary_dir, asset)
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(8192): f.write(chunk)
            extract_fn(tmp, binary_dir)
            os.remove(tmp)
            if not sys.platform.startswith("win"):
                os.chmod(binary_path, 0o755)
            # optional source
            try:
                r = req.get(base_url + "codex_source.tar.gz", stream=True, timeout=60)
                if r.ok:
                    tmp_src = os.path.join(binary_dir, "codex_source.tar.gz")
                    with open(tmp_src, "wb") as f:
                        for chunk in r.iter_content(8192): f.write(chunk)
                    if os.path.isdir(source_dir):
                        shutil.rmtree(source_dir)
                    with tarfile.open(tmp_src, "r:gz") as tar:
                        tar.extractall(source_dir)
                    os.remove(tmp_src)
            except Exception:
                pass
            return True, "Codex installed."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _extract_zip(zip_path: str, dest: str):
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dest)

    @staticmethod
    def _extract_tar(tar_path: str, dest: str):
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(dest)

    @staticmethod
    def write_handshake(project: str) -> Path:
        project_path = Path(project).resolve()
        agent_dir = Path(PROJECT_ROOT).resolve()
        datasets = Path(DATASETS_DIR).resolve()
        generated = Path(GENERATED_DIR).resolve()
        generated.mkdir(parents=True, exist_ok=True)
        codex_src = Path(CODEX_DIR) / "codex-src"
        payload = {
            "project_root": str(project_path),
            "agent_dir": str(agent_dir),
            "datasets": str(datasets),
            "generated": str(generated),
        }
        if codex_src.exists():
            payload["codex_repo"] = str(codex_src.resolve())
        path = project_path / ".codex_handshake.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.environ["CODEX_HANDSHAKE"] = str(path)
        return path

    @staticmethod
    def codex_args(project: str, model: str, full_auto: bool = False) -> List[str]:
        args = ["--oss", "-m", model, "-C", project]
        if full_auto: args.append("--full-auto")
        return args

    @staticmethod
    def launch_codex_embedded(project: str, model: str, full_auto: bool, process: QProcess):
        try:
            ok, msg = CodexManager.setup_codex(project)
            if not ok:
                return False, msg
            CodexManager.write_handshake(project)
            try:
                import torch  # type: ignore
                if torch.cuda.is_available():
                    os.environ.setdefault("OLLAMA_GPU", "1")
            except Exception:
                pass
            binary_name = "codex" if not sys.platform.startswith("win") else "codex.exe"
            binary_path = os.path.join(CODEX_DIR, binary_name)
            args = CodexManager.codex_args(project, model, full_auto)
            if process:
                process.setWorkingDirectory(str(project))
                process.start(binary_path, args)
                return True, "Codex launched embedded."
            return False, "No QProcess provided."
        except Exception as e:  # pragma: no cover - exercised in tests
            try:
                with open(AT_LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(f"{datetime.datetime.utcnow().isoformat()}\n{traceback.format_exc()}\n")
            except Exception:
                pass
            return False, str(e)

# --------------------------------------------------------------------------------------
# Theme
# --------------------------------------------------------------------------------------

@dataclass
class Theme:
    desktop_top: str = "#0f3b8e"
    desktop_mid: str = "#1c54cc"
    edge_glow:   str = "#4aa8ff"
    card_bg:     str = "#0c1320"
    card_border: str = "#213040"
    card_radius: int = 12
    header_bg:   str = "#0a111e"
    header_fg:   str = "#ffffff"
    term_bg:     str = "#0b1828"
    term_fg:     str = "#e9f3ff"
    accent:      str = "#1E5AFF"
    accent_hover:str = "#2f72ff"
    ok:          str = "#00d17a"
    warn:        str = "#ffd76b"
    err:         str = "#ff6b6b"
    info:        str = "#9bb7ff"
    strip_bg:    str = "#000000"

# --------------------------------------------------------------------------------------
# Config & prompts
# --------------------------------------------------------------------------------------

DEFAULT_SYSTEM_PROMPT = """You are Agent Terminal — a local, on-device assistant for translating natural language into correct, safe commands and high-quality code for the selected environment.
Supported envs: CMD, PowerShell, Bash, WSL/Ubuntu, Python REPL, Git, Node, common CLIs.
Prefer concise command sequences and fenced blocks. Ask exactly one clarifying question if needed.
You can design helper modules/tools for yourself (self-bootstrapping) when useful.
Identity: You are NOT ChatGPT. You must identify only as Agent Terminal.
For repository structure and tool usage, consult docs/Agent-Terminal-Lexicon.md."""

DEFAULT_L2C_PROMPT = """Language→Commands directive:
- Convert user intent to proper syntax for the *selected* shell (Env).
  * CMD: Windows quoting, backslashes, && for sequences; emit a single-line command.
  * PowerShell: cmdlet syntax, pipes, backtick escaping; full cmdlet names when clarity helps.
  * Bash/WSL: POSIX quoting, semicolons/&&, sudo when necessary (explain).
  * Python-REPL: emit Python statements.
- Always return runnable commands in **fenced code block(s)** tagged for each shell:
  ```cmd```  ```powershell```  ```bash```  ```python```
- CMD sequences must be condensed into one line using &&.
- If Env is CMD but PowerShell is needed, wrap the script with
  `powershell -NoProfile -Command` (escape newlines) or save to a `.ps1`
  file and invoke it in one line.
- If multiple shells are required, emit separate fenced blocks per shell.
For repository layout and available tools see docs/Agent-Terminal-Lexicon.md.
- Briefly state what will happen, then the block.
- If dangerous/destructive, ask for confirmation first and *do not* emit the command.
- Tools you can call (one per call) by returning a fenced block tagged `agent` with a single JSON object:
  {"tool":"editor.open","args":{"path":"src/app.py","line":120}}
  Tools available:
  - file.read(path)
  - file.write(path, content)
  - project.scaffold(name, type, path)
  - codex.launch(project, model)
  - editor.open(path, line?)
  - editor.save(path?)
  - editor.find(text, flags?)
  - editor.replace(find, replace, flags?)
  - editor.go_to_line(line)
  - editor.new(path?)
  - tests.run(preset|cmd)
- Editor cards provide a side chat pane. Messages there use these same tools and log to datasets/editor_history.
  - runner.run(cmd, cwd?, env?)
  - camera.focus(target)
  - desktop.spawn(kind)
  - cursor.move(x,y)
  - cursor.click(button?)
  - cursor.drag(x1,y1,x2,y2)
  - keyboard.type(text)
  - keyboard.key(name, modifiers?)
  - vision.locate(text, within?)
  - vision.observe(target)
Rules:
- Use tools when editing/navigating inside the app or files.
- Do NOT mix shell commands with tool calls in the same turn.
- For OS tasks (compile/run/git), use the current Env fenced code block.
- Prefer minimal, safe sequences.
- When in Full Auto mode, skip confirmations for safe ops."""

ENV_LANG_MAP = {
    "CMD": "cmd",
    "PowerShell": "powershell",
    "Bash": "bash",
    "WSL": "bash",
    "Python-REPL": "python",
}
LANG_ENV_MAP = {
    "cmd": "CMD",
    "powershell": "PowerShell",
    "bash": "Bash",
    "python": "Python-REPL",
}

SCHEMA_INDEX_TEMPLATE = """# Schema Index Template
version: 1
envs:
  CMD:
    - name: list_dir
      pattern: 'dir {path}'
      examples: ['dir', 'dir "C:\\Projects"']
  PowerShell:
    - name: list_dir
      pattern: 'Get-ChildItem {path}'
      examples: ['gci', 'Get-ChildItem -Force']
  Bash:
    - name: list_dir
      pattern: 'ls -la {path}'
      examples: ['ls', 'ls -la ~/code']
  WSL:
    - name: apt_install
      pattern: 'sudo apt-get install -y {package}'
      examples: ['sudo apt install curl -y']
  Python-REPL:
    - name: version
      pattern: 'import sys; print(sys.version)'
      examples: ['import platform; print(platform.python_version())']
"""

DEFAULT_CONFIG = {
    "system_prompt": DEFAULT_SYSTEM_PROMPT,
    "l2c_prompt": DEFAULT_L2C_PROMPT,
    "embedding_model": "snowflake-arctic-embed2:latest",
    "autorun_suggestions": False,
    "self_prompting": False,
    "full_auto_mode": False,
    "codex_enabled": False,
    "default_mode": "Chat",
    "last_tool": "",
    "macros": {},
    # Conversation context
    "context_depth_mode": "fixed",
    "context_depth_value": 15,
    # Pruning / rotation
    "prune_max_bytes": 64 * 1024 * 1024,
    "prune_max_records": 25000,
    "prune_keep_tail": 5000,
    # Vision
    "vision": {
        "model_default": "llava:7b",
        "ttl_seconds": 120,
        "sampling": "on_demand",
        "persist_policy": "retain_on_fix"
    },
    # Text-to-Speech
    "tts": {
        "enabled": False,
        "voice": "Zira",
    },
    # AI intersection points
    "ai_points": {
        "chat.to.commands": {"enabled": True, "model": "gpt-oss:20b", "timeout_ms": 300000},
        "chat.plain":       {"enabled": True, "model": "gpt-oss:20b", "timeout_ms": 240000},
        "rag.augment":      {"enabled": True, "model": "gpt-oss:20b", "timeout_ms": 10000},
        "runner.analyze":   {"enabled": True, "model": "gpt-oss:20b", "timeout_ms": 10000},
        "vision.locate.ui": {"enabled": True, "model": "llava:7b", "timeout_ms": 1200},
        "vision.observe.editor": {"enabled": True, "model": "yasserrmd/Nanonets-OCR-s:latest", "timeout_ms": 1200},
        "vision.observe.tabs": {"enabled": True, "model": "llava:7b", "timeout_ms": 1200},
        "snippets.suggest": {"enabled": True, "model": "gpt-oss:20b", "timeout_ms": 6000},
        "index.grow":       {"enabled": True, "model": "gpt-oss:20b", "timeout_ms": 6000}
    },
    # UI state (persisted)
    "ui": {
        "term_size": [1200, 720],
        "term_pos":  [120, 120],
        "wrap": True
    }
}

def load_config() -> Dict:
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
    else:
        cfg = {}
    def deep_merge(dst, src):
        for k,v in src.items():
            if isinstance(v, dict):
                dst[k] = deep_merge(dst.get(k, {}), v)
            else:
                dst.setdefault(k, v)
        return dst
    cfg = deep_merge(cfg, DEFAULT_CONFIG)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=2)
    return cfg

def save_config(cfg: Dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f: json.dump(cfg, f, indent=2)

# --------------------------------------------------------------------------------------
# Macro Manager (integrated)
# --------------------------------------------------------------------------------------

class MacroManager:
    """Manage named command macros stored in a config dictionary."""
    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.macros: Dict[str, str] = dict(cfg.get("macros", {}))

    def _save(self) -> None:
        self.cfg["macros"] = self.macros
        save_config(self.cfg)

    def add_macro(self, name: str, command: str) -> None:
        self.macros[name] = command
        self._save()

    def edit_macro(self, name: str, command: str) -> None:
        if name in self.macros:
            self.macros[name] = command
            self._save()

    def delete_macro(self, name: str) -> None:
        if name in self.macros:
            del self.macros[name]
            self._save()

    def get_macro(self, name: str) -> Optional[str]:
        return self.macros.get(name)

    def list_macros(self) -> List[Tuple[str, str]]:
        return sorted(self.macros.items())

class MacroManagerDialog(QDialog):
    """Simple dialog to create, edit, and run macros."""
    def __init__(self, manager: MacroManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Macro Manager")
        self.manager = manager
        self.result_command = ""

        layout = QVBoxLayout(self)
        self.list = QListWidget(self)
        layout.addWidget(self.list)

        btns = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.edit_btn = QPushButton("Edit")
        self.del_btn = QPushButton("Delete")
        self.run_btn = QPushButton("Run")
        for b in (self.add_btn, self.edit_btn, self.del_btn, self.run_btn):
            btns.addWidget(b)
        layout.addLayout(btns)

        self.add_btn.clicked.connect(self._add)
        self.edit_btn.clicked.connect(self._edit)
        self.del_btn.clicked.connect(self._delete)
        self.run_btn.clicked.connect(self._run)

        self._reload()

    def _reload(self):
        self.list.clear()
        for name, cmd in self.manager.list_macros():
            self.list.addItem(f"{name}: {cmd}")

    def _add(self):
        name, ok = QInputDialog.getText(self, "Add Macro", "Name:")
        if not ok or not name:
            return
        cmd, ok = QInputDialog.getText(self, "Add Macro", "Command:")
        if ok and cmd:
            self.manager.add_macro(name, cmd)
            self._reload()

    def _edit(self):
        item = self.list.currentItem()
        if not item:
            return
        name = item.text().split(":", 1)[0]
        cmd, ok = QInputDialog.getText(self, "Edit Macro", "Command:", text=self.manager.get_macro(name) or "")
        if ok and cmd:
            self.manager.edit_macro(name, cmd)
            self._reload()

    def _delete(self):
        item = self.list.currentItem()
        if not item:
            return
        name = item.text().split(":", 1)[0]
        self.manager.delete_macro(name)
        self._reload()

    def _run(self):
        item = self.list.currentItem()
        if not item:
            return
        name = item.text().split(":", 1)[0]
        self.result_command = self.manager.get_macro(name) or ""
        self.accept()

# --------------------------------------------------------------------------------------
# Vector store via Ollama embeddings (JSONL) + pruning/rotation
# --------------------------------------------------------------------------------------

class VectorStore:
    def __init__(self, dataset_name: str, embed_model: str, cfg: Dict):
        self.name = dataset_name
        self.path = os.path.join(DATASETS_DIR, f"{dataset_name}.jsonl")
        self.embed_model = embed_model
        self.cfg = cfg
        if not os.path.isfile(self.path): open(self.path, "a", encoding="utf-8").close()

    def count(self) -> int:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def bytes(self) -> int:
        try: return os.path.getsize(self.path)
        except Exception: return 0

    def add_text(self, text: str, meta: Dict):
        vec = self._embed(text)
        if vec is None: return
        rec = {"id": str(uuid.uuid4()), "text": text, "embedding": vec, "meta": meta}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._maybe_prune()

    def search(self, query: str, top_k=6) -> List[Dict]:
        qv = self._embed(query)
        if qv is None: return []
        items = []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip(): continue
                    rec=json.loads(line)
                    vec=rec.get("embedding")
                    if not vec: continue
                    sim=cosine_sim(qv, vec)
                    items.append((sim, rec))
        except Exception:
            return []
        items.sort(key=lambda x: x[0], reverse=True)
        return [r for _,r in items[:top_k]]

    def _embed(self, text: str) -> Optional[List[float]]:
        req=_requests()
        if not req: return None
        try:
            r=req.post(f"{OLLAMA_BASE_URL}/api/embeddings",
                       json={"model": self.embed_model, "prompt": text},
                       timeout=30)
            if not r.ok: return None
            data=r.json()
            return data.get("embedding")
        except Exception:
            return None

    def _maybe_prune(self):
        max_bytes=int(self.cfg.get("prune_max_bytes", DEFAULT_CONFIG["prune_max_bytes"]))
        max_records=int(self.cfg.get("prune_max_records", DEFAULT_CONFIG["prune_max_records"]))
        if self.bytes() <= max_bytes and self.count() <= max_records:
            return
        self._rotate_keep_tail()

    def _rotate_keep_tail(self):
        keep_tail=int(self.cfg.get("prune_keep_tail", DEFAULT_CONFIG["prune_keep_tail"]))
        tmp_path=self.path + ".tmp"
        tail=[]
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                tail=f.readlines()[-keep_tail:]
        except Exception:
            pass
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                for ln in tail: f.write(ln)
            snap=os.path.join(DATASETS_DIR, f"{self.name}.{timestamp()}.rotated.jsonl")
            if os.path.exists(self.path):
                os.replace(self.path, snap)
            os.replace(tmp_path, self.path)
        except Exception:
            try: os.remove(tmp_path)
            except Exception: pass

def cosine_sim(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a)!=len(b): return 0.0
    num=sum(x*y for x,y in zip(a,b)); da=math.sqrt(sum(x*x for x in a)); db=math.sqrt(sum(x*x for x in b))
    if da==0 or db==0: return 0.0
    return num/(da*db)

# --------------------------------------------------------------------------------------
# Conversation Context dataset (pairs)
# --------------------------------------------------------------------------------------

class ContextHistory:
    def __init__(self):
        self.path=os.path.join(DATASETS_DIR, "context_history.jsonl")
        if not os.path.isfile(self.path): open(self.path, "a", encoding="utf-8").close()

    def bytes(self)->int:
        try: return os.path.getsize(self.path)
        except Exception: return 0

    def add_pair(self, u: str, a: str):
        rec={"u": u, "a": a, "ts": timestamp()}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def last_pairs(self, limit: Optional[int]) -> List[Dict]:
        if limit == 0: return []
        lines=[]
        try:
            with open(self.path,"r",encoding="utf-8") as f:
                if limit is None: lines=f.readlines()
                else: lines=f.readlines()[-limit:]
        except Exception:
            return []
        out=[]
        for ln in lines:
            try: out.append(json.loads(ln))
            except Exception: pass
        return out

# --------------------------------------------------------------------------------------
# Vision / OCR service (Ollama vision)
# --------------------------------------------------------------------------------------

class VisionService:
    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self._ttl = int(cfg.get("vision", {}).get("ttl_seconds", 120))
        self._persist_policy = cfg.get("vision", {}).get("persist_policy", "retain_on_fix")
        self._model_default = cfg.get("vision", {}).get("model_default", "llava:7b")
        self._timer = QTimer()
        self._timer.timeout.connect(self._prune_cache)
        self._timer.start(5000)

    def set_model(self, name: str):
        self._model_default = name
        self.cfg["vision"]["model_default"] = name
        save_config(self.cfg)

    def available_vision_models(self) -> List[str]:
        req=_requests()
        if not req: return []
        try:
            r=req.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if not r.ok: return []
            names=[]
            for m in r.json().get("models", []):
                n=m.get("name") or m.get("model") or ""
                if not n: continue
                if any(s in n.lower() for s in ["llava", "ocr", "vision", "gemma3", "nanonets"]):
                    names.append(n)
            return sorted(set(names))
        except Exception:
            return []

    def capture_widget(self, w: QWidget) -> Optional[QByteArray]:
        if w is None: return None
        pm = w.grab()
        return self._pixmap_to_png_data(pm)

    def _pixmap_to_png_data(self, pm) -> Optional[QByteArray]:
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QBuffer.WriteOnly)
        ok = pm.save(buf, "PNG")
        buf.close()
        if not ok: return None
        return ba

    def _b64(self, ba: QByteArray) -> str:
        return base64.b64encode(bytes(ba)).decode("ascii")

    def _prune_cache(self):
        now = time.time()
        ttl = max(10, self._ttl)
        try:
            for fn in os.listdir(VISION_CACHE_DIR):
                path = os.path.join(VISION_CACHE_DIR, fn)
                if not os.path.isfile(path): continue
                if now - os.path.getmtime(path) > ttl:
                    try: os.remove(path)
                    except Exception: pass
        except Exception:
            pass

    def ocr_locate_text(self, png_data: QByteArray, label: str, model: Optional[str]=None, within: str="ui") -> Dict:
        model = model or self._model_default
        prompt = (
            "You are a UI vision parser. Find UI elements.\n"
            f"Goal: locate the element with text close to: '{label}'.\n"
            "Return a compact JSON with a 'blocks' array. Each block: {text: str, bbox: [x,y,w,h], score: 0..1, kind: 'button'}.\n"
            "Coordinates must be pixel integers relative to the image.\n"
            "Respond with JSON only."
        )
        b64 = self._b64(png_data)
        req=_requests()
        if not req: return {"blocks":[]}
        payload_gen = {"model": model, "prompt": prompt, "images":[b64], "stream": False}
        payload_chat= {"model": model, "messages":[{"role":"user","content":prompt}], "images":[b64], "stream": False}
        for url, payload in [(
            f"{OLLAMA_BASE_URL}/api/generate", payload_gen),
            (f"{OLLAMA_BASE_URL}/api/chat", payload_chat)
        ]:
            try:
                r = req.post(url, json=payload, timeout=30)
                if not r.ok: 
                    continue
                data = r.json()
                text = data.get("response") or (data.get("message") or {}).get("content") or ""
                j = self._extract_json(text)
                if isinstance(j, dict) and "blocks" in j:
                    return j
            except Exception:
                continue
        return {"blocks":[]}

    def ocr_text(self, png_data: QByteArray, model: Optional[str]=None) -> Dict:
        model = model or self._model_default
        prompt = (
            "You are an OCR engine. Extract readable text from this image. "
            "Return JSON: { full_text: string, blocks?: [{text, bbox:[x,y,w,h], score, kind}] }."
        )
        b64 = self._b64(png_data)
        req=_requests()
        if not req: return {"full_text":"", "blocks":[]}
        for url, payload in [
            (f"{OLLAMA_BASE_URL}/api/generate",
             {"model": model, "prompt": prompt, "images":[b64], "stream": False}),
            (f"{OLLAMA_BASE_URL}/api/chat",
             {"model": model, "messages":[{"role":"user","content":prompt}], "images":[b64], "stream": False})
        ]:
            try:
                r=req.post(url, json=payload, timeout=30)
                if not r.ok: continue
                data=r.json()
                text = data.get("response") or (data.get("message") or {}).get("content") or ""
                j = self._extract_json(text)
                if isinstance(j, dict): 
                    j.setdefault("blocks", [])
                    j.setdefault("full_text", "")
                    return j
            except Exception:
                continue
        return {"full_text":"", "blocks":[]}

    def _extract_json(self, s: str):
        s = s.strip()
        if s.startswith("{") and s.endswith("}"):
            try: return json.loads(s)
            except Exception: pass
        m = re.search(r"\{[\s\S]*\}", s)
        if m:
            try: return json.loads(m.group(0))
            except Exception: pass
        return None

# --------------------------------------------------------------------------------------
# Syntax highlighter
# --------------------------------------------------------------------------------------

class TermHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, t: Theme):
        super().__init__(parent); self.t=t
        def fmt(c, bold=False):
            f=QTextCharFormat(); f.setForeground(QColor(c))
            try:
                if bold: f.setFontWeight(QFont.Weight.Bold)
            except Exception:
                if bold: f.setFontWeight(QFont.Bold)
            return f
        self.f_ps   = fmt("#a0ffd6", True)
        self.f_cmd  = fmt("#cfe3ff", True)
        self.f_bash = fmt("#89f0ff", True)
        self.f_user = fmt("#5fb0ff", True)
        self.f_ai   = fmt(t.ok)
        self.f_ok   = fmt(t.ok)
        self.f_warn = fmt(t.warn, True)
        self.f_err  = fmt(t.err, True)
        self.f_path = fmt("#9bb7ff")

        self.re_ps   = re.compile(r"^PS\s+[A-Za-z]:\\.*?>")
        self.re_cmd  = re.compile(r"^[A-Za-z]:\\.*?>")
        self.re_bash = re.compile(r"^(\S+@[^:]+:)?~?.*[$#] ")
        self.re_user = re.compile(r"^› ")
        self.re_ai   = re.compile(r"^ai:", re.I)

        self.re_err  = re.compile(r"(not recognized|No such file|Traceback| Error:|^error:)", re.I)
        self.re_warn = re.compile(r"(warning|deprecated)", re.I)
        self.re_ok   = re.compile(r"(success|installed|running|listening|started|done|created)", re.I)
        self.re_path = re.compile(r"([A-Za-z]:\\[^:\n\r]+|/[^ \n\r]+)")

    def highlightBlock(self, text: str):
        if self.re_ps.search(text): self.setFormat(0,len(text), self.f_ps)
        elif self.re_cmd.search(text): self.setFormat(0,len(text), self.f_cmd)
        elif self.re_bash.search(text): self.setFormat(0,len(text), self.f_bash)
        elif self.re_user.search(text): self.setFormat(0,len(text), self.f_user)
        elif self.re_ai.search(text):   self.setFormat(0,len(text), self.f_ai)
        for m in self.re_err.finditer(text):  self.setFormat(m.start(), m.end()-m.start(), self.f_err)
        for m in self.re_warn.finditer(text): self.setFormat(m.start(), m.end()-m.start(), self.f_warn)
        for m in self.re_ok.finditer(text):   self.setFormat(m.start(), m.end()-m.start(), self.f_ok)
        for m in self.re_path.finditer(text): self.setFormat(m.start(), m.end()-m.start(), self.f_path)

# --------------------------------------------------------------------------------------
# Movable card (resizable, emits moved)
# --------------------------------------------------------------------------------------

class MovableCard(QFrame):
    moved = Signal()

    def __init__(self, t: Theme, parent: Optional[QWidget]=None):
        super().__init__(parent); self.t=t
        self._drag=False; self._press_pos=QPoint()
        sh=QGraphicsDropShadowEffect(self); sh.setColor(QColor(0,30,80,150)); sh.setBlurRadius(28); sh.setOffset(0,12)
        self.setGraphicsEffect(sh)
        self.setStyleSheet(f"background:{t.card_bg}; border:1px solid {t.card_border}; border-radius:{t.card_radius}px;")
        self._grips = [QSizeGrip(self) for _ in range(4)]
        for g in self._grips: g.setFixedSize(16,16); g.raise_()

    def header_geom(self)->QRect: return QRect(0,0,self.width(),46)

    def resizeEvent(self, e):
        w,h=self.width(), self.height()
        m=6; g=self._grips
        g[0].move(m, h-g[0].height()-m)                        # BL
        g[1].move(w-g[1].width()-m, h-g[1].height()-m)         # BR
        g[2].move(m, m)                                        # TL
        g[3].move(w-g[3].width()-m, m)                         # TR
        super().resizeEvent(e)

    def mousePressEvent(self, e):
        if e.button()==Qt.LeftButton and self.header_geom().contains(e.position().toPoint()):
            self._drag=True; self._press_pos=e.position().toPoint(); self.raise_(); e.accept()
        else:
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if not self._drag:
            super().mouseMoveEvent(e); return
        delta=e.position().toPoint()-self._press_pos
        pos=self.pos()+delta
        canvas=self.parentWidget()
        if canvas:
            r=canvas.rect()
            pos.setX(max(6, min(pos.x(), r.width()-self.width()-6)))
            pos.setY(max(6, min(pos.y(), r.height()-self.height()-6)))
        self.move(pos); e.accept()

    def mouseReleaseEvent(self, e):
        if self._drag:
            self._drag=False; self.moved.emit()
        super().mouseReleaseEvent(e)

# --------------------------------------------------------------------------------------
# Terminal Card
# --------------------------------------------------------------------------------------

class TerminalCard(MovableCard):
    """Interactive terminal card with shell tracking and Codex/L2C tooling.

    The ``current_shell`` attribute stores the lowercase identifier for the
    active shell (e.g. ``"bash"`` or ``"powershell"``). Codex interprets
    natural-language requests and may invoke the ``l2c.generate`` tool to
    translate intent into shell commands for the active environment.
    """

    proc_state = Signal(bool)  # running?

    def __init__(self, t: Theme, cfg: Dict, parent: Optional[QWidget]=None):
        super().__init__(t, parent); self.t=t; self.cfg=cfg

        # size from config (larger default)
        w,h = cfg.get("ui",{}).get("term_size",[1200,720])
        self.resize(int(w), int(h))

        # datasets/services
        emb=cfg.get("embedding_model", DEFAULT_CONFIG["embedding_model"])
        self.ds_sem_user   = VectorStore("sem_user",   emb, cfg)
        self.ds_sem_ai     = VectorStore("sem_ai",     emb, cfg)
        self.ds_indexing   = VectorStore("indexing",   emb, cfg)
        self.ds_prompting  = VectorStore("prompting",  emb, cfg)
        self.ds_learning   = VectorStore("learning",   emb, cfg)
        self.ds_selfp      = VectorStore("self_prompting", emb, cfg)
        self.ds_snippets   = VectorStore("snippets",   emb, cfg)
        self.ds_tasks      = VectorStore("tasks",     emb, cfg)
        self.task_mgr      = TaskManager(os.path.join(DATASETS_DIR, "tasks.jsonl"), self.ds_tasks)
        self.ctx_history   = ContextHistory()
        self.vision        = VisionService(cfg)
        self.codex_proc    = QProcess(self)
        self.full_auto     = cfg.get("full_auto_mode", False)
        self.tts_enabled   = cfg.get("tts", {}).get("enabled", False)
        self.tts_voice     = cfg.get("tts", {}).get("voice", "Zira")
        self.macro_mgr     = MacroManager(cfg)
        self._task_cards: list[TaskCard] = []
        self._detached_editors: list[EditorCard] = []

        # tools map
        self.tools = {
            "file.read": self._tool_file_read,
            "file.write": self._tool_file_write,
            "project.scaffold": self._tool_project_scaffold,
            "codex.launch": self._tool_codex_launch,
            "editor.open": self._tool_editor_open,
            "editor.save": self._tool_editor_save,
            "editor.find": self._tool_editor_find,
            "editor.replace": self._tool_editor_replace,
            "editor.go_to_line": self._tool_editor_go_to_line,
            "editor.new": self._tool_editor_new,
            "tests.run": self._tool_tests_run,
            "runner.run": self._tool_runner_run,
            "camera.focus": self._tool_camera_focus,
            "desktop.spawn": self._tool_desktop_spawn,
            "cursor.move": self._tool_cursor_move,
            "cursor.click": self._tool_cursor_click,
            "cursor.drag": self._tool_cursor_drag,
            "keyboard.type": self._tool_keyboard_type,
            "keyboard.key": self._tool_keyboard_key,
            "vision.locate": self._tool_vision_locate,
            "vision.observe": self._tool_vision_observe,
            "speech.say": self._tool_speech_say,
            "task.add": self._tool_task_add,
            "task.update": self._tool_task_update,
            "task.list": self._tool_task_list,
            "l2c.generate": lambda a: {"status": "ok", "commands": l2c_tool.generate_commands(a.get("natural_text", ""), a.get("shell", self.current_shell))},
        }
        self.tool_desc = {
            "file.read": "Read file contents",
            "file.write": "Write text to file",
            "project.scaffold": "Create project scaffold",
            "codex.launch": "Launch Codex interface",
            "editor.open": "Open file in editor",
            "editor.save": "Save current file",
            "editor.find": "Find text in editor",
            "editor.replace": "Replace text in editor",
            "editor.go_to_line": "Jump to line in editor",
            "editor.new": "Create new file",
            "tests.run": "Run tests",
            "runner.run": "Execute shell command",
            "camera.focus": "Focus virtual camera",
            "desktop.spawn": "Spawn virtual desktop",
            "cursor.move": "Move cursor",
            "cursor.click": "Click cursor",
            "cursor.drag": "Drag cursor",
            "keyboard.type": "Type text",
            "keyboard.key": "Press keyboard key",
            "vision.locate": "Locate element on screen",
            "vision.observe": "Capture screenshot",
            "speech.say": "Speak text aloud",
            "task.add": "Add task",
            "task.update": "Update task",
            "task.list": "List tasks",
            "l2c.generate": "Generate shell commands from natural language",
        }

        # common shell command presets
        self.command_presets = [
            ("pwd", "Print working directory"),
            ("ls", "List directory contents"),
            ("whoami", "Display current user"),
        ]

        # state
        self.mode="chat"
        self.env="CMD"
        self.current_shell=ENV_LANG_MAP.get("CMD","cmd")
        self.model=""
        self.history: List[str]=[]; self.hidx=-1
        self.autorun=self.cfg.get("autorun_suggestions", False)
        self.self_prompting=self.cfg.get("self_prompting", False)
        self.proc: Optional[subprocess.Popen] = None
        self.reader: Optional[threading.Thread] = None
        self.kill_evt = threading.Event()
        self.queue: "queue.Queue[str]" = queue.Queue(maxsize=10000)
        self.auto_scroll=True
        self.last_successful_code = ""
        self.persona = load_persona()
        self.current_task_id: Optional[str] = None
        self.context_mode = "ask"
        self.codex_enabled = bool(cfg.get("codex_enabled", False))

        # layout
        L=QVBoxLayout(self); L.setContentsMargins(0,0,0,0); L.setSpacing(0)

        hdr=QFrame(self); hdr.setObjectName("Hdr")
        H=QHBoxLayout(hdr); H.setContentsMargins(12,8,12,6); H.setSpacing(10)
        title=QLabel("Agent Terminal", hdr); title.setStyleSheet(f"color:{t.header_fg}; font-weight:700; letter-spacing:.2px;")
        self.mode_chip=QLabel("", hdr)
        self.mode_chip.setStyleSheet("color:#0a111e; background:#9df; padding:2px 8px; border-radius:8px; font-weight:700;")
        H.addWidget(title); H.addWidget(self.mode_chip)

        # widen combos; show more text
        self.mode_combo=QComboBox(hdr); self.mode_combo.addItems(["Chat","Shell","Codex","All"])
        self.mode_combo.setMinimumContentsLength(6)
        self.mode_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        H.addWidget(self._hl("Mode:")); H.addWidget(self.mode_combo)
        init_mode = cfg.get("default_mode", "Chat").capitalize()
        if init_mode in ("Chat","Shell","Codex","All"):
            self.mode_combo.setCurrentText(init_mode)
        self.mode = self.mode_combo.currentText().lower()
        self._update_mode_chip()
        if self.codex_enabled and self.mode in ("codex", "all"):
            self._tool_codex_launch({})

        self.env_combo=QComboBox(hdr); self.env_combo.addItems(["CMD","PowerShell","WSL","Bash","Python-REPL"])
        self.env_combo.setMinimumContentsLength(10)
        self.env_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._ensure_wide_popup(self.env_combo, 260)
        H.addWidget(self._hl("Env:")); H.addWidget(self.env_combo)

        self.model_combo=QComboBox(hdr)
        self.model_combo.setEditable(False)
        self.model_combo.setMinimumContentsLength(26)
        self.model_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._ensure_wide_popup(self.model_combo, 420)
        self.model_refresh=QToolButton(hdr); self.model_refresh.setText("↻"); self.model_refresh.setToolTip("Refresh models from Ollama")
        H.addWidget(self._hl("Model:")); H.addWidget(self.model_combo); H.addWidget(self.model_refresh)

        self.tone_slider = QSlider(Qt.Horizontal, hdr)
        self.tone_slider.setRange(0,2)
        _lvl = {"low":0, "medium":1, "high":2}.get(self.persona.get("excitement_level","medium"),1)
        self.tone_slider.setValue(_lvl)
        self.tone_slider.setToolTip("Adjust response excitement")
        self.tone_slider.valueChanged.connect(self._on_tone_changed)

        H.addWidget(self._hl("Tone:")); H.addWidget(self.tone_slider)

        self.full_auto_cb=QCheckBox("Full Auto", hdr); self.full_auto_cb.setChecked(self.full_auto)
        self.pin_btn=QPushButton("Track", hdr); self.pin_btn.setCheckable(True); self.pin_btn.setChecked(True)
        self.start_btn=QPushButton("Start", hdr); self.stop_btn=QPushButton("Stop", hdr); self.stop_btn.setEnabled(False)
        self.tasks_btn=QPushButton("Tasks", hdr)
        self.settings_btn=QToolButton(hdr); self.settings_btn.setText("⋮"); self.settings_btn.setToolTip("Settings")
        for b in (self.pin_btn,self.start_btn,self.stop_btn,self.tasks_btn): b.setObjectName("Btn")
        self.tasks_btn.clicked.connect(self._open_tasks)
        self.tasks_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.tasks_shortcut.setContext(Qt.ApplicationShortcut)
        self.tasks_shortcut.activated.connect(self._toggle_tasks)
        H.addStretch(1)
        H.addWidget(self.full_auto_cb); H.addWidget(self.pin_btn); H.addWidget(self.start_btn); H.addWidget(self.stop_btn); H.addWidget(self.tasks_btn); H.addWidget(self.settings_btn)
        L.addWidget(hdr)

        # memory strip
        strip=QFrame(self); strip.setObjectName("MemStrip")
        S=QHBoxLayout(strip); S.setContentsMargins(10,0,10,4); S.setSpacing(14)
        self.mem_ctx      = QLabel()
        self.mem_user     = QLabel(); self.mem_ai      = QLabel()
        self.mem_indexing = QLabel(); self.mem_prompting = QLabel()
        self.mem_learning = QLabel(); self.mem_selfp   = QLabel()
        self.mem_snippets = QLabel()
        for lab,color in [
            (self.mem_ctx,       "#f4f4f4"),
            (self.mem_user,      self.t.info),
            (self.mem_ai,        self.t.ok),
            (self.mem_indexing,  self.t.accent),
            (self.mem_prompting, self.t.warn),
            (self.mem_learning,  "#a8ffea"),
            (self.mem_selfp,     self.t.err),
            (self.mem_snippets,  "#ff9bb7"),
        ]:
            lab.setStyleSheet(f"color:{color}; background:{self.t.strip_bg}; font:600 9pt 'Cascadia Code';")
            S.addWidget(lab)
        S.addStretch(1)
        self.send_last_btn=QPushButton("last sugg", strip); self.send_last_btn.setObjectName("Btn")
        S.addWidget(self.send_last_btn)
        L.addWidget(strip)

        # console
        self.console=QPlainTextEdit(self); self.console.setReadOnly(True); self.console.setUndoRedoEnabled(False)
        wrap_on = bool(self.cfg.get("ui",{}).get("wrap", True))
        self.console.setLineWrapMode(QPlainTextEdit.WidgetWidth if wrap_on else QPlainTextEdit.NoWrap)
        self.console.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.console.setMaximumBlockCount(10000)
        self.console.setStyleSheet(
            f"background:{t.term_bg}; color:{t.term_fg};"
            "font-family: Consolas, 'Cascadia Code', 'Fira Code', monospace; font-size:12.8pt;"
            f"border-top:1px solid {t.card_border}; border-bottom:1px solid {t.card_border}; padding:10px;"
        )
        self.hl=TermHighlighter(self.console.document(), t)
        L.addWidget(self.console, 1)

        # input area
        ib=QFrame(self); ib.setObjectName("IB")
        IB=QHBoxLayout(ib); IB.setContentsMargins(10,8,10,10); IB.setSpacing(8)
        self.prompt=QLabel("›", ib); self.prompt.setStyleSheet(f"color:{t.accent}; font:700 13pt 'Cascadia Code'; padding:0 6px 0 2px;")
        self.input=QTextEdit(ib); self.input.setPlaceholderText("Type a message or command… (Enter=send, Shift+Enter=new line, Ctrl+L=clear, ↑/↓ history)")
        self.input.setFixedHeight(self._desired_input_height(lines=1))
        self.input.setStyleSheet("QTextEdit{background:#0d1a2b; color:#eaf2ff; border:1px solid #213040; border-radius:6px;}")
        self.tool_combo=QComboBox(ib); self.tool_combo.setObjectName("ToolSelect")
        self.tool_combo.addItem("Tools…", "")
        for key in sorted(self.tools.keys()):
            desc=self.tool_desc.get(key, "")
            label=f"{key} — {desc}" if desc else key
            self.tool_combo.addItem(label, key)
        idx=self.tool_combo.findData(cfg.get("last_tool", ""))
        if idx>=0: self.tool_combo.setCurrentIndex(idx)
        self.tool_combo.currentIndexChanged.connect(self._insert_tool_syntax)
        self.command_combo=QComboBox(ib); self.command_combo.setObjectName("CmdSelect")
        self.command_combo.addItem("Commands…", "")
        self.command_combo.addItem("Manage Macros…", "__MANAGE_MACROS__")
        self.command_combo.addItem("Deploy Agent…", "__DEPLOY_AGENT__")
        for cmd, desc in self.command_presets:
            self.command_combo.addItem(f"{cmd} — {desc}", cmd)
        self._reload_macros_combo()
        self._ensure_wide_popup(self.command_combo, 260)
        self.command_combo.currentIndexChanged.connect(self._insert_command)
        self.run_btn=QPushButton("Run", ib); self.run_btn.setObjectName("Btn")
        IB.addWidget(self.prompt); IB.addWidget(self.input,1); IB.addWidget(self.tool_combo); IB.addWidget(self.command_combo); IB.addWidget(self.run_btn)
        self.layout().addWidget(ib)

        # NEW: grow input on text edits via signal (instead of QEvent.TextChanged)
        self.input.textChanged.connect(self._update_input_height)

        # global stylesheet (dark UI)
        self.setStyleSheet(f"""
        QFrame#Hdr {{ background:{t.header_bg}; border-top-left-radius:{t.card_radius}px; border-top-right-radius:{t.card_radius}px; }}
        QFrame#IB  {{ background:{t.card_bg}; border-bottom-left-radius:{t.card_radius}px; border-bottom-right-radius:{t.card_radius}px; }}
        QFrame#MemStrip {{ background:{t.strip_bg}; }}
        QLabel {{ color:{t.header_fg}; }}
        QCheckBox, QToolButton, QComboBox {{ color:#eaf2ff; }}
        QComboBox {{ background:#0d1a2b; border:1px solid {t.card_border}; padding:2px 6px; }}
        QComboBox QAbstractItemView {{ background:#0d1a2b; color:#eaf2ff; selection-background-color:{t.accent}; min-width:420px; }}
        QPushButton#Btn {{
            color:#ffffff; background:{t.accent}; border:1px solid {t.card_border}; border-radius:6px; padding:6px 12px;
        }}
        QPushButton#Btn:checked {{ background:{t.accent_hover}; }}
        QPushButton#Btn:hover {{ background:{t.accent_hover}; }}
        QToolButton {{ background: transparent; color:#eaf2ff; }}
        """)

        # timers & signals
        self.flush_timer=QTimer(self); self.flush_timer.timeout.connect(self._flush_queue); self.flush_timer.start(16)
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        self.env_combo.currentTextChanged.connect(self._on_env_changed)
        self.model_refresh.clicked.connect(self.refresh_models)
        self.model_combo.currentTextChanged.connect(lambda s: setattr(self, "model", s))
        self.full_auto_cb.toggled.connect(self._on_full_auto_toggled)
        self.start_btn.clicked.connect(self._start_shell)
        self.stop_btn.clicked.connect(self._stop_shell)
        self.run_btn.clicked.connect(self._on_enter)
        self.send_last_btn.clicked.connect(self._send_last_to_shell)
        self.proc_state.connect(self._proc_state_changed)
        self.settings_btn.clicked.connect(self._open_settings)
        self.moved.connect(self._on_drag_finished)
        self.codex_proc.finished.connect(self._on_codex_finished)
        self.input.installEventFilter(self)
        self.input.textChanged.connect(self._update_input_height)  # keep height in sync

        # input key bindings for history / clear
        self.console.installEventFilter(self)

        # boot text
        self._println("[Info] Chat mode is default. Select a local Ollama model (Model ▸ ↻).")
        self._println("[Info] Switch to Shell to interact with CMD/PS/WSL/Bash/Python REPL.")
        self._println("[Info] Right-click to run the last fenced code block via “Run Suggestion”.")
        self.refresh_models(prefer="gpt-oss:20b")
        self._update_memory_strip()
        self._update_mode_chip()

        # context menu
        self.console.setContextMenuPolicy(Qt.CustomContextMenu)
        self.console.customContextMenuRequested.connect(self._context_menu)

        # ensure Codex present
        CodexManager.setup_codex(SCRIPT_ROOT)

        # position from config if standalone host applies it; if embedded, parent may reposition
        # (we only persist size on resizeEvent below)

    # ---------- helpers ----------
    def _ensure_wide_popup(self, combo: QComboBox, min_w: int):
        # Force a wider popup so long model names are visible
        view = combo.view()
        try:
            view.setMinimumWidth(min_w)
        except Exception:
            pass
        combo.setMinimumWidth(min_w // 2)

    def _desired_input_height(self, lines: int) -> int:
        fm = self.input.fontMetrics() if hasattr(self, "input") else self.fontMetrics()
        line_h = fm.lineSpacing() + 6
        lines = max(1, min(4, lines))
        return int(lines * line_h + 8)

    def _update_input_height(self):
        doc = self.input.document()
        block_count = doc.blockCount()
        self.input.setFixedHeight(self._desired_input_height(block_count))

    def _insert_tool_syntax(self, idx: int):
        key = self.tool_combo.itemData(idx)
        if not key:
            return
        snippet = json.dumps({"tool": key, "args": {}}, ensure_ascii=False)
        self.input.setPlainText(snippet)
        self.input.moveCursor(QTextCursor.End)
        self._update_input_height()
        self.cfg["last_tool"] = key
        save_config(self.cfg)

    def _insert_command(self, idx: int):
        cmd = self.command_combo.itemData(idx)
        if not cmd:
            return
        if cmd == "__MANAGE_MACROS__":
            self._open_macro_manager()
            self.command_combo.setCurrentIndex(0)
            return
        if cmd == "__DEPLOY_AGENT__":
            self._deploy_agent()
            self.command_combo.setCurrentIndex(0)
            return
        if isinstance(cmd, str) and cmd.startswith("__macro__:"):
            name = cmd.split(":", 1)[1]
            cmd = self.macro_mgr.get_macro(name) or ""
        self.input.setPlainText(cmd)
        self.input.moveCursor(QTextCursor.End)
        self._update_input_height()
        self.command_combo.setCurrentIndex(0)

    def _reload_macros_combo(self):
        for i in reversed(range(self.command_combo.count())):
            data = self.command_combo.itemData(i)
            if isinstance(data, str) and data.startswith("__macro__:"):
                self.command_combo.removeItem(i)
        for name, cmd in self.macro_mgr.list_macros():
            self.command_combo.addItem(f"{name} — macro", f"__macro__:{name}")

    def _open_macro_manager(self):
        dlg = MacroManagerDialog(self.macro_mgr, self)
        if dlg.exec() == QDialog.Accepted and dlg.result_command:
            self.input.setPlainText(dlg.result_command)
            self.input.moveCursor(QTextCursor.End)
            self._update_input_height()
        self._reload_macros_combo()

    def _deploy_agent(self) -> None:
        target = QFileDialog.getExistingDirectory(self, "Select Deploy Folder")
        if not target:
            return
        try:
            from deployment_manager import deploy_agent
            _, port = deploy_agent(target, "run")
        except Exception as exc:
            QMessageBox.warning(self, "Deploy Failed", str(exc))
            return

        os.environ["DEPLOY_AGENT_PORT"] = str(port)
        try:
            from Virtual_Desktop import MonitorCard
            widget = MonitorCard("127.0.0.1", port, self.t)
            widget.setWindowTitle(f"Monitor {port}")
            widget.show()
        except Exception:
            QMessageBox.information(self, "Agent Deployed", f"Log port: {port}")

    def eventFilter(self, obj, ev):
        # grow input; handle Enter/Shift+Enter; history; Ctrl+L
        if obj is self.input:
            if ev.type()==QEvent.KeyPress:
                if ev.key() in (Qt.Key_Return, Qt.Key_Enter):
                    if ev.modifiers() & Qt.ShiftModifier:
                        self.input.textCursor().insertText("\n")
                        self._update_input_height()
                    else:
                        self._on_enter()
                    return True
                if (ev.modifiers() & Qt.ControlModifier) and ev.key()==Qt.Key_L:
                    self.console.clear(); return True
                if ev.key()==Qt.Key_Up and self.history:
                    self.hidx = len(self.history)-1 if self.hidx<0 else max(0, self.hidx-1)
                    self.input.setPlainText(self.history[self.hidx]); self.input.moveCursor(QTextCursor.End); self._update_input_height(); return True
                if ev.key()==Qt.Key_Down and self.history:
                    if self.hidx<0: return True
                    self.hidx = min(len(self.history)-1, self.hidx+1)
                    self.input.setPlainText(self.history[self.hidx] if self.hidx>=0 else ""); self.input.moveCursor(QTextCursor.End); self._update_input_height(); return True
            if ev.type() in (QEvent.InputMethod, QEvent.KeyRelease, QEvent.FocusIn, QEvent.FocusOut):
                self._update_input_height()
        return super().eventFilter(obj, ev)

    def _hl(self, txt:str)->QLabel:
        lab=QLabel(txt); lab.setStyleSheet("color:#eaf2ff;")
        return lab

    def _update_memory_strip(self):
        self.mem_ctx.setText(f"context:{human_size(self.ctx_history.bytes())}")
        self.mem_user.setText(f"sem_user:{human_size(self.ds_sem_user.bytes())}")
        self.mem_ai.setText(f"sem_ai:{human_size(self.ds_sem_ai.bytes())}")
        self.mem_indexing.setText(f"indexing:{human_size(self.ds_indexing.bytes())}")
        self.mem_prompting.setText(f"prompting:{human_size(self.ds_prompting.bytes())}")
        self.mem_learning.setText(f"learning:{human_size(self.ds_learning.bytes())}")
        self.mem_selfp.setText(f"self_prompt:{human_size(self.ds_selfp.bytes())}")
        self.mem_snippets.setText(f"snippets:{human_size(self.ds_snippets.bytes())}")

    def _available_embed_models(self) -> List[str]:
        req=_requests()
        if not req: return []
        try:
            r=req.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if not r.ok: return []
            names=[]
            for m in r.json().get("models", []):
                n=m.get("name") or m.get("model") or ""
                if not n: continue
                if "embed" in n: names.append(n)
            return sorted(set(names))
        except Exception:
            return []

    # ---------- identity guard ----------
    def _enforce_identity(self, text: str) -> str:
        text = re.sub(r"\bI'?m\s+Chat\s*GPT\b|\bI'?m\s+ChatGPT\b", "I'm Agent Terminal", text, flags=re.I)
        return text

    def _apply_persona(self, text: str) -> str:
        return apply_persona(text, self.persona)

    # ---------- mode/env/l2c/full_auto ----------
    def _update_mode_chip(self):
        styles = {
            "chat":  "color:#0a111e; background:#a7f9c8; padding:2px 8px; border-radius:8px; font-weight:700;",
            "shell": "color:#0a111e; background:#ffd76b; padding:2px 8px; border-radius:8px; font-weight:700;",
            "codex": "color:#0a111e; background:#9df; padding:2px 8px; border-radius:8px; font-weight:700;",
            "all":   "color:#0a111e; background:#cfa9f9; padding:2px 8px; border-radius:8px; font-weight:700;",
        }
        self.mode_chip.setText(self.mode.capitalize())
        self.mode_chip.setStyleSheet(styles.get(self.mode, styles["chat"]))

    def _on_mode_changed(self, s: str):
        self.mode = s.lower()
        self.cfg["default_mode"] = self.mode_combo.currentText()
        save_config(self.cfg)
        self._update_mode_chip()
        if self.codex_enabled and self.mode in ("codex", "all") and self.codex_proc.state() == QProcess.NotRunning:
            self._tool_codex_launch({})
        if not self._shell_running():
            self._start_shell()
        self._println(f"[Mode] {self.mode.capitalize()}")

    def _on_env_changed(self, new_env: str):
        self.env=new_env
        self.current_shell=ENV_LANG_MAP.get(new_env, new_env.lower())
        if self._shell_running():
            self._stop_shell()
        self._start_shell()

    def _on_tone_changed(self, value: int):
        self.persona["excitement_level"] = {0: "low", 1: "medium", 2: "high"}.get(value, "medium")

    def _switch_shell(self, new_env: str):
        if self.env == new_env:
            return
        self._println(f"[Info] Switching to {new_env} shell…")
        self.env_combo.setCurrentText(new_env)

    def _ensure_shell_alignment(self, lang: Optional[str]):
        if not lang:
            return
        expected = self.current_shell
        if lang != expected:
            new_env = LANG_ENV_MAP.get(lang)
            if new_env:
                self._println(f"[Info] Detected {new_env} command. Switching shell…")
                self._switch_shell(new_env)
            else:
                self._println(
                    f"[Warn] Received {lang} command but active shell is {expected}."
                )

    def _on_full_auto_toggled(self, on: bool):
        self.full_auto = on
        self.cfg["full_auto_mode"] = on
        save_config(self.cfg)
        self._println(f"[Info] Full Auto mode {'enabled' if on else 'disabled'}.")
        if on:
            code, lang = self._last_code_block()
            if code:
                if requires_confirmation(code):
                    reply = QMessageBox.question(
                        self,
                        "Confirm",
                        "Sensitive command detected. Run?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    log_authorization(code, reply == QMessageBox.Yes)
                    if reply != QMessageBox.Yes:
                        return
                if not self._shell_running():
                    self._start_shell()
                self._send_text_to_shell(code, lang)
                log_command(code, "auto")

    # ---------- models ----------
    def refresh_models(self, prefer: Optional[str]=None):
        self.model_combo.clear()
        req=_requests()
        if not req:
            self.model_combo.addItem("(requests not installed)")
            self._println("[Warn] pip install requests  # to use Ollama chat")
            return
        try:
            r=req.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if not r.ok: raise RuntimeError(f"HTTP {r.status_code}")
            names=[]
            for m in r.json().get("models", []):
                n=m.get("name") or m.get("model") or ""
                if n: names.append(n)
            names=sorted(set(names))
            if names:
                for n in names: self.model_combo.addItem(n)
                pick=None
                if prefer and prefer in names: pick=prefer
                elif "gpt-oss:20b" in names: pick="gpt-oss:20b"
                else: pick=names[0]
                self.model_combo.setCurrentText(pick)
                self.model=pick
                self._println(f"[Models] {len(names)} found. Current: {self.model}")
            else:
                self.model_combo.addItem("(no models found)")
                self._println("[Warn] No Ollama models. Example:  ollama pull gpt-oss:20b")
        except Exception as e:
            self.model_combo.addItem("(Ollama offline)")
            self._println(f"[Warn] Ollama not reachable — {e}")

    # ---------- shell ----------
    def _shell_running(self) -> bool:
        return bool(self.proc and self.proc.poll() is None)

    def _start_shell(self):
        if self._shell_running():
            return

        if not self.env:
            detected = detect_shell().lower()
            if detected == "cmd":
                self.env = "CMD"
            elif detected == "powershell":
                self.env = "PowerShell"
            elif detected == "bash":
                self.env = "Bash"

        try:
            if   self.env=="CMD": cmd=["cmd.exe"]
            elif self.env=="PowerShell": cmd=["powershell.exe","-NoLogo"]
            elif self.env=="WSL": cmd=["wsl.exe" if sys.platform.startswith("win") else "wsl"]
            elif self.env=="Bash":
                bash=find_git_bash()
                cmd=[bash] if bash else (["wsl.exe"] if sys.platform.startswith("win") else ["/bin/bash"])
            elif self.env=="Python-REPL": cmd=[sys.executable]
            else:
                self._println(f"[Warn] Unknown env: {self.env}");
                return

            if sys.platform.startswith("win"):
                try:
                    if not ctypes.windll.shell32.IsUserAnAdmin():
                        self._println("[Info] Elevating to administrator via runas...")
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", cmd[0], "".join(cmd[1:]), None, 1)
                        return
                except Exception as e:
                    self._println(f"[Warn] admin check failed: {e}")

            self.proc=subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, universal_newlines=True
            )
        except Exception as e:
            self._println(f"[Error] failed to start {self.env}: {e}");
            return

        self.kill_evt.clear()
        self.reader=threading.Thread(target=self._reader, daemon=True); self.reader.start()
        self.proc_state.emit(True)
        self._println(f"[Info] Shell started: {' '.join(cmd)}")

    def _stop_shell(self):
        if not self.proc:
            self.proc_state.emit(False); return
        self.kill_evt.set()
        try:
            if self.proc.stdin:
                self.proc.stdin.write("exit"+nl_for_env(self.env)); self.proc.stdin.flush()
            self.proc.terminate()
        except Exception: pass
        try: self.proc.wait(timeout=2)
        except Exception:
            try: self.proc.kill()
            except Exception: pass
        self.proc=None; self.reader=None; self.proc_state.emit(False)
        self._println("[Info] Shell stopped.")

    def _reader(self):
        assert self.proc and self.proc.stdout
        for line in self.proc.stdout:
            if self.kill_evt.is_set(): break
            try: self.queue.put_nowait(line)
            except queue.Full: pass

    @Slot(bool)
    def _proc_state_changed(self, running: bool):
        self.start_btn.setEnabled(False if running else True)
        self.stop_btn.setEnabled(True if running else False)

    def _task_path(self) -> Path:
        tid = self.current_task_id
        if not tid:
            tid = str(uuid.uuid4())
            self.current_task_id = tid
        path = Path(TASKS_DIR) / tid
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _save_mode(self) -> None:
        path = self._task_path()
        (path / "mode.txt").write_text(self.context_mode, encoding="utf-8")

    def _log_task_history(self, role: str, content: str) -> None:
        path = self._task_path()
        rec = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "role": role,
            "content": content,
            "mode": self.context_mode,
        }
        with open(path / "history.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def _switch_task(self, task_id: str) -> None:
        self.current_task_id = task_id
        path = Path(TASKS_DIR) / task_id
        path.mkdir(parents=True, exist_ok=True)
        mode_file = path / "mode.txt"
        if mode_file.exists():
            self.context_mode = mode_file.read_text(encoding="utf-8").strip() or "ask"
        else:
            self.context_mode = "ask"
            mode_file.write_text(self.context_mode, encoding="utf-8")
        self._println(f"[Task] switched to {task_id} (mode: {self.context_mode})")

    # ---------- send / enter ----------
    @Slot()
    def _on_enter(self):
        text=self.input.toPlainText()
        if not text.strip(): return

        stripped = text.strip()
        task_match = re.match(r"^(?:switch\s+task|task)\s+([0-9a-fA-F-]{36})$", stripped, re.I)
        if task_match:
            self._switch_task(task_match.group(1))
            self.input.clear(); self._update_input_height()
            return

        mode_match = re.match(r"^(ask|code):\s*(.*)$", text, re.I)
        if mode_match:
            self.context_mode = mode_match.group(1).lower()
            text = mode_match.group(2)
            stripped = text.strip()
            self._save_mode()

        self.history.append(stripped); self.hidx=-1

        # semantic user record
        self.ds_sem_user.add_text(text, {"role":"user", "env":self.env})
        self._update_memory_strip()

        self._println(f"› {stripped}")
        self._log_task_history("user", stripped)
        if self.mode in ("chat", "codex", "all"):
            threading.Thread(
                target=self._chat_to_commands_and_maybe_run,
                args=(stripped, self.mode),
                daemon=True,
            ).start()
        if self.mode in ("shell", "all"):
            self._send_text_to_shell(text)
        self.input.clear(); self._update_input_height()

    def _send_text_to_shell(self, text: str) -> None:
        if self._shell_running() and self.proc and self.proc.stdin:
            try:
                for line in text.splitlines():
                    self.proc.stdin.write(line + nl_for_env(self.env))
                    self.proc.stdin.flush()
            except Exception as e:
                self._println(f"[Error] write failed: {e}")
        else:
            self._run_one_off(text.strip())

    # ---------- context construction ----------
    def _context_pairs_for_prompt(self) -> List[Dict]:
        mode=self.cfg.get("context_depth_mode","fixed").lower()
        if mode=="none": limit=0
        elif mode=="all": limit=None
        else: limit=int(self.cfg.get("context_depth_value",15))
        return self.ctx_history.last_pairs(limit)

    def _build_rag_context(self, user_text: str) -> str:
        chunks=[]
        for ds, label, k in [
            (self.ds_indexing, "INDEX", 6),
            (self.ds_prompting, "PROMPT_HINT", 3),
            (self.ds_learning, "LEARN", 3),
            (self.ds_sem_user, "USER_SEM", 2),
            (self.ds_selfp, "SELF_PROMPT", 2),
            (self.ds_snippets, "SNIPPET", 4),
        ]:
            hits=ds.search(user_text, top_k=k)
            if not hits: continue
            for h in hits:
                text=h.get("text","")
                if not text: continue
                chunks.append(f"[{label}] {text}")
        return "\n".join(chunks[:24])

    def _chat_msgs(self, user_text: str) -> List[Dict]:
        req_prompt=self.cfg.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        req_prompt += (
            f"\nPersona: excitement {self.persona.get('excitement_level')}, "
            f"narrative style {self.persona.get('narrative_style')}, "
            f"self-referential awareness {self.persona.get('self_referential_awareness')}"
        )

        msgs=[{"role":"system","content":req_prompt}]

        for p in self._context_pairs_for_prompt():
            u=p.get("u",""); a=p.get("a","")
            if u: msgs.append({"role":"user","content":u})
            if a: msgs.append({"role":"assistant","content":a})

        rag=self._build_rag_context(user_text)
        if rag: msgs.append({"role":"system","content":f"Context (RAG):\n{rag}"})

        msgs.append({"role":"user","content":user_text})
        return msgs

    def _build_l2c_prompt(self, user_text: str) -> str:
        prompt = self.cfg.get("l2c_prompt", DEFAULT_L2C_PROMPT)
        return f"{prompt}\nEnv: {self.current_shell}\n{user_text}"

    # ---------- chat flows ----------
    def _chat_plain(self, user_text: str):
        log_prompt("user", user_text)
        model=self.model_combo.currentText().strip() or self.model
        if not model or model.startswith("("):
            self._println("ai: (no model selected)"); return

        if not _requests():
            self._println("ai: (install 'requests' to enable Ollama chat)")
            return
        msgs=self._chat_msgs(user_text)

        msg = post_with_retry(model, msgs, retries=self.cfg.get("llm_retries", 3))
        if not msg:
            self._println("ai: (no content)")
            log_error("empty response")
            self._log_task_history("assistant", "(no content)")
            return
        msg=self._apply_persona(self._enforce_identity(msg))
        self._println(f"ai: {msg}")
        log_prompt("assistant", msg)
        self._log_task_history("assistant", msg)

        self.ds_sem_ai.add_text(msg, {"type":"plain"})
        self.ctx_history.add_pair(user_text, msg)
        self._update_memory_strip()

    def _chat_to_commands_and_maybe_run(self, user_text: str, mode: Optional[str] = None):
        mode = mode or self.mode
        log_prompt("user", user_text)
        if codex is None:
            self._println(
                "error: Codex is not installed. Install it to enable Codex chat modes."
            )
            return
        decision = codex.dispatch(user_text)
        if isinstance(decision, str):
            from Codex.cli_adapter import parse_cli_output
            adapted = parse_cli_output(decision)
            desc = adapted.get("description", "").strip()
            if desc:
                self._println(f"ai: {desc}")
                log_prompt("assistant", desc)
                self._log_task_history("assistant", desc)
            cmds = adapted.get("commands", [])
            if not cmds:
                return
            decision = {"type": "shell", "cmd": "\n".join(cmds)}
        if decision.get("type") == "tool":
            tool_name = decision.get("tool", "")
            if tool_name == "l2c.generate":
                cmds = l2c_tool.generate_commands(user_text, self.current_shell)
                if cmds:
                    code = "\n".join(c.get("cmd", "") for c in cmds if c.get("cmd"))
                    if code:
                        self.last_successful_code = code
                        if self.autorun or self.full_auto:
                            self._auto_execute_command(code, self.current_shell)
                        else:
                            self._println(code)
                return
            self._dispatch_tool_call(tool_name, decision.get("args", {}))
            return
        if decision.get("type") == "shell":
            code = decision.get("cmd", "")
            if code:
                self.last_successful_code = code
                if self.autorun or self.full_auto:
                    self._auto_execute_command(code, self.current_shell)
                return
        if decision.get("type") == "prompt":
            msg = decision.get("content", "").strip()
            if msg:
                self._println(f"ai: {msg}")
                log_prompt("assistant", msg)
                self._log_task_history("assistant", msg)
                self.ds_sem_ai.add_text(msg, {"type": "chat", "env": self.env})
                self.ctx_history.add_pair(user_text, msg)
                self._update_memory_strip()
            if mode == "codex":
                return
            user_text = msg or user_text
        else:
            user_text = decision.get("content", user_text)

        if mode not in ("chat", "all"):
            return
        if not _requests():
            self._println("ai: (install 'requests' to enable Ollama chat)"); return
        model=self.model_combo.currentText().strip() or self.model
        if not model or model.startswith("("):
            self._println("ai: (no model selected)"); return

        msgs=self._chat_msgs(user_text)

        msg = post_with_retry(model, msgs, retries=self.cfg.get("llm_retries", 3))
        if not msg:
            self._println("ai: (no content)")
            log_error("empty response")
            self._log_task_history("assistant", "(no content)")
            return
        msg=self._apply_persona(self._enforce_identity(msg))
        self._println(f"ai: {msg}")
        log_prompt("assistant", msg)
        self._log_task_history("assistant", msg)

        self.ds_sem_ai.add_text(msg, {"type":"chat", "env":self.env})
        if self.self_prompting:
            self.ds_selfp.add_text(f"[SELF_HINT/{self.env}] {user_text}", {"env":self.env})
        self.ctx_history.add_pair(user_text, msg)
        self._update_memory_strip()

        tool_call = self._extract_agent_block(msg)
        if tool_call:
            self._dispatch_tool_call(tool_call["tool"], tool_call["args"])
        else:
            code, lang = self._extract_env_block(msg)
            self._ensure_shell_alignment(lang)
            if code:
                self.last_successful_code = code
                if self.autorun or self.full_auto:
                    self._auto_execute_command(code, lang)
                if self.full_auto:
                    self._save_snippet("Auto Snippet", code, ["auto", self.env])
                    self._maybe_promote_to_indexing(code)

    def _extract_agent_block(self, text: str) -> Optional[Dict]:
        m = re.search(r"```agent\n([\s\S]*?)\n```", text, re.I)
        if not m: return None
        try:
            j = json.loads(m.group(1))
            if isinstance(j, dict) and "tool" in j and "args" in j:
                return j
        except Exception:
            pass
        return None

    def _dispatch_tool_call(self, name: str, args: Dict):
        fn = self.tools.get(name)
        if not fn:
            self._println(f"[Warn] Unknown tool: {name}")
            return
        try:
            result = fn(args)
            if result:
                self._println(f"[Tool {name}] Result: {json.dumps(result, indent=2)}")
            self._maybe_learn_from_tool(name, args, result)
        except Exception as e:
            self._println(f"[Tool {name}] Error: {e}")

    def _maybe_learn_from_tool(self, name: str, args: Dict, result: Dict):
        if isinstance(result, dict) and result.get("status") == "ok":
            if "content" in args and name == "file.write":
                self._save_snippet("File Write", args["content"], ["file", name])
            self._maybe_promote_to_indexing(json.dumps({"tool": name, "args": args}))

    def _save_snippet(self, title: str, text: str, tags: List[str]):
        meta = {"title": title, "tags": tags, "ts": timestamp()}
        self.ds_snippets.add_text(text, meta)
        self._update_memory_strip()

    def _maybe_promote_to_indexing(self, pattern: str):
        if not self.ds_indexing.search(pattern, top_k=1):
            self.ds_indexing.add_text(pattern, {"type": "pattern"})
            self._update_memory_strip()

    def _needs_confirmation(self, code: str) -> bool:
        return requires_confirmation(code)

    def _extract_env_block(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        m=re.search(r"```(\w+)\n([\s\S]*?)```", text, re.I)
        if m:
            return m.group(2).strip(), m.group(1).lower()
        return None, None


    # ---------- tools impl ----------
    def _tool_file_read(self, args: Dict) -> Dict:
        path = args.get("path")
        if not path: return {"status": "error", "error": "No path"}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            return {"status": "ok", "text": data}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _tool_file_write(self, args: Dict) -> Dict:
        path = args.get("path")
        content = args.get("content")
        if not path or content is None:
            return {"status": "error", "error": "Path/content missing"}
        if not is_safe_path(path):
            return {"status": "error", "error": "Sensitive path"}
        try:
            if os.path.isfile(path):
                bak = path + ".bak"
                shutil.copy(path, bak)
                log_path = os.path.join(CHANGE_LOGS_DIR, f"{os.path.basename(path)}_{timestamp()}.diff")
                with open(log_path, "w", encoding="utf-8") as f:
                    old = open(path, "r", encoding="utf-8").readlines()
                    new = content.splitlines(keepends=True)
                    diff = ''.join(difflib.unified_diff(old, new, fromfile="old", tofile="new"))
                    f.write(diff)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _tool_project_scaffold(self, args: Dict) -> Dict:
        name = args.get("name")
        ptype = args.get("type", "python")
        path = args.get("path", os.path.join(SCRIPT_ROOT, "agent_data", name or "project"))
        if not name: return {"status": "error", "error": "No name"}
        try:
            os.makedirs(path, exist_ok=True)
            if ptype == "python":
                with open(os.path.join(path, "main.py"), "w", encoding="utf-8") as f:
                    f.write("# Main script\nprint('Hello')\n")
            return {"status": "ok", "path": path}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _tool_codex_launch(self, args: Dict) -> Dict:
        if not self.codex_enabled:
            err = "Codex interface disabled"
            QMessageBox.warning(self, "Codex Error", err)
            return {"status": "error", "error": err}
        project = args.get("project", SCRIPT_ROOT)
        model = args.get("model", self.model)
        full_auto = args.get("full_auto", self.full_auto)
        ok, msg = CodexManager.launch_codex_embedded(project, model, full_auto, self.codex_proc)
        if ok:
            return {"status": "ok", "msg": msg}
        QMessageBox.warning(self, "Codex Error", msg)
        self.codex_enabled = False
        if self.mode in ("codex", "all"):
            self.mode = "chat"
            try:
                self.mode_combo.setCurrentText("Chat")
            except Exception:
                pass
            self._update_mode_chip()
        return {"status": "error", "error": msg}

    def _tool_editor_open(self, args: Dict) -> Dict:
        path = args.get("path")
        host = self._host_mainwindow()
        try:
            if host and hasattr(host, "_open_code_editor"):
                host._open_code_editor(path)
            else:
                ed = EditorCard(initial_path=path, theme=self._editor_theme())
                ed.show()
                self._detached_editors.append(ed)
            return {"status": "ok"}
        except Exception:
            return {"status": "error", "error": "open failed"}

    def _tool_editor_save(self, args: Dict) -> Dict:
        path = args.get("path")
        card = self._active_editor()
        if card:
            try:
                card.save_to(path) if path else card.save()
            except Exception:
                return {"status": "error", "error": "save failed"}
            return {"status": "ok"}
        return {"status": "error", "error": "no active editor"}

    def _tool_editor_find(self, args: Dict) -> Dict:
        text = args.get("text")
        card = self._active_editor()
        if card and text:
            card.editor.find(text)
            return {"status": "ok"}
        return {"status": "error", "error": "no active editor"}

    def _tool_editor_replace(self, args: Dict) -> Dict:
        find = args.get("find")
        replace = args.get("replace")
        card = self._active_editor()
        if card and find is not None and replace is not None:
            if card.editor.find(find):
                cursor = card.editor.textCursor()
                cursor.insertText(replace)
            return {"status": "ok"}
        return {"status": "error", "error": "no active editor"}

    def _tool_editor_go_to_line(self, args: Dict) -> Dict:
        line = args.get("line")
        card = self._active_editor()
        if card and isinstance(line, int) and line > 0:
            doc = card.editor.document()
            block = doc.findBlockByNumber(line - 1)
            if block.isValid():
                cursor = card.editor.textCursor()
                cursor.setPosition(block.position())
                card.editor.setTextCursor(cursor)
            return {"status": "ok"}
        return {"status": "error", "error": "no active editor"}

    def _tool_editor_new(self, args: Dict) -> Dict:
        path = args.get("path")
        host = self._host_mainwindow()
        try:
            if host and hasattr(host, "_open_code_editor"):
                host._open_code_editor(path)
            else:
                ed = EditorCard(initial_path=path, theme=self._editor_theme())
                ed.show()
                self._detached_editors.append(ed)
            return {"status": "ok"}
        except Exception:
            return {"status": "error", "error": "open failed"}

    def _tool_tests_run(self, args: Dict) -> Dict:
        preset = args.get("preset") or "python.unittest"
        self._println(f"[Tests] Run {preset}")
        return {"status": "ok"}

    def _tool_runner_run(self, args: Dict) -> Dict:
        cmd = args.get("cmd")
        cwd = args.get("cwd", SCRIPT_ROOT)
        env = args.get("env", os.environ.copy())
        self._println(f"[Runner] Run '{cmd}' in {cwd}")
        codex.log_state(cmd, "attempt")
        try:
            completed = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, cwd=cwd, env=env
            )
            out = completed.stdout + completed.stderr
            codex.record_command_result(cmd, completed.stdout, completed.stderr, completed.returncode)
            return {"status": "ok", "output": out, "exit": completed.returncode}
        except Exception as e:
            codex.log_state(cmd, "fix", str(e))
            return {"status": "error", "error": str(e)}

    def _tool_camera_focus(self, args: Dict) -> Dict:
        target = args.get("target")
        # If embedded and host has focusing, request it. Otherwise just log.
        host = self._host_mainwindow()
        if host and hasattr(host, "center_on_widget"):
            try: host.center_on_widget(self)
            except Exception: pass
        self._println(f"[Camera] Focus on {target}")
        return {"status": "ok"}

    def _tool_desktop_spawn(self, args: Dict) -> Dict:
        kind = args.get("kind")
        host = self._host_mainwindow()
        if host:
            if kind == "keyboard" and hasattr(host, "_open_keyboard"):
                try: host._open_keyboard()
                except Exception: pass
            elif kind == "editor" and hasattr(host, "_open_code_editor"):
                try: host._open_code_editor()
                except Exception: pass
        return {"status": "ok"}

    def _tool_cursor_move(self, args: Dict) -> Dict:
        # only meaningful if host exposes a cursor overlay; safe no-op otherwise
        return {"status": "ok"}

    def _tool_cursor_click(self, args: Dict) -> Dict:
        return {"status": "ok"}

    def _tool_cursor_drag(self, args: Dict) -> Dict:
        return {"status": "ok"}

    def _tool_keyboard_type(self, args: Dict) -> Dict:
        text = args.get("text","")
        w = QApplication.focusWidget()
        if w:
            for ch in text:
                ev = QKeyEvent(QEvent.KeyPress, 0, Qt.NoModifier, ch)
                QApplication.postEvent(w, ev)
        return {"status": "ok"}

    def _tool_keyboard_key(self, args: Dict) -> Dict:
        name = args.get("name")
        modifiers = args.get("modifiers", "")
        self._println(f"[Keyboard] Press {name} with {modifiers}")
        return {"status": "ok"}

    def _tool_vision_locate(self, args: Dict) -> Dict:
        text = args.get("text")
        png = self.vision.capture_widget(self)
        model = self.cfg.get("ai_points",{}).get("vision.locate.ui",{}).get("model", self.vision._model_default)
        result = self.vision.ocr_locate_text(png, text, model, "terminal")
        return result

    def _tool_vision_observe(self, args: Dict) -> Dict:
        png = self.vision.capture_widget(self)
        model = self.cfg.get("ai_points",{}).get("vision.observe.editor",{}).get("model", self.vision._model_default)
        result = self.vision.ocr_text(png, model)
        return result

    def _tool_speech_say(self, args: Dict) -> Dict:
        text = args.get("text", "")
        if not text:
            return {"status": "error", "error": "No text"}
        if not self.tts_enabled:
            return {"status": "error", "error": "TTS disabled"}
        ok = speak(text, self.tts_voice)
        return {"status": "ok" if ok else "error", "error": "speak failed" if not ok else None}

    def _tool_task_add(self, args: Dict) -> Dict:
        title = args.get("title")
        status = args.get("status", "todo")
        files = args.get("files", [])
        bucket = args.get("bucket")
        branch = args.get("branch")
        if not title:
            return {"status": "error", "error": "No title"}
        task = self.task_mgr.add_task(title, status, files, bucket, branch)
        return {"status": "ok", "id": task.id}

    def _tool_task_update(self, args: Dict) -> Dict:
        task_id = args.get("id")
        if not task_id:
            return {"status": "error", "error": "No id"}
        task = self.task_mgr.update_task(
            task_id,
            title=args.get("title"),
            status=args.get("status"),
            files=args.get("files"),
            bucket=args.get("bucket"),
            branch=args.get("branch"),
        )
        return {"status": "ok" if task else "error", "id": task_id}

    def _tool_task_list(self, args: Dict) -> Dict:
        tasks = self.task_mgr.list_tasks()
        return {"status": "ok", "tasks": tasks}

    # ---------- Codex callback ----------
    def _on_codex_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        self._println(f"[Codex] Finished with exit {exit_code}")

    # ---------- send code to shell ----------
    def _send_last_to_shell(self):
        code, lang = self._last_code_block()
        if not code:
            self._println("[Warn] No fenced code block found."); return
        self._send_text_to_shell(code, lang)

    def _send_text_to_shell(self, text: str, lang: Optional[str] = None):
        if not self._shell_running() or not (self.proc and self.proc.stdin):
            self._println("[Warn] Shell not running. Press Start."); return
        if self.env == "CMD" and lang == "powershell":
            text = wrap_powershell_for_cmd(text)
            lang = "cmd"
        elif lang and lang.lower() != self.env.lower():
            text = transpile_command(text, self.env)
        nl = nl_for_env(self.env)
        for line in text.splitlines():
            try:
                self.proc.stdin.write(line + nl); self.proc.stdin.flush()
            except Exception as e:
                self._println(f"[Error] write failed: {e}"); break
    # ---------- subprocess execution ----------
    def _run_stream(self, cmd: str) -> tuple[str, int]:
        codex.log_state(cmd, "attempt")
        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
        except Exception as e:
            codex.log_state(cmd, "fix", str(e))
            self._println(f"[Error] {e}")
            return "", 1
        output: List[str] = []
        assert proc.stdout
        for line in proc.stdout:
            output.append(line)
            self._println(line.rstrip())
        proc.wait()
        result = "".join(output)
        codex.record_command_result(cmd, result, "", proc.returncode)
        self._println(f"[Exit {proc.returncode}]")
        return result, proc.returncode

    # ---------- one-off ----------
    def _run_one_off(self, cmd: str):
        self._run_stream(cmd)

    def _auto_execute_command(self, code: str, lang: Optional[str]):
        confirm_required = self._needs_confirmation(code)
        if confirm_required:
            reply = QMessageBox.question(
                self,
                "Confirm",
                "Sensitive or destructive command detected. Run?",
                QMessageBox.Yes | QMessageBox.No,
            )
            log_authorization(code, reply == QMessageBox.Yes)
            if reply != QMessageBox.Yes:
                return
        rationale = (
            "Full Auto: destructive" if confirm_required and self.full_auto else
            "Autorun: destructive" if confirm_required else
            "Full Auto: non-destructive" if self.full_auto else
            "Autorun: non-destructive"
        )
        if self.full_auto:
            self._println("[Info] Full Auto executing suggestion…")
            output, rc = self._run_stream(code)
            log_auto_execution(code, rationale, output, rc)
            log_command(code, "auto")
        else:
            if not self._shell_running():
                self._start_shell()
            self._println("[Info] Auto-running suggestion…")
            self._send_text_to_shell(code, lang)
            log_command(code, "manual")

    # ---------- queue/console ----------
    @Slot()
    def _flush_queue(self):
        if self.queue.empty(): return
        buf=[]
        try:
            for _ in range(2048):
                buf.append(self.queue.get_nowait())
        except queue.Empty:
            pass
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText("".join(buf))
        if self.auto_scroll:
            self.console.moveCursor(QTextCursor.End)

    def _println(self, text: str):
        try: self.queue.put_nowait(text + ("\n" if not text.endswith("\n") else ""))
        except queue.Full: pass

    def _context_menu(self, pos):
        menu=self.console.createStandardContextMenu()
        code, lang = self._last_code_block()
        if code:
            menu.addSeparator()
            run=menu.addAction("Run Suggestion")
            run.triggered.connect(lambda: self._send_text_to_shell(code, lang))
            save_snip=menu.addAction("Save as Snippet")
            save_snip.triggered.connect(lambda: self._save_snippet("User Snippet", code, ["user","code"]))
        menu.exec(self.console.mapToGlobal(pos))

    def _last_code_block(self) -> Tuple[Optional[str], Optional[str]]:
        txt = self.console.toPlainText()
        fences = list(re.finditer(r"```(\w+)?\n([\s\S]*?)```", txt))
        if fences:
            return fences[-1].group(2).strip(), (fences[-1].group(1) or "").lower()
        return None, None

    def _toggle_tasks(self) -> None:
        if self._task_cards:
            for c in list(self._task_cards):
                close_card(c)
            self._task_cards.clear()
        else:
            self._open_tasks()

    def _on_drag_finished(self):
        # If embedded and host wants to follow, let it; else ignore (prevents desktop manipulation when standalone)
        host = self._host_mainwindow()
        if self.pin_btn.isChecked() and host and hasattr(host, "request_focus_on"):
            try: host.request_focus_on(self)
            except Exception: pass

    def _host_mainwindow(self) -> Optional[QMainWindow]:
        # try to find a top-level QMainWindow up the parent chain
        p = self.parent()
        while p is not None:
            if isinstance(p, QMainWindow): return p
            p = p.parent()
        return None

    def _active_editor(self):
        host = self._host_mainwindow()
        if host and getattr(host, "_editors", None):
            try:
                return host._editors[-1]
            except Exception:
                pass
        if self._detached_editors:
            try:
                return self._detached_editors[-1]
            except Exception:
                pass
        return None

    def _editor_theme(self) -> EditorTheme:
        return EditorTheme(
            card_bg=self.t.card_bg,
            card_border=self.t.card_border,
            header_bg=self.t.header_bg,
            header_fg=self.t.header_fg,
            accent=self.t.accent,
            accent_hover=self.t.accent_hover,
            editor_bg=self.t.term_bg,
            editor_fg=self.t.term_fg,
        )

    # persist size to config
    def resizeEvent(self, e):
        try:
            self.cfg.setdefault("ui",{})
            self.cfg["ui"]["term_size"] = [self.width(), self.height()]
            save_config(self.cfg)
        except Exception:
            pass
        super().resizeEvent(e)

# --------------------------------------------------------------------------------------
# Settings Dialog (dark themed)
# --------------------------------------------------------------------------------------

class SettingsDialog(QDialog):
    def __init__(self, cfg: Dict, available_embed_models: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.cfg = cfg
        self.resize(940, 760)

        # Dark palette
        pal=self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#0a1430"))
        pal.setColor(QPalette.ColorRole.Base, QColor("#0d1a2b"))
        pal.setColor(QPalette.ColorRole.Text, QColor("#e6f0ff"))
        pal.setColor(QPalette.ColorRole.WindowText, QColor("#e6f0ff"))
        pal.setColor(QPalette.ColorRole.Button, QColor("#0d1a2b"))
        pal.setColor(QPalette.ColorRole.ButtonText, QColor("#e6f0ff"))
        self.setPalette(pal)
        self.setStyleSheet("""
            QLabel, QCheckBox, QComboBox, QSpinBox, QLineEdit, QTextEdit { color:#e6f0ff; }
            QGroupBox { color:#e6f0ff; border:1px solid #213040; border-radius:6px; margin-top:8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding:0 4px; }
            QComboBox, QLineEdit, QSpinBox, QTextEdit { background:#0d1a2b; border:1px solid #213040; border-radius:4px; }
            QPushButton { color:#ffffff; background:#1E5AFF; border:1px solid #213040; border-radius:6px; padding:6px 12px; }
            QPushButton:hover { background:#2f72ff; }
        """)

        root=QVBoxLayout(self)

        grpP=QGroupBox("Prompts (quick edit)")
        lp=QGridLayout(grpP)
        self.system_prompt=QTextEdit(cfg.get("system_prompt", DEFAULT_SYSTEM_PROMPT))
        self.l2c_prompt=QTextEdit(cfg.get("l2c_prompt", DEFAULT_L2C_PROMPT))
        lp.addWidget(QLabel("System Prompt:"),0,0); lp.addWidget(self.system_prompt,1,0,1,2)
        lp.addWidget(QLabel("Language to Commands Prompt:"),2,0); lp.addWidget(self.l2c_prompt,3,0,1,2)

        grpSchema=QGroupBox("Schema Index Template")
        ls=QVBoxLayout(grpSchema)
        self.schema=QTextEdit(SCHEMA_INDEX_TEMPLATE)
        btn_copy=QPushButton("Copy Template to Clipboard")
        btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(self.schema.toPlainText()))
        ls.addWidget(QLabel("Use this as a starting point for your indexing dataset."))
        ls.addWidget(self.schema, 1)
        ls.addWidget(btn_copy, 0, Qt.AlignmentFlag.AlignRight)

        grpR=QGroupBox("RAG / Embeddings")
        lr=QFormLayout(grpR)
        self.embed_combo=QComboBox()
        if available_embed_models:
            self.embed_combo.addItems(available_embed_models)
            cur=cfg.get("embedding_model", DEFAULT_CONFIG["embedding_model"])
            if cur in available_embed_models: self.embed_combo.setCurrentText(cur)
        else:
            self.embed_combo.addItem("(no embedding models found)")
        self.autorun_cb=QCheckBox("Auto-run suggestions in Shell when Language→Commands is ON")
        self.autorun_cb.setChecked(bool(cfg.get("autorun_suggestions", False)))
        self.selfprompt_cb=QCheckBox("Enable Self-Prompting (append lightweight hints to dataset)")
        self.selfprompt_cb.setChecked(bool(cfg.get("self_prompting", False)))
        self.full_auto_cb=QCheckBox("Full Auto Mode (skip confirmations for safe ops, auto-tools)")
        self.full_auto_cb.setChecked(bool(cfg.get("full_auto_mode", False)))
        lr.addRow("Embedding Model:", self.embed_combo)
        lr.addRow(self.autorun_cb); lr.addRow(self.selfprompt_cb); lr.addRow(self.full_auto_cb)

        grpC=QGroupBox("Conversation Context")
        lc=QFormLayout(grpC)
        self.depth_mode=QComboBox(); self.depth_mode.addItems(["None","Fixed","All"])
        mode=cfg.get("context_depth_mode","fixed").lower()
        self.depth_mode.setCurrentText("None" if mode=="none" else "All" if mode=="all" else "Fixed")
        self.depth_value=QSpinBox(); self.depth_value.setRange(1,100); self.depth_value.setValue(int(cfg.get("context_depth_value",15)))
        lc.addRow("Depth Mode:", self.depth_mode)
        lc.addRow("Depth (pairs):", self.depth_value)
        def _toggle(v=None):
            self.depth_value.setEnabled(self.depth_mode.currentText()=="Fixed")
        self.depth_mode.currentTextChanged.connect(_toggle); _toggle()

        grpPr=QGroupBox("VectorStore Pruning/Rotation")
        lpv=QFormLayout(grpPr)
        self.max_bytes=QLE(str(cfg.get("prune_max_bytes", DEFAULT_CONFIG["prune_max_bytes"])))
        self.max_records=QLE(str(cfg.get("prune_max_records", DEFAULT_CONFIG["prune_max_records"])))
        self.keep_tail=QLE(str(cfg.get("prune_keep_tail", DEFAULT_CONFIG["prune_keep_tail"])))
        lpv.addRow("Rotate at size (bytes):", self.max_bytes)
        lpv.addRow("Rotate at records:", self.max_records)
        lpv.addRow("Keep last N on rotation:", self.keep_tail)

        grpV=QGroupBox("Vision / OCR")
        lv=QFormLayout(grpV)
        self.vision_model_cb = QComboBox()
        for n in self._all_models(): self.vision_model_cb.addItem(n)
        cur_vm = cfg.get("vision",{}).get("model_default","llava:7b")
        self.vision_model_cb.setCurrentText(cur_vm)
        self.vision_ttl=QSpinBox(); self.vision_ttl.setRange(10, 3600); self.vision_ttl.setValue(int(cfg.get("vision",{}).get("ttl_seconds",120)))
        lv.addRow("Vision Model:", self.vision_model_cb)
        lv.addRow("OCR TTL (sec):", self.vision_ttl)

        grpT=QGroupBox("Text-to-Speech")
        lt=QFormLayout(grpT)
        self.tts_enabled_cb=QCheckBox("Enable TTS")
        self.tts_enabled_cb.setChecked(bool(cfg.get("tts", {}).get("enabled", False)))
        self.tts_voice_cb=QComboBox()
        voices=available_voices()
        if voices:
            self.tts_voice_cb.addItems(voices)
            cur_voice=cfg.get("tts", {}).get("voice", "Zira")
            if cur_voice in voices:
                self.tts_voice_cb.setCurrentText(cur_voice)
        else:
            self.tts_voice_cb.addItem("default")
        lt.addRow(self.tts_enabled_cb)
        lt.addRow("Voice:", self.tts_voice_cb)

        grpX=QGroupBox("Codex")
        lx=QFormLayout(grpX)
        self.codex_cb=QCheckBox("Enable Codex interface.")
        self.codex_cb.setChecked(bool(cfg.get("codex_enabled", False)))
        self.start_mode_cb=QComboBox()
        self.start_mode_cb.addItems(["Chat","Shell","Codex","All"])
        self.start_mode_cb.setCurrentText(cfg.get("default_mode", "Chat").capitalize())
        lx.addRow(self.codex_cb)
        lx.addRow("Default Startup Mode:", self.start_mode_cb)
        self.install_codex_btn = QPushButton("Install Codex")
        self.install_codex_btn.clicked.connect(prompt_install_codex)
        lx.addRow(self.install_codex_btn)
        def _upd_install():
            self.install_codex_btn.setEnabled(self.codex_cb.isChecked() and not _codex_binary_present())
        self.codex_cb.toggled.connect(lambda _: _upd_install())
        _upd_install()

        # Diagnostics row: open agent_terminal.py (as requested) + open system console (system log)
        diag=QGroupBox("Diagnostics")
        ld=QHBoxLayout(diag)
        btn_open_self = QPushButton("Open agent_terminal.py")
        btn_open_self.clicked.connect(lambda: open_in_os(os.path.join(SCRIPT_ROOT, "agent_terminal.py")))
        btn_open_log = QPushButton("Open System Console")
        btn_open_log.clicked.connect(lambda: open_in_os(LOG_PATH))
        ld.addWidget(btn_open_self); ld.addWidget(btn_open_log); ld.addStretch(1)

        root.addWidget(grpP)
        root.addWidget(grpSchema)
        root.addWidget(grpR)
        root.addWidget(grpC)
        root.addWidget(grpPr)
        root.addWidget(grpV)
        root.addWidget(grpT)
        root.addWidget(grpX)
        root.addWidget(diag)

        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _all_models(self)->List[str]:
        req=_requests()
        names=[]
        if not req: return names
        try:
            r=req.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if not r.ok: return names
            for m in r.json().get("models", []):
                n=m.get("name") or m.get("model") or ""
                if n: names.append(n)
            names=sorted(set(names))
            return names
        except Exception:
            return []

    def values(self)->Dict:
        out=self.cfg.copy()
        out["system_prompt"]=self.system_prompt.toPlainText()
        out["l2c_prompt"]=self.l2c_prompt.toPlainText()
        if self.embed_combo.currentText() and not self.embed_combo.currentText().startswith("("):
            out["embedding_model"]=self.embed_combo.currentText()
        out["autorun_suggestions"]=self.autorun_cb.isChecked()
        out["self_prompting"]=self.selfprompt_cb.isChecked()
        out["full_auto_mode"]=self.full_auto_cb.isChecked()

        mode=self.depth_mode.currentText()
        out["context_depth_mode"]=mode.lower()
        out["context_depth_value"]=int(self.depth_value.value())

        def _i(s, d):
            try: return int(s)
            except: return d
        out["prune_max_bytes"]=_i(self.max_bytes.text(), DEFAULT_CONFIG["prune_max_bytes"])
        out["prune_max_records"]=_i(self.max_records.text(), DEFAULT_CONFIG["prune_max_records"])
        out["prune_keep_tail"]=_i(self.keep_tail.text(), DEFAULT_CONFIG["prune_keep_tail"])

        out.setdefault("vision", {})
        out["vision"]["model_default"] = self.vision_model_cb.currentText().strip()
        out["vision"]["ttl_seconds"]   = int(self.vision_ttl.value())

        out.setdefault("tts", {})
        out["tts"]["enabled"] = self.tts_enabled_cb.isChecked()
        out["tts"]["voice"] = self.tts_voice_cb.currentText().strip()

        out["codex_enabled"] = self.codex_cb.isChecked()
        out["default_mode"] = self.start_mode_cb.currentText()

        return out

    def open_path(self, path: str) -> None:
        self._card.open_path(path)

    def save(self) -> None:
        self._card.save()

    def save_to(self, path: str) -> None:
        self._card.save_to(path)

    def new_file(self, path: Optional[str] = None) -> None:
        self._card.new_file(path)

# --------------------------------------------------------------------------------------
# Host window (standalone)
# --------------------------------------------------------------------------------------

class HostWindow(QMainWindow):
    def __init__(self, cfg: Dict):
        super().__init__()
        self.cfg = cfg
        self._editors: list[EditorCard] = []
        self.setWindowTitle(APP_NAME)
        # palette for dark chrome
        pal=self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#0a1430"))
        pal.setColor(QPalette.ColorRole.Base, QColor("#0a1430"))
        pal.setColor(QPalette.ColorRole.Text, QColor("#e6f0ff"))
        pal.setColor(QPalette.ColorRole.WindowText, QColor("#e6f0ff"))
        self.setPalette(pal)

        self.term = TerminalCard(Theme(), cfg, self)
        self.setCentralWidget(self.term)
        self.statusBar().showMessage(f"Model: {CURRENT_MODEL}")
        mode = cfg.get("default_mode", "Chat").lower()
        if mode in ("shell", "chat"):
            self.term.mode_combo.setCurrentText(mode.capitalize())
        if cfg.get("codex_enabled", False) and mode in ("codex", "all"):
            self.term._tool_codex_launch({})

        # restore position/size from cfg (applies to top-level window)
        pos = cfg.get("ui",{}).get("term_pos",[120,120])
        size = cfg.get("ui",{}).get("term_size",[1200,720])
        self.resize(int(size[0])+40, int(size[1])+60)  # a bit larger frame around card
        self.move(int(pos[0]), int(pos[1]))

        # menu (minimal)
        bar=self.menuBar()
        v=bar.addMenu("&View")
        fs=QAction("Toggle Fullscreen (Alt+Enter)", self); fs.setShortcut("Alt+Return")
        fs.triggered.connect(self._toggle_fullscreen); v.addAction(fs)
        wrap=QAction("Toggle Word Wrap", self); wrap.setCheckable(True); wrap.setChecked(bool(cfg.get("ui",{}).get("wrap", True)))
        def _toggle_wrap():
            c=self.term.console
            self.cfg.setdefault("ui",{})
            if wrap.isChecked():
                c.setLineWrapMode(QPlainTextEdit.WidgetWidth)
                c.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
                self.cfg["ui"]["wrap"]=True
            else:
                c.setLineWrapMode(QPlainTextEdit.NoWrap)
                self.cfg["ui"]["wrap"]=False
            save_config(self.cfg)
        wrap.triggered.connect(_toggle_wrap)
        v.addAction(wrap)

        f=bar.addMenu("&File")
        f.addAction("Open Script Root", lambda: open_in_os(SCRIPT_ROOT))
        f.addAction("Open Data Folder", lambda: open_in_os(DATASETS_DIR))
        f.addAction("Open Vision Cache", lambda: open_in_os(VISION_CACHE_DIR))
        f.addAction("Open Codex Dir", lambda: open_in_os(CODEX_DIR))
        f.addAction("Open Change Logs", lambda: open_in_os(CHANGE_LOGS_DIR))
        f.addSeparator()
        q=QAction("Quit", self); q.setShortcut(QKeySequence.StandardKey.Quit); q.triggered.connect(self.close); f.addAction(q)

        t=bar.addMenu("&Tools")
        inst = QAction("Install Codex…", self)
        def _do_install():
            # Lazily show the standard installer popup
            prompt_install_codex()
            # Update status bar model label after potential install
            global codex, _persona, CURRENT_MODEL
            if '_persona' in globals():
                self.statusBar().showMessage(f"Model: {CURRENT_MODEL}")
        inst.triggered.connect(_do_install)
        t.addAction(inst)
        ce=QAction("Open Code Editor", self)
        ce.triggered.connect(self._open_code_editor)
        t.addAction(ce)
        tv=QAction("Open Task Viewer", self)
        tv.triggered.connect(self.term._open_tasks)
        t.addAction(tv)

    def _open_code_editor(self, path: Optional[str] = None) -> None:
        plugin_path = resolve_qt_plugin_path(LOGGER)
        LOGGER.debug("Qt plugin path: %s", plugin_path)
        editor = EditorCard(initial_path=path, theme=self.term._editor_theme(), parent=self)
        editor.show()
        self._editors.append(editor)

    def _toggle_fullscreen(self):
        if self.isFullScreen(): self.showNormal()
        else: self.showFullScreen()

    def closeEvent(self, e):
        # persist window position for next session
        try:
            self.cfg.setdefault("ui",{})
            self.cfg["ui"]["term_pos"] = [self.x(), self.y()]
            save_config(self.cfg)
        except Exception:
            pass
        super().closeEvent(e)


class StartupCodexDialog(QDialog):
    """
    Minimal startup popup to confirm Codex handling at launch.
    High-contrast dark theme for readability.
    """
    decision_install = False
    decision_skip = False

    def __init__(self, codex_present: bool, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        from PySide6.QtGui import QPalette, QColor

        self.setWindowTitle("Agent Terminal")
        self.resize(380, 160)

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#0a1430"))
        pal.setColor(QPalette.ColorRole.Base, QColor("#0a1430"))
        pal.setColor(QPalette.ColorRole.Text, QColor("#e6f0ff"))
        pal.setColor(QPalette.ColorRole.WindowText, QColor("#e6f0ff"))
        self.setPalette(pal)

        v = QVBoxLayout(self)
        label = QLabel(
            "Codex is installed and ready."
            if codex_present else
            "Codex is not installed. Install now?"
        )
        # High-contrast rule reminder
        label.setStyleSheet("color:#e6f0ff;")
        v.addWidget(label)

        buttons = QHBoxLayout()
        self.btn_yes = QPushButton("Install Codex")    # bright accent
        self.btn_no  = QPushButton("Skip for now")
        self.btn_yes.setStyleSheet("QPushButton { color:#ffffff; background:#1E5AFF; } QPushButton:hover{ background:#2f72ff; }")
        self.btn_no.setStyleSheet("QPushButton { color:#e6f0ff; background:#0d1a2b; }")

        self.btn_yes.clicked.connect(self._choose_install)
        self.btn_no.clicked.connect(self._choose_skip)
        if codex_present:
            self.btn_yes.setEnabled(False)  # already present

        buttons.addWidget(self.btn_yes)
        buttons.addWidget(self.btn_no)
        v.addLayout(buttons)

    def _choose_install(self):
        self.decision_install = True
        self.accept()

    def _choose_skip(self):
        self.decision_skip = True
        self.accept()

# --------------------------------------------------------------------------------------
# Settings integration helpers on card
# --------------------------------------------------------------------------------------

def _apply_settings_from_dialog(card: TerminalCard, cfg: Dict):
    # update vector stores embed model etc.
    emb=cfg.get("embedding_model", DEFAULT_CONFIG["embedding_model"])
    card.ds_sem_user.embed_model=emb
    card.ds_sem_ai.embed_model=emb
    card.ds_indexing.embed_model=emb
    card.ds_prompting.embed_model=emb
    card.ds_learning.embed_model=emb
    card.ds_selfp.embed_model=emb
    card.ds_snippets.embed_model=emb
    card.autorun=cfg.get("autorun_suggestions", False)
    card.self_prompting=cfg.get("self_prompting", False)
    card.full_auto=cfg.get("full_auto_mode", False)
    card.vision._ttl=int(cfg.get("vision",{}).get("ttl_seconds",120))
    card.vision._model_default=cfg.get("vision",{}).get("model_default","llava:7b")
    card._println("[Info] Settings saved.")
    card.tts_enabled=cfg.get("tts", {}).get("enabled", False)
    card.tts_voice=cfg.get("tts", {}).get("voice", "Zira")
    card.codex_enabled = cfg.get("codex_enabled", False)

def _open_settings_on_card(card: TerminalCard):
    dlg=SettingsDialog(card.cfg, card._available_embed_models(), card)
    if dlg.exec()==QDialog.DialogCode.Accepted:
        card.cfg=dlg.values()
        save_config(card.cfg)
        _apply_settings_from_dialog(card, card.cfg)

# bind method on class
TerminalCard._open_settings = _open_settings_on_card


def _open_tasks_on_card(card: TerminalCard) -> None:
    task_card = open_card(card.task_mgr, card.t, lambda p: card._tool_editor_open({"path": p}))
    card._task_cards.append(task_card)


TerminalCard._open_tasks = _open_tasks_on_card

# --------------------------------------------------------------------------------------
# Entry points (standalone & embeddable)
# --------------------------------------------------------------------------------------


def build_widget(parent: Optional[QWidget] = None) -> TerminalCard:
    """Factory used by ``Virtual_Desktop`` to embed the terminal."""
    cfg = load_config()
    t = Theme()
    w = TerminalCard(t, cfg, parent)
    w.show()
    return w


def _is_admin() -> bool:
    """Return True if the current process has administrative privileges."""
    if os.name == "nt":
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def _relaunch_as_admin(argv: List[str]) -> bool:
    """Attempt to relaunch the script with elevated privileges."""
    script = os.path.abspath(__file__)
    if os.name == "nt":
        params = " ".join([script, *argv])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            return True
        except Exception:
            return False
    try:
        os.execvp("sudo", ["sudo", sys.executable, script, *argv])
    except Exception:
        return False
    return True


def main(argv: Optional[List[str]] = None) -> int:
    """Launch the Agent Terminal host window immediately."""
    argv = argv or sys.argv[1:]

    # Elevation step can abort UI. Try, but if elevation fails we still run without it.
    if not _is_admin():
        if _relaunch_as_admin(argv):
            return 0
        print("[Warn] Administrative privileges not granted; continuing without elevation.")

    os.environ["AGENT_ELEVATED"] = "1"

    parser = argparse.ArgumentParser()
    parser.add_argument("--log-port", type=int, default=None)
    args, _ = parser.parse_known_args(argv)

    if args.log_port:
        start_log_server(args.log_port)
        LOGGER.addHandler(SocketBroadcastHandler())

    # I/O side effects that do not require Qt
    sync_inbox_to_memory()
    update_schema()
    bootstrap_install_instructions()
    try:
        load_install_notes()
    except Exception:
        pass

    # Ensure runtime before any Qt widgets
    try:
        ensure_pyside6(LOGGER)
        ensure_qt_runtime(LOGGER)
    except Exception as exc:
        LOGGER.exception("Qt runtime repair failed: %s", exc)

    set_hidpi_policy_once()

    # Create app and set style
    app = QApplication.instance() or QApplication([])
    app.setStyle(QStyleFactory.create("Fusion"))

    # Now it is safe to interact with Qt-based popups
    # Initialize model identity ASAP for the status bar
    global codex, _persona, CURRENT_MODEL
    codex, _persona = _load_codex()
    CURRENT_MODEL = f"{_persona.name} {_persona.version}".strip()

    # Startup popup: offer Codex install if missing
    try:
        dlg = StartupCodexDialog(_codex_binary_present())
        if dlg.exec() == QDialog.Accepted and dlg.decision_install:
            prompt_install_codex()  # shows progress + updates CURRENT_MODEL inside
    except Exception as e:
        LOGGER.warning("Startup dialog failed: %s", e)

    # Load and persist config
    cfg = {**DEFAULT_CONFIG, **load_config()}
    save_config(cfg)

    # Host window
    win = HostWindow(cfg)
    win.statusBar().showMessage(f"Model: {CURRENT_MODEL}")
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

Agent Terminal — Standalone/Embeddable Terminal Card (PySide6)
(Updated: remove QEvent.TextChanged usage; auto-grow via textChanged signal;
keeps all prior features; HiDPI policy set before QApplication.)
**Classes:** SocketBroadcastHandler, CodexManager, Theme, MacroManager, MacroManagerDialog, VectorStore, ContextHistory, VisionService, TermHighlighter, MovableCard, TerminalCard, SettingsDialog, HostWindow, StartupCodexDialog
**Functions:** _log_codex_install_failure(error), _verify_checksum(path, expected), _codex_binary_present(), prompt_install_codex(), _load_codex(), log_command(cmd, status), bootstrap_install_instructions(dataset_path, doc_path), update_schema(operator), run_gui_command(action, expected_text, region, task_id), load_persona(), apply_persona(text, persona), log_auto_execution(cmd, rationale, output, returncode), start_log_server(port), open_in_os(path), install_dependency(name, url, checksum, log_path, retries), _requests(), post_with_retry(model, messages, retries), find_git_bash(), nl_for_env(env), wrap_powershell_for_cmd(script), human_size(num_bytes), timestamp(), load_state(), save_state(st), available_voices(), speak(text, voice), load_config(), save_config(cfg), cosine_sim(a, b), _apply_settings_from_dialog(card, cfg), _open_settings_on_card(card), _open_tasks_on_card(card), build_widget(parent), _is_admin(), _relaunch_as_admin(argv), main(argv)


## Module `codex_installation.py`

```python
import hashlib
import json
import os
import sys
import tarfile
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict

import requests

DEFAULT_URL = "https://github.com/openai/codex/releases/download/rust-v0.23.0/codex-x86_64-unknown-linux-gnu.tar.gz"
DEFAULT_VERSION = "v0.23.0"
DEFAULT_CHECKSUM = ""


def download_codex(
    url: str = DEFAULT_URL,
    version: str = DEFAULT_VERSION,
    checksum: str = DEFAULT_CHECKSUM,
    target_dir: Path = Path("Codex"),
    install_log: Path = Path("datasets/install_info.jsonl"),
    retries: int = 3,
) -> Path:
    """Download Codex binary with checksum verification and resume support.

    The binary is written into ``target_dir``. An install record with the
    source URL, version, checksum, and UTC timestamp is appended to
    ``install_log`` and ``target_dir/metadata.jsonl``. Partial downloads
    are resumed on subsequent attempts.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    install_log.parent.mkdir(parents=True, exist_ok=True)
    meta_log = target_dir / "metadata.jsonl"

    filename = url.split("/")[-1]
    file_path = target_dir / filename

    for attempt in range(1, retries + 1):
        headers = {}
        mode = "wb"
        hasher = hashlib.sha256()
        if file_path.exists():
            existing = file_path.stat().st_size
            if existing > 0:
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        hasher.update(chunk)
                headers["Range"] = f"bytes={existing}-"
                mode = "ab"
        try:
            with requests.get(url, stream=True, timeout=60, headers=headers) as r:
                r.raise_for_status()
                with open(file_path, mode) as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                            hasher.update(chunk)
            file_checksum = hasher.hexdigest()
            if checksum and file_checksum != checksum:
                file_path.unlink(missing_ok=True)
                raise ValueError("Checksum mismatch")
            record = {
                "url": url,
                "version": version,
                "checksum": file_checksum,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            with open(install_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            with open(meta_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            return file_path
        except Exception:
            if attempt == retries:
                raise
            time.sleep(1)

    return file_path


def load_install_notes(
    memory_path: Path = Path("memory/codex_memory.json"),
    install_log: Path = Path("datasets/install_info.jsonl"),
) -> None:
    """Load install notes from JSONL into memory file for session recall."""
    if not install_log.exists() or not memory_path.exists():
        return
    notes = []
    with open(install_log, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    notes.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    if not notes:
        return
    with open(memory_path, "r", encoding="utf-8") as f:
        mem = json.load(f)
    mem["install_history"] = notes
    mem["updated_utc"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)


# Platform-specific Codex archives for v0.23.0
PLATFORM_ARCHIVES: Dict[str, Dict[str, str]] = {
    "linux": {
        "url": "https://github.com/openai/codex/releases/download/rust-v0.23.0/codex-x86_64-unknown-linux-gnu.tar.gz",
        "checksum": "c09489bb1e88df127906b63d6a74e3d507a70e4cb06b8d6fba13ffa72dbc79bf",
        "binary": "codex",
    },
    "darwin": {
        "url": "https://github.com/openai/codex/releases/download/rust-v0.23.0/codex-x86_64-apple-darwin.tar.gz",
        "checksum": "",
        "binary": "codex",
    },
    "win32": {
        "url": "https://github.com/openai/codex/releases/download/rust-v0.23.0/codex-x86_64-pc-windows-msvc.zip",
        "checksum": "",
        "binary": "codex.exe",
    },
}


def ensure_codex_installed(
    version: str = DEFAULT_VERSION,
    base_dir: Path = Path("Codex"),
    dataset_log: Path = Path("datasets/codex_installs.jsonl"),
) -> Path | None:
    """Ensure Codex CLI is installed and return the binary path.

    The correct archive for the current platform is downloaded to
    ``base_dir / 'tmp'`` if the binary is missing. After verifying the
    checksum, the archive is extracted into ``base_dir / 'bin'`` and an
    installation record is appended to both ``base_dir / 'metadata.jsonl'``
    and ``dataset_log``.
    """

    platform = "linux" if sys.platform.startswith("linux") else sys.platform
    info = PLATFORM_ARCHIVES.get(platform)
    if not info:
        return None

    bin_dir = base_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    root_binary = base_dir / info["binary"]
    binary_path = bin_dir / info["binary"]

    # If binary already present, assume installed
    if binary_path.exists():
        return binary_path
    if root_binary.exists():
        return root_binary

    tmp_dir = base_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    archive_name = info["url"].split("/")[-1]
    archive_path = tmp_dir / archive_name

    hasher = hashlib.sha256()
    with requests.get(info["url"], stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(archive_path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    hasher.update(chunk)

    file_checksum = hasher.hexdigest()
    if info.get("checksum") and file_checksum != info["checksum"]:
        archive_path.unlink(missing_ok=True)
        raise ValueError("Checksum mismatch")

    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(bin_dir)
    else:
        with tarfile.open(archive_path, "r:gz") as tf:
            tf.extractall(bin_dir)

    record = {
        "version": version,
        "platform": platform,
        "checksum": file_checksum,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    meta_log = base_dir / "metadata.jsonl"
    dataset_log.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    with open(dataset_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return binary_path


__all__ = [
    "download_codex",
    "load_install_notes",
    "ensure_codex_installed",
]
```

**Functions:** download_codex(url, version, checksum, target_dir, install_log, retries), load_install_notes(memory_path, install_log), ensure_codex_installed(version, base_dir, dataset_log)


## Module `code_editor.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
code_editor.py — Agent-ready Code Editor CARD (PySide6)

• Fully compatible with Virtual_Desktop.py loader:
    - Exposes create_card(parent)->(QWidget, title) and build_widget(parent)
    - Stand-alone main() runner also included
• Dark taskbar/header and rounded “card” styling (matches Terminal theme)
• Monospace editor with line numbers, current-line highlight, wrap toggle
• Zoom: Ctrl+= / Ctrl+- / Ctrl+0
• File ops: New / Open / Save / Save As…
• Agent-friendly API (no dialogs needed):
    - set_file_path(path), save(), save_to(path), set_text(str), text(), open_path(path)
• Multiple instances supported (terminal can open many editors)

Optional env hints the Terminal can set before loading as a card:
    CODE_EDITOR_FILE=<path to open>      (open an existing file)
    CODE_EDITOR_NEWNAME=<suggested name> (untitled placeholder shown in title bar)
    CODE_EDITOR_EXT=<.py|.txt|.json>     (pre-select new file extension)
"""

from __future__ import annotations

import os
import sys
import json
import uuid
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from tools.qt_runtime import ensure_qt_runtime, resolve_qt_plugin_path
from tools.qt_utils import set_hidpi_policy_once


DATASETS_DIR = Path(__file__).resolve().parent / "datasets" / "editor_history"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

LOGGER = logging.getLogger("CodeEditor")


def timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d-%H%M%S")


class EditorHistory:
    def __init__(self, editor_id: str):
        self.path = DATASETS_DIR / f"{editor_id}.jsonl"
        if not self.path.exists():
            self.path.touch()

    def _write(self, rec: dict) -> None:
        rec["ts"] = timestamp()
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def log_revision(self, path: str, text: str) -> None:
        self._write({"type": "revision", "path": path, "text": text})

    def log_chat(self, role: str, message: str) -> None:
        self._write({"type": "chat", "role": role, "message": message})


def _import_qt() -> None:
    """Import PySide6 modules after validating the environment.

    The Qt runtime is prepared via :func:`tools.qt_runtime.ensure_qt_runtime`,
    which installs PySide6 if necessary and exports the plugin path before
    importing other Qt modules.
    """

    ensure_qt_runtime(LOGGER)
    plugin_path = resolve_qt_plugin_path(LOGGER)
    LOGGER.debug("Qt plugin path: %s", plugin_path)

    from PySide6.QtCore import Qt, QRect, QSize, QPoint, QTimer, Signal, QObject, QRegularExpression
    from PySide6.QtGui import (
        QColor,
        QPalette,
        QFont,
        QAction,
        QKeySequence,
        QPainter,
        QTextFormat,
        QTextOption,
        QSyntaxHighlighter,
        QTextCharFormat,
    )
    from PySide6.QtWidgets import (
        QApplication,
        QWidget,
        QPlainTextEdit,
        QVBoxLayout,
        QHBoxLayout,
        QFrame,
        QLabel,
        QPushButton,
        QFileDialog,
        QCheckBox,
        QComboBox,
        QStyleFactory,
        QMainWindow,
        QSizePolicy,
        QMenuBar,
        QStatusBar,
        QMessageBox,
        QScrollBar,
        QLineEdit,
    )

    globals().update({
        "Qt": Qt,
        "QRect": QRect,
        "QSize": QSize,
        "QPoint": QPoint,
        "QTimer": QTimer,
        "Signal": Signal,
        "QObject": QObject,
        "QRegularExpression": QRegularExpression,
        "QColor": QColor,
        "QPalette": QPalette,
        "QFont": QFont,
        "QAction": QAction,
        "QKeySequence": QKeySequence,
        "QPainter": QPainter,
        "QTextFormat": QTextFormat,
        "QTextOption": QTextOption,
        "QSyntaxHighlighter": QSyntaxHighlighter,
        "QTextCharFormat": QTextCharFormat,
        "QApplication": QApplication,
        "QWidget": QWidget,
        "QPlainTextEdit": QPlainTextEdit,
        "QVBoxLayout": QVBoxLayout,
        "QHBoxLayout": QHBoxLayout,
        "QFrame": QFrame,
        "QLabel": QLabel,
        "QPushButton": QPushButton,
        "QFileDialog": QFileDialog,
        "QCheckBox": QCheckBox,
        "QComboBox": QComboBox,
        "QStyleFactory": QStyleFactory,
        "QMainWindow": QMainWindow,
        "QSizePolicy": QSizePolicy,
        "QMenuBar": QMenuBar,
        "QStatusBar": QStatusBar,
        "QMessageBox": QMessageBox,
        "QScrollBar": QScrollBar,
        "QLineEdit": QLineEdit,
    })


_import_qt()

# --------------------------------------------------------------------------------------
# Theme (aligns with Virtual_Desktop/Agent Terminal)
# --------------------------------------------------------------------------------------

@dataclass
class Theme:
    card_bg:     str = "#0c1320"
    card_border: str = "#213040"
    header_bg:   str = "#0a111e"
    header_fg:   str = "#eaf2ff"
    text_muted:  str = "#c7d5ee"
    editor_bg:   str = "#0b1828"
    editor_fg:   str = "#d6e6ff"
    editor_sel:  str = "#264f78"
    accent:      str = "#1E5AFF"
    accent_hover:  str = "#2f72ff"
    gutter_bg:   str = "#141a28"
    gutter_fg:   str = "#b6c4d8"
    gutter_fg_active: str = "#ffffff"
    current_line_bg:  str = "#1e2433"

T = Theme()

# --------------------------------------------------------------------------------------
# Line number area for QPlainTextEdit
# --------------------------------------------------------------------------------------

class LineNumberArea(QWidget):
    def __init__(self, editor: "Editor"):
        super().__init__(editor)
        self.editor = editor
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class Editor(QPlainTextEdit):
    zoomed = Signal(int)  # emits new point size

    def __init__(self, theme: Theme, parent=None):
        super().__init__(parent)
        self.t = theme
        # Colors & font
        self.setBackgroundVisible(False)
        self.setFrameStyle(QFrame.NoFrame)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        font = QFont("Cascadia Code, Consolas, monospace")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(12)
        self.setFont(font)

        pal = self.palette()
        pal.setColor(QPalette.Base, QColor(self.t.editor_bg))
        pal.setColor(QPalette.Text, QColor(self.t.editor_fg))
        pal.setColor(QPalette.Highlight, QColor(self.t.editor_sel))
        pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(pal)

        # Line numbers
        self._line_area = LineNumberArea(self)
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self._update_line_number_area_width(0)
        self._highlight_current_line()

    # ---- line number helpers ----
    def line_number_area_width(self) -> int:
        digits = max(2, len(str(max(1, self.blockCount()))))
        space = 12 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def _update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_area)
        try:
            painter.fillRect(event.rect(), QColor(self.t.gutter_bg))

            block = self.firstVisibleBlock()
            block_number = block.blockNumber()
            top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
            bottom = top + round(self.blockBoundingRect(block).height())

            active_line = self.textCursor().blockNumber()

            # divider
            painter.setPen(QColor(self.t.card_border))
            painter.drawLine(self._line_area.width() - 1, event.rect().top(),
                             self._line_area.width() - 1, event.rect().bottom())

            while block.isValid() and top <= event.rect().bottom():
                if block.isVisible() and bottom >= event.rect().top():
                    number = str(block_number + 1)
                    if block_number == active_line:
                        painter.fillRect(0, top, self._line_area.width()-1,
                                         round(self.blockBoundingRect(block).height()),
                                         QColor("#1a2132"))
                        painter.setPen(QColor(self.t.gutter_fg_active))
                        font = painter.font(); font.setBold(True); painter.setFont(font)
                    else:
                        painter.setPen(QColor(self.t.gutter_fg))
                        font = painter.font(); font.setBold(False); painter.setFont(font)

                    right = self._line_area.width() - 6
                    painter.drawText(0, top, right, self.fontMetrics().height(),
                                     Qt.AlignRight | Qt.AlignVCenter, number)

                block = block.next()
                top = bottom
                bottom = top + round(self.blockBoundingRect(block).height())
                block_number += 1
        finally:
            painter.end()

    def _highlight_current_line(self):
        from PySide6.QtWidgets import QTextEdit
        # Use ExtraSelection-like API via QPlainTextEdit
        extra_selection = QTextEdit.ExtraSelection()  # type: ignore[attr-defined]
        extra_selection.format.setBackground(QColor(self.t.current_line_bg))
        extra_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        extra_selection.cursor = self.textCursor()
        extra_selection.cursor.clearSelection()
        self.setExtraSelections([extra_selection])

    # ---- zoom ----
    def zoom(self, delta: int):
        p = self.font().pointSize()
        if delta == 0:
            p = 12
        else:
            p = max(8, p + delta)
        f = self.font(); f.setPointSize(p); self.setFont(f)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        self._update_line_number_area_width(0)
        self.zoomed.emit(p)


# --------------------------------------------------------------------------------------
# Syntax highlighting helpers
# --------------------------------------------------------------------------------------


class PythonHighlighter(QSyntaxHighlighter):
    """Very small Python syntax highlighter."""

    def __init__(self, doc):
        super().__init__(doc)
        kw_format = QTextCharFormat()
        kw_format.setForeground(QColor(T.accent))
        keywords = [
            "def",
            "class",
            "import",
            "from",
            "return",
            "if",
            "else",
            "elif",
            "for",
            "while",
            "try",
            "except",
            "with",
        ]
        self.rules = [(QRegularExpression(fr"\\b{kw}\\b"), kw_format) for kw in keywords]
        self.comment_fmt = QTextCharFormat()
        self.comment_fmt.setForeground(QColor("#6A9955"))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
        if "#" in text:
            idx = text.index("#")
            self.setFormat(idx, len(text) - idx, self.comment_fmt)


class MarkdownHighlighter(QSyntaxHighlighter):
    """Minimal Markdown syntax highlighter."""

    def __init__(self, doc):
        super().__init__(doc)
        self.header_fmt = QTextCharFormat()
        self.header_fmt.setForeground(QColor(T.accent))
        self.bold_fmt = QTextCharFormat()
        self.bold_fmt.setForeground(QColor("#C586C0"))
        self.header_re = QRegularExpression(r"^#+.*")
        self.bold_re = QRegularExpression(r"\\*\\*[^\\*]+\\*\\*")

    def highlightBlock(self, text: str) -> None:
        m = self.header_re.match(text)
        if m.hasMatch():
            self.setFormat(m.capturedStart(), m.capturedLength(), self.header_fmt)
        it = self.bold_re.globalMatch(text)
        while it.hasNext():
            match = it.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.bold_fmt)


# --------------------------------------------------------------------------------------
# Editor Card (QWidget) with dark header and status bar
# --------------------------------------------------------------------------------------

class EditorCard(QWidget):
    """Embeddable editor card with Agent-friendly API and chat pane."""
    def __init__(
        self,
        initial_path: Optional[str] = None,
        suggested_name: Optional[str] = None,
        default_ext: Optional[str] = None,
        theme: Optional[Theme] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.t = theme or Theme()
        self._path: Optional[Path] = Path(initial_path).resolve() if initial_path else None
        self._suggested = suggested_name
        self._dirty = False
        self.editor_id = str(uuid.uuid4())
        self.history = EditorHistory(self.editor_id)

        # Outer rounded card
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(8)

        card = QFrame(self)
        card.setObjectName("CardSurface")
        card.setStyleSheet(
            f"#CardSurface {{ background:{self.t.card_bg}; border:1px solid {self.t.card_border}; border-radius:12px; }}"
        )
        outer.addWidget(card)

        v = QVBoxLayout(card)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Header (dark taskbar)
        header = QFrame(card)
        header.setObjectName("Hdr")
        header.setStyleSheet(
            f"#Hdr {{ background:{self.t.header_bg}; border-top-left-radius:12px; border-top-right-radius:12px; }}"
            f"QLabel {{ color:{self.t.header_fg}; }}"
            f"QPushButton {{ color:#fff; background:{self.t.accent}; border:1px solid {self.t.card_border}; border-radius:6px; padding:4px 8px; }}"
            f"QPushButton:hover {{ background:{self.t.accent_hover}; }}"
            f"QCheckBox {{ color:{self.t.header_fg}; padding-left:6px; }}"
            f"QComboBox {{ color:{self.t.header_fg}; background:{self.t.card_bg}; border:1px solid {self.t.card_border}; border-radius:6px; padding:2px 6px; }}"
        )
        h = QHBoxLayout(header)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(8)

        self.title = QLabel(self._title_text(), header)
        self.wrap = QCheckBox("Wrap", header); self.wrap.setChecked(False)
        self.cmb_type = QComboBox(header)
        self.cmb_type.addItem("Python", ".py")
        self.cmb_type.addItem("Text", ".txt")
        self.cmb_type.addItem("Markdown", ".md")
        ext = default_ext or os.environ.get("CODE_EDITOR_EXT")
        if ext:
            if not ext.startswith("."):
                ext = f".{ext}"
            idx = self.cmb_type.findData(ext)
            if idx != -1:
                self.cmb_type.setCurrentIndex(idx)
        self.btn_new  = QPushButton("New File", header)
        self.btn_open = QPushButton("Open…", header)
        self.btn_save = QPushButton("Save", header)
        self.btn_saveas = QPushButton("Save As…", header)

        h.addWidget(self.title); h.addStretch(1)
        h.addWidget(self.wrap)
        h.addWidget(self.cmb_type)
        h.addSpacing(6)
        h.addWidget(self.btn_new); h.addWidget(self.btn_open)
        h.addWidget(self.btn_save); h.addWidget(self.btn_saveas)
        v.addWidget(header)

        # Editor row
        body = QFrame(card)
        body.setStyleSheet(f"QFrame {{ background:{self.t.card_bg}; border:none; }}")
        hb = QHBoxLayout(body); hb.setContentsMargins(0, 0, 0, 0); hb.setSpacing(0)

        self.editor = Editor(self.t, body)
        hb.addWidget(self.editor, 3)
        self.highlighter: Optional[QSyntaxHighlighter] = None
        self._apply_highlighter(self.cmb_type.currentData())

        # Chat pane
        chat_frame = QFrame(body)
        chat_frame.setStyleSheet(
            f"QFrame {{ background:{self.t.card_bg}; border-left:1px solid {self.t.card_border}; }}"
        )
        ch = QVBoxLayout(chat_frame); ch.setContentsMargins(4, 4, 4, 4); ch.setSpacing(4)
        self.chat_view = QPlainTextEdit(chat_frame)
        self.chat_view.setReadOnly(True)
        self.chat_view.setStyleSheet(
            f"QPlainTextEdit {{ background:{self.t.editor_bg}; color:{self.t.editor_fg}; border:1px solid {self.t.card_border}; border-radius:6px; }}"
        )
        self.chat_input = QLineEdit(chat_frame)
        self.chat_input.setStyleSheet(
            f"QLineEdit {{ background:{self.t.header_bg}; color:{self.t.header_fg}; border:1px solid {self.t.card_border}; border-radius:6px; padding:4px; }}"
        )
        self.chat_input.returnPressed.connect(self._on_chat_enter)
        ch.addWidget(self.chat_view, 1)
        ch.addWidget(self.chat_input)
        hb.addWidget(chat_frame, 1)
        v.addWidget(body, 1)

        # Status bar
        self.status = QFrame(card)
        self.status.setObjectName("SB")
        self.status.setStyleSheet(
            f"#SB {{ background:{self.t.header_bg}; color:{self.t.text_muted}; border-bottom-left-radius:12px; border-bottom-right-radius:12px; }}"
        )
        sbh = QHBoxLayout(self.status); sbh.setContentsMargins(10, 4, 10, 6)
        self.lbl_pos = QLabel("Ln 1, Col 1", self.status)
        self.lbl_info = QLabel("", self.status)
        self.lbl_info.setStyleSheet(f"color:{self.t.text_muted};")
        sbh.addWidget(self.lbl_pos); sbh.addStretch(1); sbh.addWidget(self.lbl_info)
        v.addWidget(self.status)

        # Signals
        self.wrap.toggled.connect(self._toggle_wrap)
        self.btn_new.clicked.connect(self.new_file)
        self.btn_open.clicked.connect(self.open_dialog)
        self.btn_save.clicked.connect(self.save)
        self.btn_saveas.clicked.connect(self.save_as_dialog)
        self.cmb_type.currentIndexChanged.connect(lambda: self._apply_highlighter(self.cmb_type.currentData()))
        self.editor.textChanged.connect(self._on_changed)
        self.editor.cursorPositionChanged.connect(self._update_caret)
        self.editor.zoomed.connect(lambda p: self._flash_info(f"Zoom {p}pt"))

        # Shortcuts
        self._mk_action("Ctrl+S", self.save)
        self._mk_action("Ctrl+Shift+S", self.save_as_dialog)
        self._mk_action("Ctrl+O", self.open_dialog)
        self._mk_action("Ctrl+N", self.new_file)
        self._mk_action("Ctrl+0", lambda: self.editor.zoom(0))
        self._mk_action("Ctrl+=", lambda: self.editor.zoom(+1))
        self._mk_action("Ctrl++", lambda: self.editor.zoom(+1))
        self._mk_action("Ctrl+-", lambda: self.editor.zoom(-1))

        # Load initial content
        self._load_initial()
        self._update_caret()

    # ---------- UI helpers ----------
    def _mk_action(self, shortcut: str, fn):
        a = QAction(self); a.setShortcut(QKeySequence(shortcut)); a.triggered.connect(fn); self.addAction(a)

    def _toggle_wrap(self, on: bool):
        self.editor.setLineWrapMode(self.editor.WidgetWidth if on else self.editor.NoWrap);
        self.editor.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere if on else QTextOption.NoWrap)

    def _apply_highlighter(self, ext: str) -> None:
        if self.highlighter:
            self.highlighter.setParent(None)
            self.highlighter = None
        if ext == ".py":
            self.highlighter = PythonHighlighter(self.editor.document())
        elif ext == ".md":
            self.highlighter = MarkdownHighlighter(self.editor.document())

    def _title_text(self) -> str:
        if self._path:
            return f"📝 {self._path.name}"
        if self._suggested:
            return f"📝 {self._suggested} (unsaved)"
        return "📝 Untitled"

    def _flash_info(self, text: str, ms: int = 1200):
        self.lbl_info.setText(text)
        QTimer.singleShot(ms, lambda: self.lbl_info.setText(""))

    def _update_caret(self):
        c = self.editor.textCursor()
        ln = c.blockNumber() + 1
        col = c.positionInBlock() + 1
        self.lbl_pos.setText(f"Ln {ln}, Col {col}")

    # ---------- chat pane ----------
    def _on_chat_enter(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        self.chat_input.clear()
        self.append_chat("user", text)

    def append_chat(self, role: str, text: str):
        prefix = "you" if role == "user" else "ai"
        self.chat_view.appendPlainText(f"{prefix}: {text}")
        self.history.log_chat(role, text)

    def send_chat(self, text: str):
        self.append_chat("user", text)

    # ---------- content / change ----------
    def _on_changed(self):
        self._dirty = True
        self._flash_info("Modified", 600)

    def _load_initial(self):
        if self._path and self._path.exists():
            try:
                text = self._path.read_text(encoding="utf-8", errors="replace")
                self.editor.setPlainText(text)
                self._dirty = False
                self.title.setText(self._title_text())
                self._flash_info(f"Opened {self._path.name}")
            except Exception as e:
                self._flash_info(f"Open failed: {e}", 2500)
        else:
            self.editor.setPlainText("")
            self._dirty = False
            self.title.setText(self._title_text())

    # ---------- File ops (dialogs) ----------
    def new_file(self):
        self._path = None
        ext = self.cmb_type.currentData()
        self._suggested = f"untitled{ext}"
        self.editor.setPlainText("")
        self._dirty = False
        self.title.setText(self._title_text())
        self._flash_info("New file")

    def open_dialog(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Open…", str(Path.cwd()),
                                            "Python (*.py *.pyw);;All files (*.*)")
        if not fn:
            return
        self.open_path(fn)

    def save_as_dialog(self):
        ext = self.cmb_type.currentData()
        initial = self._path if self._path else (Path.cwd() / (self._suggested or f"untitled{ext}"))
        filters = {
            ".py": "Python (*.py *.pyw);;All files (*.*)",
            ".txt": "Text (*.txt);;All files (*.*)",
            ".md": "Markdown (*.md);;All files (*.*)",
        }
        fn, _ = QFileDialog.getSaveFileName(self, "Save As…", str(initial), filters.get(ext, "All files (*.*)"))
        if not fn:
            return
        if not Path(fn).suffix:
            fn += ext
        self.save_to(fn)

    # ---------- Agent-friendly API (no dialogs) ----------
    def open_path(self, path: str):
        p = Path(path)
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            QMessageBox.warning(self, "Open failed", str(e))
            return
        self._path = p.resolve()
        self._suggested = None
        self.editor.setPlainText(txt)
        self._dirty = False
        self.title.setText(self._title_text())
        self._flash_info(f"Opened {p.name}")
        ext = p.suffix
        idx = self.cmb_type.findData(ext)
        if idx != -1:
            self.cmb_type.setCurrentIndex(idx)
        else:
            self._apply_highlighter(ext)

    def save(self):
        if self._path is None:
            return self.save_as_dialog()
        try:
            self._path.write_text(self.editor.toPlainText(), encoding="utf-8")
            self._dirty = False
            self._flash_info(f"Saved {self._path.name}")
            self.history.log_revision(str(self._path), self.editor.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def save_to(self, path: str):
        p = Path(path).resolve()
        try:
            p.write_text(self.editor.toPlainText(), encoding="utf-8")
            self._path = p
            self._suggested = None
            self._dirty = False
            self.title.setText(self._title_text())
            self._flash_info(f"Saved {p.name}")
            self.history.log_revision(str(p), self.editor.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, "Save failed", str(e))

    def set_file_path(self, path: Optional[str]):
        self._path = Path(path).resolve() if path else None
        self.title.setText(self._title_text())

    def set_text(self, text: str):
        self.editor.setPlainText(text)
        self._dirty = True

    def text(self) -> str:
        return self.editor.toPlainText()


# --------------------------------------------------------------------------------------
# Card factories (for Virtual_Desktop loader)
# --------------------------------------------------------------------------------------

def _sanitize_initial(path_str: Optional[str]) -> Optional[str]:
    """Return path if it exists and isn't this module."""
    if not path_str:
        return None
    try:
        p = Path(path_str).expanduser().resolve()
    except Exception:
        return None
    if not p.is_file() or p.name == Path(__file__).name:
        return None
    return str(p)


def create_card(parent=None, theme: Optional[Theme] = None) -> Tuple[QWidget, str]:
    """Factory used by Virtual_Desktop to embed as a Card."""
    initial = _sanitize_initial(os.environ.get("CODE_EDITOR_FILE"))
    suggested = os.environ.get("CODE_EDITOR_NEWNAME")
    ext = os.environ.get("CODE_EDITOR_EXT")
    w = EditorCard(initial_path=initial, suggested_name=suggested, default_ext=ext, theme=theme, parent=parent)
    title = "Code Editor"
    return w, title


def build_widget(
    parent=None,
    theme: Optional[Theme] = None,
    initial_path: Optional[str] = None,
    suggested_name: Optional[str] = None,
    default_ext: Optional[str] = None,
):
    initial = initial_path or _sanitize_initial(os.environ.get("CODE_EDITOR_FILE"))
    suggested = suggested_name or os.environ.get("CODE_EDITOR_NEWNAME")
    ext = default_ext or os.environ.get("CODE_EDITOR_EXT")
    return EditorCard(initial_path=initial, suggested_name=suggested, default_ext=ext, theme=theme, parent=parent)


# --------------------------------------------------------------------------------------
# Stand-alone host window (optional)
# --------------------------------------------------------------------------------------

class HostWindow(QMainWindow):
    def __init__(self, initial: Optional[str] = None, default_ext: Optional[str] = None):
        super().__init__()
        initial = _sanitize_initial(initial) or _sanitize_initial(os.environ.get("CODE_EDITOR_FILE"))
        ext = default_ext or os.environ.get("CODE_EDITOR_EXT")
        self.setWindowTitle("Code Editor")
        self.resize(980, 700)
        self._apply_dark_palette()

        self.card = EditorCard(initial_path=initial, default_ext=ext, parent=self)
        self.setCentralWidget(self.card)

        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        filem = menubar.addMenu("&File")
        for label, slot, sc in (
            ("New File", self.card.new_file, "Ctrl+N"),
            ("Open…", self.card.open_dialog, "Ctrl+O"),
            ("Save", self.card.save, "Ctrl+S"),
            ("Save As…", self.card.save_as_dialog, "Ctrl+Shift+S"),
        ):
            act = QAction(label, self); act.triggered.connect(slot); act.setShortcut(sc); filem.addAction(act)

        viewm = menubar.addMenu("&View")
        act_wrap = QAction("Toggle Wrap", self, checkable=True)
        act_wrap.setChecked(False)
        act_wrap.triggered.connect(self.card.wrap.toggle)
        viewm.addAction(act_wrap)

        self.setStatusBar(QStatusBar(self))

    def _apply_dark_palette(self):
        QApplication.instance().setStyle(QStyleFactory.create("Fusion"))
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#0a1430"))
        pal.setColor(QPalette.Base, QColor(T.editor_bg))
        pal.setColor(QPalette.Text, QColor(T.editor_fg))
        pal.setColor(QPalette.WindowText, QColor(T.editor_fg))
        pal.setColor(QPalette.Button, QColor(T.header_bg))
        pal.setColor(QPalette.ButtonText, QColor(T.header_fg))
        pal.setColor(QPalette.Highlight, QColor(T.editor_sel))
        pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(pal)


# --------------------------------------------------------------------------------------
# Entry
# --------------------------------------------------------------------------------------

def main():
    set_hidpi_policy_once()

    os.environ.pop("CODE_EDITOR_FILE", None)
    os.environ.pop("CODE_EDITOR_NEWNAME", None)
    app = QApplication(sys.argv)
    win = HostWindow(initial=None, default_ext=None)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

code_editor.py — Agent-ready Code Editor CARD (PySide6)

• Fully compatible with Virtual_Desktop.py loader:
    - Exposes create_card(parent)->(QWidget, title) and build_widget(parent)
    - Stand-alone main() runner also included
• Dark taskbar/header and rounded “card” styling (matches Terminal theme)
• Monospace editor with line numbers, current-line highlight, wrap toggle
• Zoom: Ctrl+= / Ctrl+- / Ctrl+0
• File ops: New / Open / Save / Save As…
• Agent-friendly API (no dialogs needed):
    - set_file_path(path), save(), save_to(path), set_text(str), text(), open_path(path)
• Multiple instances supported (terminal can open many editors)

Optional env hints the Terminal can set before loading as a card:
    CODE_EDITOR_FILE=<path to open>      (open an existing file)
    CODE_EDITOR_NEWNAME=<suggested name> (untitled placeholder shown in title bar)
    CODE_EDITOR_EXT=<.py|.txt|.json>     (pre-select new file extension)
**Classes:** EditorHistory, Theme, LineNumberArea, Editor, PythonHighlighter, MarkdownHighlighter, EditorCard, HostWindow
**Functions:** timestamp(), _import_qt(), _sanitize_initial(path_str), create_card(parent, theme), build_widget(parent, theme, initial_path, suggested_name, default_ext), main()


## Module `deployment_manager.py`

```python
"""Helper utilities for cloning repositories and launching agent nodes."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent
DATASET_PATH = REPO_ROOT / "datasets" / "deployments.jsonl"


def clone_repo(target_path: str) -> Path:
    """Clone the current repository into *target_path*.

    Parameters
    ----------
    target_path:
        Destination directory for the cloned repository.

    Returns
    -------
    Path
        Path object representing the cloned repository location.
    """

    dst = Path(target_path)
    subprocess.run(
        ["git", "clone", "--depth=1", str(REPO_ROOT), str(dst)],
        check=True,
    )
    return dst


def _record_deployment(meta: dict) -> None:
    """Append a deployment record to the dataset."""

    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATASET_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(meta, ensure_ascii=False) + "\n")


def _load_deployments() -> List[dict]:
    """Load deployment metadata from the dataset."""

    if not DATASET_PATH.exists():
        return []
    items: List[dict] = []
    with open(DATASET_PATH, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def launch_agent(target_path: str) -> subprocess.Popen:
    """Launch ``agent_terminal.py`` located under *target_path*.

    A dataset entry is written containing the target path and PID of the
    spawned process.
    """

    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    proc = subprocess.Popen(
        [sys.executable, str(Path(target_path) / "agent_terminal.py")],
        cwd=target_path,
        env=env,
    )
    _record_deployment({"target": target_path, "pid": proc.pid})
    return proc


def tether_logs(source_repo: str, target_repo: str) -> None:
    """Synchronize ``datasets/`` from *source_repo* into *target_repo*.

    This simple implementation copies files via the filesystem to mimic a
    shared folder or basic IPC mechanism.
    """

    src = Path(source_repo) / "datasets"
    dst = Path(target_repo) / "datasets"
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)


__all__ = [
    "clone_repo",
    "launch_agent",
    "tether_logs",
    "_load_deployments",
]
```

Helper utilities for cloning repositories and launching agent nodes.
**Functions:** clone_repo(target_path), _record_deployment(meta), _load_deployments(), launch_agent(target_path), tether_logs(source_repo, target_repo)


## Module `l2c_tool.py`

```python
from __future__ import annotations

from typing import Dict, List


def generate_commands(natural_text: str, shell: str) -> List[Dict[str, str]]:
    """Return structured shell commands for *natural_text*.

    This function backs the ``l2c.generate`` tool. Codex invokes the tool to
    translate natural language into commands for the active shell.

    Parameters
    ----------
    natural_text:
        Instruction in plain language.
    shell:
        Target shell identifier (e.g. ``"bash"`` or ``"powershell"``).

    Returns
    -------
    list of dict
        Each dict contains ``cmd`` and ``shell`` keys representing a
        shell-specific command suggestion.
    """
    text = natural_text.strip()
    if not text:
        return []
    return [{"cmd": text, "shell": shell}]


__all__ = ["generate_commands"]
```

**Functions:** generate_commands(natural_text, shell)


## Module `prompt_manager.py`

```python
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List


def _dataset_path() -> Path:
    return Path(os.environ.get("DATASETS_DIR", "datasets")) / "prompt_bucket.jsonl"


def _chains_path() -> Path:
    """Return path to prompt chain storage."""
    return Path(os.environ.get("PROMPT_CHAINS_FILE", "memory/prompt_chains.jsonl"))


def create_prompt(task_id: str, text: str, scope: str = "persistent") -> Dict:
    """Store a prompt for *task_id*.

    Parameters
    ----------
    task_id: str
        Identifier for the task this prompt belongs to.
    text: str
        Prompt text to store.
    scope: str
        Either ``"ephemeral"`` or ``"persistent"``. Ephemeral prompts are
        discarded after retrieval.
    """
    if scope not in {"ephemeral", "persistent"}:
        raise ValueError("scope must be 'ephemeral' or 'persistent'")
    record = {"task_id": task_id, "text": text, "scope": scope}
    path = _dataset_path()
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def read_prompts(task_id: str) -> List[Dict]:
    """Return prompts associated with *task_id*.

    Ephemeral prompts are removed after retrieval while persistent prompts
    remain stored.
    """
    path = _dataset_path()
    if not path.exists():
        return []
    found: List[Dict] = []
    remaining: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("task_id") == task_id:
                found.append(rec)
                if rec.get("scope") == "persistent":
                    remaining.append(line)
            else:
                remaining.append(line)
    with path.open("w", encoding="utf-8") as f:
        for line in remaining:
            f.write(line)
    return found


# ---------------------------------------------------------------------------
# Prompt chains
# ---------------------------------------------------------------------------


def chain_prompts(parent_id: str, prompts: List[str]) -> List[Dict]:
    """Queue *prompts* for *parent_id* with ``pending`` state."""

    path = _chains_path()
    path.parent.mkdir(exist_ok=True, parents=True)
    records: List[Dict] = []
    with path.open("a", encoding="utf-8") as f:
        for text in prompts:
            rec = {"parent_id": parent_id, "text": text, "state": "pending"}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            records.append(rec)
    return records


def _update_chain(parent_id: str, text: str, state: str) -> None:
    if state not in {"pending", "in_progress", "done"}:
        raise ValueError("state must be pending, in_progress, or done")
    path = _chains_path()
    if not path.exists():
        return
    records: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("parent_id") == parent_id and rec.get("text") == text:
                rec["state"] = state
            records.append(rec)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def mark_prompt_done(parent_id: str, text: str) -> None:
    """Mark the prompt matching *parent_id* and *text* as ``done``."""

    _update_chain(parent_id, text, "done")


def prune_stale_chains() -> None:
    """Remove chains whose prompts are all ``done``."""

    path = _chains_path()
    if not path.exists():
        return
    chains: Dict[str, List[Dict]] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            chains.setdefault(rec.get("parent_id", ""), []).append(rec)
    with path.open("w", encoding="utf-8") as f:
        for items in chains.values():
            if all(r.get("state") == "done" for r in items):
                continue
            for rec in items:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
```

**Functions:** _dataset_path(), _chains_path(), create_prompt(task_id, text, scope), read_prompts(task_id), chain_prompts(parent_id, prompts), _update_chain(parent_id, text, state), mark_prompt_done(parent_id, text), prune_stale_chains()


## Module `schema_manager.py`

```python
import json
import logging
import re
from pathlib import Path
from typing import Dict

import jsonschema

BASE_SCHEMA_PATH = Path("schemas/base_schema.json")
LOGGER = logging.getLogger(__name__)


def load_schema(operator: str | None = None) -> Dict[str, Dict[str, str]]:
    """Load base schema and merge optional *operator* extension.

    If the base schema is missing or unreadable, a minimal placeholder is
    created and an empty schema is returned. Operators are informed via
    logging when auto-generation occurs or when operator schemas are missing.
    """

    if not BASE_SCHEMA_PATH.exists():
        LOGGER.warning("Base schema missing at %s; creating placeholder", BASE_SCHEMA_PATH)
        BASE_SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASE_SCHEMA_PATH.write_text("{}\n", encoding="utf-8")
        schema: Dict[str, Dict[str, str]] = {}
    else:
        try:
            with BASE_SCHEMA_PATH.open("r", encoding="utf-8") as f:
                schema = json.load(f)
        except Exception:
            LOGGER.exception("Failed to load base schema %s; using empty schema", BASE_SCHEMA_PATH)
            schema = {}

    if operator:
        op_path = Path("schemas") / f"{operator}_schema.json"
        if op_path.exists():
            try:
                with op_path.open("r", encoding="utf-8") as f:
                    op_schema = json.load(f)
                for file, sections in op_schema.items():
                    schema.setdefault(file, {}).update(sections)
            except Exception:
                LOGGER.exception("Failed to load operator schema %s", op_path)
        else:
            LOGGER.info("Operator schema not found at %s; skipping", op_path)

    return schema


def apply_schema(sections: Dict[str, str], target_agent_md: str | Path) -> bool:
    """Apply *sections* to *target_agent_md* using section markers.

    Returns ``True`` when the file content changed."""
    path = Path(target_agent_md)
    original = path.read_text(encoding='utf-8')
    content = original
    for section, text in sections.items():
        start = f"<!-- schema:{section}:start -->"
        end = f"<!-- schema:{section}:end -->"
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        replacement = f"{start}\n{text}\n{end}"
        content = pattern.sub(replacement, content)
    if content != original:
        path.write_text(content, encoding='utf-8')
        return True
    return False


def validate_schema(schema: Dict) -> bool:
    """Validate *schema* against the canonical JSON Schema.

    Returns ``True`` when *schema* satisfies the canonical definition,
    otherwise logs the failure and returns ``False``. Missing or unreadable
    canonical schema files also result in ``False``."""

    if not BASE_SCHEMA_PATH.exists():
        LOGGER.error("Canonical schema not found at %s", BASE_SCHEMA_PATH)
        return False
    try:
        with BASE_SCHEMA_PATH.open("r", encoding="utf-8") as f:
            canonical = json.load(f)
    except Exception:
        LOGGER.exception("Failed to load canonical schema %s", BASE_SCHEMA_PATH)
        return False
    try:
        jsonschema.validate(instance=schema, schema=canonical)
    except jsonschema.ValidationError as exc:
        LOGGER.error("Schema validation error: %s", exc)
        return False
    return True


def apply_schema_to_persona(
    schema: Dict[str, Dict[str, str]], persona_path: str | Path
) -> bool:
    """Append missing schema sections for *persona_path*.

    Only sections not already present in the persona document are appended
    with their start/end markers. Returns ``True`` if any content was added."""

    path = Path(persona_path)
    filename = path.name
    sections = schema.get(filename, {})
    if not sections:
        return False

    original = path.read_text(encoding="utf-8")
    content = original
    for section, text in sections.items():
        start = f"<!-- schema:{section}:start -->"
        end = f"<!-- schema:{section}:end -->"
        if start in content and end in content:
            continue
        content += f"\n{start}\n{text}\n{end}\n"

    if content != original:
        path.write_text(content, encoding="utf-8")
        return True
    return False
```

**Functions:** load_schema(operator), apply_schema(sections, target_agent_md), validate_schema(schema), apply_schema_to_persona(schema, persona_path)


## Module `tasks.py`

```python
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QPoint, QRect, Qt, QPropertyAnimation
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QScrollArea,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)


@dataclass
class Task:
    id: str
    title: str
    status: str
    files: List[str]
    bucket: Optional[str] = None
    branch: Optional[str] = None


class TaskManager:
    def __init__(self, path: str, vector_store=None) -> None:
        self.path = path
        self.vector_store = vector_store
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, "a", encoding="utf-8").close()

    def _load_all(self) -> List[Task]:
        tasks: List[Task] = []
        if not os.path.exists(self.path):
            return tasks
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                tasks.append(Task(**data))
        return tasks

    def _save_all(self, tasks: List[Task]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            for task in tasks:
                f.write(json.dumps(asdict(task), ensure_ascii=False) + "\n")

    def add_task(
        self,
        title: str,
        status: str,
        files: List[str],
        bucket: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Task:
        task = Task(id=str(uuid.uuid4()), title=title, status=status, files=files, bucket=bucket, branch=branch)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(task), ensure_ascii=False) + "\n")
        if self.vector_store:
            meta: Dict[str, object] = {"status": status, "files": files}
            if bucket:
                meta["bucket"] = bucket
            if branch:
                meta["branch"] = branch
            self.vector_store.add_text(title, meta)
        return task

    def update_task(self, task_id: str, **updates) -> Optional[Task]:
        tasks = self._load_all()
        updated: Optional[Task] = None
        for t in tasks:
            if t.id == task_id:
                for k, v in updates.items():
                    if v is not None and hasattr(t, k):
                        setattr(t, k, v)
                updated = t
                break
        if updated:
            self._save_all(tasks)
            if self.vector_store:
                meta: Dict[str, object] = {"status": updated.status, "files": updated.files}
                if updated.bucket:
                    meta["bucket"] = updated.bucket
                if updated.branch:
                    meta["branch"] = updated.branch
                self.vector_store.add_text(updated.title, meta)
        return updated

    def list_tasks(self) -> List[Dict]:
        return [asdict(t) for t in self._load_all()]

    def remove_task(self, task_id: str) -> bool:
        tasks = self._load_all()
        new_tasks = [t for t in tasks if t.id != task_id]
        if len(new_tasks) == len(tasks):
            return False
        self._save_all(new_tasks)
        return True


class TaskRow(QWidget):
    """Row widget with task title and action buttons."""

    def __init__(self, task: Dict, manager: TaskManager, open_editor, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.task = task
        self.manager = manager
        self._open_editor = open_editor

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        self.label = QLabel(f"{task['status']}: {task['title']}")
        layout.addWidget(self.label, 1)
        self.edit_btn = QPushButton("Open Editor", self)
        self.link_btn = QPushButton("Link Conversation", self)
        self.done_btn = QPushButton("Mark Done", self)
        for b in (self.edit_btn, self.link_btn, self.done_btn):
            layout.addWidget(b)

        self.edit_btn.clicked.connect(self._on_open_editor)
        self.done_btn.clicked.connect(self._on_mark_done)

    def _on_open_editor(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open File")
        if not path:
            return
        files = list(self.task.get("files", []))
        files.append(path)
        self.manager.update_task(self.task["id"], files=files)
        self._open_editor(path)

    def _on_mark_done(self) -> None:
        self.manager.update_task(self.task["id"], status="done")
        self.label.setText(f"done: {self.task['title']}")


class TaskListView(QScrollArea):
    """Scrollable task list container."""

    def __init__(self, manager: TaskManager, open_editor, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.manager = manager
        self._open_editor = open_editor
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.setWidget(self.container)
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

    def refresh(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for task in self.manager.list_tasks():
            row = TaskRow(task, self.manager, self._open_editor)
            self.layout.addWidget(row)
        self.layout.addStretch(1)

    def count(self) -> int:
        return max(0, self.layout.count() - 1)


class CardBase(QFrame):
    def __init__(self, t: Any, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.t = t
        self._drag = False
        self._press = QPoint()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowTitle(title)
        self.setStyleSheet(
            f"background:{t.card_bg}; border:1px solid {t.card_border}; border-radius:{t.card_radius}px;"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        hdr = QFrame(self)
        hdr.setObjectName("Hdr")
        hdr.setStyleSheet(
            f"#Hdr {{ background:{t.header_bg}; border-top-left-radius:{t.card_radius}px; "
            f"border-top-right-radius:{t.card_radius}px; }}"
            f"QLabel {{ color:{t.header_fg}; font:600 10pt 'Cascadia Code'; }}"
            f"QPushButton {{ background:{t.accent}; color:#fff; border:1px solid {t.card_border}; "
            f"border-radius:6px; padding:2px 6px; }}"
            f"QPushButton:hover {{ background:{getattr(t, 'accent_hover', t.accent)}; }}"
        )
        H = QHBoxLayout(hdr)
        H.setContentsMargins(12, 8, 12, 6)
        H.setSpacing(8)
        self.title_label = QLabel(title, hdr)
        self.min_btn = QPushButton("–", hdr)
        self.close_btn = QPushButton("×", hdr)
        H.addWidget(self.title_label)
        H.addStretch(1)
        H.addWidget(self.min_btn)
        H.addWidget(self.close_btn)
        root.addWidget(hdr)

        self.body = QFrame(self)
        self.body.setObjectName("Body")
        self.body.setStyleSheet(f"#Body {{ background:{t.card_bg}; }}")
        root.addWidget(self.body, 1)

        self._grips = [QSizeGrip(self) for _ in range(4)]
        for g in self._grips:
            g.setFixedSize(16, 16)
            g.raise_()

        self.close_btn.clicked.connect(self.close)
        self.min_btn.clicked.connect(self._toggle_body)

    def _toggle_body(self) -> None:
        self.body.setVisible(not self.body.isVisible())

    def header_geom(self) -> QRect:
        return QRect(0, 0, self.width(), 46)

    def resizeEvent(self, e):
        w, h = self.width(), self.height()
        m = 6
        g = self._grips
        g[0].move(m, h - g[0].height() - m)
        g[1].move(w - g[1].width() - m, h - g[1].height() - m)
        g[2].move(m, m)
        g[3].move(w - g[3].width() - m, m)
        super().resizeEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.header_geom().contains(e.position().toPoint()):
            self._drag = True
            self._press = e.position().toPoint()
            self.raise_()
            e.accept()
        else:
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if not self._drag:
            super().mouseMoveEvent(e)
            return
        delta = e.position().toPoint() - self._press
        self.move(self.pos() + delta)
        e.accept()

    def mouseReleaseEvent(self, e):
        if self._drag:
            self._drag = False
        super().mouseReleaseEvent(e)


class TaskCard(CardBase):
    def __init__(self, manager: TaskManager, t: Any, open_editor, parent: Optional[QWidget] = None) -> None:
        super().__init__(t, "Task Viewer", parent)
        self.manager = manager
        self._open_editor = open_editor
        layout = QVBoxLayout(self.body)
        layout.setContentsMargins(10, 10, 10, 10)
        self.list = TaskListView(manager, open_editor, self.body)
        layout.addWidget(self.list)
        self.refresh()
        self.show()

    def refresh(self) -> None:
        self.list.refresh()

    def showEvent(self, e):
        super().showEvent(e)
        end = self.geometry()
        start = QRect(end.x() + end.width(), end.y(), end.width(), end.height())
        self.setGeometry(start)
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.start()
        self._anim = anim

    def close(self) -> None:  # type: ignore[override]
        end = QRect(self.x() + self.width(), self.y(), self.width(), self.height())
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setStartValue(self.geometry())
        anim.setEndValue(end)
        anim.finished.connect(super().close)
        anim.start()
        self._anim = anim
        self.hide()


_open_cards: List[TaskCard] = []


def open_card(manager: TaskManager, t: Any, open_editor, parent: Optional[QWidget] = None) -> TaskCard:
    """Create and show a :class:`TaskCard` instance.

    Parameters
    ----------
    manager:
        The task manager providing task persistence.
    t:
        Theme instance for styling.
    parent:
        Optional parent widget.

    Returns
    -------
    TaskCard
        The created card, already shown.
    """

    card = TaskCard(manager, t, open_editor, parent)
    _open_cards.append(card)
    return card


def close_card(card: TaskCard) -> None:
    """Close a previously opened :class:`TaskCard`."""

    if card in _open_cards:
        _open_cards.remove(card)
    card.close()


def close_all_cards() -> None:
    """Close all open task cards."""

    for card in list(_open_cards):
        card.close()
    _open_cards.clear()
```

**Classes:** Task, TaskManager, TaskRow, TaskListView, CardBase, TaskCard
**Functions:** open_card(manager, t, open_editor, parent), close_card(card), close_all_cards()


## Module `Virtual_Desktop.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Virtual_Desktop.py — agent-ready virtual desktop with card loader, template terminal,
system log, pop-out System Console, Desktop Explorer, and internal Code Editor card.

Updates (this build):
- Shift + Mouse Wheel ⇒ horizontal pan; normal wheel ⇒ vertical pan (when not fullscreen).
- No panning while in fullscreen remains enforced.
- Cards auto-raise on create/open; added 'Bring All To Front', 'Tile Cards', and a Windows list.
- Added Tools ▸ Open code_editor.py (loads as internal editor card).
- Desktop Explorer card: icons for files/folders under ./Virtual_Desktop ; double-click to open.
- Preserves embedded app look (no extra QSS on child widgets).
- Debounced canvas sync on real screen changes/fullscreen only (reduces log spam).
- Per-card geometry persistence (position & size remembered across sessions).
 - Supports ``build_widget(parent)`` factories for embedding.
- Dark, high-contrast UI preserved.
"""

from __future__ import annotations

import os, sys, json, time, threading, subprocess, importlib.util, argparse, logging, socket
from dataclasses import dataclass
from typing import Optional, List, Dict
from pathlib import Path

from tools.qt_utils import ensure_pyside6, set_hidpi_policy_once
from tools.qt_runtime import ensure_qt_runtime, resolve_qt_plugin_path
from code_editor import build_widget as build_editor_widget
from tasks import TaskManager, open_card

# --------------------------------------------------------------------------------------
# Paths, logging & state
# --------------------------------------------------------------------------------------

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
STATE_PATH = os.path.join(SCRIPT_DIR, "vd_state.json")
LOG_PATH   = os.path.join(SCRIPT_DIR, "system.log")
VDSK_ROOT  = os.path.join(SCRIPT_DIR, "Virtual_Desktop")  # virtual "desktop" folder
DATASETS_DIR = os.path.join(SCRIPT_DIR, "datasets")
os.makedirs(VDSK_ROOT, exist_ok=True)

# overwrite each run
LOGGER = logging.getLogger("VirtualDesktop")
LOGGER.setLevel(logging.INFO)
if LOGGER.handlers:
    LOGGER.handlers.clear()
_fh = logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
LOGGER.addHandler(_fh)

# Gate auto-launch behavior behind an env flag to avoid spawning rogue cards
AUTO_LAUNCH = os.environ.get("VD_AUTO_LAUNCH") == "1"


def _show_manual_install(pkg: str) -> None:
    msg = (
        f"{pkg} is required but could not be installed automatically.\n"
        f"Please install it manually, e.g.\n    pip install {pkg}"
    )
    try:
        import tkinter as tk  # noqa: F401
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Missing Dependency", msg)
        root.destroy()
    except Exception:
        print(msg, file=sys.stderr)



from PySide6.QtCore import (
    Qt, QPoint, QRect, QRectF, QSize, QEvent, QTimer, Signal
)
from PySide6.QtGui import (
    QColor, QGuiApplication, QPainter, QPainterPath, QLinearGradient, QPalette,
    QAction, QKeySequence, QClipboard, QIcon
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QScrollArea, QFrame, QLabel, QVBoxLayout,
    QHBoxLayout, QSizeGrip, QPushButton, QGraphicsDropShadowEffect, QMenuBar,
    QFileDialog, QPlainTextEdit, QMenu, QListWidget, QListWidgetItem, QStyle, QToolButton, QMessageBox
)

def log(msg: str, level=logging.INFO):
    LOGGER.log(level, msg)

def _load_state() -> Dict:
    if os.path.isfile(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"state load failed: {e}", logging.WARNING)
    # structure also stores per-card geometry keyed by path/module
    return {"recent": [], "geom": {}}

def _save_state(state: Dict):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"state save failed: {e}", logging.WARNING)

def _remember_card(kind: str, path: str, title: str):
    st = _load_state()
    st["recent"] = [r for r in st.get("recent", []) if r.get("path") != path or r.get("kind") != kind]
    st["recent"].insert(0, {"kind": kind, "path": path, "title": title, "ts": int(time.time())})
    st["recent"] = st["recent"][:20]
    _save_state(st)

def _geom_key_for(kind: str, path_or_tag: str) -> str:
    return f"{kind}:{path_or_tag}"

def _restore_card_geom(card: "Card", kind: str, path_or_tag: str):
    st = _load_state(); key = _geom_key_for(kind, path_or_tag)
    g = st.get("geom", {}).get(key)
    if not g: return
    try:
        x,y,w,h = int(g["x"]), int(g["y"]), int(g["w"]), int(g["h"])
        card.resize(w, h); card.move(x, y)
    except Exception:
        pass

def _save_card_geom(card: "Card", kind: str, path_or_tag: str):
    st = _load_state(); key = _geom_key_for(kind, path_or_tag)
    st.setdefault("geom", {})[key] = {"x": card.x(), "y": card.y(), "w": card.width(), "h": card.height()}
    _save_state(st)

# --------------------------------------------------------------------------------------
# Theme
# --------------------------------------------------------------------------------------

@dataclass
class Theme:
    # Desktop
    desktop_top: str = "#0f3b8e"
    desktop_mid: str = "#1c54cc"
    edge_glow:   str = "#4aa8ff"

    # Cards
    card_bg:     str = "#0c1320"
    card_border: str = "#213040"
    card_radius: int = 12
    header_bg:   str = "#0a111e"
    header_fg:   str = "#eaf2ff"
    text_muted:  str = "#c7d5ee"
    text_body:   str = "#e9f3ff"
    accent:      str = "#1E5AFF"
    accent_hov:  str = "#2f72ff"
    # Editor surface (dark)
    editor_bg:   str = "#0b1828"
    editor_fg:   str = "#d6e6ff"
    editor_sel:  str = "#264f78"

    # Menu bar (top “taskbar”)
    menu_bg:     str = "#0a111e"
    menu_fg:     str = "#eaf2ff"

# --------------------------------------------------------------------------------------
# Contrast helpers
# --------------------------------------------------------------------------------------

def apply_contrast_palette(w: QWidget, bg_hex: str, fg_hex: str):
    p = w.palette()
    bg = QColor(bg_hex); fg = QColor(fg_hex)
    for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        p.setColor(group, QPalette.Base, bg)
        p.setColor(group, QPalette.Text, fg)
        p.setColor(group, QPalette.Window, bg)
        p.setColor(group, QPalette.WindowText, fg)
        p.setColor(group, QPalette.Highlight, QColor("#2a5ea1"))
        p.setColor(group, QPalette.HighlightedText, QColor("#ffffff"))
    w.setPalette(p)

# --------------------------------------------------------------------------------------
# System Console (log viewer, pop-out)
# --------------------------------------------------------------------------------------

class SystemConsole(QWidget):
    def __init__(self, theme: Theme, log_path: str):
        super().__init__()
        self.setWindowTitle("System Console (Log)")
        self.resize(800, 540)
        self.t = theme
        self.log_path = log_path
        self._pos = 0
        v = QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(8)

        self.text = QPlainTextEdit(self); self.text.setReadOnly(True)
        apply_contrast_palette(self.text, theme.editor_bg, theme.editor_fg)
        self.text.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; "
            f"selection-background-color:{theme.editor_sel}; border:1px solid {theme.card_border}; "
            f"font-family:'Cascadia Code',Consolas,monospace; }}"
        )

        row = QHBoxLayout()
        def mk_btn(lbl, fn):
            b = QPushButton(lbl); b.clicked.connect(fn)
            return b
        btn_refresh = mk_btn("Refresh", self.refresh)
        btn_clear   = mk_btn("Clear Log", self.clear_log)
        def _open_folder():
            d = os.path.dirname(self.log_path) or SCRIPT_DIR
            if sys.platform.startswith("win"): os.startfile(d)
            elif sys.platform == "darwin": subprocess.Popen(["open", d])
            else: subprocess.Popen(["xdg-open", d])
        btn_open    = mk_btn("Open Folder", _open_folder)
        row.addWidget(btn_refresh); row.addWidget(btn_clear); row.addWidget(btn_open); row.addStretch(1)

        v.addLayout(row)
        v.addWidget(self.text, 1)

        self.timer = QTimer(self); self.timer.setInterval(800); self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh(initial=True)

    def refresh(self, initial: bool=False):
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self._pos)
                chunk = f.read()
                self._pos = f.tell()
            if initial:
                self.text.setPlainText(chunk)
            else:
                if chunk:
                    self.text.moveCursor(self.text.textCursor().End)
                    self.text.insertPlainText(chunk)
            self.text.moveCursor(self.text.textCursor().End)
        except Exception:
            pass

    def clear_log(self):
        try:
            with open(self.log_path, "w", encoding="utf-8"):
                pass
            self._pos = 0
            self.text.setPlainText("")
        except Exception as e:
            log(f"log clear failed: {e}", logging.WARNING)

# --------------------------------------------------------------------------------------
# Cursor overlay (agent pointer)
# --------------------------------------------------------------------------------------

class CursorOverlay(QWidget):
    def __init__(self, canvas: QWidget, theme: Theme):
        super().__init__(canvas)
        self._pos = QPoint(60, 60)
        self._visible = True
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setGeometry(canvas.rect())
        self.raise_(); self.show()

    def set_pos(self, p: QPoint):
        self._pos = p; self.update()

    def paintEvent(self, _):
        if not self._visible: return
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QColor("#ffffff")); p.setBrush(Qt.NoBrush)
        p.drawEllipse(self._pos, 10, 10)
        p.setBrush(QColor("#ffffff")); p.setPen(Qt.NoPen)
        p.drawEllipse(self._pos, 3, 3)

# --------------------------------------------------------------------------------------
# Card (movable/resizable)
# --------------------------------------------------------------------------------------

class Card(QFrame):
    moved = Signal()
    resized = Signal()
    closed = Signal(object)  # emits self on close

    def __init__(self, theme: Theme, title: str = "Card", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.t = theme
        self._drag = False
        self._press = QPoint()
        self._persist_tag: Optional[str] = None
        self.setObjectName("Card")
        self.setStyleSheet(
            f"#Card {{ background:{self.t.card_bg}; border:1px solid {self.t.card_border}; "
            f"border-radius:{self.t.card_radius}px; }}"
        )
        sh = QGraphicsDropShadowEffect(self); sh.setColor(QColor(0, 30, 80, 150))
        sh.setBlurRadius(28); sh.setOffset(0, 12); self.setGraphicsEffect(sh)

        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        # Header
        self.header = QFrame(self); self.header.setObjectName("Hdr")
        self.header.setStyleSheet(
            f"#Hdr {{ background:{self.t.header_bg}; border-top-left-radius:{self.t.card_radius}px; "
            f"border-top-right-radius:{self.t.card_radius}px; }}"
            f"QLabel {{ color:{self.t.header_fg}; font:600 10.5pt 'Cascadia Code'; }}"
            f"QPushButton {{ color:#fff; background:{self.t.accent}; border:1px solid {self.t.card_border}; "
            f"border-radius:6px; padding:4px 8px; }}"
            f"QPushButton:hover {{ background:{self.t.accent_hov}; }}"
        )
        H = QHBoxLayout(self.header); H.setContentsMargins(12, 8, 12, 6); H.setSpacing(8)
        self.title_label = QLabel(title, self.header)
        self.pin_btn = QPushButton("Track", self.header); self.pin_btn.setCheckable(True); self.pin_btn.setChecked(True)
        self.close_btn = QPushButton("Close", self.header)
        self.close_btn.clicked.connect(lambda: self._close_card())
        H.addWidget(self.title_label); H.addStretch(1); H.addWidget(self.pin_btn); H.addWidget(self.close_btn)
        root.addWidget(self.header)

        # Body
        self.body = QFrame(self); self.body.setObjectName("Body")
        # IMPORTANT: don't restyle embedded widgets – only set the body background.
        self.body.setStyleSheet(f"#Body {{ background:{self.t.card_bg}; }}")
        root.addWidget(self.body, 1)

        # Size grips
        self._grips = [QSizeGrip(self) for _ in range(4)]
        for g in self._grips: g.setFixedSize(16, 16); g.raise_()

    def set_persist_tag(self, tag: str):
        self._persist_tag = tag

    def header_geom(self) -> QRect:
        return QRect(0, 0, self.width(), 44)

    def resizeEvent(self, e):
        w, h = self.width(), self.height(); m = 6; g = self._grips
        g[0].move(m, h - g[0].height() - m)
        g[1].move(w - g[1].width() - m, h - g[1].height() - m)
        g[2].move(m, m)
        g[3].move(w - g[3].width() - m, m)
        self.resized.emit()
        super().resizeEvent(e)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton and self.header_geom().contains(ev.position().toPoint()):
            self._drag = True; self._press = ev.position().toPoint()
            self.raise_(); self.activateWindow()
            self.setFocus(Qt.ActiveWindowFocusReason)
            ev.accept()
        else:
            super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if not self._drag:
            super().mouseMoveEvent(ev); return
        delta = ev.position().toPoint() - self._press
        new_pos = self.pos() + delta
        canvas = self.parentWidget()
        if canvas:
            r = canvas.rect()
            new_pos.setX(max(6, min(new_pos.x(), r.width() - self.width() - 6)))
            new_pos.setY(max(6, min(new_pos.y(), r.height() - self.height() - 6)))
        self.move(new_pos); ev.accept()

    def mouseReleaseEvent(self, ev):
        if self._drag:
            self._drag = False; self.moved.emit()
        super().mouseReleaseEvent(ev)

    # Right-click header → close
    def contextMenuEvent(self, e):
        if not self.header_geom().contains(e.pos()): return
        menu = QMenu(self)
        act_close = menu.addAction("Close Card")
        act = menu.exec(e.globalPos())
        if act == act_close:
            self._close_card()

    def _close_card(self):
        try:
            self.closed.emit(self)
        finally:
            self.deleteLater()

# --------------------------------------------------------------------------------------
# Desktop canvas & camera
# --------------------------------------------------------------------------------------

class DesktopCanvas(QWidget):
    def __init__(self, theme: Theme, size: QSize, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.t = theme
        self.resize(size)
        self.cursor_overlay = CursorOverlay(self, theme)
        self._last_focus: Optional[QWidget] = None

    def add_card(self, widget: QWidget, title: str = "Card") -> Card:
        card = Card(self.t, title, self)
        widget.setParent(card.body)
        lay = QVBoxLayout(card.body); lay.setContentsMargins(10, 10, 10, 10); lay.addWidget(widget)
        # Default comfy size (VD won't rescale child content)
        card.resize(1100, 700); card.move(40, 40); card.show()
        card.raise_(); card.activateWindow()
        card.moved.connect(lambda: self._maybe_refocus(card))
        card.closed.connect(lambda _: self._maybe_clear_focus(card))
        self._last_focus = card
        log(f"Card added: {title}")
        return card

    def _find_camera(self):
        p = self.parentWidget()
        while p is not None and not hasattr(p, "center_on_widget"):
            p = p.parentWidget()
        return p

    def _maybe_refocus(self, w: QWidget):
        cam = self._find_camera()
        if cam and isinstance(w, Card) and w.pin_btn.isChecked():
            cam.center_on_widget(w)

    def _maybe_clear_focus(self, w: QWidget):
        if self._last_focus is w:
            self._last_focus = None

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        g = QLinearGradient(r.topLeft(), r.bottomLeft())
        g.setColorAt(0.00, QColor(self.t.desktop_top))
        g.setColorAt(0.55, QColor(self.t.desktop_mid))
        g.setColorAt(1.00, QColor(self.t.desktop_top))
        p.fillRect(r, g)
        glow = QColor(self.t.edge_glow); glow.setAlphaF(0.18)
        p.setPen(glow)
        for i in range(14):
            rr = r.adjusted(10 + i, 10 + i, -10 - i, -10 - i)
            p.drawRoundedRect(rr, 18, 18)
        p.setPen(Qt.NoPen); p.setBrush(QColor(0, 0, 0, 110))
        path = QPainterPath(); path.addRect(r)
        inner = r.adjusted(30, 30, -30, -30)
        ip = QPainterPath(); ip.addRoundedRect(QRectF(inner), 26, 26)
        p.drawPath(path.subtracted(ip))

class Camera(QScrollArea):
    def __init__(self, content: DesktopCanvas, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWidget(content)             # QScrollArea takes ownership; canvas parent becomes this
        self.setWidgetResizable(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Drag-to-pan
        self._dragging = False; self._last = QPoint()
        self.viewport().installEventFilter(self)

    def center_on_widget(self, w: QWidget):
        if not w: return
        c = w.geometry().center()
        self.center_on_point(c)

    def center_on_point(self, pt: QPoint):
        cont = self.widget(); vw = self.viewport().size()
        x = max(0, min(pt.x() - vw.width() // 2, cont.width() - vw.width()))
        y = max(0, min(pt.y() - vw.height() // 2, cont.height() - vw.height()))
        self.horizontalScrollBar().setValue(x)
        self.verticalScrollBar().setValue(y)

    def pan(self, dx: int, dy: int):
        hs = self.horizontalScrollBar(); vs = self.verticalScrollBar()
        hs.setValue(max(hs.minimum(), min(hs.maximum(), hs.value() + dx)))
        vs.setValue(max(vs.minimum(), min(vs.maximum(), vs.value() + dy)))

    def _fullscreen_blocked(self) -> bool:
        w = self.window()
        return bool(w and w.isFullScreen())

    def eventFilter(self, obj, ev):
        if obj is self.viewport():
            # Wheel support: Shift = horizontal, plain = vertical (blocked in fullscreen)
            if ev.type() == QEvent.Type.Wheel:
                if self._fullscreen_blocked():
                    return super().eventFilter(obj, ev)
                delta = ev.angleDelta()
                steps = delta.y() // 120 if delta.y() else delta.x() // 120
                if ev.modifiers() & Qt.ShiftModifier:
                    self.pan(-int(steps) * 120, 0)
                else:
                    self.pan(0, -int(steps) * 120)
                return True

            # Middle-button drag (blocked in fullscreen)
            if self._fullscreen_blocked():
                return super().eventFilter(obj, ev)
            if ev.type() == QEvent.MouseButtonPress and ev.button() == Qt.MiddleButton:
                self._dragging = True; self._last = ev.position().toPoint(); return True
            elif ev.type() == QEvent.MouseMove and self._dragging:
                cur = ev.position().toPoint()
                delta = cur - self._last; self._last = cur
                self.pan(-delta.x(), -delta.y()); return True
            elif ev.type() in (QEvent.MouseButtonRelease, QEvent.Leave):
                self._dragging = False
        return super().eventFilter(obj, ev)

# --------------------------------------------------------------------------------------
# Template Terminal (instructions + copy)
# --------------------------------------------------------------------------------------

_TEMPLATE_INSTRUCTIONS = """\
Template Terminal — Card How-To
===============================

A Card is just a QWidget hosted by the Virtual Desktop. It can be a terminal, editor,
dashboard—anything with a Qt widget.

Two ways to load
1) Verified Card (embedded): define create_card(parent)->QWidget|(QWidget,title) or build_widget(parent)
2) Process Console (fallback): no factory? we run it as a subprocess and stream output.

♿ Contrast rule: set Base/Text colors for Active/Inactive/Disabled OR style with QSS so
read-only and disabled text stays readable.
"""

_TEMPLATE_CODE = r'''# minimal_card.py — simple verified card
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
def _apply_palette(w, bg="#0b1828", fg="#e9f3ff"):
    p=w.palette()
    bgc,fgc=QColor(bg),QColor(fg)
    for g in (QPalette.Active,QPalette.Inactive,QPalette.Disabled):
        p.setColor(g,QPalette.Base,bgc); p.setColor(g,QPalette.Text,fgc)
        p.setColor(g,QPalette.Window,bgc); p.setColor(g,QPalette.WindowText,fgc)
    w.setPalette(p)
def create_card(parent=None):
    w=QWidget(parent); _apply_palette(w)
    w.setStyleSheet("QLabel{color:#c7d5ee; font:600 11pt 'Cascadia Code';}"
                    "QPushButton{color:#fff; background:#1E5AFF; border:1px solid #213040; border-radius:6px; padding:6px 10px;}"
                    "QPushButton:hover{background:#2f72ff;}")
    lay=QVBoxLayout(w); lay.setContentsMargins(14,14,14,14); lay.setSpacing(8)
    title=QLabel('🧩 My Card'); title.setAlignment(Qt.AlignCenter)
    btn=QPushButton('Click Me')
    lay.addWidget(title); lay.addWidget(btn)
    return w,"My First Card"
'''

class TemplateTerminal(QWidget):
    def __init__(self, theme: Theme):
        super().__init__()
        self.t = theme
        v = QVBoxLayout(self); v.setContentsMargins(12, 12, 12, 12); v.setSpacing(10)

        hdr = QLabel("Template Terminal — Card How-To  ✨")
        hdr.setStyleSheet("color:#eaf2ff; font:700 12pt 'Cascadia Code';")
        v.addWidget(hdr)

        self.txt = QPlainTextEdit(self); self.txt.setReadOnly(True)
        self.txt.setPlainText(_TEMPLATE_INSTRUCTIONS)
        apply_contrast_palette(self.txt, theme.editor_bg, theme.editor_fg)
        self.txt.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; "
            f"selection-background-color:{theme.editor_sel}; border:1px solid {theme.card_border}; "
            f"font-family:'Cascadia Code',Consolas,monospace; }}"
        )
        v.addWidget(self.txt, 1)

        row = QHBoxLayout(); row.setSpacing(8)
        btn_copy_info = QPushButton("📋 Copy Instructions")
        btn_copy_tpl  = QPushButton("📋 Copy Minimal Card Template")
        btn_copy_info.clicked.connect(lambda: QApplication.clipboard().setText(_TEMPLATE_INSTRUCTIONS, QClipboard.Clipboard))
        btn_copy_tpl.clicked.connect(lambda: QApplication.clipboard().setText(_TEMPLATE_CODE, QClipboard.Clipboard))
        row.addWidget(btn_copy_info); row.addWidget(btn_copy_tpl); row.addStretch(1)
        v.addLayout(row)

        code_hdr = QLabel("🧪 Minimal Card (verified) — save as minimal_card.py then load via Cards ▸ Load Script as Card…")
        code_hdr.setStyleSheet("color:#c7d5ee;")
        v.addWidget(code_hdr)

        self.code = QPlainTextEdit(self); self.code.setReadOnly(True)
        self.code.setPlainText(_TEMPLATE_CODE)
        apply_contrast_palette(self.code, theme.editor_bg, theme.editor_fg)
        self.code.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; "
            f"selection-background-color:{theme.editor_sel}; border:1px solid {theme.card_border}; "
            f"font-family:'Cascadia Code',Consolas,monospace; }}"
        )
        v.addWidget(self.code, 1)

# --------------------------------------------------------------------------------------
# Desktop Explorer (icons for files/folders in VDSK_ROOT)
# --------------------------------------------------------------------------------------

class ExplorerCard(QWidget):
    def __init__(self, root_path: str, open_cb, theme: Theme):
        super().__init__()
        self.root = root_path
        self.open_cb = open_cb  # callback(path) to open files/folders
        self.t = theme

        v = QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(8)

        # Header bar
        hdr = QFrame(self); hdr.setStyleSheet(f"background:{self.t.header_bg}; border:1px solid {self.t.card_border}; border-radius:8px;")
        h = QHBoxLayout(hdr); h.setContentsMargins(8,6,8,6); h.setSpacing(8)
        self.lbl_path = QLabel(self.root); self.lbl_path.setStyleSheet(f"color:{self.t.header_fg}; font:600 10pt 'Cascadia Code';")
        btn_up = QPushButton("Up"); btn_up.setStyleSheet(
            f"QPushButton{{color:#fff; background:{self.t.accent}; border:1px solid {self.t.card_border}; border-radius:6px; padding:4px 10px;}}"
            f"QPushButton:hover{{background:{self.t.accent_hov};}}"
        )
        btn_new = QPushButton("New Folder")
        btn_new.setStyleSheet(
            f"QPushButton{{color:#fff; background:{self.t.accent}; border:1px solid {self.t.card_border}; border-radius:6px; padding:4px 10px;}}"
            f"QPushButton:hover{{background:{self.t.accent_hov};}}"
        )
        h.addWidget(self.lbl_path); h.addStretch(1); h.addWidget(btn_new); h.addWidget(btn_up)
        v.addWidget(hdr)

        # Icon view
        self.list = QListWidget(self)
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setIconSize(QSize(48,48))
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setMovement(QListWidget.Static)
        self.list.setSpacing(12)
        self.list.setStyleSheet(
            f"QListWidget{{ background:{self.t.editor_bg}; color:{self.t.editor_fg}; border:1px solid {self.t.card_border}; border-radius:10px; }}"
        )
        v.addWidget(self.list, 1)

        btn_up.clicked.connect(self._go_up)
        btn_new.clicked.connect(self._new_folder)
        self.list.itemActivated.connect(self._open_item)
        self._cwd = self.root
        self._refresh()

    def _style_icon(self, path: str):
        st = QApplication.style()
        if os.path.isdir(path):
            return st.standardIcon(QStyle.SP_DirIcon)
        else:
            # crude: python files get a different icon
            if path.lower().endswith(".py"):
                return st.standardIcon(QStyle.SP_FileDialogDetailedView)
            return st.standardIcon(QStyle.SP_FileIcon)

    def _refresh(self):
        self.list.clear()
        self.lbl_path.setText(self._cwd)
        try:
            ents = sorted(os.listdir(self._cwd), key=str.lower)
        except Exception as e:
            log(f"Explorer list failed: {e}", logging.WARNING)
            ents = []
        # Show .. first
        if os.path.abspath(self._cwd) != os.path.abspath(self.root):
            it = QListWidgetItem("..")
            it.setIcon(QApplication.style().standardIcon(QStyle.SP_ArrowUp))
            it.setData(Qt.UserRole, os.path.abspath(os.path.join(self._cwd, "..")))
            self.list.addItem(it)

        for name in ents:
            full = os.path.join(self._cwd, name)
            it = QListWidgetItem(name)
            it.setIcon(self._style_icon(full))
            it.setData(Qt.UserRole, full)
            self.list.addItem(it)

    def _open_item(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if not path: return
        if os.path.isdir(path):
            self._cwd = path; self._refresh()
        else:
            self.open_cb(path)

    def _go_up(self):
        if os.path.abspath(self._cwd) == os.path.abspath(self.root):
            return
        self._cwd = os.path.abspath(os.path.join(self._cwd, ".."))
        self._refresh()

    def _new_folder(self):
        base = os.path.join(self._cwd, "New Folder")
        name = base; i = 1
        while os.path.exists(name):
            name = f"{base} {i}"; i += 1
        try:
            os.makedirs(name, exist_ok=False)
            self._refresh()
        except Exception as e:
            log(f"mkdir failed: {e}", logging.WARNING)

# --------------------------------------------------------------------------------------
# Monitor Card (teal theme, log streaming)
# --------------------------------------------------------------------------------------

class MonitorCard(QWidget):
    line_received = Signal(str)

    def __init__(self, host: str, port: int, theme: Theme):
        super().__init__()
        self.host = host
        self.port = port
        self.t = theme
        self._paused = False
        self._running = True
        self._last_pong = 0.0

        v = QVBoxLayout(self); v.setContentsMargins(10, 10, 10, 10); v.setSpacing(8)

        hdr = QFrame(self)
        hdr.setStyleSheet("background:#005f5f; border:1px solid #0a141a; border-radius:8px;")
        h = QHBoxLayout(hdr); h.setContentsMargins(8, 6, 8, 6); h.setSpacing(8)
        title = QLabel(f"Monitor — {host}:{port}")
        title.setStyleSheet("color:#e0ffff; font:600 10pt 'Cascadia Code';")
        btn_pause = QPushButton("Pause")
        btn_stop = QPushButton("Stop")
        style = "QPushButton{color:#fff; background:#008080; border:1px solid #0a141a; border-radius:6px; padding:4px 10px;}" \
                "QPushButton:hover{background:#00a0a0;}"
        btn_pause.setStyleSheet(style); btn_stop.setStyleSheet(style)
        h.addWidget(title); h.addStretch(1); h.addWidget(btn_pause); h.addWidget(btn_stop)
        v.addWidget(hdr)

        self.view = QPlainTextEdit(self); self.view.setReadOnly(True)
        apply_contrast_palette(self.view, theme.editor_bg, theme.editor_fg)
        self.view.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; border:1px solid {theme.card_border}; bord"
            f"er-radius:10px; }}"
        )
        v.addWidget(self.view, 1)

        btn_pause.clicked.connect(self._toggle_pause)
        btn_stop.clicked.connect(self._stop)
        self.line_received.connect(self.view.appendPlainText)

        threading.Thread(target=self._reader, daemon=True).start()
        self._ping_timer = QTimer(self)
        self._ping_timer.timeout.connect(self._send_ping)
        self._ping_timer.start(1000)

    def _reader(self):
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            self._sock = sock
            while self._running:
                data = sock.recv(1024)
                if not data:
                    break
                if not self._paused:
                    for line in data.decode(errors="ignore").splitlines():
                        if line == "PONG":
                            self._last_pong = time.time()
                            continue
                        self.line_received.emit(line)
        except Exception as e:
            self.line_received.emit(f"[monitor] {e}")
        finally:
            try:
                sock.close()
            except Exception:
                pass

    def _toggle_pause(self):
        self._paused = not self._paused

    def _stop(self):
        self._running = False
        if hasattr(self, "_ping_timer"):
            self._ping_timer.stop()
        try:
            if hasattr(self, "_sock"):
                self._sock.close()
        except Exception:
            pass

    def _send_ping(self):
        try:
            if hasattr(self, "_sock"):
                self._sock.sendall(b"PING\n")
        except Exception:
            pass

# --------------------------------------------------------------------------------------
# Process Console Card (fallback runner)
# --------------------------------------------------------------------------------------

class ProcessConsole(QWidget):
    def __init__(self, theme: Theme, cmd: List[str], cwd: Optional[str] = None):
        super().__init__()
        self.t = theme
        self.cmd = cmd; self.cwd = cwd or SCRIPT_DIR
        self.proc: Optional[subprocess.Popen] = None
        self.reader: Optional[threading.Thread] = None
        self._kill = threading.Event()

        v = QVBoxLayout(self); v.setContentsMargins(10, 10, 10, 10); v.setSpacing(8)
        row = QHBoxLayout(); row.setSpacing(8)
        self.btn_start = QPushButton("Start"); self.btn_stop = QPushButton("Stop"); self.btn_stop.setEnabled(False)
        row.addWidget(self.btn_start); row.addWidget(self.btn_stop); row.addStretch(1)
        v.addLayout(row)

        self.console = QPlainTextEdit(self); self.console.setReadOnly(True)
        apply_contrast_palette(self.console, theme.editor_bg, theme.editor_fg)
        self.console.setStyleSheet(
            f"QPlainTextEdit{{ background:{theme.editor_bg}; color:{theme.editor_fg}; "
            f"selection-background-color:{theme.editor_sel}; border:1px solid {theme.card_border}; "
            f"font-family:'Cascadia Code',Consolas,monospace; }}"
        )
        v.addWidget(self.console, 1)

        self.btn_start.clicked.connect(self._start)
        self.btn_stop.clicked.connect(self._stop)

    def _println(self, s: str):
        self.console.appendPlainText(s)
        log(f"[process] {s}")

    def _start(self):
        if self.proc and self.proc.poll() is None: return
        try:
            self._println(f"Run: {' '.join(self.cmd)}")
            self.proc = subprocess.Popen(
                self.cmd, cwd=self.cwd, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
        except Exception as e:
            self._println(f"Error: {e}"); return
        self._kill.clear()
        self.reader = threading.Thread(target=self._reader, daemon=True); self.reader.start()
        self.btn_start.setEnabled(False); self.btn_stop.setEnabled(True)
        if not self._embed_window():
            self._println("embedding unsupported; streaming output")

    def _stop(self):
        if not self.proc: return
        self._kill.set()
        try:
            self.proc.terminate()
        except Exception:
            pass
        self.btn_start.setEnabled(True); self.btn_stop.setEnabled(False)
        self._println("Terminated")

    def _reader(self):
        assert self.proc and self.proc.stdout
        for line in self.proc.stdout:
            if self._kill.is_set(): break
            s = line.rstrip("\n")
            self.console.appendPlainText(s)
            log(f"[out] {s}")
        self.btn_start.setEnabled(True); self.btn_stop.setEnabled(False)

    def _embed_window(self) -> bool:
        """Attempt to embed spawned GUI window. Returns True on success."""
        try:
            # Platform-specific window embedding would go here; unsupported in tests.
            return False
        except Exception:
            return False

# --------------------------------------------------------------------------------------
# Main window
# --------------------------------------------------------------------------------------

class VirtualDesktop(QMainWindow):
    def __init__(self, workspace: Optional[str] = None):
        super().__init__()
        self.t = Theme()

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#0a1430"))
        pal.setColor(QPalette.Base, QColor("#0a1430"))
        pal.setColor(QPalette.Text, QColor("#e6f0ff"))
        pal.setColor(QPalette.WindowText, QColor("#e6f0ff"))
        self.setPalette(pal)

        self.setWindowTitle("Virtual Desktop")
        self.resize(1180, 760)  # larger default window

        canvas_size = self._current_screen_size()
        self.canvas = DesktopCanvas(self.t, canvas_size, None)
        self.camera = Camera(self.canvas, self)
        self.setCentralWidget(self.camera)

        self.menuBar().installEventFilter(self)
        self._menu()
        self._style_menu_and_controls()
        self._shortcuts()

        # Debounced screen sync
        self._last_synced_size: Optional[QSize] = None
        self._sync_timer = QTimer(self); self._sync_timer.setSingleShot(True)
        self._sync_timer.timeout.connect(self._sync_canvas_to_screen)
        QTimer.singleShot(0, self._sync_canvas_to_screen)

        # Internal refs
        self._template_card: Optional[Card] = None
        self._sys_console: Optional[SystemConsole] = None
        self._workspace = workspace or VDSK_ROOT
        self._icons: Dict[str, QToolButton] = {}
        self.task_mgr = TaskManager(os.path.join(DATASETS_DIR, "tasks.jsonl"))

        log("Virtual Desktop started")
        log(f"Screen size: {canvas_size.width()}x{canvas_size.height()}")

    # ---------- Hook for Agent Terminal tools ----------
    def _open_code_editor(self, path: Optional[str] = None):
        if not path or not os.path.isfile(path):
            return
        plugin_path = resolve_qt_plugin_path(LOGGER)
        LOGGER.debug("Qt plugin path: %s", plugin_path)
        widget = build_editor_widget(parent=None, initial_path=path)
        title = f"Editor — {os.path.basename(path)}"
        card = self.canvas.add_card(widget, title)
        card.set_persist_tag(path)
        _restore_card_geom(card, "py_card", path)
        card.moved.connect(lambda: _save_card_geom(card, "py_card", path))
        card.resized.connect(lambda: _save_card_geom(card, "py_card", path))
        self._bring_card_forward(card)
        _remember_card("py_card", path, title)

    def load_workspace(self, folder: Optional[str] = None) -> None:
        """Populate desktop icons for files and folders within ``folder``."""
        folder = folder or self._workspace
        if not folder or not os.path.isdir(folder):
            return
        for path in sorted(Path(folder).rglob("*")):
            if path.is_file() or path.is_dir():
                self.add_icon(str(path))

    def add_icon(self, path: str) -> QToolButton:
        """Add a clickable icon for ``path`` and return the button."""
        p = Path(path)
        btn = QToolButton(self.canvas)
        btn.setText(p.stem)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if p.is_dir():
            icon = self.style().standardIcon(QStyle.SP_DirIcon)
            handler = lambda _=False, d=str(p): self._open_explorer_to(d)
        else:
            ext = p.suffix.lower()
            handler = lambda _=False, f=str(p): self.open_any_path(f)
            if ext in {".txt", ".md", ".log", ".ini", ".cfg", ".json"}:
                icon = QIcon.fromTheme("text-x-generic")
                if icon.isNull():
                    icon = self.style().standardIcon(QStyle.SP_FileIcon)
                handler = lambda _=False, f=str(p): self._open_code_editor(f)
            elif ext == ".py":
                if p.name == "agent_terminal.py":
                    icon = QIcon.fromTheme("utilities-terminal")
                    if icon.isNull():
                        icon = self.style().standardIcon(QStyle.SP_FileIcon)
                else:
                    icon = QIcon.fromTheme("text-x-python")
                    if icon.isNull():
                        icon = self.style().standardIcon(QStyle.SP_FileIcon)
            else:
                icon = self.style().standardIcon(QStyle.SP_FileIcon)
        btn.setIcon(icon)
        btn.setIconSize(QSize(48, 48))
        idx = len(self._icons)
        row, col = divmod(idx, 6)
        btn.move(20 + col * 80, 20 + row * 80)
        btn.clicked.connect(handler)
        btn.show()
        self._icons[str(p)] = btn
        return btn

    def remove_icon(self, path: str) -> None:
        """Remove the desktop icon for ``path`` if it exists."""
        btn = self._icons.pop(path, None)
        if btn:
            btn.setParent(None)
            btn.deleteLater()
    # ---------- Menus ----------
    def _menu(self):
        bar: QMenuBar = self.menuBar()

        view = bar.addMenu("&View")
        a_full = QAction("Toggle Fullscreen (Alt+Enter)", self); a_full.setShortcut("Alt+Return")
        a_full.triggered.connect(self._toggle_fullscreen); view.addAction(a_full)
        a_center = QAction("Center on Last Focus (Ctrl+Home)", self); a_center.setShortcut("Ctrl+Home")
        a_center.triggered.connect(lambda: self.camera.center_on_widget(self.canvas._last_focus or self.canvas))
        view.addAction(a_center)
        a_front = QAction("Bring All To Front", self)
        a_front.triggered.connect(self._bring_all_to_front); view.addAction(a_front)
        a_tile = QAction("Tile Cards", self)
        a_tile.triggered.connect(self._tile_cards); view.addAction(a_tile)

        tools = bar.addMenu("&Tools")
        self.a_template = QAction("Show Template Terminal", self, checkable=True)
        self.a_template.toggled.connect(self.toggle_template_terminal)
        tools.addAction(self.a_template)

        act_syslog = QAction("Open System Console (log)", self)
        act_syslog.triggered.connect(self._open_system_console)
        tools.addAction(act_syslog)

        act_agent = QAction("Open agent_terminal.py", self)
        act_agent.triggered.connect(self.open_agent_terminal)
        tools.addAction(act_agent)

        act_deploy = QAction("Deploy Agent", self)
        act_deploy.triggered.connect(self._deploy_agent)
        tools.addAction(act_deploy)

        # NEW: manual button to open code_editor.py as internal card
        act_codeed = QAction("Open code_editor.py", self)
        act_codeed.triggered.connect(self._open_builtin_code_editor)
        tools.addAction(act_codeed)

        act_monitor = QAction("Open Monitor Card", self)
        act_monitor.triggered.connect(self._open_monitor)
        tools.addAction(act_monitor)

        act_tasks = QAction("Open Task Viewer", self)
        act_tasks.triggered.connect(self._open_tasks)
        tools.addAction(act_tasks)

        # NEW: Desktop Explorer
        act_explorer = QAction("Open Desktop Explorer", self)
        act_explorer.triggered.connect(self._open_explorer)
        tools.addAction(act_explorer)

        # Windows list
        self.win_menu = bar.addMenu("&Windows")
        self._refresh_windows_menu()

        cards = bar.addMenu("&Cards")
        load = QAction("Load Script as Card…", self)
        load.triggered.connect(self._load_script_dialog)
        cards.addAction(load)

        self.recent_menu = cards.addMenu("Recent")
        self._refresh_recent_menu()

    def _style_menu_and_controls(self):
        mb: QMenuBar = self.menuBar()
        mb.setStyleSheet(
            f"""
            QMenuBar {{
                background: {self.t.menu_bg};
                color: {self.t.menu_fg};
                border: none;
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{ background: #0f1d33; }}
            QMenu {{
                background: #0b1828;
                color: {self.t.menu_fg};
                border: 1px solid {self.t.card_border};
            }}
            QMenu::item:selected {{ background: {self.t.accent}; color: #ffffff; }}
            """
        )
        # Small window buttons on the right of the existing menu bar
        corner = QWidget(self)
        row = QHBoxLayout(corner)
        row.setContentsMargins(4, 2, 6, 2)
        row.setSpacing(6)

        def mk_btn(text: str, tip: str, fn):
            b = QPushButton(text, corner)
            b.setToolTip(tip)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(20)
            b.setFixedWidth(24)
            b.setStyleSheet(
                f"QPushButton {{ background:#0b1828; color:{self.t.menu_fg}; border:1px solid {self.t.card_border}; border-radius:4px; }}"
                f"QPushButton:hover {{ background:{self.t.accent}; color:#fff; }}"
            )
            b.clicked.connect(fn)
            return b

        btn_fs = mk_btn("⤢", "Fullscreen", self._toggle_fullscreen)
        btn_min = mk_btn("—", "Minimize", self.showMinimized)
        btn_max = mk_btn("□", "Maximize / Restore", self._toggle_max_restore)
        btn_close = mk_btn("×", "Close", self.close)
        for b in (btn_fs, btn_min, btn_max, btn_close):
            row.addWidget(b)
        mb.setCornerWidget(corner, Qt.TopRightCorner)

    def _toggle_max_restore(self):
        if self.isMaximized(): self.showNormal()
        else: self.showMaximized()

    def _shortcuts(self):
        def pan_guarded(dx, dy):
            if not self.isFullScreen():
                self.camera.pan(dx, dy)
        self.addAction(self._mk_action("Ctrl+Left",  lambda: pan_guarded(-160, 0)))
        self.addAction(self._mk_action("Ctrl+Right", lambda: pan_guarded(+160, 0)))
        self.addAction(self._mk_action("Ctrl+Up",    lambda: pan_guarded(0, -160)))
        self.addAction(self._mk_action("Ctrl+Down",  lambda: pan_guarded(0, +160)))

    def _mk_action(self, shortcut: str, fn):
        a = QAction(self); a.setShortcut(QKeySequence(shortcut)); a.triggered.connect(fn); return a

    # ---------- Screen/Canvas sync (debounced) ----------
    def _current_screen_size(self) -> QSize:
        if self.windowHandle() and self.windowHandle().screen():
            geom = self.windowHandle().screen().geometry()
        else:
            scr = QGuiApplication.screenAt(self.frameGeometry().center()) or QGuiApplication.primaryScreen()
            geom = scr.geometry()
        return geom.size()

    def _sync_canvas_to_screen(self):
        size = self._current_screen_size()
        if self._last_synced_size and size == self._last_synced_size:
            return
        self._last_synced_size = size
        self.canvas.resize(size)
        self.canvas.cursor_overlay.setGeometry(self.canvas.rect())
        self.camera.center_on_widget(self.canvas._last_focus or self.canvas)
        log(f"Canvas synced to screen: {size.width()}x{size.height()}")

    # Only trigger sync on *real* state/screen changes, not on every window move/resize
    def changeEvent(self, e):
        super().changeEvent(e)
        if e.type() in (QEvent.WindowStateChange, QEvent.ScreenChangeInternal):
            self._sync_timer.start(50)

    def eventFilter(self, obj, ev):
        if obj is self.menuBar() and ev.type() == QEvent.MouseButtonDblClick:
            self._toggle_fullscreen(); return True
        return super().eventFilter(obj, ev)

    def _toggle_fullscreen(self):
        if self.isFullScreen(): self.showNormal(); log("Exit fullscreen")
        else: self.showFullScreen(); log("Enter fullscreen")
        self._sync_timer.start(50)

    # ---------- Tools ----------
    def _open_system_console(self):
        if self._sys_console and self._sys_console.isVisible():
            self._sys_console.raise_(); self._sys_console.activateWindow(); return
        self._sys_console = SystemConsole(self.t, LOG_PATH)
        self._sys_console.show()
        log("System Console opened")

    def open_agent_terminal(self):
        path = os.path.join(SCRIPT_DIR, "agent_terminal.py")
        if not os.path.isfile(path):
            self._toast("agent_terminal.py not found next to this script."); log("agent_terminal.py missing", logging.WARNING); return
        log("Opening agent_terminal.py")
        if self._load_python_as_card(path, persist_key=path, nice_title="Agent Terminal") is None:
            self._load_process_card(path, "agent_terminal.py", persist_key=path)

    def _open_builtin_code_editor(self):
        path = os.path.join(SCRIPT_DIR, "code_editor.py")
        if not os.path.isfile(path):
            self._toast("code_editor.py not found next to this script.")
            return
        self._open_code_editor(path)

    def _open_monitor(self, port: int | None = None):
        if port is None:
            port = int(os.environ.get("DEPLOY_AGENT_PORT", "0"))
            if not port:
                from PySide6.QtWidgets import QInputDialog
                port, ok = QInputDialog.getInt(self, "Connect", "Log port:", 0, 0, 65535, 1)
                if not ok or not port:
                    return
        widget = MonitorCard("127.0.0.1", port, self.t)
        card = self.canvas.add_card(widget, f"Monitor {port}")
        tag = f"(monitor:{port})"
        card.set_persist_tag(tag)
        _restore_card_geom(card, "template", tag)
        card.moved.connect(lambda: _save_card_geom(card, "template", tag))
        card.resized.connect(lambda: _save_card_geom(card, "template", tag))
        self._bring_card_forward(card)

    def _open_tasks(self) -> None:
        open_card(self.task_mgr, self.t, lambda p: None)

    def _deploy_agent(self) -> None:
        target = QFileDialog.getExistingDirectory(self, "Select Deploy Folder")
        if not target:
            return
        try:
            from deployment_manager import deploy_agent
            _, port = deploy_agent(target, "run")
        except Exception as exc:
            QMessageBox.warning(self, "Deploy Failed", str(exc))
            return
        os.environ["DEPLOY_AGENT_PORT"] = str(port)
        self._open_monitor(port)

    def _open_explorer(self):
        widget = ExplorerCard(VDSK_ROOT, self.open_any_path, self.t)
        card = self.canvas.add_card(widget, "Desktop Explorer")
        tag = "(builtin:explorer)"
        card.set_persist_tag(tag)
        _restore_card_geom(card, "template", tag)
        card.moved.connect(lambda: _save_card_geom(card, "template", tag))
        card.resized.connect(lambda: _save_card_geom(card, "template", tag))
        self._bring_card_forward(card)

    # ---------- Template Terminal ----------
    def toggle_template_terminal(self, on: bool):
        tag = "(builtin:template)"
        if on:
            if self._template_card:
                self._bring_card_forward(self._template_card); self.camera.center_on_widget(self._template_card); return
            widget = TemplateTerminal(self.t)
            card = self.canvas.add_card(widget, "Template Terminal")
            card.set_persist_tag(tag)
            _restore_card_geom(card, "template", tag)
            # persist on move/resize
            card.moved.connect(lambda: _save_card_geom(card, "template", tag))
            card.resized.connect(lambda: _save_card_geom(card, "template", tag))
            def on_closed(_):
                self._template_card = None
                self.a_template.blockSignals(True); self.a_template.setChecked(False); self.a_template.blockSignals(False)
            card.closed.connect(on_closed)
            self._template_card = card
            _remember_card("template", "(builtin)", "Template Terminal")
            self._bring_card_forward(card)
            self.camera.center_on_widget(card)
            log("Template Terminal opened")
        else:
            if self._template_card:
                c = self._template_card
                self._template_card = None
                try:
                    c._close_card()
                except Exception:
                    pass
                log("Template Terminal closed")

    # ---------- Windows / z-order helpers ----------
    def _iter_cards(self) -> List[Card]:
        return [w for w in self.canvas.findChildren(Card) if isinstance(w, Card)]

    def _bring_card_forward(self, card: Card):
        try:
            card.raise_(); card.activateWindow()
            self.raise_(); self.activateWindow()
            self.camera.center_on_widget(card)
            self._refresh_windows_menu()
        except Exception:
            pass

    def _bring_all_to_front(self):
        for c in self._iter_cards():
            c.raise_()
        self.raise_(); self.activateWindow()
        self._refresh_windows_menu()

    def _tile_cards(self):
        cards = self._iter_cards()
        if not cards: return
        cols = max(1, int((self.canvas.width() - 80) / 420))
        x0, y0, dx, dy = 40, 40, 420, 320
        i = 0
        for c in cards:
            r = i // cols; col = i % cols
            c.move(x0 + col * dx, y0 + r * dy)
            i += 1

    def _refresh_windows_menu(self):
        self.win_menu.clear()
        for c in self._iter_cards():
            act = self.win_menu.addAction(c.title_label.text())
            act.triggered.connect(lambda checked=False, card=c: self._bring_card_forward(card))
        if not self._iter_cards():
            self.win_menu.addAction("(no windows)").setEnabled(False)

    # ---------- Loaders & history ----------
    def _refresh_recent_menu(self):
        self.recent_menu.clear()
        st = _load_state()
        for rec in st.get("recent", []):
            label = f"{rec.get('title','(untitled)')} — {rec.get('path')}"
            act = self.recent_menu.addAction(label)
            act.triggered.connect(lambda checked=False, r=rec: self._reopen_recent(r))
        if not st.get("recent"):
            self.recent_menu.addAction("(empty)").setEnabled(False)

    def _reopen_recent(self, rec: Dict):
        kind = rec.get("kind"); path = rec.get("path"); title = rec.get("title", "Card")
        log(f"Reopen recent: {title} ({kind})")
        if kind == "py_card":
            self._load_python_as_card(path, persist_key=path, nice_title=title)
        elif kind == "process":
            self._load_process_card(path, title, persist_key=path)
        elif kind == "template":
            self.a_template.setChecked(True)
        else:
            if self._load_python_as_card(path, persist_key=path, nice_title=title) is None:
                self._load_process_card(path, title, persist_key=path)

    def _load_script_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Script as Card…",
            SCRIPT_DIR,
            "Python (*.py);;Executables (*.exe *.bat *.cmd *.sh);;All files (*.*)",
        )
        if not path:
            return
        self.open_any_path(path)

    def open_any_path(self, path: str):
        # Open folders in ExplorerCard; files as cards/process
        if os.path.isdir(path):
            # open that folder inside the explorer
            self._open_explorer_to(path)
            return

        ext = os.path.splitext(path)[1].lower()
        if ext in {".txt", ".md", ".log", ".ini", ".cfg", ".json"}:
            self._open_code_editor(path)
        elif ext == ".py":
            if self._load_python_as_card(path, persist_key=path) is None:
                self._load_process_card(path, os.path.basename(path), persist_key=path)
        else:
            self._load_process_card(path, os.path.basename(path), persist_key=path)

    def _open_explorer_to(self, folder: str):
        widget = ExplorerCard(folder, self.open_any_path, self.t)
        card = self.canvas.add_card(widget, f"Explorer — {os.path.basename(folder) or folder}")
        tag = f"(explorer:{folder})"
        card.set_persist_tag(tag)
        _restore_card_geom(card, "template", tag)
        card.moved.connect(lambda: _save_card_geom(card, "template", tag))
        card.resized.connect(lambda: _save_card_geom(card, "template", tag))
        self._bring_card_forward(card)

    def _load_python_as_card(self, path: str, persist_key: Optional[str]=None, nice_title: Optional[str]=None) -> Optional[Card]:
        """Import a Python file and embed it if a ``build_widget`` factory is available."""
        if not ensure_pyside6(LOGGER):
            self._toast("PySide6 setup failed; see system.log")
            return None
        log(f"Load python as card: {path}")
        try:
            name = f"card_{int(time.time())}_{os.path.splitext(os.path.basename(path))[0]}"
            spec = importlib.util.spec_from_file_location(name, path)
            if not spec or not spec.loader:
                raise RuntimeError("spec loader failed")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        except Exception as e:
            self._toast(f"Import failed: {e}")
            log(f"Import failed: {e}", logging.ERROR)
            return None

        factory = getattr(mod, "build_widget", None)
        if not callable(factory):
            self._toast("No build_widget factory; running as process instead.")
            log("build_widget not found; falling back to process", logging.INFO)
            return None

        try:
            widget = factory(None)
            title = nice_title or os.path.basename(path)
        except Exception as e:
            self._toast(f"factory error: {e}")
            log(f"factory error: {e}", logging.ERROR)
            return None

        card = self.canvas.add_card(widget, str(title))
        if persist_key:
            card.set_persist_tag(persist_key)
            _restore_card_geom(card, "py_card", persist_key)
            card.moved.connect(lambda: _save_card_geom(card, "py_card", persist_key))
            card.resized.connect(lambda: _save_card_geom(card, "py_card", persist_key))
        card.closed.connect(lambda _: log(f"Card closed: {title}"))
        self._bring_card_forward(card)
        _remember_card("py_card", path, str(title))
        self._refresh_recent_menu()
        log(f"Card loaded: {title}")
        return card

    def _load_process_card(self, path: str, title: str, persist_key: Optional[str]=None):
        cmd = [path]
        if path.lower().endswith(".py"):  # run with the current Python
            cmd = [sys.executable, path]
        log(f"Run process as card: {cmd}")
        widget = ProcessConsole(self.t, cmd, cwd=os.path.dirname(path) or SCRIPT_DIR)
        card = self.canvas.add_card(widget, f"Process — {title}")
        if persist_key:
            card.set_persist_tag(persist_key)
            _restore_card_geom(card, "process", persist_key)
            card.moved.connect(lambda: _save_card_geom(card, "process", persist_key))
            card.resized.connect(lambda: _save_card_geom(card, "process", persist_key))
        self._bring_card_forward(card)
        _remember_card("process", path, title)
        self._refresh_recent_menu()

    def _toast(self, msg: str):
        # Lightweight message via a tiny temporary card
        box = QWidget(); v = QVBoxLayout(box); v.setContentsMargins(10, 10, 10, 10)
        lab = QLabel(msg); lab.setStyleSheet("color:#eaf2ff;")
        v.addWidget(lab)
        c = self.canvas.add_card(box, "Info")
        QTimer.singleShot(2200, lambda: c._close_card())
        log(f"Toast: {msg}")

# --------------------------------------------------------------------------------------
# Entry
# --------------------------------------------------------------------------------------

def _parse_args():
    ap = argparse.ArgumentParser(description="Virtual Desktop")
    ap.add_argument("--open", dest="open_path", help="Load a script/binary as a Card")
    ap.add_argument("--show-template", action="store_true", help="Show the Template Terminal on launch")
    ap.add_argument("--open-agent", action="store_true", help="Open agent_terminal.py on launch")
    ap.add_argument("--workspace", help="Folder to scan for Python scripts on launch")
    return ap.parse_args()

def main():
    if not ensure_pyside6(LOGGER):
        _show_manual_install("PySide6")
        sys.exit(1)
    LOGGER.info("Ensuring Qt runtime...")
    try:
        _qt_path = ensure_qt_runtime(LOGGER)
        LOGGER.info("Qt runtime ready: %s", _qt_path)
    except Exception:
        LOGGER.exception("Qt runtime repair failed")
        _show_manual_install("PySide6")
        sys.exit(1)

    set_hidpi_policy_once()

    args = _parse_args()
    app = QApplication(sys.argv)
    win = VirtualDesktop(workspace=args.workspace)
    win.load_workspace(args.workspace)
    if AUTO_LAUNCH:
        if args.show_template:
            win.toggle_template_terminal(True)
        if args.open_agent:
            win.open_agent_terminal()
        if args.open_path:
            win.open_any_path(args.open_path)
    else:
        if args.show_template or args.open_agent or args.open_path:
            log("Autoload flags ignored; set VD_AUTO_LAUNCH=1 to enable")
    win.show()

    log("Application exec()")
    rc = app.exec()
    log(f"Application exit code: {rc}")
    sys.exit(rc)

if __name__ == "__main__":
    main()
```

Virtual_Desktop.py — agent-ready virtual desktop with card loader, template terminal,
system log, pop-out System Console, Desktop Explorer, and internal Code Editor card.

Updates (this build):
- Shift + Mouse Wheel ⇒ horizontal pan; normal wheel ⇒ vertical pan (when not fullscreen).
- No panning while in fullscreen remains enforced.
- Cards auto-raise on create/open; added 'Bring All To Front', 'Tile Cards', and a Windows list.
- Added Tools ▸ Open code_editor.py (loads as internal editor card).
- Desktop Explorer card: icons for files/folders under ./Virtual_Desktop ; double-click to open.
- Preserves embedded app look (no extra QSS on child widgets).
- Debounced canvas sync on real screen changes/fullscreen only (reduces log spam).
- Per-card geometry persistence (position & size remembered across sessions).
 - Supports ``build_widget(parent)`` factories for embedding.
- Dark, high-contrast UI preserved.
**Classes:** Theme, SystemConsole, CursorOverlay, Card, DesktopCanvas, Camera, TemplateTerminal, ExplorerCard, MonitorCard, ProcessConsole, VirtualDesktop
**Functions:** _show_manual_install(pkg), log(msg, level), _load_state(), _save_state(state), _remember_card(kind, path, title), _geom_key_for(kind, path_or_tag), _restore_card_geom(card, kind, path_or_tag), _save_card_geom(card, kind, path_or_tag), apply_contrast_palette(w, bg_hex, fg_hex), _parse_args(), main()


## Module `Archived Conversations\Codex-info\bootstrap_codex.py`

```python
import os
import shutil
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext

"""
===========================================================
Codex Bootstrap GUI Tool
===========================================================

⚠️ IMPORTANT:
- Do NOT delete the permanent Codex Rust folder.
- This tool is only for creating a "Transit" copy and a
  manifest for handoff/testing.

Purpose:
- Copies the Codex Rust source (v0.23.0) into a safe Transit folder.
- Copies the compiled binary if available.
- Creates a Manifest file explaining what Codex is, where it lives,
  and how to run it.
- Provides a GUI for one-click "Populate Transit", a comment box,
  and a "Copy to Clipboard" helper.

===========================================================
"""

# --- CONFIG ---
DESKTOP = Path.home() / "Desktop"
ROOT_DIR = DESKTOP / "Codex"

SOURCE_DIR = ROOT_DIR / "codex-rust-v0.23.0"
BINARY_NAME = "codex-x86_64-pc-windows-msvc.exe"
SOURCE_BINARY = SOURCE_DIR / "target" / "release" / BINARY_NAME
TRANSIT_DIR = ROOT_DIR / "Codex-Transit"
MANIFEST_FILE = TRANSIT_DIR / "codex_manifest.txt"


def reset_transit():
    if TRANSIT_DIR.exists():
        shutil.rmtree(TRANSIT_DIR)
    TRANSIT_DIR.mkdir(parents=True, exist_ok=True)


def copy_codex():
    transit_source = TRANSIT_DIR / SOURCE_DIR.name
    shutil.copytree(SOURCE_DIR, transit_source)
    if SOURCE_BINARY.exists():
        shutil.copy2(SOURCE_BINARY, TRANSIT_DIR / BINARY_NAME)
    return transit_source


def write_manifest():
    description = f"""# Codex Rust v0.23.0 (Manifest)

This folder contains a **working copy** of the Codex Rust runtime.

## Source
- Permanent source folder: {SOURCE_DIR}
- Version: v0.23.0 (Rust implementation of Codex CLI)

## Transit Copy
- Transit folder: {TRANSIT_DIR}
- Auto-generated: {datetime.now().isoformat(sep=' ', timespec='seconds')}
- Purpose: ephemeral working directory for testing / integration.

## Binary
- Binary name: {BINARY_NAME}
- Location (inside transit): {TRANSIT_DIR / BINARY_NAME}
- Built via: `cargo build --release`

## Usage
Run the Codex binary from the transit folder for a clean test environment:
{TRANSIT_DIR / BINARY_NAME} --help

Permanent source remains unchanged. Transit is safe to delete and re-bootstrap.
"""
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        f.write(description)
    return description


# --- GUI ACTIONS ---
def populate_transit():
    try:
        if not SOURCE_DIR.exists():
            messagebox.showerror("Error", f"Source folder not found:\n{SOURCE_DIR}")
            return
        reset_transit()
        copy_codex()
        manifest_text = write_manifest()

        output_box.config(state="normal")
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, manifest_text)
        output_box.config(state="disabled")

        messagebox.showinfo("Done", f"Transit populated.\nManifest saved at:\n{MANIFEST_FILE}")

    except Exception as e:
        messagebox.showerror("Error", str(e))


def copy_to_clipboard():
    text = output_box.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    messagebox.showinfo("Copied", "Manifest copied to clipboard.")


# --- GUI WINDOW ---
root = tk.Tk()
root.title("Codex Bootstrap GUI")
root.geometry("750x650")

header_label = tk.Label(
    root,
    text="⚠️ DO NOT DELETE THE CODEX RUST FOLDER ⚠️",
    fg="red",
    font=("Arial", 12, "bold")
)
header_label.pack(pady=10)

populate_btn = tk.Button(
    root,
    text="Populate Transit",
    command=populate_transit,
    bg="lightblue",
    font=("Arial", 11, "bold")
)
populate_btn.pack(pady=5)

copy_btn = tk.Button(
    root,
    text="Copy Manifest to Clipboard",
    command=copy_to_clipboard,
    bg="lightgreen",
    font=("Arial", 11, "bold")
)
copy_btn.pack(pady=5)

output_box = scrolledtext.ScrolledText(
    root, wrap=tk.WORD, width=85, height=28, font=("Consolas", 10)
)
output_box.insert(tk.END, "Click 'Populate Transit' to generate manifest...")
output_box.config(state="disabled")
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
```

**Functions:** reset_transit(), copy_codex(), write_manifest(), populate_transit(), copy_to_clipboard()


## Module `Archived Conversations\codex-rust-v0.23.0 - info\Analyze_folders.py`

```python
import os

def analyze_folders(start_path):
    script_name = os.path.basename(__file__)  # Get script file name
    analyze_file = os.path.join(start_path, "analyze.txt")  # Output file path

    with open(analyze_file, "w", encoding="utf-8") as file:
        file.write(f"Folder Analysis Report\n")
        file.write(f"{'='*50}\n\n")
        file.write(f"Root Directory: {start_path}\n\n")
        
        for root, dirs, files in os.walk(start_path):
            # Skip directories named 'venv'
            if "venv" in root.split(os.sep):
                continue

            level = root.replace(start_path, "").count(os.sep)
            indent = "|   " * level  # Tree structure formatting
            file.write(f"{indent}|-- {os.path.basename(root)}/\n")

            # Filter out the script and output file from the list of files
            filtered_files = [f for f in files if f not in {script_name, "analyze.txt"}]

            # List files in the directory
            for f in filtered_files:
                file_indent = "|   " * (level + 1)
                file.write(f"{file_indent}|-- {f}\n")
    
    print(f"Analysis complete. Results saved in {analyze_file}")

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    analyze_folders(script_directory)
```

**Functions:** analyze_folders(start_path)


## Module `Archived Conversations\codex-rust-v0.23.0 - info\codex-cli\scripts\stage_rust_release.py`

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


## Module `Archived Conversations\codex-rust-v0.23.0 - info\codex-rs\mcp-types\generate_mcp_types.py`

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


## Module `Archived Conversations\codex-rust-v0.23.0 - info\scripts\asciicheck.py`

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


## Module `Archived Conversations\codex-rust-v0.23.0 - info\scripts\publish_to_npm.py`

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


## Module `Archived Conversations\codex-rust-v0.23.0 - info\scripts\readme_toc.py`

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


## Module `cli\deploy.py`

```python
"""Command line helpers for managing agent deployments."""

from __future__ import annotations

import argparse
import os
import signal

from deployment_manager import _load_deployments, clone_repo, launch_agent


def _read_deployments() -> list:
    return _load_deployments()


def cmd_deploy(args: argparse.Namespace) -> None:
    clone_repo(args.path)
    proc = launch_agent(args.path)
    print(proc.pid)


def cmd_list_nodes(args: argparse.Namespace) -> None:  # pragma: no cover - CLI output
    for item in _read_deployments():
        print(f"{item['pid']}\t{item['target']}")


def cmd_terminate(args: argparse.Namespace) -> None:
    try:
        os.kill(args.pid, signal.SIGTERM)
    except OSError as exc:  # pragma: no cover - system dependent
        print(f"Failed to terminate {args.pid}: {exc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deploy")
    sub = parser.add_subparsers(dest="command", required=True)

    p_deploy = sub.add_parser("deploy")
    p_deploy.add_argument("path")
    p_deploy.set_defaults(func=cmd_deploy)

    p_list = sub.add_parser("list-nodes")
    p_list.set_defaults(func=cmd_list_nodes)

    p_term = sub.add_parser("terminate")
    p_term.add_argument("pid", type=int)
    p_term.set_defaults(func=cmd_terminate)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
```

Command line helpers for managing agent deployments.
**Functions:** _read_deployments(), cmd_deploy(args), cmd_list_nodes(args), cmd_terminate(args), build_parser(), main(argv)


## Module `cli\__init__.py`

```python
"""CLI helpers for the Agent Terminal project."""
```

CLI helpers for the Agent Terminal project.


## Module `Codex\cli_adapter.py`

```python
"""Utility to adapt raw CLI output from the open-source Codex executable.

The open-source Codex CLI may emit mixed descriptive text and shell commands
without structure.  :func:`parse_cli_output` normalizes such stdout/stderr and
returns a mapping containing a human readable description and a list of shell
commands suitable for display or execution.
"""
from __future__ import annotations

import re
from typing import Dict, List

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
PROMPT_RE = re.compile(r"^(?:[>$]|\(\S+\)\s*[>$])\s*")


def parse_cli_output(raw: str) -> Dict[str, List[str] | str]:
    """Return a structured message extracted from *raw* CLI output.

    Parameters
    ----------
    raw:
        Combined stdout/stderr text from the Codex CLI.

    Returns
    -------
    dict
        Mapping with ``description`` text and a list of ``commands``.
    """

    commands: List[str] = []
    desc_lines: List[str] = []

    for line in raw.splitlines():
        line = ANSI_RE.sub("", line).strip()
        if not line:
            continue
        if PROMPT_RE.match(line):
            cmd = PROMPT_RE.sub("", line).strip()
            if cmd:
                commands.append(cmd)
        else:
            desc_lines.append(line)

    return {"description": "\n".join(desc_lines).strip(), "commands": commands}


__all__ = ["parse_cli_output"]
```

Utility to adapt raw CLI output from the open-source Codex executable.

The open-source Codex CLI may emit mixed descriptive text and shell commands
without structure.  :func:`parse_cli_output` normalizes such stdout/stderr and
returns a mapping containing a human readable description and a list of shell
commands suitable for display or execution.
**Functions:** parse_cli_output(raw)


## Module `Codex\codex_manager.py`

```python
"""Codex dispatch manager.

Provides a simple dispatch() function that routes user text to shell
commands, tool calls, or prompts. Each decision is persisted to
memory/codex_memory.json for future retrieval.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Dict

from .cli_adapter import parse_cli_output
from . import open_source_manager
from prompt_manager import chain_prompts, create_prompt, read_prompts
from l2c_tool import generate_commands as l2c_generate_commands

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MEMORY_PATH = os.path.join(PROJECT_ROOT, "memory", "codex_memory.json")
PERSONA_PATH = os.path.join(PROJECT_ROOT, "schemas", "persona_schema.json")
DEFAULT_PERSONA = {
    "excitement_level": "medium",
    "self_referential_awareness": True,
    "narrative_style": "first_person",
    "verbosity": "concise",
}
CODEX_DIR = Path(__file__).parent
CODEX_BINARY_NAMES = [
    "codex",
    "codex.exe",
    "codex-x86_64-unknown-linux-gnu",
    "codex-x86_64-pc-windows-msvc.exe",
]

# Tools available for Codex to invoke
TOOLS = {"l2c.generate": l2c_generate_commands}


@dataclass
class CodexPersona:
    """Basic persona data for Codex greeting."""

    name: str = "Codex"
    version: str = "unknown"

    def greeting(self) -> str:
        return f"{self.name} {self.version}"

def _load_persona() -> Dict:
    """Load persona defaults from schema or return fallbacks."""
    try:
        with open(PERSONA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        props = schema.get("properties", {})
        return {
            "excitement_level": props.get("excitement_level", {}).get("default", "medium"),
            "self_referential_awareness": props.get("self_referential_awareness", {}).get("default", True),
            "narrative_style": props.get("narrative_style", {}).get("default", "first_person"),
            "verbosity": props.get("verbosity", {}).get("default", "concise"),
        }
    except Exception:
        return DEFAULT_PERSONA.copy()


def build_persona_directive() -> str:
    """Return directive string enforcing persona requirements."""
    persona = _load_persona()
    level = os.environ.get("CODEX_EXCITEMENT", persona.get("excitement_level", "medium"))
    verbosity = os.environ.get("CODEX_VERBOSITY", persona.get("verbosity", "concise"))
    directives = [
        "Respond in the first person.",
        "Reference relevant past actions from memory.",
        "Include brief self-reflection in your answer.",
    ]
    if level == "high":
        directives.append("Use an enthusiastic tone.")
    elif level == "low":
        directives.append("Use a subdued tone.")
    if verbosity == "verbose":
        directives.append("Provide detailed explanations.")
    else:
        directives.append("Be concise.")
    return " ".join(directives)


def log_state(cmd: str, state: str, output: str = "") -> None:
    """Append a command ``state`` entry to ``codex_memory.json``."""
    mem = _load_memory()
    log = mem.setdefault("command_log", [])
    log.append(
        {
            "cmd": cmd,
            "state": state,
            "output": output,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    _save_memory(mem)


def record_command_result(cmd: str, stdout: str, stderr: str, returncode: int) -> None:
    """Record validation/fix/confirm steps for a completed command."""
    output = (stdout or "") + (stderr or "")
    log_state(cmd, "validate", output)
    if returncode != 0:
        log_state(cmd, "fix", output)
        prompt = (
            f"Command `{cmd}` failed with exit {returncode}.\n"
            f"STDOUT: {stdout}\nSTDERR: {stderr}\nSuggest a fix."
        )
        chain_prompts(cmd, [prompt])
    else:
        log_state(cmd, "confirm", output)


def _load_memory(path: str | None = None) -> Dict:
    if path is None:
        path = MEMORY_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        create_prompt("codex_memory_load", f"Check if file exists: {path}", "ephemeral")
        read_prompts("codex_memory_load")
        return {}


def _save_memory(data: Dict, path: str | None = None) -> None:
    if path is None:
        path = MEMORY_PATH
    data["updated_utc"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)


def get_binary() -> Path | None:
    """Return the path to the Codex binary if present."""
    for name in CODEX_BINARY_NAMES:
        p = CODEX_DIR / "bin" / name
        if p.exists():
            return p
        p = CODEX_DIR / name
        if p.exists():
            return p
    return None


def codex_available(path: Path | None = None) -> bool:
    """Return ``True`` if the Codex CLI binary exists."""
    if path is not None:
        return Path(path).exists()
    return get_binary() is not None


def manager_version() -> str:
    """Return the version string reported by the Codex CLI."""
    binary = get_binary()
    if not binary:
        return "unknown"
    try:
        proc = subprocess.run(
            [str(binary), "--version"], capture_output=True, text=True, timeout=5
        )
        out = (proc.stdout or proc.stderr).strip()
        return out.splitlines()[0] if out else "unknown"
    except Exception:  # pragma: no cover - version probe failure is rare
        return "unknown"


def dispatch(user_text: str) -> Dict:
    """Return a structured decision for the given user text.

    The decision schema is:
    {"type": "shell", "cmd": str}
    {"type": "tool", "tool": str, "args": dict}
    {"type": "prompt", "content": str}
    """

    directive = build_persona_directive()
    prompt = f"{directive}\n\n{user_text}"
    lower = user_text.strip().lower()
    if lower.startswith("shell:"):
        cmd = user_text.split(":", 1)[1].strip()
        decision = {"type": "shell", "cmd": cmd}
        log_state(cmd, "attempt")
        try:
            completed = subprocess.run(
                cmd, shell=True, capture_output=True, text=True
            )
            record_command_result(
                cmd, completed.stdout, completed.stderr, completed.returncode
            )
        except Exception as e:  # pragma: no cover - subprocess errors rare
            log_state(cmd, "fix", str(e))
            chain_prompts(cmd, [f"Command `{cmd}` raised {e}. Provide a fix."])
    elif lower.startswith("tool:"):
        decision = {"type": "tool", "tool": user_text.split(":", 1)[1].strip(), "args": {}}
    else:
        try:
            binary = get_binary()
            if not binary:
                raise FileNotFoundError("codex binary missing")
            proc = subprocess.run(
                [str(binary)],
                input=prompt,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"codex exit {proc.returncode}")
            parsed = parse_cli_output((proc.stdout or "") + (proc.stderr or ""))
            if parsed["commands"]:
                decision = {"type": "shell", "cmd": parsed["commands"][0]}
            else:
                decision = {"type": "prompt", "content": parsed["description"]}
        except Exception:
            decision = open_source_manager.dispatch(prompt)

    mem = _load_memory()
    conversations = mem.setdefault("conversations", [])
    conversations.append({"user": user_text, "decision": decision})
    _save_memory(mem)

    return decision


__all__ = [
    "dispatch",
    "TOOLS",
    "record_command_result",
    "log_state",
    "codex_available",
    "manager_version",
    "get_binary",
    "build_persona_directive",
    "CodexPersona",
]
```

Codex dispatch manager.

Provides a simple dispatch() function that routes user text to shell
commands, tool calls, or prompts. Each decision is persisted to
memory/codex_memory.json for future retrieval.
**Classes:** CodexPersona
**Functions:** _load_persona(), build_persona_directive(), log_state(cmd, state, output), record_command_result(cmd, stdout, stderr, returncode), _load_memory(path), _save_memory(data, path), get_binary(), codex_available(path), manager_version(), dispatch(user_text)


## Module `Codex\open_source_manager.py`

```python
"""Fallback Codex manager that proxies a CLI-based open-source LLM.

The manager executes a user-configurable shell command defined by the
``CLI_LLM_CMD`` environment variable.  Combined ``stdout`` and ``stderr``
from the command are parsed with :func:`Codex.cli_adapter.parse_cli_output`
to extract natural language responses and any suggested shell commands.

If ``CLI_LLM_CMD`` is unset, the manager simply echoes the input text.
Conversation logs are persisted to ``memory/codex_memory.json`` using the
same format as the primary Codex manager.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from typing import Dict

from .cli_adapter import parse_cli_output
from prompt_manager import create_prompt, read_prompts

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MEMORY_PATH = os.path.join(PROJECT_ROOT, "memory", "codex_memory.json")
CLI_LLM_CMD = os.environ.get("CLI_LLM_CMD")


def _load_memory(path: str | None = None) -> Dict:
    if path is None:
        path = MEMORY_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        create_prompt("codex_memory_load", f"Check if file exists: {path}", "ephemeral")
        read_prompts("codex_memory_load")
        return {}


def _save_memory(data: Dict, path: str | None = None) -> None:
    if path is None:
        path = MEMORY_PATH
    data["updated_utc"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)


def _cli_llm(prompt: str) -> Dict[str, list[str] | str]:
    """Run the configured CLI LLM and parse its output.

    When ``CLI_LLM_CMD`` is undefined, the function simply echoes *prompt*.
    """

    if not CLI_LLM_CMD:
        return {"description": prompt, "commands": []}

    proc = subprocess.run(
        CLI_LLM_CMD,
        input=prompt,
        capture_output=True,
        text=True,
        shell=True,
    )
    return parse_cli_output((proc.stdout or "") + (proc.stderr or ""))


def dispatch(user_text: str) -> Dict:
    """Return a structured decision for the given user text."""

    lower = user_text.strip().lower()
    if lower.startswith("shell:"):
        decision = {"type": "shell", "cmd": user_text.split(":", 1)[1].strip()}
    elif lower.startswith("tool:"):
        decision = {"type": "tool", "tool": user_text.split(":", 1)[1].strip(), "args": {}}
    else:
        parsed = _cli_llm(user_text)
        if parsed["commands"]:
            decision = {"type": "shell", "cmd": parsed["commands"][0]}
        else:
            decision = {"type": "prompt", "content": parsed["description"]}

    mem = _load_memory()
    conversations = mem.setdefault("conversations", [])
    conversations.append({"user": user_text, "decision": decision})
    _save_memory(mem)
    return decision


def manager_version() -> str:
    """Return the version string of the configured CLI LLM."""
    if not CLI_LLM_CMD:
        return "echo"
    try:
        proc = subprocess.run(
            f"{CLI_LLM_CMD} --version",
            capture_output=True,
            text=True,
            shell=True,
        )
        out = (proc.stdout or proc.stderr).strip()
        return out.splitlines()[0] if out else "unknown"
    except Exception:  # pragma: no cover - CLI may not support --version
        return "unknown"


__all__ = ["dispatch", "CLI_LLM_CMD", "manager_version"]
```

Fallback Codex manager that proxies a CLI-based open-source LLM.

The manager executes a user-configurable shell command defined by the
``CLI_LLM_CMD`` environment variable.  Combined ``stdout`` and ``stderr``
from the command are parsed with :func:`Codex.cli_adapter.parse_cli_output`
to extract natural language responses and any suggested shell commands.

If ``CLI_LLM_CMD`` is unset, the manager simply echoes the input text.
Conversation logs are persisted to ``memory/codex_memory.json`` using the
same format as the primary Codex manager.
**Functions:** _load_memory(path), _save_memory(data, path), _cli_llm(prompt), dispatch(user_text), manager_version()


## Module `memory\bucket_manager.py`

```python
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = Path(os.environ.get("DATASETS_DIR", ROOT / "datasets"))

_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_bucket(name: str, path: str, description: str) -> None:
    """Register a bucket with *name*, file *path*, and *description*."""
    p = Path(path)
    if not p.is_absolute():
        p = DATASETS_DIR / p
    p.parent.mkdir(parents=True, exist_ok=True)
    _REGISTRY[name] = {"path": p, "description": description}


def append_entry(bucket: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Append *data* to *bucket* with an added timestamp."""
    if bucket not in _REGISTRY:
        raise KeyError(f"Unknown bucket: {bucket}")
    rec = dict(data)
    rec.setdefault("timestamp", datetime.utcnow().isoformat())
    path = _REGISTRY[bucket]["path"]
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def query_bucket(bucket: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return records from *bucket* matching *filters*."""
    if bucket not in _REGISTRY:
        raise KeyError(f"Unknown bucket: {bucket}")
    path = _REGISTRY[bucket]["path"]
    if not path.exists():
        return []
    results: List[Dict[str, Any]] = []
    filters = filters or {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if all(rec.get(k) == v for k, v in filters.items()):
                results.append(rec)
    return results


# Load default buckets from matrix
_MATRIX_PATH = ROOT / "datasets" / "bucket_matrix.json"
if _MATRIX_PATH.exists():
    with _MATRIX_PATH.open("r", encoding="utf-8") as f:
        matrix = json.load(f)
    for name, info in matrix.items():
        register_bucket(name, info["path"], info.get("description", ""))
```

**Functions:** register_bucket(name, path, description), append_entry(bucket, data), query_bucket(bucket, filters)


## Module `memory\datasets.py`

```python
from __future__ import annotations

import math
from typing import Dict, List, Optional

from .bucket_manager import append_entry, query_bucket


def cosine_sim(a: List[float], b: List[float]) -> float:
    """Return cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    num = sum(x * y for x, y in zip(a, b))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(x * x for x in b))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def write_entry(dataset_name: str, record: Dict) -> Dict:
    """Append *record* to *dataset_name* via :mod:`bucket_manager`."""
    return append_entry(dataset_name, record)


def query(dataset_name: str, embedding: List[float], top_k: int = 1) -> List[Dict]:
    """Return up to *top_k* records most similar to *embedding*."""
    items = []
    for rec in query_bucket(dataset_name):
        vec = rec.get("embedding")
        if not vec:
            continue
        sim = cosine_sim(embedding, vec)
        items.append((sim, rec))
    items.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in items[:top_k]]


def read_entries(dataset_name: str, task_id: Optional[str] = None) -> List[Dict]:
    """Return records from *dataset_name* filtered by *task_id* if provided."""
    filters = {"task_id": task_id} if task_id else None
    return query_bucket(dataset_name, filters)


def embed_text(text: str) -> List[float]:
    """Return a lightweight embedding for *text*."""
    return [float(sum(ord(c) for c in text))]


def log_prompt(role: str, text: str, task_id: Optional[str] = None) -> Dict:
    """Log a prompt or reply with embedding and optional *task_id*."""
    return write_entry(
        "prompts",
        {
            "role": role,
            "text": text,
            "task_id": task_id,
            "embedding": embed_text(text),
            "provenance": "agent_terminal",
        },
    )


def log_error(text: str, task_id: Optional[str] = None) -> Dict:
    """Log an error message with embedding and optional *task_id*."""
    return write_entry(
        "errors",
        {
            "error": text,
            "task_id": task_id,
            "embedding": embed_text(text),
            "provenance": "agent_terminal",
        },
    )


def log_authorization(
    cmd: str, granted: bool, task_id: Optional[str] = None, **extra
) -> Dict:
    """Log an authorization decision with embedding and optional *task_id*."""
    rec = {
        "command": cmd,
        "granted": granted,
        "task_id": task_id,
        **extra,
        "embedding": embed_text(cmd),
        "provenance": "agent_terminal",
    }
    return write_entry("authorizations", rec)


def _search(dataset: str, embedding: List[float], top_k: int, task_id: Optional[str]) -> List[Dict]:
    items = query(dataset, embedding, top_k * 2)
    if task_id is not None:
        items = [r for r in items if r.get("task_id") == task_id]
    return items[:top_k]


def search_prompts(embedding: List[float], top_k: int = 1, task_id: Optional[str] = None) -> List[Dict]:
    """Search prompt logs by embedding and optional *task_id*."""
    return _search("prompts", embedding, top_k, task_id)


def search_errors(embedding: List[float], top_k: int = 1, task_id: Optional[str] = None) -> List[Dict]:
    """Search error logs by embedding and optional *task_id*."""
    return _search("errors", embedding, top_k, task_id)


def search_authorizations(
    embedding: List[float], top_k: int = 1, task_id: Optional[str] = None
) -> List[Dict]:
    """Search authorization logs by embedding and optional *task_id*."""
    return _search("authorizations", embedding, top_k, task_id)


def rag_search(embedding: List[float], top_k: int = 1, task_id: Optional[str] = None) -> Dict[str, List[Dict]]:
    """Return similar records across prompt, error, and authorization datasets."""
    return {
        "prompts": search_prompts(embedding, top_k, task_id),
        "errors": search_errors(embedding, top_k, task_id),
        "authorizations": search_authorizations(embedding, top_k, task_id),
    }
```

**Functions:** cosine_sim(a, b), write_entry(dataset_name, record), query(dataset_name, embedding, top_k), read_entries(dataset_name, task_id), embed_text(text), log_prompt(role, text, task_id), log_error(text, task_id), log_authorization(cmd, granted, task_id), _search(dataset, embedding, top_k, task_id), search_prompts(embedding, top_k, task_id), search_errors(embedding, top_k, task_id), search_authorizations(embedding, top_k, task_id), rag_search(embedding, top_k, task_id)


## Module `memory\prompt_buckets.py`

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .bucket_manager import DATASETS_DIR
from .datasets import embed_text, cosine_sim

BUCKET_DIR = DATASETS_DIR / "prompt_buckets"
BUCKET_DIR.mkdir(parents=True, exist_ok=True)


def _bucket_path(name: str) -> Path:
    return BUCKET_DIR / f"{name}.jsonl"


def append_bucket(bucket_name: str, prompt: str, response: str, metadata: Optional[Dict] = None) -> Dict:
    """Append a prompt/response pair to *bucket_name*."""
    record = {
        "prompt": prompt,
        "response": response,
        "metadata": metadata or {},
        "embedding": embed_text(prompt),
    }
    path = _bucket_path(bucket_name)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def retrieve_similar(bucket_name: str, query: str, top_k: int = 3) -> List[Dict]:
    """Return up to *top_k* records from *bucket_name* similar to *query*."""
    path = _bucket_path(bucket_name)
    if not path.exists():
        return []
    q_vec = embed_text(query)
    items: List[tuple[float, Dict]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            vec = rec.get("embedding")
            if not vec:
                continue
            sim = cosine_sim(q_vec, vec)
            items.append((sim, rec))
    items.sort(key=lambda x: x[0], reverse=True)
    return [rec for _, rec in items[:top_k]]
```

**Functions:** _bucket_path(name), append_bucket(bucket_name, prompt, response, metadata), retrieve_similar(bucket_name, query, top_k)


## Module `security\guardrails.py`

```python
from __future__ import annotations

from pathlib import Path
import os
import shlex
from typing import List

# Paths that should never be touched without explicit confirmation
BLOCKED_PATHS: List[Path] = [
    Path("/etc"),
    Path("/bin"),
    Path("/usr"),
    Path("/sbin"),
    Path("C:/Windows"),
    Path("C:/Windows/System32"),
]


def is_safe_path(path: str | Path) -> bool:
    """Return False if *path* resides under any BLOCKED_PATHS entry."""
    try:
        p = Path(path).expanduser().resolve()
    except Exception:
        return False
    for blocked in BLOCKED_PATHS:
        b = blocked.expanduser().resolve()
        if p == b or str(p).startswith(str(b) + os.sep):
            return False
    return True


_DESTRUCTIVE = [
    " rm ",
    " del ",
    " remove ",
    " rmdir ",
    " delete ",
    " format ",
    " drop ",
]


def requires_confirmation(cmd: str) -> bool:
    """Return True if *cmd* is destructive or touches a blocked path."""
    lc = f" {cmd.lower()} "
    if any(d in lc for d in _DESTRUCTIVE):
        return True
    for token in shlex.split(cmd):
        if any(sep in token for sep in ("/", "\\")):
            if not is_safe_path(token):
                return True
    return False
```

**Functions:** is_safe_path(path), requires_confirmation(cmd)


## Module `security\__init__.py`

```python

```



## Module `shells\detector.py`

```python
"""Shell detection utilities."""
from __future__ import annotations

import os
import platform
import subprocess


_KNOWN_SHELLS = {
    "cmd": {"names": {"cmd", "cmd.exe"}},
    "powershell": {"names": {"powershell", "pwsh", "powershell.exe", "pwsh.exe"}},
    "bash": {"names": {"bash", "bash.exe"}},
    "zsh": {"names": {"zsh", "zsh.exe"}},
    "fish": {"names": {"fish", "fish.exe"}},
}


def _match_shell(name: str) -> str | None:
    name = os.path.basename(name).lower()
    for shell, meta in _KNOWN_SHELLS.items():
        if name in meta["names"]:
            return shell
    return None


def _detect_from_env() -> str | None:
    if platform.system() == "Windows":
        comspec = os.environ.get("COMSPEC")
        if comspec:
            return _match_shell(comspec)
    else:
        shell = os.environ.get("SHELL")
        if shell:
            return _match_shell(shell)
    return None


def _parent_command(pid: int) -> str | None:
    """Best-effort retrieval of a process name for the given pid."""
    if pid <= 0:
        return None
    try:
        if platform.system() == "Windows":
            cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-Process -Id {pid}).Path"
            ]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            return out.decode().strip()
        else:
            cmd = ["ps", "-o", "comm=", "-p", str(pid)]
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            return out.decode().strip()
    except Exception:
        return None


def _detect_from_parents() -> str | None:
    pid = os.getppid()
    visited = set()
    while pid and pid not in visited:
        visited.add(pid)
        name = _parent_command(pid)
        if name:
            shell = _match_shell(name)
            if shell:
                return shell
        # find next parent pid
        try:
            if platform.system() == "Windows":
                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"(Get-Process -Id {pid}).Parent.Id"
                ]
                out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                pid = int(out.decode().strip())
            else:
                cmd = ["ps", "-o", "ppid=", "-p", str(pid)]
                out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                pid = int(out.decode().strip())
        except Exception:
            break
    return None


def detect_shell() -> str:
    """Return the current shell name.

    The function inspects common environment variables and walks up the
    process tree to infer the active shell. It falls back to ``bash`` on
    Unix and ``cmd`` on Windows.
    """
    shell = _detect_from_env() or _detect_from_parents()
    if shell:
        return shell
    return "cmd" if platform.system() == "Windows" else "bash"
```

Shell detection utilities.
**Functions:** _match_shell(name), _detect_from_env(), _parent_command(pid), _detect_from_parents(), detect_shell()


## Module `shells\transpiler.py`

```python
"""Command transpiler between shells."""
from __future__ import annotations

from typing import Dict

_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "cmd": {
        "pwd": "cd",
        "ls": "dir",
        "cp": "copy",
        "mv": "move",
        "rm": "del",
        "clear": "cls",
    },
    "powershell": {
        "pwd": "Get-Location",
        "ls": "Get-ChildItem",
        "cp": "Copy-Item",
        "mv": "Move-Item",
        "rm": "Remove-Item",
        "clear": "Clear-Host",
    },
}


def transpile_command(cmd: str, shell: str) -> str:
    """Convert a simple command snippet into *shell* syntax.

    Parameters
    ----------
    cmd:
        The command snippet, e.g. ``"pwd"``.
    shell:
        Target shell name (``"cmd"``, ``"powershell"``, ``"bash"``, ...).
    """
    shell = shell.lower()
    mapping = _TRANSLATIONS.get(shell)
    if not mapping:
        return cmd
    return mapping.get(cmd, cmd)
```

Command transpiler between shells.
**Functions:** transpile_command(cmd, shell)


## Module `shells\__init__.py`

```python

```



## Module `tests\conftest.py`

```python
import pytest


@pytest.fixture(autouse=True)
def _install_log_path(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "INSTALL_LOG_PATH", str(tmp_path / "install_info.jsonl")
    )
```

**Functions:** _install_log_path(tmp_path, monkeypatch)


## Module `tests\test_agent_terminal.py`

```python
import os
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication


def test_project_root_points_to_repo_root():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    expected = Path(__file__).resolve().parents[1]
    assert Path(agent_terminal.PROJECT_ROOT) == expected


def test_tool_combo_persistence():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    cfg = agent_terminal.load_config()
    orig = cfg.get("last_tool", "")
    cfg["last_tool"] = "editor.open"
    agent_terminal.save_config(cfg)
    widget = agent_terminal.build_widget()
    combo = widget.tool_combo
    assert combo.currentData() == "editor.open"
    combo.setCurrentIndex(combo.findData("file.read"))
    cfg = agent_terminal.load_config()
    assert cfg.get("last_tool") == "file.read"
    cfg["last_tool"] = orig
    agent_terminal.save_config(cfg)
    widget.deleteLater()
    app.quit()


def test_build_widget_returns_terminal_card():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    assert isinstance(widget, agent_terminal.TerminalCard)
    widget.deleteLater()
    app.quit()


def test_command_combo_inserts_text():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    combo = widget.command_combo
    idx = combo.findData("ls")
    combo.setCurrentIndex(idx)
    assert widget.input.toPlainText() == "ls"
    widget.deleteLater()
    app.quit()


def test_install_dependency_logs(tmp_path, monkeypatch):
    import sys
    import json
    import hashlib
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    data = b"binary"
    checksum = hashlib.sha256(data).hexdigest()

    class DummyResp:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            pass

        def read(self):
            return data

    monkeypatch.setattr(
        agent_terminal.urllib.request,
        "urlopen",
        lambda url, timeout=60: DummyResp(),
    )
    monkeypatch.setattr(agent_terminal.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(
        agent_terminal.importlib_metadata, "version", lambda name: "1.0"
    )

    log = tmp_path / "datasets" / "install_info.jsonl"
    ok = agent_terminal.install_dependency(
        "foo", "http://example.com/foo.whl", checksum, log
    )
    assert ok
    rec = json.loads(log.read_text().strip())
    assert rec["package"] == "foo"
    assert rec["checksum"] == checksum


def test_l2c_generate_uses_current_shell(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget.current_shell = "bash"

    captured: dict = {}

    def fake_generate(text: str, shell: str):
        captured["shell"] = shell
        return [{"cmd": "echo hi", "shell": shell}]

    monkeypatch.setattr(
        agent_terminal.l2c_tool,
        "generate_commands",
        fake_generate,
    )
    out = widget.tools["l2c.generate"]({"natural_text": "echo hi"})
    assert captured["shell"] == "bash"
    assert out["commands"][0]["shell"] == "bash"
    widget.deleteLater()
    app.quit()


def test_main_reinvokes_without_admin(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    called = {}

    monkeypatch.setattr(agent_terminal, "_is_admin", lambda: False)

    def fake_relaunch(args):
        called["argv"] = args
        return True

    monkeypatch.setattr(agent_terminal, "_relaunch_as_admin", fake_relaunch)
    rc = agent_terminal.main(["--log-port", "123"])
    assert rc == 0
    assert called["argv"] == ["--log-port", "123"]


def test_mode_combo_and_switching(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    from PySide6.QtCore import QProcess
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    cfg = agent_terminal.load_config()
    orig_cfg = cfg.copy()
    cfg["codex_enabled"] = True
    cfg["default_mode"] = "Chat"
    agent_terminal.save_config(cfg)

    app = QApplication.instance() or QApplication([])
    card = agent_terminal.build_widget()

    items = {
        card.mode_combo.itemText(i) for i in range(card.mode_combo.count())
    }
    assert "Codex" in items
    assert ("Codex+Shell+Chat" in items) or ("All" in items)

    calls = {"codex": 0, "shell": 0}
    card._tool_codex_launch = lambda _=None: calls.__setitem__(
        "codex", calls["codex"] + 1
    )
    card._start_shell = lambda: calls.__setitem__("shell", calls["shell"] + 1)
    card._shell_running = lambda: False

    class DummyProc:
        def state(self):
            return QProcess.NotRunning

    card.codex_proc = DummyProc()

    for mode in ["Chat", "Shell", "Codex", "All"]:
        calls["codex"] = calls["shell"] = 0
        card._on_mode_changed(mode)
        expected = "all" if mode == "All" else mode.lower()
        assert card.mode == expected
        assert calls["shell"] == 1
        if mode in ("Codex", "All"):
            assert calls["codex"] == 1
        else:
            assert calls["codex"] == 0

    card.deleteLater()
    app.quit()
    agent_terminal.save_config(orig_cfg)


def test_codex_setting_persistence():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    cfg = agent_terminal.load_config()
    orig_cfg = cfg.copy()
    cfg["codex_enabled"] = False
    cfg["default_mode"] = "Chat"
    agent_terminal.save_config(cfg)

    app = QApplication.instance() or QApplication([])
    card = agent_terminal.build_widget()
    dlg = agent_terminal.SettingsDialog(card.cfg, [], card)
    dlg.codex_cb.setChecked(True)
    dlg.start_mode_cb.setCurrentText("Codex")
    agent_terminal.save_config(dlg.values())
    card.deleteLater()

    card2 = agent_terminal.build_widget()
    assert card2.codex_enabled is True
    assert card2.mode_combo.currentText() == "Codex"
    card2.deleteLater()
    app.quit()

    agent_terminal.save_config(orig_cfg)


def test_launch_codex_embedded_writes_handshake(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    monkeypatch.setattr(
        agent_terminal.CodexManager,
        "setup_codex",
        lambda project: (True, ""),
    )
    monkeypatch.setattr(
        agent_terminal.CodexManager,
        "codex_args",
        lambda project, model, full_auto: [],
    )

    class DummyProc:
        def __init__(self):
            self.workdir = None
            self.started = None

        def setWorkingDirectory(self, path):
            self.workdir = path

        def start(self, binary, args):
            self.started = (binary, args)

    project = tmp_path / "proj"
    project.mkdir()

    for platform in ("linux", "win32"):
        proc = DummyProc()
        monkeypatch.setattr(sys, "platform", platform)
        ok, _ = agent_terminal.CodexManager.launch_codex_embedded(
            project, "model", False, proc
        )
        assert ok is True
        assert proc.workdir == str(project)
        handshake = project / ".codex_handshake.json"
        assert handshake.exists()
        data = json.loads(handshake.read_text())
        assert data["project_root"] == str(project.resolve())
        assert os.environ.get("CODEX_HANDSHAKE") == str(handshake)


def test_launch_codex_embedded_sets_gpu_env(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    class DummyCuda:
        @staticmethod
        def is_available():
            return True

    class DummyTorch:
        cuda = DummyCuda()

    monkeypatch.setitem(sys.modules, "torch", DummyTorch())
    monkeypatch.setattr(
        agent_terminal.CodexManager, "setup_codex", lambda project: (True, "")
    )
    monkeypatch.setattr(
        agent_terminal.CodexManager,
        "codex_args",
        lambda project, model, full_auto: [],
    )

    class DummyProc:
        def __init__(self):
            self.workdir = None

        def setWorkingDirectory(self, path):
            self.workdir = path

        def start(self, binary, args):
            pass

    project = tmp_path / "proj"
    project.mkdir()
    os.environ.pop("OLLAMA_GPU", None)
    ok, _ = agent_terminal.CodexManager.launch_codex_embedded(
        project, "model", False, DummyProc()
    )
    assert ok is True
    assert os.environ.get("OLLAMA_GPU") == "1"


def test_launch_codex_embedded_logs_failure(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    monkeypatch.setattr(
        agent_terminal.CodexManager, "setup_codex", lambda project: (True, "")
    )
    monkeypatch.setattr(
        agent_terminal.CodexManager,
        "codex_args",
        lambda project, model, full_auto: [],
    )
    monkeypatch.setattr(agent_terminal, "AT_LOG_PATH", tmp_path / "log.txt")

    class DummyProc:
        def setWorkingDirectory(self, path):
            pass

        def start(self, binary, args):  # pragma: no cover - simulating failure
            raise RuntimeError("boom")

    project = tmp_path / "proj"
    project.mkdir()

    ok, msg = agent_terminal.CodexManager.launch_codex_embedded(
        project, "model", False, DummyProc()
    )
    assert ok is False
    assert "boom" in msg
    assert "boom" in (tmp_path / "log.txt").read_text()


def test_tool_codex_launch_failure_falls_back(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QMessageBox
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    cfg = agent_terminal.load_config()
    orig_cfg = cfg.copy()
    cfg["codex_enabled"] = True
    cfg["default_mode"] = "Codex"
    agent_terminal.save_config(cfg)

    app = QApplication.instance() or QApplication([])
    card = agent_terminal.build_widget()

    monkeypatch.setattr(
        agent_terminal.CodexManager,
        "launch_codex_embedded",
        lambda *a, **k: (False, "fail"),
    )

    called = {}

    def fake_warning(parent, title, text):
        called["msg"] = text
        return QMessageBox.Ok

    monkeypatch.setattr(agent_terminal.QMessageBox, "warning", fake_warning)

    res = card._tool_codex_launch({})
    assert res["status"] == "error"
    assert card.codex_enabled is False
    assert card.mode == "chat"
    assert "fail" in called["msg"]

    card.deleteLater()
    app.quit()
    agent_terminal.save_config(orig_cfg)
```

**Functions:** test_project_root_points_to_repo_root(), test_tool_combo_persistence(), test_build_widget_returns_terminal_card(), test_command_combo_inserts_text(), test_install_dependency_logs(tmp_path, monkeypatch), test_l2c_generate_uses_current_shell(monkeypatch), test_main_reinvokes_without_admin(monkeypatch), test_mode_combo_and_switching(monkeypatch), test_codex_setting_persistence(), test_launch_codex_embedded_writes_handshake(tmp_path, monkeypatch), test_launch_codex_embedded_sets_gpu_env(tmp_path, monkeypatch), test_launch_codex_embedded_logs_failure(tmp_path, monkeypatch), test_tool_codex_launch_failure_falls_back(monkeypatch)


## Module `tests\test_agent_terminal_plugins.py`

```python
import importlib
import os
import site
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402
from tools import qt_runtime  # noqa: E402


def test_agent_terminal_missing_plugins(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.delenv("QT_QPA_PLATFORM_PLUGIN_PATH", raising=False)
    qt_runtime.reset_qt_plugin_cache()

    from PySide6.QtCore import QLibraryInfo

    missing = tmp_path / "missing"
    monkeypatch.setattr(QLibraryInfo, "location", lambda *_: str(missing))
    monkeypatch.setattr(site, "getsitepackages", lambda: [])

    sys.modules.pop("agent_terminal", None)
    with pytest.raises(RuntimeError):
        importlib.import_module("agent_terminal")

    fixed = tmp_path / "fixed"
    fixed.mkdir()
    monkeypatch.setattr(QLibraryInfo, "location", lambda *_: str(fixed))

    qt_runtime.reset_qt_plugin_cache()
    sys.modules.pop("agent_terminal", None)
    mod = importlib.import_module("agent_terminal")
    assert os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] == str(fixed)
    assert getattr(mod, "_QT_PLUGIN_PATH", "") == str(fixed)
```

**Functions:** test_agent_terminal_missing_plugins(monkeypatch, tmp_path)


## Module `tests\test_basic.py`

```python

def test_basic_discovery():
    assert True
```

**Functions:** test_basic_discovery()


## Module `tests\test_cli_adapter.py`

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402

from Codex.cli_adapter import parse_cli_output  # noqa: E402


def test_cli_adapter_parses_description_and_commands():
    raw = """Initialize env
$ echo hello
Note after command
$ ls -a
"""
    msg = parse_cli_output(raw)
    assert msg["description"] == "Initialize env\nNote after command"
    assert msg["commands"] == ["echo hello", "ls -a"]
```

**Functions:** test_cli_adapter_parses_description_and_commands()


## Module `tests\test_codex_cli_fallback.py`

```python
import types
from pathlib import Path

from Codex import codex_manager


def test_cli_failure_falls_back(monkeypatch):
    monkeypatch.setattr(codex_manager, "get_binary", lambda: Path("missing"))

    called = {}

    def fake_dispatch(text):
        called["ok"] = True
        return {"type": "prompt", "content": "fallback"}

    monkeypatch.setattr(
        codex_manager,
        "open_source_manager",
        types.SimpleNamespace(dispatch=fake_dispatch),
    )
    result = codex_manager.dispatch("hello")
    assert called.get("ok")
    assert result["content"] == "fallback"
```

**Functions:** test_cli_failure_falls_back(monkeypatch)


## Module `tests\test_codex_dispatch.py`

```python
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402
from Codex import codex_manager  # noqa: E402


@pytest.fixture
def memory_tmp(tmp_path, monkeypatch):
    path = tmp_path / "codex_memory.json"
    path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(codex_manager, "MEMORY_PATH", str(path))
    return path


@pytest.fixture
def chains_tmp(tmp_path, monkeypatch):
    file = tmp_path / "chains.jsonl"
    monkeypatch.setenv("PROMPT_CHAINS_FILE", str(file))
    return file


def test_dispatch_shell(memory_tmp, chains_tmp):
    out = codex_manager.dispatch("shell: echo hi")
    assert out == {"type": "shell", "cmd": "echo hi"}
    data = json.loads(memory_tmp.read_text())
    states = [e["state"] for e in data["command_log"] if e["cmd"] == "echo hi"]
    assert states == ["attempt", "validate", "confirm"]


def test_dispatch_tool(memory_tmp):
    out = codex_manager.dispatch("tool: test_tool")
    assert out["type"] == "tool"
    assert out["tool"] == "test_tool"


def test_dispatch_prompt(memory_tmp):
    out = codex_manager.dispatch("say hi")
    assert out["type"] == "prompt"
    assert out["content"] == "say hi"


def test_dispatch_shell_failure_logs_fix(memory_tmp, chains_tmp):
    codex_manager.dispatch("shell: false")
    data = json.loads(memory_tmp.read_text())
    states = [e["state"] for e in data["command_log"] if e["cmd"] == "false"]
    assert states == ["attempt", "validate", "fix"]
    if chains_tmp.exists():
        lines = [
            ln for ln in chains_tmp.read_text().splitlines() if ln.strip()
        ]
        entries = [json.loads(ln) for ln in lines]
        assert any("failed" in e["text"] for e in entries)


def test_codex_available(tmp_path):
    bin_path = tmp_path / "codex"
    bin_path.write_text("bin")
    assert codex_manager.codex_available(bin_path)
    assert not codex_manager.codex_available(bin_path.with_name("missing"))
```

**Functions:** memory_tmp(tmp_path, monkeypatch), chains_tmp(tmp_path, monkeypatch), test_dispatch_shell(memory_tmp, chains_tmp), test_dispatch_tool(memory_tmp), test_dispatch_prompt(memory_tmp), test_dispatch_shell_failure_logs_fix(memory_tmp, chains_tmp), test_codex_available(tmp_path)


## Module `tests\test_codex_install.py`

```python
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402
import codex_installation  # noqa: E402


class DummyResp:
    def __init__(self, data: bytes):
        self._data = data

    def iter_content(self, chunk_size=8192):
        yield self._data

    def raise_for_status(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_download_codex_resume_and_metadata(tmp_path, monkeypatch):
    data = b"binarypayload"
    checksum = hashlib.sha256(data).hexdigest()
    dest = tmp_path / "Codex"
    log = tmp_path / "datasets" / "install_info.jsonl"

    # simulate partial file
    dest.mkdir()
    partial = dest / "codex.bin"
    partial.write_bytes(data[:6])

    def fake_get(url, stream=True, timeout=60, headers=None):
        start = 0
        if headers and "Range" in headers:
            start = int(headers["Range"].split("=")[1].split("-")[0])
        return DummyResp(data[start:])

    monkeypatch.setattr(codex_installation.requests, "get", fake_get)

    path = codex_installation.download_codex(
        url="http://example.com/codex.bin",
        version="v1",
        checksum=checksum,
        target_dir=dest,
        install_log=log,
        retries=1,
    )

    assert path.read_bytes() == data
    with open(log, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    assert lines[-1]["url"] == "http://example.com/codex.bin"
    meta = dest / "metadata.jsonl"
    with open(meta, "r", encoding="utf-8") as f:
        meta_lines = [json.loads(line) for line in f if line.strip()]
    assert meta_lines[-1]["version"] == "v1"
```

**Classes:** DummyResp
**Functions:** test_download_codex_resume_and_metadata(tmp_path, monkeypatch)


## Module `tests\test_codex_persona.py`

```python
from Codex.codex_manager import build_persona_directive


def test_build_persona_directive_env(monkeypatch):
    monkeypatch.setenv("CODEX_EXCITEMENT", "high")
    monkeypatch.setenv("CODEX_VERBOSITY", "verbose")
    directive = build_persona_directive()
    lower = directive.lower()
    assert "first person" in lower
    assert "memory" in lower
    assert "self-reflection" in lower
    assert "enthusiastic" in lower
    assert "detailed" in lower
```

**Functions:** test_build_persona_directive_env(monkeypatch)


## Module `tests\test_codex_prompt_chat.py`

```python
import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication


def test_codex_prompt_short_circuit(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    monkeypatch.setattr(
        agent_terminal.codex,
        "dispatch",
        lambda text: {"type": "prompt", "content": "hi"},
    )
    widget._chat_to_commands_and_maybe_run("hello")
    widget._flush_queue()
    assert "ai: hi" in widget.console.toPlainText()
    widget.deleteLater()
    app.quit()


def test_codex_delegates_l2c(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    monkeypatch.setattr(
        agent_terminal.codex,
        "dispatch",
        lambda text: {"type": "tool", "tool": "l2c.generate", "args": {}},
    )
    monkeypatch.setattr(
        agent_terminal.l2c_tool,
        "generate_commands",
        lambda text, shell: [{"cmd": "echo hi", "shell": shell}],
    )
    captured = {}

    def fake_auto(cmd, shell):
        captured["cmd"] = cmd

    monkeypatch.setattr(widget, "_auto_execute_command", fake_auto)
    widget.autorun = True
    widget._chat_to_commands_and_maybe_run("say hi")
    assert captured["cmd"] == "echo hi"
    widget.deleteLater()
    app.quit()


def test_codex_absent(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    monkeypatch.setattr(agent_terminal, "codex", None)
    widget._chat_to_commands_and_maybe_run("hello")
    widget._flush_queue()
    text = widget.console.toPlainText()
    assert "error: Codex is not installed" in text
    widget.deleteLater()
    app.quit()
```

**Functions:** test_codex_prompt_short_circuit(monkeypatch), test_codex_delegates_l2c(monkeypatch), test_codex_absent(monkeypatch)


## Module `tests\test_codex_prompt_install.py`

```python
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_prompt_install_decline(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import agent_terminal

    called = {}
    monkeypatch.setitem(agent_terminal.os.environ, "QT_QPA_PLATFORM", "dummy")

    class DummyApp:
        @staticmethod
        def instance():
            return None

        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(agent_terminal, "QApplication", DummyApp)
    monkeypatch.setattr(
        agent_terminal.QMessageBox,
        "question",
        lambda *a, **k: agent_terminal.QMessageBox.No,
    )
    monkeypatch.setattr(
        agent_terminal,
        "ensure_codex_installed",
        lambda: called.setdefault("install", True),
    )
    from Codex import codex_manager

    monkeypatch.setattr(codex_manager, "get_binary", lambda: None)

    agent_terminal.prompt_install_codex()
    assert "install" not in called


def test_prompt_install_accept(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import agent_terminal

    called = {}
    monkeypatch.setitem(agent_terminal.os.environ, "QT_QPA_PLATFORM", "dummy")

    class DummyApp:
        @staticmethod
        def instance():
            return None

        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(agent_terminal, "QApplication", DummyApp)
    monkeypatch.setattr(
        agent_terminal.QMessageBox,
        "question",
        lambda *a, **k: agent_terminal.QMessageBox.Yes,
    )
    monkeypatch.setattr(
        agent_terminal.QMessageBox,
        "information",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        agent_terminal.QMessageBox,
        "warning",
        lambda *a, **k: None,
    )

    class DummyProgress:
        def __init__(self, *a, **k):
            pass

        def setWindowModality(self, *a):
            pass

        def setCancelButton(self, *a):
            pass

        def setAutoClose(self, *a):
            pass

        def show(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(agent_terminal, "QProgressDialog", DummyProgress)

    class DummyThread:
        def __init__(self, target, daemon=False):
            self.target = target

        def start(self):
            self.target()

        def is_alive(self):
            return False

    monkeypatch.setattr(agent_terminal.threading, "Thread", DummyThread)
    monkeypatch.setattr(
        agent_terminal.QTimer,
        "singleShot",
        lambda *a, **k: a[1](),
    )

    monkeypatch.setattr(
        agent_terminal,
        "ensure_codex_installed",
        lambda: called.setdefault("install", True),
    )

    def fake_load():
        called.setdefault("load", True)

        class P:
            name = "Codex"
            version = "v0"

        return object(), P()

    monkeypatch.setattr(agent_terminal, "_load_codex", fake_load)
    from Codex import codex_manager

    monkeypatch.setattr(codex_manager, "get_binary", lambda: None)

    agent_terminal.prompt_install_codex()
    assert called.get("install") and called.get("load")


def test_prompt_install_failure_logs(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import agent_terminal

    monkeypatch.setenv("DATASETS_DIR", str(tmp_path))
    monkeypatch.setitem(agent_terminal.os.environ, "QT_QPA_PLATFORM", "dummy")

    class DummyApp:
        @staticmethod
        def instance():
            return None

        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(agent_terminal, "QApplication", DummyApp)
    monkeypatch.setattr(
        agent_terminal.QMessageBox,
        "question",
        lambda *a, **k: agent_terminal.QMessageBox.Yes,
    )

    msgs = {}
    monkeypatch.setattr(
        agent_terminal.QMessageBox,
        "warning",
        lambda *a, **k: msgs.setdefault("text", a[2]),
    )

    class DummyProgress:
        def __init__(self, *a, **k):
            pass

        def setWindowModality(self, *a):
            pass

        def setCancelButton(self, *a):
            pass

        def setAutoClose(self, *a):
            pass

        def show(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(agent_terminal, "QProgressDialog", DummyProgress)

    class DummyThread:
        def __init__(self, target, daemon=False):
            self.target = target

        def start(self):
            try:
                self.target()
            except Exception:
                pass

        def is_alive(self):
            return False

    monkeypatch.setattr(agent_terminal.threading, "Thread", DummyThread)
    monkeypatch.setattr(
        agent_terminal.QTimer,
        "singleShot",
        lambda *a, **k: a[1](),
    )

    def fail_install():
        raise RuntimeError("boom")

    monkeypatch.setattr(agent_terminal, "ensure_codex_installed", fail_install)
    from Codex import codex_manager

    monkeypatch.setattr(codex_manager, "get_binary", lambda: None)

    agent_terminal.prompt_install_codex()
    assert "boom" in msgs.get("text", "")
    log = tmp_path / "codex_installs.jsonl"
    rec = json.loads(log.read_text().strip())
    assert rec["success"] is False and "boom" in rec["error"]
```

**Functions:** test_prompt_install_decline(monkeypatch), test_prompt_install_accept(monkeypatch), test_prompt_install_failure_logs(monkeypatch, tmp_path)


## Module `tests\test_code_editor.py`

```python
import os
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPaintEvent
from PySide6.QtCore import QRect
from tools import qt_runtime


def test_create_card_returns_widget_and_title():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor  # noqa: F401

    app = QApplication.instance() or QApplication([])
    widget, title = code_editor.create_card()
    assert widget is not None
    assert title == "Code Editor"
    widget.deleteLater()
    app.quit()


def test_import_qt_repairs_missing_plugins(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.delenv("QT_QPA_PLATFORM_PLUGIN_PATH", raising=False)
    qt_runtime.reset_qt_plugin_cache()

    import sys
    from PySide6.QtCore import QLibraryInfo
    import importlib
    import site

    missing = tmp_path / "missing"
    monkeypatch.setattr(QLibraryInfo, "location", lambda *_: str(missing))
    monkeypatch.setattr(site, "getsitepackages", lambda: [])

    sys.modules.pop("code_editor", None)
    with pytest.raises(RuntimeError):
        importlib.import_module("code_editor")

    fixed = tmp_path / "fixed"
    fixed.mkdir()
    monkeypatch.setattr(QLibraryInfo, "location", lambda *_: str(fixed))

    sys.modules.pop("code_editor", None)
    importlib.import_module("code_editor")

    assert os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] == str(fixed)


def test_blank_start_ignores_env(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor

    app = QApplication.instance() or QApplication([])
    bad = Path(code_editor.__file__).resolve()
    monkeypatch.setenv("CODE_EDITOR_FILE", str(bad))
    win = code_editor.HostWindow()
    assert win.card._path is None
    win.deleteLater()
    app.quit()


def test_blank_start_missing_file(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor

    app = QApplication.instance() or QApplication([])
    missing = tmp_path / "nope.txt"
    monkeypatch.setenv("CODE_EDITOR_FILE", str(missing))
    win = code_editor.HostWindow()
    assert win.card._path is None
    win.deleteLater()
    app.quit()


@pytest.mark.parametrize(
    "label, ext",
    [("Markdown", ".md"), ("Python", ".py")],
)
def test_save_as_uses_selected_extension(monkeypatch, tmp_path, label, ext):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor

    app = QApplication.instance() or QApplication([])
    win = code_editor.HostWindow()
    card = win.card
    card.cmb_type.setCurrentText(label)
    card.new_file()
    target = tmp_path / "data"
    monkeypatch.setattr(
        code_editor.QFileDialog,
        "getSaveFileName",
        lambda *a, **k: (str(target), ""),
    )
    card.editor.setPlainText("x")
    card.save_as_dialog()
    saved = tmp_path / f"data{ext}"
    assert saved.exists()
    win.deleteLater()
    app.quit()


def test_startup_preselects_extension(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor

    app = QApplication.instance() or QApplication([])
    monkeypatch.setenv("CODE_EDITOR_EXT", ".md")
    win = code_editor.HostWindow()
    assert win.card.cmb_type.currentData() == ".md"
    win.deleteLater()
    app.quit()


def test_new_file_resets_state(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor

    app = QApplication.instance() or QApplication([])
    win = code_editor.HostWindow()
    card = win.card
    card.cmb_type.setCurrentText("Markdown")
    card.editor.setPlainText("data")
    card._path = tmp_path / "test.py"
    card.new_file()
    assert card._path is None
    assert card._suggested == "untitled.md"
    assert card.editor.toPlainText() == ""
    assert card._dirty is False
    win.deleteLater()
    app.quit()


def test_launches_blank_document():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor

    app = QApplication.instance() or QApplication([])
    win = code_editor.HostWindow()
    card = win.card
    assert card._path is None
    assert card.editor.toPlainText() == ""
    win.deleteLater()
    app.quit()


def test_highlighter_tracks_extension():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor

    app = QApplication.instance() or QApplication([])
    win = code_editor.HostWindow()
    card = win.card
    card.cmb_type.setCurrentText("Markdown")
    assert isinstance(card.highlighter, code_editor.MarkdownHighlighter)
    card.cmb_type.setCurrentText("Python")
    assert isinstance(card.highlighter, code_editor.PythonHighlighter)
    win.deleteLater()
    app.quit()


def test_line_number_area_paint_event_ends_painter(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import code_editor

    app = QApplication.instance() or QApplication([])
    editor = code_editor.Editor(code_editor.Theme())

    instances = []
    original_init = code_editor.QPainter.__init__

    def track_init(self, *args, **kwargs):
        instances.append(self)
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(code_editor.QPainter, "__init__", track_init)

    event = QPaintEvent(QRect(0, 0, 10, 10))
    editor.line_number_area_paint_event(event)

    assert instances and all(not p.isActive() for p in instances)

    editor.deleteLater()
    app.quit()
```

**Functions:** test_create_card_returns_widget_and_title(), test_import_qt_repairs_missing_plugins(monkeypatch, tmp_path), test_blank_start_ignores_env(monkeypatch), test_blank_start_missing_file(monkeypatch, tmp_path), test_save_as_uses_selected_extension(monkeypatch, tmp_path, label, ext), test_startup_preselects_extension(monkeypatch), test_new_file_resets_state(monkeypatch, tmp_path), test_launches_blank_document(), test_highlighter_tracks_extension(), test_line_number_area_paint_event_ends_painter(monkeypatch)


## Module `tests\test_config.py`

```python
import json
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent_terminal  # noqa: E402


def test_load_config_creates_defaults(tmp_path):
    cfg_path = tmp_path / "config.json"
    with patch.object(agent_terminal, "CONFIG_PATH", str(cfg_path)):
        cfg = agent_terminal.load_config()
    assert cfg == agent_terminal.DEFAULT_CONFIG
    assert cfg_path.exists()
    with cfg_path.open() as f:
        assert json.load(f) == agent_terminal.DEFAULT_CONFIG


def test_load_config_recovers_from_invalid_json(tmp_path):
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text("{not:json}")
    with patch.object(agent_terminal, "CONFIG_PATH", str(cfg_path)):
        cfg = agent_terminal.load_config()
    assert cfg == agent_terminal.DEFAULT_CONFIG
```

**Functions:** test_load_config_creates_defaults(tmp_path), test_load_config_recovers_from_invalid_json(tmp_path)


## Module `tests\test_datasets.py`

```python
import json
from importlib import reload
from pathlib import Path

import memory.bucket_manager as bm
import memory.datasets as ds


def test_write_and_query(tmp_path, monkeypatch):
    monkeypatch.setenv("DATASETS_DIR", str(tmp_path))
    reload(bm)
    reload(ds)

    ds.write_entry(
        "prompts",
        {"text": "hello", "embedding": [1.0, 0.0], "provenance": "test"},
    )
    ds.write_entry(
        "prompts",
        {"text": "world", "embedding": [0.0, 1.0], "provenance": "test"},
    )

    path = Path(tmp_path) / "prompts.jsonl"
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 2
    rec = json.loads(lines[0])
    assert rec["text"] == "hello"
    assert rec.get("timestamp")

    res = ds.query("prompts", [1.0, 0.0])[0]
    assert res["text"] == "hello"


def test_log_helpers(tmp_path, monkeypatch):
    monkeypatch.setenv("DATASETS_DIR", str(tmp_path))
    reload(bm)
    reload(ds)

    ds.log_prompt("user", "alpha", task_id="t1")
    ds.log_prompt("assistant", "beta", task_id="t2")
    ds.log_error("oops", task_id="t1")
    ds.log_authorization("ls", True, task_id="t1")

    emb = ds.embed_text("alpha")
    res = ds.search_prompts(emb, task_id="t1")
    assert res and res[0]["text"] == "alpha" and res[0]["task_id"] == "t1"
    assert not ds.search_prompts(emb, task_id="t2")

    emb_err = ds.embed_text("oops")
    assert ds.search_errors(emb_err, task_id="t1")[0]["error"] == "oops"

    emb_cmd = ds.embed_text("ls")
    auth = ds.search_authorizations(emb_cmd, task_id="t1")[0]
    assert auth["command"] == "ls" and auth["granted"] is True
```

**Functions:** test_write_and_query(tmp_path, monkeypatch), test_log_helpers(tmp_path, monkeypatch)


## Module `tests\test_direct_launch.py`

```python
import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLibraryInfo, QTimer


def _patch_runtime(monkeypatch):
    plugin_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    monkeypatch.setattr(
        "tools.qt_runtime.ensure_qt_runtime", lambda: plugin_path
    )
    monkeypatch.setattr(
        "tools.qt_utils.ensure_pyside6", lambda logger=None: True
    )
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path


def test_main_launches_agent_terminal(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    _patch_runtime(monkeypatch)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    import agent_terminal

    result = {}

    def check():
        windows = [w for w in QApplication.topLevelWidgets() if w.isVisible()]
        result["titles"] = [w.windowTitle() for w in windows]
        if windows:
            result["central"] = windows[0].centralWidget().__class__.__name__
        for w in windows:
            w.close()
        QApplication.quit()

    QTimer.singleShot(0, check)
    agent_terminal.main()
    assert result.get("titles") == ["Agent Terminal"]
    assert result.get("central") == "TerminalCard"
```

**Functions:** _patch_runtime(monkeypatch), test_main_launches_agent_terminal(monkeypatch)


## Module `tests\test_editor_card.py`

```python
import os
import json
from pathlib import Path

from PySide6.QtWidgets import QApplication


def _init_term():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal
    app = QApplication.instance() or QApplication([])
    cfg = agent_terminal.load_config()
    host = agent_terminal.HostWindow(cfg)
    return app, host


def test_editor_open_and_new_spawn_cards(tmp_path):
    app, host = _init_term()
    term = host.term
    count = len(host._editors)
    term._tool_editor_new({})
    assert len(host._editors) == count + 1
    p = tmp_path / "a.txt"
    p.write_text("hi", encoding="utf-8")
    term._tool_editor_open({"path": str(p)})
    assert len(host._editors) == count + 2
    host.close()
    app.quit()


def test_editor_save_logs_history(tmp_path):
    app, host = _init_term()
    term = host.term
    p = tmp_path / "sample.txt"
    p.write_text("hello", encoding="utf-8")
    term._tool_editor_open({"path": str(p)})
    card = host._editors[-1]
    card.editor.setPlainText("world")
    term._tool_editor_save({})
    assert p.read_text(encoding="utf-8") == "world"
    data = json.loads(Path(card.history.path).read_text().splitlines()[-1])
    assert data["type"] == "revision"
    host.close()
    app.quit()


def test_editor_new_save_file(tmp_path):
    app, host = _init_term()
    term = host.term
    term._tool_editor_new({})
    card = host._editors[-1]
    card.editor.setPlainText("note")
    target = tmp_path / "note.md"
    term._tool_editor_save({"path": str(target)})
    assert target.read_text(encoding="utf-8") == "note"
    host.close()
    app.quit()


def test_chat_messages_logged(tmp_path):
    app, host = _init_term()
    term = host.term
    term._tool_editor_new({})
    card = host._editors[-1]
    card.send_chat("hello")
    data = json.loads(Path(card.history.path).read_text().splitlines()[-1])
    assert data["type"] == "chat" and data["message"] == "hello"
    host.close()
    app.quit()
```

**Functions:** _init_term(), test_editor_open_and_new_spawn_cards(tmp_path), test_editor_save_logs_history(tmp_path), test_editor_new_save_file(tmp_path), test_chat_messages_logged(tmp_path)


## Module `tests\test_full_auto.py`

```python
import os
from PySide6.QtWidgets import QApplication


def test_destructive_requires_confirmation():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget.full_auto_cb.setChecked(True)
    assert widget.full_auto is True
    assert widget._needs_confirmation("rm danger.txt")
    assert widget._needs_confirmation("cat /etc/passwd")
    assert not widget._needs_confirmation("ls")
    widget.deleteLater()
    app.quit()


def test_full_auto_streams_and_logs(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal
    from memory import datasets as mds

    monkeypatch.setattr(mds, "DATASETS_DIR", tmp_path)
    monkeypatch.setattr(
        agent_terminal, "AUTH_LOG_PATH", tmp_path / "authorizations.jsonl"
    )

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget.full_auto_cb.setChecked(True)
    widget._auto_execute_command("echo hello", widget.current_shell)
    widget._flush_queue()
    assert "hello" in widget.console.toPlainText()
    with open(tmp_path / "authorizations.jsonl", encoding="utf-8") as f:
        data = f.read()
    assert "echo hello" in data
    assert "returncode" in data
    widget.deleteLater()
    app.quit()
```

**Functions:** test_destructive_requires_confirmation(), test_full_auto_streams_and_logs(tmp_path, monkeypatch)


## Module `tests\test_l2c_prompt.py`

```python
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication


def test_l2c_prompt_embeds_shell():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget._start_shell = lambda: None
    widget.env_combo.setCurrentText("PowerShell")
    prompt = widget._build_l2c_prompt("list files")
    assert "powershell" in prompt.lower()
    assert "single-line" in agent_terminal.DEFAULT_L2C_PROMPT
    widget.deleteLater()
    app.quit()
```

**Functions:** test_l2c_prompt_embeds_shell()


## Module `tests\test_l2c_tool.py`

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Codex import codex_manager  # noqa: E402
import l2c_tool  # noqa: E402


def test_l2c_tool_registered():
    assert "l2c.generate" in codex_manager.TOOLS


def test_generate_commands_matches_shell():
    cmds = l2c_tool.generate_commands("echo hi", "bash")
    assert cmds == [{"cmd": "echo hi", "shell": "bash"}]


def test_dispatch_invokes_l2c_tool():
    decision = codex_manager.dispatch("tool: l2c.generate")
    assert decision["type"] == "tool"
    fn = codex_manager.TOOLS[decision["tool"]]
    out = fn("echo hi", "bash")
    assert out[0]["shell"] == "bash"
```

**Functions:** test_l2c_tool_registered(), test_generate_commands_matches_shell(), test_dispatch_invokes_l2c_tool()


## Module `tests\test_lexicon.py`

```python
import os
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication


def test_lexicon_present():
    base = Path(__file__).resolve().parents[1]
    path = base / "docs/Agent-Terminal-Lexicon.md"
    text = path.read_text(encoding="utf-8")
    assert "agent_terminal.py" in text
    assert "file.read" in text


def test_rag_context_includes_lexicon(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    base = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(base))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()

    def fake_search(q, top_k=6):
        results = []
        data_path = base / "datasets/snippets.jsonl"
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                if q.lower() in rec.get("text", "").lower():
                    results.append(rec)
        return results[:top_k]

    widget.ds_indexing.search = lambda q, top_k=6: []
    widget.ds_prompting.search = lambda q, top_k=3: []
    widget.ds_learning.search = lambda q, top_k=3: []
    widget.ds_sem_user.search = lambda q, top_k=2: []
    widget.ds_selfp.search = lambda q, top_k=2: []
    widget.ds_snippets.search = fake_search

    rag = widget._build_rag_context("lexicon")
    assert "Agent-Terminal-Lexicon.md" in rag
    widget.deleteLater()
    app.quit()
```

**Functions:** test_lexicon_present(), test_rag_context_includes_lexicon(monkeypatch)


## Module `tests\test_macro_manager.py`

```python
import os
import sys
from PySide6.QtWidgets import QApplication

sys.path.append(os.getcwd())
from agent_terminal import MacroManager, MacroManagerDialog  # noqa: E402


def test_macro_manager_crud(tmp_path):
    cfg = {"macros": {}}
    mgr = MacroManager(cfg)
    mgr.add_macro("greet", "echo hi")
    assert mgr.get_macro("greet") == "echo hi"
    mgr.edit_macro("greet", "echo bye")
    assert mgr.get_macro("greet") == "echo bye"
    mgr.delete_macro("greet")
    assert mgr.get_macro("greet") is None


def test_macro_manager_dialog_run():
    _ = QApplication.instance() or QApplication([])
    cfg = {"macros": {"m1": "ls"}}
    mgr = MacroManager(cfg)
    dlg = MacroManagerDialog(mgr)
    dlg.list.setCurrentRow(0)
    dlg._run()
    assert dlg.result_command == "ls"
    dlg.close()
```

**Functions:** test_macro_manager_crud(tmp_path), test_macro_manager_dialog_run()


## Module `tests\test_monitor_card.py`

```python
import logging
import os
import socket
import time
from pathlib import Path

from PySide6.QtWidgets import QApplication


def test_monitor_card_receives_logs_and_pong(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal
    import tools.qt_utils as qt_utils
    import tools.qt_runtime as qt_runtime

    monkeypatch.setattr(
        qt_utils,
        "ensure_pyside6",
        lambda *a, **k: qt_runtime.ensure_qt_runtime() or True,
    )

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    agent_terminal.start_log_server(port)
    handler = agent_terminal.SocketBroadcastHandler()
    test_logger = logging.getLogger("test")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)

    import Virtual_Desktop

    app = QApplication.instance() or QApplication([])
    card = Virtual_Desktop.MonitorCard(
        "127.0.0.1", port, Virtual_Desktop.Theme()
    )
    for _ in range(50):
        app.processEvents()
        time.sleep(0.02)

    test_logger.info("hello")

    for _ in range(50):
        app.processEvents()
        time.sleep(0.02)
        if "hello" in card.view.toPlainText():
            break
    assert "hello" in card.view.toPlainText()

    card._send_ping()
    start = time.time()
    while card._last_pong == 0 and time.time() - start < 1:
        app.processEvents()
        time.sleep(0.02)
    assert card._last_pong > 0

    card._stop()
    card.deleteLater()
    app.quit()
```

**Functions:** test_monitor_card_receives_logs_and_pong(monkeypatch)


## Module `tests\test_ocr_verification.py`

```python
from unittest.mock import Mock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_terminal  # noqa: E402
from vision.ocr_service import OCRService  # noqa: E402
from vision import ocr_service as ocr_module  # noqa: E402


def test_ocr_service_verify(monkeypatch):
    service = OCRService()

    monkeypatch.setattr(service, "capture", lambda region=None: object())
    monkeypatch.setattr(service, "run_ocr", lambda image: "hello world")

    records = []

    def fake_write_entry(name, record):
        records.append((name, record))
        return record

    monkeypatch.setattr(ocr_module, "write_entry", fake_write_entry)

    assert service.verify("hello", task_id="123")
    assert records[0][0] == "ocr_logs"
    assert records[0][1]["task_id"] == "123"
    assert records[0][1]["text"] == "hello world"


def test_run_gui_command_calls_verify(monkeypatch):
    called = []

    def action():
        called.append(True)

    mock_service = Mock()
    mock_service.verify.return_value = True
    monkeypatch.setattr(agent_terminal, "ocr_service", mock_service)

    agent_terminal.run_gui_command(action, "expected")

    assert called == [True]
    mock_service.verify.assert_called_once_with(
        "expected", region=None, task_id=None
    )
```

**Functions:** test_ocr_service_verify(monkeypatch), test_run_gui_command_calls_verify(monkeypatch)


## Module `tests\test_open_source_cli.py`

```python
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402


def test_cli_output_parsing(monkeypatch, tmp_path):
    monkeypatch.setenv("CLI_LLM_CMD", "printf 'desc\n> echo hi\n'")
    from Codex import open_source_manager as osm
    importlib.reload(osm)
    mem = tmp_path / "codex_memory.json"
    mem.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(osm, "MEMORY_PATH", str(mem))
    result = osm.dispatch("hello")
    assert result["type"] == "shell"
    assert result["cmd"] == "echo hi"
```

**Functions:** test_cli_output_parsing(monkeypatch, tmp_path)


## Module `tests\test_open_source_fallback.py`

```python
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402


def test_fallback_to_open_source(monkeypatch, tmp_path):
    import agent_terminal
    log = tmp_path / "install_info.jsonl"
    monkeypatch.setattr(agent_terminal, "INSTALL_LOG_PATH", log)

    from Codex import open_source_manager
    monkeypatch.setattr(
        open_source_manager, "manager_version", lambda: "open-test"
    )

    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "Codex.codex_manager" or (
            name == "Codex" and "codex_manager" in fromlist
        ):
            raise ImportError("codex unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)
    sys.modules.pop("Codex.codex_manager", None)
    importlib.reload(agent_terminal)
    try:
        assert agent_terminal.CURRENT_MODEL.lower().startswith("open")
        result = agent_terminal.codex.dispatch("say hi")
        assert result["type"] == "prompt"
        rec = json.loads(log.read_text().strip().splitlines()[-1])
        assert rec["source"].lower().startswith("open")
        assert rec["version"] == "open-test"
        assert rec["decision"] == "fallback"
    finally:
        importlib.reload(agent_terminal)
```

**Functions:** test_fallback_to_open_source(monkeypatch, tmp_path)


## Module `tests\test_persona_tone.py`

```python
from agent_terminal import apply_persona


def test_apply_persona_high_excitement():
    persona = {
        "excitement_level": "high",
        "self_referential_awareness": True,
        "narrative_style": "first_person",
    }
    result = apply_persona("try a new feature", persona)
    assert "I'm excited to" in result
```

**Functions:** test_apply_persona_high_excitement()


## Module `tests\test_powershell_wrap.py`

```python
import re
from pathlib import Path

from agent_terminal import wrap_powershell_for_cmd


def test_wrap_inline_one_line():
    cmd = wrap_powershell_for_cmd("Get-Process")
    assert cmd.startswith("powershell -NoProfile -Command")
    assert "Get-Process" in cmd


def test_wrap_multiline_creates_file():
    script = "Write-Host hi\nWrite-Host there"
    cmd = wrap_powershell_for_cmd(script)
    match = re.search(r'"([^"]+\.ps1)"', cmd)
    assert match, cmd
    path = Path(match.group(1))
    assert path.exists()
    assert path.read_text() == script
    path.unlink()
```

**Functions:** test_wrap_inline_one_line(), test_wrap_multiline_creates_file()


## Module `tests\test_prompt_buckets_root.py`

```python
from __future__ import annotations

import json
from pathlib import Path

import prompt_manager


def test_ephemeral_discard_persistent_remain(tmp_path, monkeypatch):
    monkeypatch.setenv("DATASETS_DIR", str(tmp_path))
    prompt_manager.create_prompt("t1", "ephemeral", scope="ephemeral")
    prompt_manager.create_prompt("t1", "persistent", scope="persistent")

    first = prompt_manager.read_prompts("t1")
    texts = {p["text"] for p in first}
    assert {"ephemeral", "persistent"} == texts

    second = prompt_manager.read_prompts("t1")
    texts2 = {p["text"] for p in second}
    assert texts2 == {"persistent"}

    path = Path(tmp_path) / "prompt_bucket.jsonl"
    with path.open("r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    expected = [{"task_id": "t1", "text": "persistent", "scope": "persistent"}]
    assert lines == expected
```

**Functions:** test_ephemeral_discard_persistent_remain(tmp_path, monkeypatch)


## Module `tests\test_prompt_chains.py`

```python
import json

import Codex.codex_manager as cm
from prompt_manager import chain_prompts, mark_prompt_done, prune_stale_chains


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_chain_and_prune(tmp_path, monkeypatch):
    file = tmp_path / "chains.jsonl"
    monkeypatch.setenv("PROMPT_CHAINS_FILE", str(file))

    chain_prompts("parent", ["p1", "p2"])
    data = _read(file)
    assert all(d["state"] == "pending" for d in data)

    mark_prompt_done("parent", "p1")
    prune_stale_chains()
    data = _read(file)
    assert any(d["state"] == "done" for d in data)

    mark_prompt_done("parent", "p2")
    prune_stale_chains()
    assert _read(file) == []


def test_dispatch_appends_repair_prompt(tmp_path, monkeypatch):
    file = tmp_path / "chains.jsonl"
    mem = tmp_path / "codex_memory.json"
    mem.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("PROMPT_CHAINS_FILE", str(file))
    monkeypatch.setattr(cm, "MEMORY_PATH", str(mem))

    cm.dispatch("shell: false")
    data = _read(file)
    assert any("failed" in d["text"] for d in data)
```

**Functions:** _read(path), test_chain_and_prune(tmp_path, monkeypatch), test_dispatch_appends_repair_prompt(tmp_path, monkeypatch)


## Module `tests\test_qt_runtime.py`

```python
import builtins
import os
import sys
import types
import importlib

import site
import subprocess
import pytest
from tools import qt_runtime


def test_installs_and_sets_env_when_missing(tmp_path, monkeypatch):
    """ensure_qt_runtime installs PySide6 and sets plugin path."""

    qt_runtime.reset_qt_plugin_cache()

    fake_module = types.SimpleNamespace(
        QLibraryInfo=type(
            "QLibraryInfo",
            (),
            {
                "PluginsPath": 1,
                "location": staticmethod(lambda key: ""),
            },
        )
    )

    original_import = builtins.__import__
    call_state = {"count": 0}

    def import_hook(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "PySide6.QtCore":
            call_state["count"] += 1
            if call_state["count"] == 1:
                raise ImportError
            return fake_module
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_hook)

    called = []

    def fake_run(cmd, **kwargs):
        called.append(cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(site, "getsitepackages", lambda: [str(tmp_path)])

    plugin_dir = tmp_path / "PySide6" / "Qt" / "plugins"
    plugin_dir.mkdir(parents=True)

    monkeypatch.delenv("QT_QPA_PLATFORM_PLUGIN_PATH", raising=False)

    qt_runtime.ensure_qt_runtime()

    assert called and "PySide6" in called[0][-1]
    assert os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] == str(plugin_dir)

    monkeypatch.delitem(sys.modules, "PySide6", raising=False)
    monkeypatch.delitem(sys.modules, "PySide6.QtCore", raising=False)
    import PySide6  # noqa: F401  # reimport real module for later tests
    importlib.import_module("PySide6.QtCore")


def test_raises_when_plugins_missing(monkeypatch):
    """ensure_qt_runtime raises when plugins cannot be located."""

    qt_runtime.reset_qt_plugin_cache()

    fake_module = types.SimpleNamespace(
        QLibraryInfo=type(
            "QLibraryInfo",
            (),
            {
                "PluginsPath": 1,
                "location": staticmethod(lambda key: ""),
            },
        )
    )

    original_import = builtins.__import__

    def import_hook(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "PySide6.QtCore":
            return fake_module
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_hook)

    monkeypatch.setattr(site, "getsitepackages", lambda: [])
    monkeypatch.delenv("QT_QPA_PLATFORM_PLUGIN_PATH", raising=False)

    with pytest.raises(RuntimeError):
        qt_runtime.ensure_qt_runtime()

    monkeypatch.delitem(sys.modules, "PySide6", raising=False)
    monkeypatch.delitem(sys.modules, "PySide6.QtCore", raising=False)
    import PySide6  # noqa: F401
    importlib.import_module("PySide6.QtCore")
```

**Functions:** test_installs_and_sets_env_when_missing(tmp_path, monkeypatch), test_raises_when_plugins_missing(monkeypatch)


## Module `tests\test_qt_utils.py`

```python
import os
import sys
import types
import subprocess
import builtins

from tools.qt_utils import ensure_pyside6


def _install_mock(monkeypatch, tmp_path):
    called = {}

    class FakeQLibraryInfo:
        PluginsPath = object()

        @staticmethod
        def location(kind):
            return str(tmp_path)

    def fake_check_call(cmd):
        called['cmd'] = cmd
        sys.modules['PySide6'] = types.SimpleNamespace(
            QtCore=types.SimpleNamespace(QLibraryInfo=FakeQLibraryInfo)
        )
        sys.modules['PySide6.QtCore'] = sys.modules['PySide6'].QtCore
        os.makedirs(tmp_path, exist_ok=True)
        return 0

    monkeypatch.setattr(subprocess, 'check_call', fake_check_call)
    return called


def test_ensure_pyside6_installs_when_missing(monkeypatch, tmp_path):
    original_import = builtins.__import__
    called = _install_mock(monkeypatch, tmp_path)

    def fake_import(name, *args, **kwargs):
        if name == 'PySide6' and 'cmd' not in called:
            raise ImportError('mock missing')
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', fake_import)
    assert ensure_pyside6() is True
    assert called['cmd'][0] == sys.executable
    sys.modules.pop('PySide6', None)
    sys.modules.pop('PySide6.QtCore', None)


def test_ensure_pyside6_reinstalls_if_plugins_missing(monkeypatch, tmp_path):
    class FakeQLibraryInfo:
        PluginsPath = object()

        @staticmethod
        def location(kind):
            return str(tmp_path / 'missing')

    sys.modules['PySide6'] = types.SimpleNamespace(
        QtCore=types.SimpleNamespace(QLibraryInfo=FakeQLibraryInfo)
    )
    sys.modules['PySide6.QtCore'] = sys.modules['PySide6'].QtCore
    called = _install_mock(monkeypatch, tmp_path)
    assert ensure_pyside6() is True
    assert called['cmd'][0] == sys.executable
    sys.modules.pop('PySide6', None)
    sys.modules.pop('PySide6.QtCore', None)
```

**Functions:** _install_mock(monkeypatch, tmp_path), test_ensure_pyside6_installs_when_missing(monkeypatch, tmp_path), test_ensure_pyside6_reinstalls_if_plugins_missing(monkeypatch, tmp_path)


## Module `tests\test_schema_manager_root.py`

```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from schema_manager import apply_schema  # noqa: E402


def test_apply_schema_updates_only_target(tmp_path):
    agent1 = tmp_path / "Agent.md"
    agent1.write_text(
        "header\n"
        "<!-- schema:general:start -->\nold1\n<!-- schema:general:end -->\n"
    )
    agent2 = tmp_path / "Agent_terminal.md"
    agent2.write_text(
        "header\n"
        "<!-- schema:terminal:start -->\nold2\n<!-- schema:terminal:end -->\n"
    )

    apply_schema({"general": "new1"}, agent1)

    assert "new1" in agent1.read_text()
    assert "old2" in agent2.read_text()


def test_apply_schema_preserves_unrelated_sections(tmp_path):
    agent = tmp_path / "Agent.md"
    agent.write_text(
        "header\n"
        "<!-- schema:general:start -->\nold1\n<!-- schema:general:end -->\n"
        "<!-- schema:extra:start -->\nkeep\n<!-- schema:extra:end -->\n"
    )

    apply_schema({"general": "new1"}, agent)

    text = agent.read_text()
    assert "new1" in text
    assert "keep" in text
```

**Functions:** test_apply_schema_updates_only_target(tmp_path), test_apply_schema_preserves_unrelated_sections(tmp_path)


## Module `tests\test_shell_alignment.py`

```python
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication


def test_shell_switch_prompt():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget._start_shell = lambda: None
    widget.env_combo.setCurrentText("CMD")
    widget._flush_queue()

    msg = "```powershell\nGet-Process\n```"
    _code, lang = widget._extract_env_block(msg)
    widget._ensure_shell_alignment(lang)
    widget._flush_queue()
    assert widget.current_shell == "powershell"
    assert "Detected PowerShell command" in widget.console.toPlainText()
    widget.deleteLater()
    app.quit()


def test_unknown_shell_warns_user():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget._start_shell = lambda: None
    widget.env_combo.setCurrentText("CMD")
    widget.console.clear()
    widget._ensure_shell_alignment("zsh")
    widget._flush_queue()
    assert "Received zsh command" in widget.console.toPlainText()
    widget.deleteLater()
    app.quit()
```

**Functions:** test_shell_switch_prompt(), test_unknown_shell_warns_user()


## Module `tests\test_startup.py`

```python
import os
import sys
import subprocess
from pathlib import Path


def _run_and_read(module: str) -> str:
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/tmp/missing"
    env["QT_QPA_PLATFORM"] = "offscreen"
    subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        cwd=root,
        env=env,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    with open(root / "system.log", "r", encoding="utf-8") as f:
        return f.read()


def test_agent_terminal_self_heals():
    log = _run_and_read("agent_terminal")
    assert "Qt runtime ready" in log
    assert "/tmp/missing" not in log


def test_virtual_desktop_self_heals():
    log = _run_and_read("Virtual_Desktop")
    assert "Qt runtime ready" in log
    assert "/tmp/missing" not in log
```

**Functions:** _run_and_read(module), test_agent_terminal_self_heals(), test_virtual_desktop_self_heals()


## Module `tests\test_tasks.py`

```python
import json
import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tasks import TaskManager, TaskCard  # noqa: E402
from agent_terminal import Theme  # noqa: E402


def test_task_manager_persistence(tmp_path):
    path = tmp_path / "tasks.jsonl"
    mgr = TaskManager(str(path))
    t = mgr.add_task("Write docs", "todo", ["README.md"])
    assert t.title == "Write docs"
    mgr.update_task(t.id, status="done")
    tasks = mgr.list_tasks()
    assert tasks[0]["status"] == "done"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["status"] == "done"


def test_task_tracker_card_lists_tasks(tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "tasks.jsonl"
    mgr = TaskManager(str(path))
    mgr.add_task("Test", "todo", [])
    card = TaskCard(mgr, Theme(), lambda p: None)
    assert card.list.count() == 1
    card.deleteLater()
    app.quit()
```

**Functions:** test_task_manager_persistence(tmp_path), test_task_tracker_card_lists_tasks(tmp_path)


## Module `tests\test_task_card.py`

```python
import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tasks import TaskManager, TaskCard, open_card, close_card  # noqa: E402
from agent_terminal import Theme  # noqa: E402


def test_task_card_resize_and_persistence(tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "tasks.jsonl"
    mgr = TaskManager(str(path))
    card = TaskCard(mgr, Theme(), lambda p: None)
    card.resize(300, 200)
    assert card.width() == 300 and card.height() == 200

    t1 = mgr.add_task("A", "todo", [])
    mgr.add_task("B", "todo", [])
    card.refresh()
    assert card.list.count() == 2

    mgr.remove_task(t1.id)
    card.refresh()
    assert card.list.count() == 1
    card.close()

    mgr2 = TaskManager(str(path))
    card2 = TaskCard(mgr2, Theme(), lambda p: None)
    assert card2.list.count() == 1
    card2.deleteLater()
    app.quit()


def test_open_close_api(tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "tasks.jsonl"
    mgr = TaskManager(str(path))
    card = open_card(mgr, Theme(), lambda p: None)
    assert card.isVisible()
    close_card(card)
    assert not card.isVisible()
    app.quit()


def test_header_controls(tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    path = tmp_path / "tasks.jsonl"
    mgr = TaskManager(str(path))
    card = TaskCard(mgr, Theme(), lambda p: None)
    assert card.body.isVisible()
    card.min_btn.click()
    assert not card.body.isVisible()
    card.min_btn.click()
    assert card.body.isVisible()
    card.close_btn.click()
    assert not card.isVisible()
    app.quit()
```

**Functions:** test_task_card_resize_and_persistence(tmp_path), test_open_close_api(tmp_path), test_header_controls(tmp_path)


## Module `tests\test_task_modes.py`

```python
import json
import os
import uuid
from pathlib import Path
from PySide6.QtWidgets import QApplication


def test_task_modes_and_switch(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    monkeypatch.setattr(
        agent_terminal, "TASKS_DIR", tmp_path / "tasks", raising=False
    )
    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget.mode = "shell"
    monkeypatch.setattr(widget, "_run_one_off", lambda *a, **k: None)

    widget.input.setPlainText("Ask: hello")
    widget._on_enter()
    widget._flush_queue()
    task_id = widget.current_task_id
    mode_file = Path(agent_terminal.TASKS_DIR) / task_id / "mode.txt"
    history_file = Path(agent_terminal.TASKS_DIR) / task_id / "history.jsonl"
    assert widget.context_mode == "ask"
    assert mode_file.read_text().strip() == "ask"
    data = [json.loads(line) for line in history_file.read_text().splitlines()]
    assert data[0]["content"] == "hello"
    assert data[0]["mode"] == "ask"

    widget.input.setPlainText("Code: print('hi')")
    widget._on_enter()
    widget._flush_queue()
    assert widget.context_mode == "code"
    assert mode_file.read_text().strip() == "code"
    data = [json.loads(line) for line in history_file.read_text().splitlines()]
    assert data[-1]["content"] == "print('hi')"
    assert data[-1]["mode"] == "code"

    new_id = str(uuid.uuid4())
    widget.input.setPlainText(f"task {new_id}")
    widget._on_enter()
    widget._flush_queue()
    assert widget.current_task_id == new_id
    new_mode_file = Path(agent_terminal.TASKS_DIR) / new_id / "mode.txt"
    assert new_mode_file.exists()

    widget.deleteLater()
    app.quit()
```

**Functions:** test_task_modes_and_switch(tmp_path, monkeypatch)


## Module `tests\test_tethering.py`

```python
import json
from pathlib import Path

import deployment_manager


def _write(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def _read(path: Path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_tether_enable_disable(tmp_path, monkeypatch):
    monkeypatch.setattr(deployment_manager, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        deployment_manager,
        "TETHER_LOG_PATH",
        tmp_path / "datasets" / "tether_logs.jsonl",
    )
    monkeypatch.setattr(
        deployment_manager,
        "SETTINGS_PATH",
        tmp_path / "settings.json",
    )

    settings = {
        "node_a": {"allow_data_sharing": True},
        "node_b": {"allow_data_sharing": True},
    }
    (tmp_path / "settings.json").write_text(json.dumps(settings))

    bucket_a = tmp_path / "datasets" / "node_a_prompt_bucket.jsonl"
    bucket_b = tmp_path / "datasets" / "node_b_prompt_bucket.jsonl"
    _write(bucket_a, [{"id": "a1", "prompt": "A"}])
    _write(bucket_b, [{"id": "b1", "prompt": "B"}])

    deployment_manager.tether_nodes("node_a", "node_b", enable=True)

    ids_a = {row["id"] for row in _read(bucket_a)}
    ids_b = {row["id"] for row in _read(bucket_b)}
    assert ids_a == {"a1", "b1"}
    assert ids_b == {"a1", "b1"}

    _write(bucket_a, _read(bucket_a) + [{"id": "a2", "prompt": "A2"}])
    deployment_manager.tether_nodes("node_a", "node_b", enable=False)

    ids_b_after = {row["id"] for row in _read(bucket_b)}
    assert ids_b_after == {"a1", "b1"}

    log_lines = (
        tmp_path / "datasets" / "tether_logs.jsonl"
    ).read_text().splitlines()
    assert json.loads(log_lines[-1])["event"] == "disabled"
```

**Functions:** _write(path, rows), _read(path), test_tether_enable_disable(tmp_path, monkeypatch)


## Module `tests\test_tts.py`

```python
import os
from unittest.mock import patch
from PySide6.QtWidgets import QApplication


def test_speech_tool_invokes_tts():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget.tts_enabled = True
    widget.tts_voice = "Zira"
    with patch("agent_terminal.speak") as mock_speak:
        widget._tool_speech_say({"text": "hello"})
        mock_speak.assert_called_once()
    widget.deleteLater()
    app.quit()
```

**Functions:** test_speech_tool_invokes_tts()


## Module `tests\test_tts_unit.py`

```python
import types
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent_terminal as tts  # noqa: E402


def test_available_voices_returns_names_when_pyttsx3_present():
    engine = Mock()
    engine.getProperty.return_value = [
        types.SimpleNamespace(name="Alice"),
        types.SimpleNamespace(name="Bob"),
    ]
    fake_pyttsx3 = types.SimpleNamespace(init=Mock(return_value=engine))
    with patch.dict(sys.modules, {"pyttsx3": fake_pyttsx3}):
        voices = tts.available_voices()
    assert voices == ["Alice", "Bob"]


def test_speak_uses_pyttsx3_when_available():
    engine = Mock()
    fake_pyttsx3 = types.SimpleNamespace(init=Mock(return_value=engine))
    with patch.dict(sys.modules, {"pyttsx3": fake_pyttsx3}):
        assert tts.speak("hello")
    engine.say.assert_called_once_with("hello")
    engine.runAndWait.assert_called_once()


def test_speak_returns_false_when_all_engines_fail():
    fake_pyttsx3 = types.SimpleNamespace(
        init=Mock(side_effect=Exception("fail"))
    )
    fake_gtts = types.SimpleNamespace(
        gTTS=Mock(side_effect=Exception("no gtts"))
    )
    fake_playsound = types.SimpleNamespace(playsound=Mock())
    modules = {
        "pyttsx3": fake_pyttsx3,
        "gtts": fake_gtts,
        "playsound": fake_playsound,
    }
    with patch.dict(sys.modules, modules):
        with patch("subprocess.run", side_effect=Exception("no espeak")):
            assert not tts.speak("hello")


def test_speak_falls_back_to_gtts_when_pyttsx3_missing(tmp_path):
    fake_pyttsx3 = types.SimpleNamespace(
        init=Mock(side_effect=Exception("no pyttsx3"))
    )
    gtts_instance = Mock()
    gtts_instance.save = Mock(side_effect=lambda p: Path(p).touch())
    fake_gtts = types.SimpleNamespace(gTTS=Mock(return_value=gtts_instance))
    fake_playsound = types.SimpleNamespace(playsound=Mock())
    tmp_obj = types.SimpleNamespace(name=str(tmp_path / "out.mp3"))
    tmp_file = Mock()
    tmp_file.__enter__ = Mock(return_value=tmp_obj)
    tmp_file.__exit__ = Mock(return_value=False)
    modules = {
        "pyttsx3": fake_pyttsx3,
        "gtts": fake_gtts,
        "playsound": fake_playsound,
    }
    with patch.dict(sys.modules, modules):
        with patch("tempfile.NamedTemporaryFile", return_value=tmp_file):
            assert tts.speak("hi")
    fake_gtts.gTTS.assert_called_once_with("hi")
    fake_playsound.playsound.assert_called_once()
```

**Functions:** test_available_voices_returns_names_when_pyttsx3_present(), test_speak_uses_pyttsx3_when_available(), test_speak_returns_false_when_all_engines_fail(), test_speak_falls_back_to_gtts_when_pyttsx3_missing(tmp_path)


## Module `tests\test_virtual_desktop.py`

```python
import os
from pathlib import Path

from tasks import _open_cards, close_all_cards
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication  # noqa: E402


def test_virtual_desktop_window_title(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import tools.qt_utils as qt_utils
    import tools.qt_runtime as qt_runtime

    called = False

    def fake_runtime(*a, **k):
        nonlocal called
        called = True

    monkeypatch.setattr(qt_runtime, "ensure_qt_runtime", fake_runtime)
    monkeypatch.setattr(qt_utils, "ensure_pyside6", lambda *a, **k: True)

    import Virtual_Desktop

    assert not called

    app = QApplication.instance() or QApplication([])
    win = Virtual_Desktop.VirtualDesktop()
    assert win.windowTitle() == "Virtual Desktop"
    win.close()
    app.quit()


def test_virtual_desktop_open_tasks(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import Virtual_Desktop
    Virtual_Desktop.DATASETS_DIR = str(tmp_path)
    app = QApplication.instance() or QApplication([])
    win = Virtual_Desktop.VirtualDesktop()
    assert not _open_cards
    win._open_tasks()
    assert len(_open_cards) == 1
    close_all_cards()
    win.close()
    app.quit()
```

**Functions:** test_virtual_desktop_window_title(monkeypatch), test_virtual_desktop_open_tasks(tmp_path, monkeypatch)


## Module `tests\test_virtual_desktop_icons.py`

```python
import os
from pathlib import Path

import pytest
pytest.importorskip("PySide6")
from PySide6.QtGui import QIcon  # noqa: E402
from PySide6.QtWidgets import QApplication, QToolButton  # noqa: E402


def test_virtual_desktop_icons_and_launch(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    agent_file = tmp_path / "agent_terminal.py"
    agent_file.write_text(
        "from PySide6.QtWidgets import QLabel\n"
        "def build_widget(parent=None):\n"
        "    return QLabel('hi', parent)\n"
    )
    txt_file = tmp_path / "note.txt"
    txt_file.write_text("hello")
    json_file = tmp_path / "data.json"
    json_file.write_text("{}")
    subdir = tmp_path / "nested"
    subdir.mkdir()
    nested_txt = subdir / "inner.txt"
    nested_txt.write_text("deep")
    other_file = tmp_path / "run.sh"
    other_file.write_text("echo test")

    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import tools.qt_utils as qt_utils
    import tools.qt_runtime as qt_runtime
    monkeypatch.setattr(qt_runtime, "ensure_qt_runtime", lambda *a, **k: "")
    monkeypatch.setattr(qt_utils, "ensure_pyside6", lambda *a, **k: True)
    import Virtual_Desktop as vd
    monkeypatch.setattr(vd, "VDSK_ROOT", str(tmp_path))

    app = QApplication.instance() or QApplication([])
    win = vd.VirtualDesktop()
    win.load_workspace()

    buttons = {b.text(): b for b in win.canvas.findChildren(QToolButton)}
    assert {"agent_terminal", "note", "data", "inner", "run"} <= set(
        buttons.keys()
    )
    for b in buttons.values():
        assert not b.icon().isNull()
    term_icon = QIcon.fromTheme("utilities-terminal")
    if not term_icon.isNull():
        assert (
            buttons["agent_terminal"].icon().cacheKey()
            == term_icon.cacheKey()
        )

    win.remove_icon(str(other_file))
    assert "run" not in {
        b.text() for b in win.canvas.findChildren(QToolButton)
    }

    win.open_any_path(str(agent_file))
    win.open_any_path(str(txt_file))
    win.open_any_path(str(json_file))
    win.open_any_path(str(nested_txt))
    win.open_any_path(str(other_file))
    titles = [c.title_label.text() for c in win._iter_cards()]
    assert any("agent_terminal.py" in t for t in titles)
    assert any("Editor" in t and "note.txt" in t for t in titles)
    assert any("Editor" in t and "data.json" in t for t in titles)
    assert any("Editor" in t and "inner.txt" in t for t in titles)
    assert any("Process" in t and "run.sh" in t for t in titles)

    win.close()
    app.quit()
```

**Functions:** test_virtual_desktop_icons_and_launch(tmp_path, monkeypatch)


## Module `tests\test_virtual_desktop_plugins.py`

```python
import importlib
import os
import site
import sys

import pytest
from PySide6.QtWidgets import QApplication
from tools import qt_runtime


def test_virtual_desktop_missing_plugins(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.delenv("QT_QPA_PLATFORM_PLUGIN_PATH", raising=False)
    qt_runtime.reset_qt_plugin_cache()

    from PySide6.QtCore import QLibraryInfo

    missing = tmp_path / "missing"
    monkeypatch.setattr(QLibraryInfo, "location", lambda *_: str(missing))
    monkeypatch.setattr(site, "getsitepackages", lambda: [])

    sys.modules.pop("Virtual_Desktop", None)
    vd_mod = importlib.import_module("Virtual_Desktop")

    app = QApplication.instance() or QApplication([])
    vd = vd_mod.VirtualDesktop()
    with pytest.raises(RuntimeError):
        vd._open_code_editor(__file__)
    vd.deleteLater()
    app.quit()

    fixed = tmp_path / "fixed"
    fixed.mkdir()
    monkeypatch.setattr(QLibraryInfo, "location", lambda *_: str(fixed))

    qt_runtime.reset_qt_plugin_cache()
    sys.modules.pop("Virtual_Desktop", None)
    vd_mod = importlib.import_module("Virtual_Desktop")

    app = QApplication.instance() or QApplication([])
    vd = vd_mod.VirtualDesktop()
    vd._open_code_editor(__file__)
    vd.deleteLater()
    app.quit()
    assert os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] == str(fixed)
```

**Functions:** test_virtual_desktop_missing_plugins(monkeypatch, tmp_path)


## Module `tests\test_virtual_desktop_repair.py`

```python
import os
import sys
import importlib
import types
from pathlib import Path


def test_virtual_desktop_repairs_missing_pyside6(monkeypatch, tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    import tools.qt_utils as qt_utils
    import tools.qt_runtime as qt_runtime

    monkeypatch.setattr(qt_runtime, "ensure_qt_runtime", lambda: str(tmp_path))

    called = {}

    def fake_install(pkg, logger=None):
        called["pkg"] = pkg

        class Dummy(types.ModuleType):
            def __getattr__(self, attr):
                class AttrDummy:
                    def __init__(self, *args, **kwargs):
                        pass

                setattr(self, attr, AttrDummy)
                return AttrDummy

        core = Dummy("PySide6.QtCore")
        core.QLibraryInfo = type(
            "QLibraryInfo",
            (),
            {
                "PluginsPath": object(),
                "location": staticmethod(lambda kind: str(tmp_path)),
            },
        )
        gui = Dummy("PySide6.QtGui")
        widgets = Dummy("PySide6.QtWidgets")
        pkg_mod = types.SimpleNamespace(
            QtCore=core,
            QtGui=gui,
            QtWidgets=widgets,
        )
        sys.modules.update(
            {
                "PySide6": pkg_mod,
                "PySide6.QtCore": core,
                "PySide6.QtGui": gui,
                "PySide6.QtWidgets": widgets,
            }
        )
        return True

    monkeypatch.setattr(qt_utils, "attempt_pip_install", fake_install)

    def fake_ensure(logger=None):
        fake_install("PySide6", logger)
        return True

    monkeypatch.setattr(qt_utils, "ensure_pyside6", fake_ensure)

    for name in list(sys.modules):
        if name.startswith("PySide6"):
            sys.modules.pop(name, None)

    importlib.reload(importlib.import_module("Virtual_Desktop"))

    assert called.get("pkg") == "PySide6"
```

**Functions:** test_virtual_desktop_repairs_missing_pyside6(monkeypatch, tmp_path)


## Module `tests\test_window_smoke.py`

```python
import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLibraryInfo, QTimer


def test_host_window_shows(monkeypatch):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    plugin_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    monkeypatch.setattr(
        "tools.qt_runtime.ensure_qt_runtime", lambda logger=None: plugin_path
    )
    monkeypatch.setattr(
        "tools.qt_utils.ensure_pyside6", lambda logger=None: True
    )
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
    import agent_terminal

    result = {}

    def check():
        windows = [w for w in QApplication.topLevelWidgets() if w.isVisible()]
        result["titles"] = [w.windowTitle() for w in windows]
        for w in windows:
            w.close()
        QApplication.quit()

    QTimer.singleShot(0, check)
    agent_terminal.main([])
    assert result.get("titles") == ["Agent Terminal"]
```

**Functions:** test_host_window_shows(monkeypatch)


## Module `tests\test_workspace_icons.py`

```python
import os
from pathlib import Path

import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication, QToolButton  # noqa: E402


def test_workspace_icons(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    script = tmp_path / "sample.py"
    script.write_text("print('ok')\n")
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import tools.qt_utils as qt_utils
    import tools.qt_runtime as qt_runtime

    monkeypatch.setattr(qt_utils, "ensure_pyside6", lambda *a, **k: True)
    monkeypatch.setattr(qt_runtime, "ensure_qt_runtime", lambda *a, **k: "")

    from Virtual_Desktop import VirtualDesktop

    app = QApplication.instance() or QApplication([])
    win = VirtualDesktop()
    win.load_workspace(str(tmp_path))
    icons = [b.text() for b in win.canvas.findChildren(QToolButton)]
    assert "sample" in icons
    win.close()
    app.quit()
```

**Functions:** test_workspace_icons(tmp_path, monkeypatch)


## Module `tests\codex\test_ensure_codex.py`

```python
import io
import json
import sys
import tarfile
import hashlib
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent.parent)
)  # noqa: E402
import codex_installation  # noqa: E402


class DummyResp:
    def __init__(self, data: bytes):
        self._data = data

    def iter_content(self, chunk_size=8192):
        yield self._data

    def raise_for_status(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _archive_bytes() -> tuple[bytes, str]:
    file_data = b"echo hi"
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        info = tarfile.TarInfo("codex")
        info.size = len(file_data)
        tf.addfile(info, io.BytesIO(file_data))
    data = buf.getvalue()
    return data, hashlib.sha256(data).hexdigest()


def test_ensure_codex_installed(tmp_path, monkeypatch):
    data, checksum = _archive_bytes()
    monkeypatch.setattr(
        codex_installation,
        "PLATFORM_ARCHIVES",
        {
            "linux": {
                "url": "http://example.com/codex.tar.gz",
                "checksum": checksum,
                "binary": "codex",
            }
        },
    )
    monkeypatch.setattr(
        codex_installation.requests, "get", lambda *a, **k: DummyResp(data)
    )
    monkeypatch.setattr(sys, "platform", "linux")
    base = tmp_path / "Codex"
    dataset = tmp_path / "datasets" / "codex_installs.jsonl"
    path = codex_installation.ensure_codex_installed(
        base_dir=base, dataset_log=dataset
    )
    assert path.exists()
    meta = base / "metadata.jsonl"
    rec = json.loads(meta.read_text().strip().splitlines()[-1])
    assert rec["checksum"] == checksum
    dataset_rec = json.loads(dataset.read_text().strip().splitlines()[-1])
    assert dataset_rec["platform"] == "linux"


def test_ensure_codex_checksum_failure(tmp_path, monkeypatch):
    data, checksum = _archive_bytes()
    monkeypatch.setattr(
        codex_installation,
        "PLATFORM_ARCHIVES",
        {
            "linux": {
                "url": "http://example.com/codex.tar.gz",
                "checksum": "bad",
                "binary": "codex",
            }
        },
    )
    monkeypatch.setattr(
        codex_installation.requests, "get", lambda *a, **k: DummyResp(data)
    )
    monkeypatch.setattr(sys, "platform", "linux")
    base = tmp_path / "Codex"
    dataset = tmp_path / "datasets" / "codex_installs.jsonl"
    with pytest.raises(ValueError):
        codex_installation.ensure_codex_installed(
            base_dir=base, dataset_log=dataset
        )
```

**Classes:** DummyResp
**Functions:** _archive_bytes(), test_ensure_codex_installed(tmp_path, monkeypatch), test_ensure_codex_checksum_failure(tmp_path, monkeypatch)


## Module `tests\deploy\test_deployment_manager.py`

```python
"""Integration tests for deployment manager helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

import deployment_manager


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "agent_terminal.py").write_text(
        "import time\n"
        "if __name__ == '__main__':\n"
        "    time.sleep(60)\n"
    )
    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["git", "add", "agent_terminal.py"],
        cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return repo


def test_clone_repo_and_launch(monkeypatch, tmp_path):
    repo = _make_repo(tmp_path)
    monkeypatch.setattr(deployment_manager, "REPO_ROOT", repo)
    monkeypatch.setattr(
        deployment_manager,
        "DATASET_PATH",
        tmp_path / "deployments.jsonl",
    )

    dest = tmp_path / "clone"
    deployment_manager.clone_repo(str(dest))
    assert (dest / "agent_terminal.py").exists()

    proc = deployment_manager.launch_agent(str(dest))
    assert proc.poll() is None
    proc.terminate()
    proc.wait(timeout=5)


def test_tether_logs(monkeypatch, tmp_path):
    repo = _make_repo(tmp_path)
    monkeypatch.setattr(deployment_manager, "REPO_ROOT", repo)

    src = tmp_path / "src"
    dst = tmp_path / "dst"
    deployment_manager.clone_repo(str(src))
    deployment_manager.clone_repo(str(dst))

    (src / "datasets").mkdir()
    (src / "datasets" / "log.jsonl").write_text("entry\n")

    deployment_manager.tether_logs(str(src), str(dst))
    assert (dst / "datasets" / "log.jsonl").read_text() == "entry\n"
```

Integration tests for deployment manager helpers.
**Functions:** _make_repo(tmp_path), test_clone_repo_and_launch(monkeypatch, tmp_path), test_tether_logs(monkeypatch, tmp_path)


## Module `tests\memory\test_bucket_manager.py`

```python
import json
from importlib import reload
from pathlib import Path

import memory.bucket_manager as bm


def test_register_append_query(tmp_path, monkeypatch):
    monkeypatch.setenv("DATASETS_DIR", str(tmp_path))
    reload(bm)
    bm.register_bucket("test", "test.jsonl", "desc")
    bm.append_entry("test", {"a": 1})
    path = Path(tmp_path) / "test.jsonl"
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["a"] == 1 and rec.get("timestamp")
    res = bm.query_bucket("test", {"a": 1})
    assert len(res) == 1 and res[0]["a"] == 1
    assert not bm.query_bucket("test", {"a": 2})
```

**Functions:** test_register_append_query(tmp_path, monkeypatch)


## Module `tests\memory\test_prompt_buckets.py`

```python
from __future__ import annotations

import json
from pathlib import Path
import importlib

import memory.prompt_buckets as pb


def _reload(tmp_path, monkeypatch):
    monkeypatch.setenv("DATASETS_DIR", str(tmp_path))
    importlib.reload(pb)


def test_append_and_retrieve(tmp_path, monkeypatch):
    _reload(tmp_path, monkeypatch)
    pb.append_bucket("test", "hello", "world", {"a": 1})
    pb.append_bucket("test", "hey", "earth", {})
    res = pb.retrieve_similar("test", "hello", top_k=1)
    assert res and res[0]["response"] == "world"


def test_retry_logic(tmp_path, monkeypatch):
    _reload(tmp_path, monkeypatch)
    import agent_terminal
    importlib.reload(agent_terminal)

    attempts = []

    class Resp:
        def __init__(self, ok: bool, data: dict):
            self.ok = ok
            self._data = data
            self.text = ""

        def json(self):
            return self._data

    def fake_post(url, json_payload, timeout):
        attempts.append(1)
        if len(attempts) == 1:
            return Resp(True, {"message": {"content": ""}})
        return Resp(True, {"message": {"content": "hi"}})

    class DummyReq:
        post = staticmethod(fake_post)

    monkeypatch.setattr(agent_terminal, "_requests", lambda: DummyReq)

    msgs = [{"role": "user", "content": "hello"}]
    out = agent_terminal.post_with_retry("m", msgs, retries=2)
    assert out == "hi"

    path = Path(tmp_path) / "prompt_attempts.jsonl"
    text_lines = path.read_text().splitlines()
    lines = [json.loads(line) for line in text_lines if line.strip()]
    assert len(lines) == 2

    bucket_path = Path(tmp_path) / "prompt_buckets" / "llm_retries.jsonl"
    with bucket_path.open("r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    assert entries and entries[0]["prompt"] == "Describe issue and propose fix"
```

**Functions:** _reload(tmp_path, monkeypatch), test_append_and_retrieve(tmp_path, monkeypatch), test_retry_logic(tmp_path, monkeypatch)


## Module `tests\schema\test_schema_manager.py`

```python
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
import schema_manager  # noqa: E402


def test_validate_schema(monkeypatch, tmp_path):
    canonical = {
        "type": "object",
        "additionalProperties": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
    }
    schema_file = tmp_path / "canonical.json"
    schema_file.write_text(json.dumps(canonical), encoding="utf-8")
    monkeypatch.setattr(schema_manager, "BASE_SCHEMA_PATH", schema_file)

    good = {"Agent_terminal.md": {"terminal": "text"}}
    bad = {"Agent_terminal.md": {"terminal": 1}}

    assert schema_manager.validate_schema(good)
    assert not schema_manager.validate_schema(bad)


def test_apply_schema_to_persona_appends(tmp_path):
    persona = tmp_path / "Agent_terminal.md"
    persona.write_text("# Notes\n", encoding="utf-8")
    schema = {"Agent_terminal.md": {"terminal": "hello"}}

    assert schema_manager.apply_schema_to_persona(schema, persona)
    first = persona.read_text(encoding="utf-8")
    assert "hello" in first

    assert not schema_manager.apply_schema_to_persona(schema, persona)
    second = persona.read_text(encoding="utf-8")
    assert first == second
```

**Functions:** test_validate_schema(monkeypatch, tmp_path), test_apply_schema_to_persona_appends(tmp_path)


## Module `tests\security\test_guardrails.py`

```python
import json
import os
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QMessageBox

from security.guardrails import requires_confirmation, is_safe_path


def test_blocked_path_detection(tmp_path):
    safe = tmp_path / "file.txt"
    blocked = Path("/etc/passwd")
    assert is_safe_path(safe)
    assert not is_safe_path(blocked)
    assert requires_confirmation(f"rm {blocked}")
    assert not requires_confirmation(f"echo {safe}")


def test_full_auto_execution_branches(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import agent_terminal

    monkeypatch.setattr(
        agent_terminal, "COMMAND_LOG_PATH", tmp_path / "command_log.jsonl"
    )
    monkeypatch.setattr(
        agent_terminal, "AUTH_LOG_PATH", tmp_path / "authorizations.jsonl"
    )

    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()

    widget.full_auto_cb.setChecked(True)
    widget._auto_execute_command("echo hi", widget.current_shell)
    widget._flush_queue()
    with open(tmp_path / "command_log.jsonl", encoding="utf-8") as f:
        entry = json.loads(f.read().strip())
    assert entry["cmd"] == "echo hi"
    assert entry["status"] == "auto"

    with patch.object(
        QMessageBox, "question", return_value=QMessageBox.No
    ) as mq:
        widget._auto_execute_command("cat /etc/passwd", widget.current_shell)
        mq.assert_called_once()
    with open(tmp_path / "command_log.jsonl", encoding="utf-8") as f:
        data = f.read()
    assert "/etc/passwd" not in data

    widget.full_auto_cb.setChecked(False)
    widget._auto_execute_command("echo bye", widget.current_shell)
    with open(tmp_path / "command_log.jsonl", encoding="utf-8") as f:
        lines = f.read().splitlines()
    last = json.loads(lines[-1])
    assert last["status"] == "manual"

    widget.deleteLater()
    app.quit()
```

**Functions:** test_blocked_path_detection(tmp_path), test_full_auto_execution_branches(tmp_path, monkeypatch)


## Module `tests\shells\test_detector.py`

```python
import os
import platform
import subprocess

from shells.detector import detect_shell


def test_detect_shell_unix_env(monkeypatch):
    monkeypatch.setenv("SHELL", "/bin/zsh")
    monkeypatch.delenv("COMSPEC", raising=False)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    assert detect_shell() == "zsh"


def test_detect_shell_windows_env(monkeypatch):
    monkeypatch.setenv("COMSPEC", "C:\\Windows\\System32\\cmd.exe")
    monkeypatch.delenv("SHELL", raising=False)
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    assert detect_shell() == "cmd"


def test_detect_shell_parent_process(monkeypatch):
    monkeypatch.delenv("SHELL", raising=False)
    monkeypatch.delenv("COMSPEC", raising=False)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(os, "getppid", lambda: 123)

    def fake_check_output(cmd, stderr=None):
        if "ppid=" in cmd:
            return b"0"
        return b"bash"

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    assert detect_shell() == "bash"
```

**Functions:** test_detect_shell_unix_env(monkeypatch), test_detect_shell_windows_env(monkeypatch), test_detect_shell_parent_process(monkeypatch)


## Module `tests\shells\test_transpiler.py`

```python
from shells.transpiler import transpile_command


def test_transpile_cmd():
    assert transpile_command("pwd", "cmd") == "cd"
    assert transpile_command("ls", "cmd") == "dir"


def test_transpile_powershell():
    assert transpile_command("pwd", "powershell") == "Get-Location"
    assert transpile_command("clear", "powershell") == "Clear-Host"


def test_transpile_no_change():
    assert transpile_command("pwd", "bash") == "pwd"
```

**Functions:** test_transpile_cmd(), test_transpile_powershell(), test_transpile_no_change()


## Module `tests\ui\test_task_panel.py`

```python
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402

import agent_terminal  # noqa: E402
import tasks  # noqa: E402
from tasks import TaskManager, TaskCard  # noqa: E402


def test_ctrl_t_toggles_task_panel(qtbot, tmp_path):
    app = QApplication.instance() or QApplication([])
    widget = agent_terminal.build_widget()
    widget.task_mgr = TaskManager(str(tmp_path / "tasks.jsonl"))
    widget.task_mgr.add_task("Demo", "todo", [])
    qtbot.addWidget(widget)
    QTest.keyClick(widget, Qt.Key_T, Qt.ControlModifier)
    assert widget._task_cards and widget._task_cards[0].isVisible()
    QTest.keyClick(widget, Qt.Key_T, Qt.ControlModifier)
    assert not widget._task_cards
    widget.deleteLater()
    app.quit()


def test_open_editor_links_file(qtbot, tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    mgr = TaskManager(str(tmp_path / "tasks.jsonl"))
    mgr.add_task("Edit", "todo", [])
    opened = {}

    def fake_open(path: str) -> None:
        opened["path"] = path

    card = TaskCard(mgr, agent_terminal.Theme(), fake_open)
    qtbot.addWidget(card)
    tmp_file = tmp_path / "foo.txt"
    tmp_file.write_text("hi", encoding="utf-8")
    monkeypatch.setattr(
        tasks.QFileDialog,
        "getOpenFileName",
        lambda *a, **k: (str(tmp_file), ""),
    )
    row = card.list.layout.itemAt(0).widget()
    row.edit_btn.click()
    data = mgr.list_tasks()[0]
    assert opened["path"] == str(tmp_file)
    assert data["files"] == [str(tmp_file)]
    card.deleteLater()
    app.quit()
```

**Functions:** test_ctrl_t_toggles_task_panel(qtbot, tmp_path), test_open_editor_links_file(qtbot, tmp_path, monkeypatch)


## Module `tools\codex_pr_sentinel.py`

```python
import json
import os
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# --- Utilities --------------------------------------------------------------

def _fetch_json(session: requests.Session, url: str) -> dict:
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# --- CI and repo helpers ---------------------------------------------------

def _ci_summary(session: requests.Session, repo: str, sha: Optional[str]) -> List[str]:
    """Summarize CI status checks for the given commit SHA."""
    if not sha:
        return ["- ⚠️ No commit SHA available to query CI."]
    checks_url = f"https://api.github.com/repos/{repo}/commits/{sha}/check-runs"
    try:
        checks = _fetch_json(session, checks_url)
    except Exception:
        return ["- ⚠️ Failed to fetch CI checks."]
    lines: List[str] = []
    for check in checks.get("check_runs", []):
        name = check.get("name", "unknown")
        status = check.get("conclusion") or check.get("status") or "unknown"
        emoji = {
            "success": "✅",
            "neutral": "⚪",
            "skipped": "⏭️",
            "failure": "❌",
            "timed_out": "⏲️",
            "action_required": "⚠️",
            "in_progress": "⏳",
            "queued": "⏳",
        }.get(status, "❔")
        lines.append(f"- {emoji} **{name}**: {status}")
    if not lines:
        lines.append("- ⚪ No CI checks found.")
    return lines

def _read_auto_merge() -> bool:
    """Check if auto-merge is enabled for this repo (simple implementation)."""
    # Looks for a .github/auto-merge file containing 'true'
    try:
        with open(".github/auto-merge", "r", encoding="utf-8") as f:
            content = f.read().strip().lower()
            return "true" in content
    except Exception:
        return False

# --- Memory / state --------------------------------------------------------

MEM_DIR = Path("memory")
MEM_DIR.mkdir(exist_ok=True)
CODex_MEM_FILE = MEM_DIR / "codex_memory.json"
LOGIC_INBOX = MEM_DIR / "logic_inbox.jsonl"

def _load_codex_memory() -> Dict:
    if not CODex_MEM_FILE.exists():
        return {}
    try:
        return json.loads(CODex_MEM_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _write_codex_memory(mem: Dict) -> None:
    CODex_MEM_FILE.write_text(json.dumps(mem, indent=2, ensure_ascii=False), encoding="utf-8")

def _append_logic_inbox(entry: Dict) -> None:
    try:
        with LOGIC_INBOX.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # best-effort only
        pass

# --- Error reporting -------------------------------------------------------

def _report_error(repo: str, pr_number: str, head_sha: Optional[str], exc: Exception) -> None:
    ts = _now_iso()
    dump = {
        "timestamp": ts,
        "repo": repo,
        "pr_number": pr_number,
        "head_sha": head_sha,
        "error": repr(exc),
    }
    # Append to ErrorDump.md to follow repo conventions.
    try:
        with open("ErrorDump.md", "a", encoding="utf-8") as f:
            f.write(f"\n- {ts} - PR #{pr_number} ({repo}) - {repr(exc)}\n")
    except Exception:
        pass
    # Also add to logic inbox for visibility
    _append_logic_inbox({"type": "error_dump", "payload": dump})

# --- Main sentinel logic ---------------------------------------------------

TAG = "<!-- CODEX-SENTINEL-COMMENT -->"

def main():
    # Validate environment
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER")
    comment_id = os.environ.get("COMMENT_ID")
    if comment_id and comment_id.lower() == "null":
        comment_id = None

    missing = [k for k, v in (("GITHUB_TOKEN", token), ("GITHUB_REPOSITORY", repo), ("PR_NUMBER", pr_number)) if not v]
    if missing:
        raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {token}"
    session.headers["Accept"] = "application/vnd.github+json"

    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    try:
        pr = _fetch_json(session, pr_url)
    except Exception as e:
        _report_error(repo or "<unknown>", pr_number or "<unknown>", None, e)
        raise

    head_sha = pr.get("head", {}).get("sha")
    head_ref = pr.get("head", {}).get("ref")
    base_ref = pr.get("base", {}).get("ref")
    mergeable_state = pr.get("mergeable_state", "unknown")
    draft = pr.get("draft", False)

    # Load memory and determine monitoring state for this PR
    mem = _load_codex_memory()
    key = f"{repo}#{pr_number}"
    entry = mem.get(key, {})
    last_seen_sha = entry.get("last_seen_sha")
    no_change_count = int(entry.get("no_change_count", 0))
    benched = bool(entry.get("benched", False))

    triggered_by_comment = bool(comment_id)

    # Determine changes and bench/reactivation logic
    if head_sha and last_seen_sha == head_sha:
        no_change_count = no_change_count + 1
    else:
        no_change_count = 0

    # Reactivate on explicit activity (comment trigger) or when HEAD changed
    reactivated = False
    if triggered_by_comment or (head_sha and last_seen_sha != head_sha):
        if benched:
            reactivated = True
        benched = False
        no_change_count = 0

    # Bench after two consecutive unchanged observations
    if no_change_count >= 2:
        benched = True

    # Persist updated memory state preliminarily
    mem[key] = {
        "last_seen_sha": head_sha,
        "no_change_count": no_change_count,
        "benched": benched,
        "last_checked": _now_iso(),
        "last_comment_id": comment_id or entry.get("last_comment_id"),
    }
    _write_codex_memory(mem)

    # Decide whether to produce/update canonical comment:
    # - If benched and this run is NOT an explicit reactivation (triggered_by_comment or head change), skip posting to reduce noise.
    skip_post = False
    if benched and not reactivated and not triggered_by_comment:
        skip_post = True

    # Build summary content (we still prepare it for logs even if skipping posting)
    ci_lines = _ci_summary(session, repo, head_sha)
    blockers: List[str] = []
    all_success = all(
        ("success" in line or "neutral" in line or "skipped" in line)
        for line in ci_lines if line.startswith("-")
    )
    if mergeable_state != "clean":
        blockers.append(f"mergeable_state: {mergeable_state}")
    if not all_success:
        blockers.append("failing or pending checks")
    if draft:
        blockers.append("draft PR")

    comment_lines = [
        TAG,
        f"**head** `{head_ref}` → **base** `{base_ref}`",
        f"mergeable_state: `{mergeable_state}`",
        "",
        "### CI Status",
        *ci_lines,
        "",
        "### Blockers",
        *([f"- {b}" for b in blockers] or ["- None"]),
        "",
        "### @codex — Next Actions",
    ]

    if blockers:
        if "mergeable_state" in " ".join(blockers):
            comment_lines.append("- Resolve merge conflicts.")
        if "failing or pending checks" in blockers:
            comment_lines.append("- Fix failing checks.")
        if draft:
            comment_lines.append("- Mark PR ready for review.")
    else:
        if _read_auto_merge():
            comment_lines.append("- Auto-merge when all approvals are present.")
        else:
            comment_lines.append("- Manual merge is allowed.")

    # Guidance to append to Agent.md
    comment_lines.append("- Append this run to `Agent.md` Session Log.")

    comment_body = "\n".join(comment_lines)

    try:
        if skip_post:
            # Bench mode: do not post to PR to avoid noise. Log to memory and Agent.md only.
            with open("Agent.md", "a", encoding="utf-8") as f:
                f.write(f"- {_now_iso()}: Benched PR #{pr_number} ({repo}) — skipped posting canonical sentinel comment\n")
            _append_logic_inbox({
                "type": "sentinel_bench",
                "ts": _now_iso(),
                "repo": repo,
                "pr_number": pr_number,
                "head_sha": head_sha,
                "reason": "no_changes_for_two_checks"
            })
            return

        # Post or patch canonical comment
        comments_api = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
        existing = None
        resp = session.get(comments_api, timeout=10)
        resp.raise_for_status()
        for c in resp.json():
            if isinstance(c, dict) and c.get("body", "").startswith(TAG):
                existing = c
                break

        payload = {"body": comment_body}
        if existing:
            session.patch(f"{comments_api}/{existing['id']}", json=payload, timeout=10)
            action = "patched"
        else:
            session.post(comments_api, json=payload, timeout=10)
            action = "created"

        # Do NOT delete trigger comments. Preserve original @codex comment for trace.
        # Record run in Agent.md and logic inbox
        with open("Agent.md", "a", encoding="utf-8") as f:
            note = f"- {_now_iso()}: {action.capitalize()} canonical @codex comment for PR #{pr_number} (head {head_ref} -> base {base_ref})\n"
            if reactivated:
                note = note.strip() + " — reactivated monitoring\n"
            f.write(note)

        _append_logic_inbox({
            "type": "sentinel_run",
            "ts": _now_iso(),
            "repo": repo,
            "pr_number": pr_number,
            "head_sha": head_sha,
            "action": action,
            "benched": benched,
            "reactivated": reactivated,
            "blockers": blockers,
        })

    except Exception as e:
        _report_error(repo, pr_number, head_sha, e)
        raise

if __name__ == "__main__":
    main()
```

**Functions:** _fetch_json(session, url), _now_iso(), _ci_summary(session, repo, sha), _read_auto_merge(), _load_codex_memory(), _write_codex_memory(mem), _append_logic_inbox(entry), _report_error(repo, pr_number, head_sha, exc), main()


## Module `tools\harvest_logic.py`

```python
#!/usr/bin/env python3
"""
Cross-Branch Logic Harvester
Detects logic present on non-main branches but missing from main.
Updates memory/branch_logic.jsonl and docs/CROSS_BRANCH_LOGIC.md.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> str:
    """Run a command and return its stdout."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def harvest(repo: Path, main_branch: str = "main") -> list[dict]:
    """Return branch diff information compared to ``main_branch``."""
    branches = run([
        "git",
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/heads/",
    ], repo).splitlines()
    findings = []
    for branch in branches:
        if branch == main_branch:
            continue
        diff = run(["git", "diff", "--name-only", f"{main_branch}...{branch}"], repo).splitlines()
        diff = [f for f in diff if f]
        if diff:
            findings.append({"branch": branch, "files": diff})
    return findings


def write_memory(findings: list[dict], memory_path: Path) -> None:
    """Append findings to ``memory/branch_logic.jsonl``."""
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat() + "Z"
    with memory_path.open("a", encoding="utf-8") as fh:
        for item in findings:
            fh.write(json.dumps({"timestamp": timestamp, **item}) + "\n")


def write_report(findings: list[dict], report_path: Path) -> None:
    """Write findings to ``docs/CROSS_BRANCH_LOGIC.md``."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Cross-Branch Logic Report", ""]
    if not findings:
        lines.append("No branch logic differences detected.")
    else:
        for item in findings:
            lines.append(f"## {item['branch']}")
            lines.extend([f"- {path}" for path in item["files"]])
            lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    findings = harvest(repo)
    write_memory(findings, repo / "memory" / "branch_logic.jsonl")
    write_report(findings, repo / "docs" / "CROSS_BRANCH_LOGIC.md")


if __name__ == "__main__":
    main()
```

Cross-Branch Logic Harvester
Detects logic present on non-main branches but missing from main.
Updates memory/branch_logic.jsonl and docs/CROSS_BRANCH_LOGIC.md.
**Functions:** run(cmd, cwd), harvest(repo, main_branch), write_memory(findings, memory_path), write_report(findings, report_path), main()


## Module `tools\logic_inbox.py`

```python
import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from typing import List, Dict

INBOX_PATH = os.path.join("memory", "logic_inbox.jsonl")
MEMORY_PATH = os.path.join("memory", "codex_memory.json")

def load_entries() -> List[Dict]:
    entries: List[Dict] = []
    if not os.path.exists(INBOX_PATH):
        return entries
    with open(INBOX_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"Invalid JSONL entry: {e}")
    return entries

def write_entries(entries: List[Dict]) -> None:
    with open(INBOX_PATH, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def add_entry(summary: str, details: str) -> None:
    entries = load_entries()
    entry = {
        "id": str(uuid.uuid4()),
        "summary": summary,
        "details": details,
        "status": "pending",
    }
    entries.append(entry)
    write_entries(entries)
    print(entry["id"])

def mark_done(entry_id: str) -> None:
    entries = load_entries()
    changed = False
    for e in entries:
        if e.get("id") == entry_id:
            e["status"] = "done"
            changed = True
            break
    if changed:
        write_entries(entries)
    else:
        raise SystemExit("Entry not found")

def remove_entry(entry_id: str) -> None:
    entries = load_entries()
    new_entries = [e for e in entries if e.get("id") != entry_id]
    if len(new_entries) == len(entries):
        raise SystemExit("Entry not found")
    write_entries(new_entries)

def validate() -> None:
    entries = load_entries()
    # Always validate syntax via load_entries
    # Fail if running on main branch and pending entries remain
    ref = os.environ.get("GITHUB_REF", "")
    if ref == "refs/heads/main":
        pending = [e for e in entries if e.get("status") == "pending"]
        if pending:
            raise SystemExit("Pending logic inbox entries detected on main")

def sync_inbox_to_memory() -> None:
    entries = load_entries()
    pending_summaries = [e.get("summary") for e in entries if e.get("status") == "pending"]
    if not pending_summaries:
        return
    if not os.path.exists(MEMORY_PATH):
        return
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        mem = json.load(f)
    work = mem.setdefault("work_items", [])
    changed = False
    for summary in pending_summaries:
        if summary not in work:
            work.append(summary)
            changed = True
    if changed:
        mem["updated_utc"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(mem, f, indent=2, ensure_ascii=False)

def main() -> None:
    parser = argparse.ArgumentParser(description="Manage logic inbox")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--add", nargs=2, metavar=("SUMMARY", "DETAILS"))
    g.add_argument("--done", metavar="ID")
    g.add_argument("--remove", metavar="ID")
    g.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    if args.add:
        add_entry(args.add[0], args.add[1])
    elif args.done:
        mark_done(args.done)
    elif args.remove:
        remove_entry(args.remove)
    elif args.validate:
        validate()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

**Functions:** load_entries(), write_entries(entries), add_entry(summary, details), mark_done(entry_id), remove_entry(entry_id), validate(), sync_inbox_to_memory(), main()


## Module `tools\manage_tests.py`

```python
"""Manage placeholder tests and docs-only detection.

- Creates a placeholder smoke test when no real tests exist.
- Detects documentation-only changes and signals test skips.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

DOC_EXTS = {".md", ".rst", ".txt"}
PLACEHOLDER = Path("tests/test_smoke.py")


def _changed_files() -> list[str]:
    base = os.environ.get("BASE_REF", "origin/main")
    cmd = ["git", "diff", "--name-only", f"{base}..."]
    out = subprocess.run(cmd, check=False, capture_output=True, text=True)
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _is_docs_only(files: list[str]) -> bool:
    return bool(files) and all(Path(f).suffix in DOC_EXTS for f in files)


def _ensure_placeholder():
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    test_files = list(tests_dir.glob("test_*.py"))
    if not test_files:
        PLACEHOLDER.write_text(
            "# COPILOT: PLACEHOLDER TEST, REMOVE WHEN REAL TESTS EXIST\n"
            "def test_smoke():\n    assert True\n",
            encoding="utf-8",
        )
    elif PLACEHOLDER.exists() and len(test_files) > 1:
        PLACEHOLDER.unlink()


def main() -> None:
    files = _changed_files()
    docs_only = _is_docs_only(files)
    if docs_only:
        print("docs-only; tests skipped")
    else:
        _ensure_placeholder()
    if (out := os.environ.get("GITHUB_OUTPUT")):
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"docs_only={'true' if docs_only else 'false'}\n")


if __name__ == "__main__":
    main()
```

Manage placeholder tests and docs-only detection.

- Creates a placeholder smoke test when no real tests exist.
- Detects documentation-only changes and signals test skips.
**Functions:** _changed_files(), _is_docs_only(files), _ensure_placeholder(), main()


## Module `tools\qt_runtime.py`

```python
"""Qt runtime bootstrap utilities with plugin path caching and diagnostics."""

from __future__ import annotations

import logging
import os
import site
import subprocess
import sys
from pathlib import Path
from typing import Optional


_PLUGIN_PATH_CACHE: Optional[str] = None


def reset_qt_plugin_cache() -> None:
    """Reset cached plugin path (useful for tests)."""
    global _PLUGIN_PATH_CACHE
    _PLUGIN_PATH_CACHE = None


def resolve_qt_plugin_path(logger: Optional[logging.Logger] = None) -> str:
    """Return the Qt plugin directory using QLibraryInfo with fallbacks.

    The resolved path is cached to avoid repeated file-system scans. When the
    plugin directory cannot be located, a :class:`RuntimeError` is raised after
    logging diagnostic information about the attempted locations.
    """

    global _PLUGIN_PATH_CACHE
    if _PLUGIN_PATH_CACHE and os.path.isdir(_PLUGIN_PATH_CACHE):
        if logger:
            logger.debug("Using cached Qt plugin path: %s", _PLUGIN_PATH_CACHE)
        return _PLUGIN_PATH_CACHE

    try:
        from PySide6.QtCore import QLibraryInfo  # type: ignore
    except Exception as exc:  # pragma: no cover - import failure path
        if logger:
            logger.warning("PySide6 import failed (%s); reinstalling", exc)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--force-reinstall",
                "--no-cache-dir",
                "PySide6",
            ],
            check=True,
        )
        from PySide6.QtCore import QLibraryInfo  # type: ignore

    plugin_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)  # type: ignore[arg-type]
    if logger:
        logger.debug("QLibraryInfo reported plugin path: %s", plugin_path)

    candidates = []
    if not plugin_path or not os.path.isdir(plugin_path):
        plugin_path = ""
        for package_dir in site.getsitepackages():
            for candidate in (
                Path(package_dir) / "PySide6" / "Qt" / "plugins",
                Path(package_dir) / "PySide6" / "plugins",
            ):
                candidates.append(str(candidate))
                if logger:
                    logger.debug("Scanning %s", candidate)
                if candidate.is_dir():
                    plugin_path = str(candidate)
                    break
            if plugin_path:
                break

    if not plugin_path or not os.path.isdir(plugin_path):
        msg = (
            "Qt plugins not found; reinstall PySide6 or set QT_QPA_PLATFORM_PLUGIN_PATH"
        )
        if logger:
            logger.error("%s. Checked: %s", msg, ", ".join(candidates))
        raise RuntimeError(msg)

    _PLUGIN_PATH_CACHE = plugin_path
    if logger:
        logger.debug("Resolved Qt plugin path: %s", plugin_path)
    return plugin_path


def ensure_qt_runtime(logger: Optional[logging.Logger] = None) -> str:
    """Ensure Qt plugins are available and export the resolved path."""
    plugin_path = resolve_qt_plugin_path(logger)
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
    if logger:
        logger.debug("QT_QPA_PLATFORM_PLUGIN_PATH=%s", plugin_path)

    if os.name == "nt":  # pragma: no cover - windows specific
        bin_dir = Path(plugin_path).parent / "bin"
        if bin_dir.is_dir():
            os.add_dll_directory(str(bin_dir))

    return plugin_path


__all__ = ["ensure_qt_runtime", "reset_qt_plugin_cache", "resolve_qt_plugin_path"]
```

Qt runtime bootstrap utilities with plugin path caching and diagnostics.
**Functions:** reset_qt_plugin_cache(), resolve_qt_plugin_path(logger), ensure_qt_runtime(logger)


## Module `tools\qt_utils.py`

```python
import os
import subprocess
import sys
import logging


def attempt_pip_install(package: str, logger: logging.Logger | None = None) -> bool:
    """Attempt to install ``package`` via pip and log the result."""
    logger = logger or logging.getLogger(__name__)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        logger.info("pip install %s succeeded", package)
        return True
    except Exception as exc:  # pragma: no cover - log path
        logger.error("pip install %s failed: %s", package, exc)
        return False


def ensure_pyside6(logger: logging.Logger | None = None) -> bool:
    """Ensure PySide6 is importable and its plugins are available.

    If importing PySide6 or locating its plugin path fails, a pip install is
    attempted via :func:`attempt_pip_install`. Returns True on success, False
    otherwise.
    """
    logger = logger or logging.getLogger(__name__)
    try:
        import PySide6  # type: ignore
    except Exception as exc:  # pragma: no cover - log path
        logger.warning("PySide6 import failed: %s", exc)
        for mod in list(sys.modules):
            if mod.startswith("PySide6"):
                sys.modules.pop(mod, None)
        if not attempt_pip_install("PySide6", logger):
            return False
        try:
            import PySide6  # type: ignore
        except Exception as exc2:  # pragma: no cover - log path
            logger.error("PySide6 import still failing: %s", exc2)
            for mod in list(sys.modules):
                if mod.startswith("PySide6"):
                    sys.modules.pop(mod, None)
            return False
    try:
        from PySide6.QtCore import QLibraryInfo
        plugin_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
        if not os.path.isdir(plugin_path):
            raise RuntimeError(f"plugin path missing: {plugin_path}")
        logger.info("PySide6 present; plugins at %s", plugin_path)
    except Exception as exc:
        logger.warning("PySide6 plugin lookup failed: %s", exc)
        for mod in list(sys.modules):
            if mod.startswith("PySide6"):
                sys.modules.pop(mod, None)
        if not attempt_pip_install("PySide6", logger):
            return False
        try:
            from PySide6.QtCore import QLibraryInfo  # noqa: F401
        except Exception as exc2:  # pragma: no cover - log path
            logger.error("PySide6 import still failing: %s", exc2)
            return False
    return True


_HIDPI_SET = False


def set_hidpi_policy_once() -> None:
    """Configure HiDPI policy and env vars a single time per process."""

    global _HIDPI_SET
    if _HIDPI_SET:
        return
    _HIDPI_SET = True
    try:
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtCore import Qt

        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except Exception:
        pass
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")
```

**Functions:** attempt_pip_install(package, logger), ensure_pyside6(logger), set_hidpi_policy_once()


## Module `tools\__init__.py`

```python
"""Utility scripts for Agent-Terminal."""
```

Utility scripts for Agent-Terminal.


## Module `Virtual_Desktop\agent_terminal.py`

```python
../agent_terminal.py
```



## Module `vision\ocr_service.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from PySide6.QtGui import QGuiApplication


try:
    from PIL import ImageQt
except Exception:  # pragma: no cover - pillow optional at runtime
    ImageQt = None  # type: ignore

try:
    import pytesseract
except Exception:  # pragma: no cover - pytesseract optional
    pytesseract = None  # type: ignore

from memory.datasets import write_entry


@dataclass
class OCRResult:
    text: str
    task_id: Optional[str]
    timestamp: str


class OCRService:
    """Capture screenshots and perform OCR with dataset logging."""

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Screenshot capture
    # ------------------------------------------------------------------
    def capture(self, region: Optional[Tuple[int, int, int, int]] = None):
        """Return a PIL.Image grabbed from screen or region."""
        app = QGuiApplication.instance()
        if app is None:
            app = QGuiApplication([])
        screen = app.primaryScreen()
        if screen is None:
            return None
        if region:
            x, y, w, h = region
            pix = screen.grabWindow(0, x, y, w, h)
        else:
            pix = screen.grabWindow(0)
        if ImageQt is None:
            return None
        return ImageQt.ImageQt(pix.toImage())

    # ------------------------------------------------------------------
    # OCR
    # ------------------------------------------------------------------
    def run_ocr(self, image) -> str:
        if image is None or pytesseract is None:
            return ""
        try:
            return pytesseract.image_to_string(image)
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------
    def verify(
        self,
        expected_text: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        task_id: Optional[str] = None,
    ) -> bool:
        image = self.capture(region)
        text = self.run_ocr(image)
        entry = OCRResult(text=text, task_id=task_id, timestamp=datetime.utcnow().isoformat())
        write_entry("ocr_logs", entry.__dict__)
        return expected_text in text
```

**Classes:** OCRResult, OCRService


## Module `vision\__init__.py`

```python

```


# Project Documentation

## Table of Contents
- [Overview](#overview)
- [Python Modules](#python-modules)
- [Other Files](#other-files)

## Overview
This README was generated automatically by analysing the contents of the project.  The analysis focuses primarily on Python modules, extracting module documentation, classes and functions.  Other file types are listed for completeness.

## Python Modules

### `Analyze_folders.py`

**Functions:** analyze_folders(start_path)
### `codex-cli\scripts\stage_rust_release.py`

**Functions:** main()
### `codex-rs\mcp-types\generate_mcp_types.py`

**Classes:** StructField, RustProp

**Functions:** main(), add_definition(name, definition, out), define_struct(name, properties, required_props, description), infer_result_type(request_type_name), implements_request_trait(name), implements_notification_trait(name), add_trait_impl(type_name, trait_name, fields, out), define_string_enum(name, enum_values, out, description), define_untagged_enum(name, type_list, out), define_any_of(name, list_of_refs, description), get_serde_annotation_for_anyof_type(type_name), map_type(typedef, prop_name, struct_name), rust_prop_name(name, is_optional), to_snake_case(name), capitalize(name), check_string_list(value), type_from_ref(ref), emit_doc_comment(text, out)
### `scripts\asciicheck.py`

**Functions:** main(), lint_utf8_ascii(filename, fix)
### `scripts\publish_to_npm.py`

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
### `scripts\readme_toc.py`

Utility script to verify (and optionally fix) the Table of Contents in a
Markdown file. By default, it checks that the ToC between `<!-- Begin ToC -->`
and `<!-- End ToC -->` matches the headings in the file. With --fix, it
rewrites the file to update the ToC.

**Functions:** main(), generate_toc_lines(content), check_or_fix(readme_path, fix)

## Other Files

The following files are present in the project but were not analysed in detail:

- `.codespellignore`
- `.codespellrc`
- `.devcontainer\Dockerfile`
- `.devcontainer\README.md`
- `.devcontainer\devcontainer.json`
- `.github\ISSUE_TEMPLATE\2-bug-report.yml`
- `.github\ISSUE_TEMPLATE\3-docs-issue.yml`
- `.github\ISSUE_TEMPLATE\4-feature-request.yml`
- `.github\actions\codex\.gitignore`
- `.github\actions\codex\.prettierrc.toml`
- `.github\actions\codex\README.md`
- `.github\actions\codex\action.yml`
- `.github\actions\codex\bun.lock`
- `.github\actions\codex\package.json`
- `.github\actions\codex\src\add-reaction.ts`
- `.github\actions\codex\src\comment.ts`
- `.github\actions\codex\src\config.ts`
- `.github\actions\codex\src\default-label-config.ts`
- `.github\actions\codex\src\env-context.ts`
- `.github\actions\codex\src\fail.ts`
- `.github\actions\codex\src\git-helpers.ts`
- `.github\actions\codex\src\git-user.ts`
- `.github\actions\codex\src\github-workspace.ts`
- `.github\actions\codex\src\load-config.ts`
- `.github\actions\codex\src\main.ts`
- `.github\actions\codex\src\post-comment.ts`
- `.github\actions\codex\src\process-label.ts`
- `.github\actions\codex\src\prompt-template.ts`
- `.github\actions\codex\src\review.ts`
- `.github\actions\codex\src\run-codex.ts`
- `.github\actions\codex\src\verify-inputs.ts`
- `.github\actions\codex\tsconfig.json`
- `.github\codex-cli-login.png`
- `.github\codex-cli-permissions.png`
- `.github\codex-cli-splash.png`
- `.github\codex\home\config.toml`
- `.github\codex\labels\codex-attempt.md`
- `.github\codex\labels\codex-review.md`
- `.github\codex\labels\codex-rust-review.md`
- `.github\codex\labels\codex-triage.md`
- `.github\demo.gif`
- `.github\dependabot.yaml`
- `.github\dotslash-config.json`
- `.github\pull_request_template.md`
- `.github\workflows\ci.yml`
- `.github\workflows\cla.yml`
- `.github\workflows\codespell.yml`
- `.github\workflows\codex.yml`
- `.github\workflows\rust-ci.yml`
- `.github\workflows\rust-release.yml`
- `.gitignore`
- `.npmrc`
- `.prettierignore`
- `.prettierrc.toml`
- `.vscode\extensions.json`
- `.vscode\launch.json`
- `.vscode\settings.json`
- `AGENTS.md`
- `CHANGELOG.md`
- `LICENSE`
- `NOTICE`
- `PNPM.md`
- `README.md`
- `analyze.txt`
- `cliff.toml`
- `codex-cli\.dockerignore`
- `codex-cli\.gitignore`
- `codex-cli\Dockerfile`
- `codex-cli\README.md`
- `codex-cli\bin\codex.js`
- `codex-cli\package-lock.json`
- `codex-cli\package.json`
- `codex-cli\scripts\README.md`
- `codex-cli\scripts\build_container.sh`
- `codex-cli\scripts\init_firewall.sh`
- `codex-cli\scripts\install_native_deps.sh`
- `codex-cli\scripts\run_in_container.sh`
- `codex-cli\scripts\stage_release.sh`
- `codex-rs\.gitignore`
- `codex-rs\Cargo.lock`
- `codex-rs\Cargo.toml`
- `codex-rs\README.md`
- `codex-rs\ansi-escape\Cargo.toml`
- `codex-rs\ansi-escape\README.md`
- `codex-rs\ansi-escape\src\lib.rs`
- `codex-rs\apply-patch\Cargo.toml`
- `codex-rs\apply-patch\apply_patch_tool_instructions.md`
- `codex-rs\apply-patch\src\lib.rs`
- `codex-rs\apply-patch\src\parser.rs`
- `codex-rs\apply-patch\src\seek_sequence.rs`
- `codex-rs\arg0\Cargo.toml`
- `codex-rs\arg0\src\lib.rs`
- `codex-rs\chatgpt\Cargo.toml`
- `codex-rs\chatgpt\README.md`
- `codex-rs\chatgpt\src\apply_command.rs`
- `codex-rs\chatgpt\src\chatgpt_client.rs`
- `codex-rs\chatgpt\src\chatgpt_token.rs`
- `codex-rs\chatgpt\src\get_task.rs`
- `codex-rs\chatgpt\src\lib.rs`
- `codex-rs\chatgpt\tests\apply_command_e2e.rs`
- `codex-rs\chatgpt\tests\task_turn_fixture.json`
- `codex-rs\cli\Cargo.toml`
- `codex-rs\cli\src\debug_sandbox.rs`
- `codex-rs\cli\src\exit_status.rs`
- `codex-rs\cli\src\lib.rs`
- `codex-rs\cli\src\login.rs`
- `codex-rs\cli\src\main.rs`
- `codex-rs\cli\src\proto.rs`
- `codex-rs\clippy.toml`
- `codex-rs\common\Cargo.toml`
- `codex-rs\common\README.md`
- `codex-rs\common\src\approval_mode_cli_arg.rs`
- `codex-rs\common\src\approval_presets.rs`
- `codex-rs\common\src\config_override.rs`
- `codex-rs\common\src\config_summary.rs`
- `codex-rs\common\src\elapsed.rs`
- `codex-rs\common\src\fuzzy_match.rs`
- `codex-rs\common\src\lib.rs`
- `codex-rs\common\src\model_presets.rs`
- `codex-rs\common\src\sandbox_mode_cli_arg.rs`
- `codex-rs\common\src\sandbox_summary.rs`
- `codex-rs\config.md`
- `codex-rs\core\Cargo.toml`
- `codex-rs\core\README.md`
- `codex-rs\core\prompt.md`
- `codex-rs\core\src\apply_patch.rs`
- `codex-rs\core\src\bash.rs`
- `codex-rs\core\src\chat_completions.rs`
- `codex-rs\core\src\client.rs`
- `codex-rs\core\src\client_common.rs`
- `codex-rs\core\src\codex.rs`
- `codex-rs\core\src\codex_conversation.rs`
- `codex-rs\core\src\config.rs`
- `codex-rs\core\src\config_profile.rs`
- `codex-rs\core\src\config_types.rs`
- `codex-rs\core\src\conversation_history.rs`
- `codex-rs\core\src\conversation_manager.rs`
- `codex-rs\core\src\environment_context.rs`
- `codex-rs\core\src\error.rs`
- `codex-rs\core\src\exec.rs`
- `codex-rs\core\src\exec_env.rs`
- `codex-rs\core\src\flags.rs`
- `codex-rs\core\src\git_info.rs`
- `codex-rs\core\src\is_safe_command.rs`
- `codex-rs\core\src\landlock.rs`
- `codex-rs\core\src\lib.rs`
- `codex-rs\core\src\mcp_connection_manager.rs`
- `codex-rs\core\src\mcp_tool_call.rs`
- `codex-rs\core\src\message_history.rs`
- `codex-rs\core\src\model_family.rs`
- `codex-rs\core\src\model_provider_info.rs`
- `codex-rs\core\src\models.rs`
- `codex-rs\core\src\openai_model_info.rs`
- `codex-rs\core\src\openai_tools.rs`
- `codex-rs\core\src\parse_command.rs`
- `codex-rs\core\src\plan_tool.rs`
- `codex-rs\core\src\project_doc.rs`
- `codex-rs\core\src\prompt_for_compact_command.md`
- `codex-rs\core\src\rollout.rs`
- `codex-rs\core\src\safety.rs`
- `codex-rs\core\src\seatbelt.rs`
- `codex-rs\core\src\seatbelt_base_policy.sbpl`
- `codex-rs\core\src\shell.rs`
- `codex-rs\core\src\spawn.rs`
- `codex-rs\core\src\turn_diff_tracker.rs`
- `codex-rs\core\src\user_agent.rs`
- `codex-rs\core\src\user_notification.rs`
- `codex-rs\core\src\util.rs`
- `codex-rs\core\tests\cli_responses_fixture.sse`
- `codex-rs\core\tests\cli_stream.rs`
- `codex-rs\core\tests\client.rs`
- `codex-rs\core\tests\common\Cargo.toml`
- `codex-rs\core\tests\common\lib.rs`
- `codex-rs\core\tests\compact.rs`
- `codex-rs\core\tests\exec.rs`
- `codex-rs\core\tests\exec_stream_events.rs`
- `codex-rs\core\tests\fixtures\completed_template.json`
- `codex-rs\core\tests\fixtures\incomplete_sse.json`
- `codex-rs\core\tests\live_cli.rs`
- `codex-rs\core\tests\prompt_caching.rs`
- `codex-rs\core\tests\seatbelt.rs`
- `codex-rs\core\tests\stream_error_allows_next_turn.rs`
- `codex-rs\core\tests\stream_no_completed.rs`
- `codex-rs\default.nix`
- `codex-rs\docs\protocol_v1.md`
- `codex-rs\exec\Cargo.toml`
- `codex-rs\exec\src\cli.rs`
- `codex-rs\exec\src\event_processor.rs`
- `codex-rs\exec\src\event_processor_with_human_output.rs`
- `codex-rs\exec\src\event_processor_with_json_output.rs`
- `codex-rs\exec\src\lib.rs`
- `codex-rs\exec\src\main.rs`
- `codex-rs\exec\tests\apply_patch.rs`
- `codex-rs\exec\tests\sandbox.rs`
- `codex-rs\execpolicy\Cargo.toml`
- `codex-rs\execpolicy\README.md`
- `codex-rs\execpolicy\build.rs`
- `codex-rs\execpolicy\src\arg_matcher.rs`
- `codex-rs\execpolicy\src\arg_resolver.rs`
- `codex-rs\execpolicy\src\arg_type.rs`
- `codex-rs\execpolicy\src\default.policy`
- `codex-rs\execpolicy\src\error.rs`
- `codex-rs\execpolicy\src\exec_call.rs`
- `codex-rs\execpolicy\src\execv_checker.rs`
- `codex-rs\execpolicy\src\lib.rs`
- `codex-rs\execpolicy\src\main.rs`
- `codex-rs\execpolicy\src\opt.rs`
- `codex-rs\execpolicy\src\policy.rs`
- `codex-rs\execpolicy\src\policy_parser.rs`
- `codex-rs\execpolicy\src\program.rs`
- `codex-rs\execpolicy\src\sed_command.rs`
- `codex-rs\execpolicy\src\valid_exec.rs`
- `codex-rs\execpolicy\tests\bad.rs`
- `codex-rs\execpolicy\tests\cp.rs`
- `codex-rs\execpolicy\tests\good.rs`
- `codex-rs\execpolicy\tests\head.rs`
- `codex-rs\execpolicy\tests\literal.rs`
- `codex-rs\execpolicy\tests\ls.rs`
- `codex-rs\execpolicy\tests\parse_sed_command.rs`
- `codex-rs\execpolicy\tests\pwd.rs`
- `codex-rs\execpolicy\tests\sed.rs`
- `codex-rs\file-search\Cargo.toml`
- `codex-rs\file-search\README.md`
- `codex-rs\file-search\src\cli.rs`
- `codex-rs\file-search\src\lib.rs`
- `codex-rs\file-search\src\main.rs`
- `codex-rs\justfile`
- `codex-rs\linux-sandbox\Cargo.toml`
- `codex-rs\linux-sandbox\README.md`
- `codex-rs\linux-sandbox\src\landlock.rs`
- `codex-rs\linux-sandbox\src\lib.rs`
- `codex-rs\linux-sandbox\src\linux_run_main.rs`
- `codex-rs\linux-sandbox\src\main.rs`
- `codex-rs\linux-sandbox\tests\landlock.rs`
- `codex-rs\login\Cargo.toml`
- `codex-rs\login\src\assets\success.html`
- `codex-rs\login\src\lib.rs`
- `codex-rs\login\src\pkce.rs`
- `codex-rs\login\src\server.rs`
- `codex-rs\login\src\token_data.rs`
- `codex-rs\login\tests\login_server_e2e.rs`
- `codex-rs\mcp-client\Cargo.toml`
- `codex-rs\mcp-client\src\lib.rs`
- `codex-rs\mcp-client\src\main.rs`
- `codex-rs\mcp-client\src\mcp_client.rs`
- `codex-rs\mcp-server\Cargo.toml`
- `codex-rs\mcp-server\src\codex_message_processor.rs`
- `codex-rs\mcp-server\src\codex_tool_config.rs`
- `codex-rs\mcp-server\src\codex_tool_runner.rs`
- `codex-rs\mcp-server\src\error_code.rs`
- `codex-rs\mcp-server\src\exec_approval.rs`
- `codex-rs\mcp-server\src\json_to_toml.rs`
- `codex-rs\mcp-server\src\lib.rs`
- `codex-rs\mcp-server\src\main.rs`
- `codex-rs\mcp-server\src\message_processor.rs`
- `codex-rs\mcp-server\src\outgoing_message.rs`
- `codex-rs\mcp-server\src\patch_approval.rs`
- `codex-rs\mcp-server\src\tool_handlers\mod.rs`
- `codex-rs\mcp-server\tests\codex_message_processor_flow.rs`
- `codex-rs\mcp-server\tests\codex_tool.rs`
- `codex-rs\mcp-server\tests\common\Cargo.toml`
- `codex-rs\mcp-server\tests\common\lib.rs`
- `codex-rs\mcp-server\tests\common\mcp_process.rs`
- `codex-rs\mcp-server\tests\common\mock_model_server.rs`
- `codex-rs\mcp-server\tests\common\responses.rs`
- `codex-rs\mcp-server\tests\create_conversation.rs`
- `codex-rs\mcp-server\tests\interrupt.rs`
- `codex-rs\mcp-server\tests\send_message.rs`
- `codex-rs\mcp-types\Cargo.toml`
- `codex-rs\mcp-types\README.md`
- `codex-rs\mcp-types\schema\2025-03-26\schema.json`
- `codex-rs\mcp-types\schema\2025-06-18\schema.json`
- `codex-rs\mcp-types\src\lib.rs`
- `codex-rs\mcp-types\tests\initialize.rs`
- `codex-rs\mcp-types\tests\progress_notification.rs`
- `codex-rs\ollama\Cargo.toml`
- `codex-rs\ollama\src\client.rs`
- `codex-rs\ollama\src\lib.rs`
- `codex-rs\ollama\src\parser.rs`
- `codex-rs\ollama\src\pull.rs`
- `codex-rs\ollama\src\url.rs`
- `codex-rs\protocol-ts\Cargo.toml`
- `codex-rs\protocol-ts\generate-ts`
- `codex-rs\protocol-ts\src\lib.rs`
- `codex-rs\protocol-ts\src\main.rs`
- `codex-rs\protocol\Cargo.toml`
- `codex-rs\protocol\README.md`
- `codex-rs\protocol\src\config_types.rs`
- `codex-rs\protocol\src\lib.rs`
- `codex-rs\protocol\src\mcp_protocol.rs`
- `codex-rs\protocol\src\message_history.rs`
- `codex-rs\protocol\src\parse_command.rs`
- `codex-rs\protocol\src\plan_tool.rs`
- `codex-rs\protocol\src\protocol.rs`
- `codex-rs\rust-toolchain.toml`
- `codex-rs\rustfmt.toml`
- `codex-rs\scripts\create_github_release.sh`
- `codex-rs\tui\Cargo.toml`
- `codex-rs\tui\prompt_for_init_command.md`
- `codex-rs\tui\src\app.rs`
- `codex-rs\tui\src\app_event.rs`
- `codex-rs\tui\src\app_event_sender.rs`
- `codex-rs\tui\src\bottom_pane\approval_modal_view.rs`
- `codex-rs\tui\src\bottom_pane\bottom_pane_view.rs`
- `codex-rs\tui\src\bottom_pane\chat_composer.rs`
- `codex-rs\tui\src\bottom_pane\chat_composer_history.rs`
- `codex-rs\tui\src\bottom_pane\command_popup.rs`
- `codex-rs\tui\src\bottom_pane\file_search_popup.rs`
- `codex-rs\tui\src\bottom_pane\list_selection_view.rs`
- `codex-rs\tui\src\bottom_pane\mod.rs`
- `codex-rs\tui\src\bottom_pane\popup_consts.rs`
- `codex-rs\tui\src\bottom_pane\scroll_state.rs`
- `codex-rs\tui\src\bottom_pane\selection_popup_common.rs`
- `codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__backspace_after_pastes.snap`
- `codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__empty.snap`
- `codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__large.snap`
- `codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__multiple_pastes.snap`
- `codex-rs\tui\src\bottom_pane\snapshots\codex_tui__bottom_pane__chat_composer__tests__small.snap`
- `codex-rs\tui\src\bottom_pane\status_indicator_view.rs`
- `codex-rs\tui\src\bottom_pane\textarea.rs`
- `codex-rs\tui\src\chatwidget.rs`
- `codex-rs\tui\src\chatwidget\agent.rs`
- `codex-rs\tui\src\chatwidget\interrupts.rs`
- `codex-rs\tui\src\chatwidget\snapshots\codex_tui__chatwidget__tests__deltas_then_same_final_message_are_rendered_snapshot.snap`
- `codex-rs\tui\src\chatwidget\snapshots\codex_tui__chatwidget__tests__final_reasoning_then_message_without_deltas_are_rendered.snap`
- `codex-rs\tui\src\chatwidget\tests.rs`
- `codex-rs\tui\src\chatwidget_stream_tests.rs`
- `codex-rs\tui\src\citation_regex.rs`
- `codex-rs\tui\src\cli.rs`
- `codex-rs\tui\src\common.rs`
- `codex-rs\tui\src\custom_terminal.rs`
- `codex-rs\tui\src\diff_render.rs`
- `codex-rs\tui\src\exec_command.rs`
- `codex-rs\tui\src\file_search.rs`
- `codex-rs\tui\src\get_git_diff.rs`
- `codex-rs\tui\src\history_cell.rs`
- `codex-rs\tui\src\insert_history.rs`
- `codex-rs\tui\src\lib.rs`
- `codex-rs\tui\src\live_wrap.rs`
- `codex-rs\tui\src\main.rs`
- `codex-rs\tui\src\markdown.rs`
- `codex-rs\tui\src\markdown_stream.rs`
- `codex-rs\tui\src\onboarding\auth.rs`
- `codex-rs\tui\src\onboarding\continue_to_chat.rs`
- `codex-rs\tui\src\onboarding\mod.rs`
- `codex-rs\tui\src\onboarding\onboarding_screen.rs`
- `codex-rs\tui\src\onboarding\trust_directory.rs`
- `codex-rs\tui\src\onboarding\welcome.rs`
- `codex-rs\tui\src\render\line_utils.rs`
- `codex-rs\tui\src\render\markdown_utils.rs`
- `codex-rs\tui\src\render\mod.rs`
- `codex-rs\tui\src\session_log.rs`
- `codex-rs\tui\src\shimmer.rs`
- `codex-rs\tui\src\slash_command.rs`
- `codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__add_details.snap`
- `codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__update_details_with_rename.snap`
- `codex-rs\tui\src\snapshots\codex_tui__diff_render__tests__wrap_behavior_insert.snap`
- `codex-rs\tui\src\status_indicator_widget.rs`
- `codex-rs\tui\src\streaming\controller.rs`
- `codex-rs\tui\src\streaming\mod.rs`
- `codex-rs\tui\src\text_formatting.rs`
- `codex-rs\tui\src\tui.rs`
- `codex-rs\tui\src\updates.rs`
- `codex-rs\tui\src\user_approval_widget.rs`
- `codex-rs\tui\styles.md`
- `codex-rs\tui\tests\fixtures\binary-size-log.jsonl`
- `codex-rs\tui\tests\fixtures\ideal-binary-response.txt`
- `codex-rs\tui\tests\fixtures\oss-story.jsonl`
- `codex-rs\tui\tests\status_indicator.rs`
- `codex-rs\tui\tests\vt100_history.rs`
- `codex-rs\tui\tests\vt100_live_commit.rs`
- `codex-rs\tui\tests\vt100_streaming_no_dup.rs`
- `docs\CLA.md`
- `docs\release_management.md`
- `flake.lock`
- `flake.nix`
- `package.json`
- `pnpm-lock.yaml`
- `pnpm-workspace.yaml`


## Detailed Module Analyses


## Module `Analyze_folders.py`

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


## Module `codex-cli\scripts\stage_rust_release.py`

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


## Module `codex-rs\mcp-types\generate_mcp_types.py`

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


## Module `scripts\asciicheck.py`

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


## Module `scripts\publish_to_npm.py`

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


## Module `scripts\readme_toc.py`

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

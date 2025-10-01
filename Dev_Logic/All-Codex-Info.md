Owner avatar
codex
Public
openai/codex
This commit does not belong to any branch on this repository, and may belong to a fork outside of the repository.
Go to file
t
Name		
bolinfest
bolinfest
Release 0.34.0
0d2ceb1
 · 
3 days ago
.devcontainer
chore: install an extension for TOML syntax highlighting in the devco…
2 months ago
.github
No fail fast (#3387)
4 days ago
.vscode
chore: add rust-lang.rust-analyzer and vadimcn.vscode-lldb to the lis…
last week
codex-cli
fix: include arm64 Windows executable in npm module (#3067)
2 weeks ago
codex-rs
Release 0.34.0
3 days ago
docs
Remove a broken link to prompting_guide.md in docs/getting-started.md (…
3 days ago
scripts
README / docs refactor (#2724)
2 weeks ago
.codespellignore
feat: make it possible to toggle mouse mode in the Rust TUI (#971)
4 months ago
.codespellrc
Re-add markdown streaming (#2029)
last month
.gitignore
restructure flake for codex-rs (#888)
4 months ago
.npmrc
chore: migrate to pnpm for improved monorepo management (#287)
5 months ago
.prettierignore
[apply-patch] Clean up apply-patch tool definitions (#2539)
3 weeks ago
.prettierrc.toml
Initial commit
5 months ago
AGENTS.md
syntax-highlight bash lines (#3142)
last week
CHANGELOG.md
Point the CHANGELOG to the releases page (#2780)
2 weeks ago
LICENSE
Initial commit
5 months ago
NOTICE
resizable viewport (#1732)
2 months ago
PNPM.md
fix: include pnpm lock file (#377)
5 months ago
README.md
docs: fix broken link to the "Memory with AGENTS.md" section in codex…
last week
cliff.toml
bump(version): 0.1.2504251709 (#660)
5 months ago
flake.lock
restructure flake for codex-rs (#888)
4 months ago
flake.nix
restructure flake for codex-rs (#888)
4 months ago
package.json
[codex-cli] Add ripgrep as a dependency for node environment (#2237)
last month
pnpm-lock.yaml
chore: remove the TypeScript code from the repository (#2048)
last month
pnpm-workspace.yaml
chore: remove the TypeScript code from the repository (#2048)
last month
Repository files navigation
README
Contributing
License
License
OpenAI Codex CLI
npm i -g @openai/codex
or brew install codex

Codex CLI is a coding agent from OpenAI that runs locally on your computer.
If you are looking for the cloud-based agent from OpenAI, Codex Web, see chatgpt.com/codex.

Codex CLI splash

Quickstart
Installing and running Codex CLI
Install globally with your preferred package manager. If you use npm:

npm install -g @openai/codex
Alternatively, if you use Homebrew:

brew install codex
Then simply run codex to get started:

codex
You can also go to the latest GitHub Release and download the appropriate binary for your platform.
Using Codex with your ChatGPT plan
Codex CLI login

Run codex and select Sign in with ChatGPT. We recommend signing into your ChatGPT account to use Codex as part of your Plus, Pro, Team, Edu, or Enterprise plan. Learn more about what's included in your ChatGPT plan.

You can also use Codex with an API key, but this requires additional setup. If you previously used an API key for usage-based billing, see the migration steps. If you're having trouble with login, please comment on this issue.

Model Context Protocol (MCP)
Codex CLI supports MCP servers. Enable by adding an mcp_servers section to your ~/.codex/config.toml.

Configuration
Codex CLI supports a rich set of configuration options, with preferences stored in ~/.codex/config.toml. For full configuration options, see Configuration.

Docs & FAQ
Getting started
CLI usage
Running with a prompt as input
Example prompts
Memory with AGENTS.md
Configuration
Sandbox & approvals
Authentication
Auth methods
Login on a "Headless" machine
Advanced
Non-interactive / CI mode
Tracing / verbose logging
Model Context Protocol (MCP)
Zero data retention (ZDR)
Contributing
Install & build
System Requirements
DotSlash
Build from source
FAQ
Open source fund
License
This repository is licensed under the Apache-2.0 License.

## Advanced

## Non-interactive / CI mode

Run Codex head-less in pipelines. Example GitHub Action step:

```yaml
- name: Update changelog via Codex
  run: |
    npm install -g @openai/codex
    codex login --api-key "${{ secrets.OPENAI_KEY }}"
    codex exec --full-auto "update CHANGELOG for next release"
```

## Tracing / verbose logging

Because Codex is written in Rust, it honors the `RUST_LOG` environment variable to configure its logging behavior.

The TUI defaults to `RUST_LOG=codex_core=info,codex_tui=info` and log messages are written to `~/.codex/log/codex-tui.log`, so you can leave the following running in a separate terminal to monitor log messages as they are written:

```
tail -F ~/.codex/log/codex-tui.log
```

By comparison, the non-interactive mode (`codex exec`) defaults to `RUST_LOG=error`, but messages are printed inline, so there is no need to monitor a separate file.

See the Rust documentation on [`RUST_LOG`](https://docs.rs/env_logger/latest/env_logger/#enabling-logging) for more information on the configuration options.

## Model Context Protocol (MCP)

The Codex CLI can be configured to leverage MCP servers by defining an [`mcp_servers`](./config.md#mcp_servers) section in `~/.codex/config.toml`. It is intended to mirror how tools such as Claude and Cursor define `mcpServers` in their respective JSON config files, though the Codex format is slightly different since it uses TOML rather than JSON, e.g.:

```toml
# IMPORTANT: the top-level key is `mcp_servers` rather than `mcpServers`.
[mcp_servers.server-name]
command = "npx"
args = ["-y", "mcp-server"]
env = { "API_KEY" = "value" }
```

## Using Codex as an MCP Server

The Codex CLI can also be run as an MCP _server_ via `codex mcp`. For example, you can use `codex mcp` to make Codex available as a tool inside of a multi-agent framework like the OpenAI [Agents SDK](https://platform.openai.com/docs/guides/agents).

### Codex MCP Server Quickstart
You can launch a Codex MCP server with the [Model Context Protocol Inspector](https://modelcontextprotocol.io/legacy/tools/inspector):

``` bash
npx @modelcontextprotocol/inspector codex mcp
```
Send a `tools/list` request and you will see that there are two tools available:

**`codex`** - Run a Codex session. Accepts configuration parameters matching the Codex Config struct. The `codex` tool takes the following properties:

Property           | Type     | Description
-------------------|----------|----------------------------------------------------------------------------------------------------------
**`prompt`** (required)             | string   | The initial user prompt to start the Codex conversation.
`approval-policy`    | string   | Approval policy for shell commands generated by the model: `untrusted`, `on-failure`, `never`.
`base-instructions`  | string   | The set of instructions to use instead of the default ones.
`config`             | object   | Individual [config settings](https://github.com/openai/codex/blob/main/docs/config.md#config) that will override what is in `$CODEX_HOME/config.toml`.
`cwd`                | string   | Working directory for the session. If relative, resolved against the server process's current directory.
`include-plan-tool`  | boolean  | Whether to include the plan tool in the conversation.
`model`             | string   | Optional override for the model name (e.g. `o3`, `o4-mini`).
`profile`            | string   | Configuration profile from `config.toml` to specify default options.
`sandbox`           | string   | Sandbox mode: `read-only`, `workspace-write`, or `danger-full-access`.

**`codex-reply`** - Continue a Codex session by providing the conversation id and prompt. The `codex-reply` tool takes the following properties:

Property   | Type   | Description
-----------|--------|---------------------------------------------------------------
**`prompt`** (required)     | string | The next user prompt to continue the Codex conversation.
**`conversationId`** (required)  | string | The id of the conversation to continue.

### Trying it Out
> [!TIP]
> Codex often takes a few minutes to run. To accommodate this, adjust the MCP inspector's Request and Total timeouts to 600000ms (10 minutes) under ⛭ Configuration.

Use the MCP inspector and `codex mcp` to build a simple tic-tac-toe game with the following settings:

**approval-policy:** never

**prompt:** Implement a simple tic-tac-toe game with HTML, Javascript, and CSS. Write the game in a single file called index.html.

**sandbox:** workspace-write

Click "Run Tool" and you should see a list of events emitted from the Codex MCP server as it builds the game.


-----

# Authentication

## Usage-based billing alternative: Use an OpenAI API key

If you prefer to pay-as-you-go, you can still authenticate with your OpenAI API key:

```shell
codex login --api-key "your-api-key-here"
```

This key must, at minimum, have write access to the Responses API.

## Migrating to ChatGPT login from API key

If you've used the Codex CLI before with usage-based billing via an API key and want to switch to using your ChatGPT plan, follow these steps:

1. Update the CLI and ensure `codex --version` is `0.20.0` or later
2. Delete `~/.codex/auth.json` (on Windows: `C:\\Users\\USERNAME\\.codex\\auth.json`)
3. Run `codex login` again

## Connecting on a "Headless" Machine

Today, the login process entails running a server on `localhost:1455`. If you are on a "headless" server, such as a Docker container or are `ssh`'d into a remote machine, loading `localhost:1455` in the browser on your local machine will not automatically connect to the webserver running on the _headless_ machine, so you must use one of the following workarounds:

### Authenticate locally and copy your credentials to the "headless" machine

The easiest solution is likely to run through the `codex login` process on your local machine such that `localhost:1455` _is_ accessible in your web browser. When you complete the authentication process, an `auth.json` file should be available at `$CODEX_HOME/auth.json` (on Mac/Linux, `$CODEX_HOME` defaults to `~/.codex` whereas on Windows, it defaults to `%USERPROFILE%\\.codex`).

Because the `auth.json` file is not tied to a specific host, once you complete the authentication flow locally, you can copy the `$CODEX_HOME/auth.json` file to the headless machine and then `codex` should "just work" on that machine. Note to copy a file to a Docker container, you can do:

```shell
# substitute MY_CONTAINER with the name or id of your Docker container:
CONTAINER_HOME=$(docker exec MY_CONTAINER printenv HOME)
docker exec MY_CONTAINER mkdir -p "$CONTAINER_HOME/.codex"
docker cp auth.json MY_CONTAINER:"$CONTAINER_HOME/.codex/auth.json"
```

whereas if you are `ssh`'d into a remote machine, you likely want to use [`scp`](https://en.wikipedia.org/wiki/Secure_copy_protocol):

```shell
ssh user@remote 'mkdir -p ~/.codex'
scp ~/.codex/auth.json user@remote:~/.codex/auth.json
```

or try this one-liner:

```shell
ssh user@remote 'mkdir -p ~/.codex && cat > ~/.codex/auth.json' < ~/.codex/auth.json
```

### Connecting through VPS or remote

If you run Codex on a remote machine (VPS/server) without a local browser, the login helper starts a server on `localhost:1455` on the remote host. To complete login in your local browser, forward that port to your machine before starting the login flow:

```bash
# From your local machine
ssh -L 1455:localhost:1455 <user>@<remote-host>
```

Then, in that SSH session, run `codex` and select "Sign in with ChatGPT". When prompted, open the printed URL (it will be `http://localhost:1455/...`) in your local browser. The traffic will be tunneled to the remote server. 


-----

# Config


Codex supports several mechanisms for setting config values:

- Config-specific command-line flags, such as `--model o3` (highest precedence).
- A generic `-c`/`--config` flag that takes a `key=value` pair, such as `--config model="o3"`.
  - The key can contain dots to set a value deeper than the root, e.g. `--config model_providers.openai.wire_api="chat"`.
  - For consistency with `config.toml`, values are a string in TOML format rather than JSON format, so use `key='{a = 1, b = 2}'` rather than `key='{"a": 1, "b": 2}'`.
    - The quotes around the value are necessary, as without them your shell would split the config argument on spaces, resulting in `codex` receiving `-c key={a` with (invalid) additional arguments `=`, `1,`, `b`, `=`, `2}`.
  - Values can contain any TOML object, such as `--config shell_environment_policy.include_only='["PATH", "HOME", "USER"]'`.
  - If `value` cannot be parsed as a valid TOML value, it is treated as a string value. This means that `-c model='"o3"'` and `-c model=o3` are equivalent.
    - In the first case, the value is the TOML string `"o3"`, while in the second the value is `o3`, which is not valid TOML and therefore treated as the TOML string `"o3"`.
    - Because quotes are interpreted by one's shell, `-c key="true"` will be correctly interpreted in TOML as `key = true` (a boolean) and not `key = "true"` (a string). If for some reason you needed the string `"true"`, you would need to use `-c key='"true"'` (note the two sets of quotes).
- The `$CODEX_HOME/config.toml` configuration file where the `CODEX_HOME` environment value defaults to `~/.codex`. (Note `CODEX_HOME` will also be where logs and other Codex-related information are stored.)

Both the `--config` flag and the `config.toml` file support the following options:

## model

The model that Codex should use.

```toml
model = "o3"  # overrides the default of "gpt-5"
```

## model_providers

This option lets you override and amend the default set of model providers bundled with Codex. This value is a map where the key is the value to use with `model_provider` to select the corresponding provider.

For example, if you wanted to add a provider that uses the OpenAI 4o model via the chat completions API, then you could add the following configuration:

```toml
# Recall that in TOML, root keys must be listed before tables.
model = "gpt-4o"
model_provider = "openai-chat-completions"

[model_providers.openai-chat-completions]
# Name of the provider that will be displayed in the Codex UI.
name = "OpenAI using Chat Completions"
# The path `/chat/completions` will be amended to this URL to make the POST
# request for the chat completions.
base_url = "https://api.openai.com/v1"
# If `env_key` is set, identifies an environment variable that must be set when
# using Codex with this provider. The value of the environment variable must be
# non-empty and will be used in the `Bearer TOKEN` HTTP header for the POST request.
env_key = "OPENAI_API_KEY"
# Valid values for wire_api are "chat" and "responses". Defaults to "chat" if omitted.
wire_api = "chat"
# If necessary, extra query params that need to be added to the URL.
# See the Azure example below.
query_params = {}
```

Note this makes it possible to use Codex CLI with non-OpenAI models, so long as they use a wire API that is compatible with the OpenAI chat completions API. For example, you could define the following provider to use Codex CLI with Ollama running locally:

```toml
[model_providers.ollama]
name = "Ollama"
base_url = "http://localhost:11434/v1"
```

Or a third-party provider (using a distinct environment variable for the API key):

```toml
[model_providers.mistral]
name = "Mistral"
base_url = "https://api.mistral.ai/v1"
env_key = "MISTRAL_API_KEY"
```

Note that Azure requires `api-version` to be passed as a query parameter, so be sure to specify it as part of `query_params` when defining the Azure provider:

```toml
[model_providers.azure]
name = "Azure"
# Make sure you set the appropriate subdomain for this URL.
base_url = "https://YOUR_PROJECT_NAME.openai.azure.com/openai"
env_key = "AZURE_OPENAI_API_KEY"  # Or "OPENAI_API_KEY", whichever you use.
query_params = { api-version = "2025-04-01-preview" }
```

It is also possible to configure a provider to include extra HTTP headers with a request. These can be hardcoded values (`http_headers`) or values read from environment variables (`env_http_headers`):

```toml
[model_providers.example]
# name, base_url, ...

# This will add the HTTP header `X-Example-Header` with value `example-value`
# to each request to the model provider.
http_headers = { "X-Example-Header" = "example-value" }

# This will add the HTTP header `X-Example-Features` with the value of the
# `EXAMPLE_FEATURES` environment variable to each request to the model provider
# _if_ the environment variable is set and its value is non-empty.
env_http_headers = { "X-Example-Features" = "EXAMPLE_FEATURES" }
```

### Per-provider network tuning

The following optional settings control retry behaviour and streaming idle timeouts **per model provider**. They must be specified inside the corresponding `[model_providers.<id>]` block in `config.toml`. (Older releases accepted top‑level keys; those are now ignored.)

Example:

```toml
[model_providers.openai]
name = "OpenAI"
base_url = "https://api.openai.com/v1"
env_key = "OPENAI_API_KEY"
# network tuning overrides (all optional; falls back to built‑in defaults)
request_max_retries = 4            # retry failed HTTP requests
stream_max_retries = 10            # retry dropped SSE streams
stream_idle_timeout_ms = 300000    # 5m idle timeout
```

#### request_max_retries

How many times Codex will retry a failed HTTP request to the model provider. Defaults to `4`.

#### stream_max_retries

Number of times Codex will attempt to reconnect when a streaming response is interrupted. Defaults to `5`.

#### stream_idle_timeout_ms

How long Codex will wait for activity on a streaming response before treating the connection as lost. Defaults to `300_000` (5 minutes).

## model_provider

Identifies which provider to use from the `model_providers` map. Defaults to `"openai"`. You can override the `base_url` for the built-in `openai` provider via the `OPENAI_BASE_URL` environment variable.

Note that if you override `model_provider`, then you likely want to override
`model`, as well. For example, if you are running ollama with Mistral locally,
then you would need to add the following to your config in addition to the new entry in the `model_providers` map:

```toml
model_provider = "ollama"
model = "mistral"
```

## approval_policy

Determines when the user should be prompted to approve whether Codex can execute a command:

```toml
# Codex has hardcoded logic that defines a set of "trusted" commands.
# Setting the approval_policy to `untrusted` means that Codex will prompt the
# user before running a command not in the "trusted" set.
#
# See https://github.com/openai/codex/issues/1260 for the plan to enable
# end-users to define their own trusted commands.
approval_policy = "untrusted"
```

If you want to be notified whenever a command fails, use "on-failure":

```toml
# If the command fails when run in the sandbox, Codex asks for permission to
# retry the command outside the sandbox.
approval_policy = "on-failure"
```

If you want the model to run until it decides that it needs to ask you for escalated permissions, use "on-request":

```toml
# The model decides when to escalate
approval_policy = "on-request"
```

Alternatively, you can have the model run until it is done, and never ask to run a command with escalated permissions:

```toml
# User is never prompted: if the command fails, Codex will automatically try
# something out. Note the `exec` subcommand always uses this mode.
approval_policy = "never"
```

## profiles

A _profile_ is a collection of configuration values that can be set together. Multiple profiles can be defined in `config.toml` and you can specify the one you
want to use at runtime via the `--profile` flag.

Here is an example of a `config.toml` that defines multiple profiles:

```toml
model = "o3"
approval_policy = "untrusted"

# Setting `profile` is equivalent to specifying `--profile o3` on the command
# line, though the `--profile` flag can still be used to override this value.
profile = "o3"

[model_providers.openai-chat-completions]
name = "OpenAI using Chat Completions"
base_url = "https://api.openai.com/v1"
env_key = "OPENAI_API_KEY"
wire_api = "chat"

[profiles.o3]
model = "o3"
model_provider = "openai"
approval_policy = "never"
model_reasoning_effort = "high"
model_reasoning_summary = "detailed"

[profiles.gpt3]
model = "gpt-3.5-turbo"
model_provider = "openai-chat-completions"

[profiles.zdr]
model = "o3"
model_provider = "openai"
approval_policy = "on-failure"
```

Users can specify config values at multiple levels. Order of precedence is as follows:

1. custom command-line argument, e.g., `--model o3`
2. as part of a profile, where the `--profile` is specified via a CLI (or in the config file itself)
3. as an entry in `config.toml`, e.g., `model = "o3"`
4. the default value that comes with Codex CLI (i.e., Codex CLI defaults to `gpt-5`)

## model_reasoning_effort

If the selected model is known to support reasoning (for example: `o3`, `o4-mini`, `codex-*`, `gpt-5`), reasoning is enabled by default when using the Responses API. As explained in the [OpenAI Platform documentation](https://platform.openai.com/docs/guides/reasoning?api-mode=responses#get-started-with-reasoning), this can be set to:

- `"minimal"`
- `"low"`
- `"medium"` (default)
- `"high"`

Note: to minimize reasoning, choose `"minimal"`.

## model_reasoning_summary

If the model name starts with `"o"` (as in `"o3"` or `"o4-mini"`) or `"codex"`, reasoning is enabled by default when using the Responses API. As explained in the [OpenAI Platform documentation](https://platform.openai.com/docs/guides/reasoning?api-mode=responses#reasoning-summaries), this can be set to:

- `"auto"` (default)
- `"concise"`
- `"detailed"`

To disable reasoning summaries, set `model_reasoning_summary` to `"none"` in your config:

```toml
model_reasoning_summary = "none"  # disable reasoning summaries
```

## model_verbosity

Controls output length/detail on GPT‑5 family models when using the Responses API. Supported values:

- `"low"`
- `"medium"` (default when omitted)
- `"high"`

When set, Codex includes a `text` object in the request payload with the configured verbosity, for example: `"text": { "verbosity": "low" }`.

Example:

```toml
model = "gpt-5"
model_verbosity = "low"
```

Note: This applies only to providers using the Responses API. Chat Completions providers are unaffected.

## model_supports_reasoning_summaries

By default, `reasoning` is only set on requests to OpenAI models that are known to support them. To force `reasoning` to set on requests to the current model, you can force this behavior by setting the following in `config.toml`:

```toml
model_supports_reasoning_summaries = true
```

## sandbox_mode

Codex executes model-generated shell commands inside an OS-level sandbox.

In most cases you can pick the desired behaviour with a single option:

```toml
# same as `--sandbox read-only`
sandbox_mode = "read-only"
```

The default policy is `read-only`, which means commands can read any file on
disk, but attempts to write a file or access the network will be blocked.

A more relaxed policy is `workspace-write`. When specified, the current working directory for the Codex task will be writable (as well as `$TMPDIR` on macOS). Note that the CLI defaults to using the directory where it was spawned as `cwd`, though this can be overridden using `--cwd/-C`.

On macOS (and soon Linux), all writable roots (including `cwd`) that contain a `.git/` folder _as an immediate child_ will configure the `.git/` folder to be read-only while the rest of the Git repository will be writable. This means that commands like `git commit` will fail, by default (as it entails writing to `.git/`), and will require Codex to ask for permission.

```toml
# same as `--sandbox workspace-write`
sandbox_mode = "workspace-write"

# Extra settings that only apply when `sandbox = "workspace-write"`.
[sandbox_workspace_write]
# By default, the cwd for the Codex session will be writable as well as $TMPDIR
# (if set) and /tmp (if it exists). Setting the respective options to `true`
# will override those defaults.
exclude_tmpdir_env_var = false
exclude_slash_tmp = false

# Optional list of _additional_ writable roots beyond $TMPDIR and /tmp.
writable_roots = ["/Users/YOU/.pyenv/shims"]

# Allow the command being run inside the sandbox to make outbound network
# requests. Disabled by default.
network_access = false
```

To disable sandboxing altogether, specify `danger-full-access` like so:

```toml
# same as `--sandbox danger-full-access`
sandbox_mode = "danger-full-access"
```

This is reasonable to use if Codex is running in an environment that provides its own sandboxing (such as a Docker container) such that further sandboxing is unnecessary.

Though using this option may also be necessary if you try to use Codex in environments where its native sandboxing mechanisms are unsupported, such as older Linux kernels or on Windows.

## Approval presets

Codex provides three main Approval Presets:

- Read Only: Codex can read files and answer questions; edits, running commands, and network access require approval.
- Auto: Codex can read files, make edits, and run commands in the workspace without approval; asks for approval outside the workspace or for network access.
- Full Access: Full disk and network access without prompts; extremely risky.

You can further customize how Codex runs at the command line using the `--ask-for-approval` and `--sandbox` options.

## mcp_servers

Defines the list of MCP servers that Codex can consult for tool use. Currently, only servers that are launched by executing a program that communicate over stdio are supported. For servers that use the SSE transport, consider an adapter like [mcp-proxy](https://github.com/sparfenyuk/mcp-proxy).

**Note:** Codex may cache the list of tools and resources from an MCP server so that Codex can include this information in context at startup without spawning all the servers. This is designed to save resources by loading MCP servers lazily.

Each server may set `startup_timeout_ms` to adjust how long Codex waits for it to start and respond to a tools listing. The default is `10_000` (10 seconds).

This config option is comparable to how Claude and Cursor define `mcpServers` in their respective JSON config files, though because Codex uses TOML for its config language, the format is slightly different. For example, the following config in JSON:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "mcp-server"],
      "env": {
        "API_KEY": "value"
      }
    }
  }
}
```

Should be represented as follows in `~/.codex/config.toml`:

```toml
# IMPORTANT: the top-level key is `mcp_servers` rather than `mcpServers`.
[mcp_servers.server-name]
command = "npx"
args = ["-y", "mcp-server"]
env = { "API_KEY" = "value" }
# Optional: override the default 10s startup timeout
startup_timeout_ms = 20_000
```

## shell_environment_policy

Codex spawns subprocesses (e.g. when executing a `local_shell` tool-call suggested by the assistant). By default it now passes **your full environment** to those subprocesses. You can tune this behavior via the **`shell_environment_policy`** block in `config.toml`:

```toml
[shell_environment_policy]
# inherit can be "all" (default), "core", or "none"
inherit = "core"
# set to true to *skip* the filter for `"*KEY*"` and `"*TOKEN*"`
ignore_default_excludes = false
# exclude patterns (case-insensitive globs)
exclude = ["AWS_*", "AZURE_*"]
# force-set / override values
set = { CI = "1" }
# if provided, *only* vars matching these patterns are kept
include_only = ["PATH", "HOME"]
```

| Field                     | Type                       | Default | Description                                                                                                                                     |
| ------------------------- | -------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `inherit`                 | string                     | `all`   | Starting template for the environment:<br>`all` (clone full parent env), `core` (`HOME`, `PATH`, `USER`, …), or `none` (start empty).           |
| `ignore_default_excludes` | boolean                    | `false` | When `false`, Codex removes any var whose **name** contains `KEY`, `SECRET`, or `TOKEN` (case-insensitive) before other rules run.              |
| `exclude`                 | array<string>        | `[]`    | Case-insensitive glob patterns to drop after the default filter.<br>Examples: `"AWS_*"`, `"AZURE_*"`.                                           |
| `set`                     | table<string,string> | `{}`    | Explicit key/value overrides or additions – always win over inherited values.                                                                   |
| `include_only`            | array<string>        | `[]`    | If non-empty, a whitelist of patterns; only variables that match _one_ pattern survive the final step. (Generally used with `inherit = "all"`.) |

The patterns are **glob style**, not full regular expressions: `*` matches any
number of characters, `?` matches exactly one, and character classes like
`[A-Z]`/`[^0-9]` are supported. Matching is always **case-insensitive**. This
syntax is documented in code as `EnvironmentVariablePattern` (see
`core/src/config_types.rs`).

If you just need a clean slate with a few custom entries you can write:

```toml
[shell_environment_policy]
inherit = "none"
set = { PATH = "/usr/bin", MY_FLAG = "1" }
```

Currently, `CODEX_SANDBOX_NETWORK_DISABLED=1` is also added to the environment, assuming network is disabled. This is not configurable.

## notify

Specify a program that will be executed to get notified about events generated by Codex. Note that the program will receive the notification argument as a string of JSON, e.g.:

```json
{
  "type": "agent-turn-complete",
  "turn-id": "12345",
  "input-messages": ["Rename `foo` to `bar` and update the callsites."],
  "last-assistant-message": "Rename complete and verified `cargo build` succeeds."
}
```

The `"type"` property will always be set. Currently, `"agent-turn-complete"` is the only notification type that is supported.

As an example, here is a Python script that parses the JSON and decides whether to show a desktop push notification using [terminal-notifier](https://github.com/julienXX/terminal-notifier) on macOS:

```python
#!/usr/bin/env python3

import json
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: notify.py <NOTIFICATION_JSON>")
        return 1

    try:
        notification = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        return 1

    match notification_type := notification.get("type"):
        case "agent-turn-complete":
            assistant_message = notification.get("last-assistant-message")
            if assistant_message:
                title = f"Codex: {assistant_message}"
            else:
                title = "Codex: Turn Complete!"
            input_messages = notification.get("input_messages", [])
            message = " ".join(input_messages)
            title += message
        case _:
            print(f"not sending a push notification for: {notification_type}")
            return 0

    subprocess.check_output(
        [
            "terminal-notifier",
            "-title",
            title,
            "-message",
            message,
            "-group",
            "codex",
            "-ignoreDnD",
            "-activate",
            "com.googlecode.iterm2",
        ]
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

To have Codex use this script for notifications, you would configure it via `notify` in `~/.codex/config.toml` using the appropriate path to `notify.py` on your computer:

```toml
notify = ["python3", "/Users/mbolin/.codex/notify.py"]
```

## history

By default, Codex CLI records messages sent to the model in `$CODEX_HOME/history.jsonl`. Note that on UNIX, the file permissions are set to `o600`, so it should only be readable and writable by the owner.

To disable this behavior, configure `[history]` as follows:

```toml
[history]
persistence = "none"  # "save-all" is the default value
```

## file_opener

Identifies the editor/URI scheme to use for hyperlinking citations in model output. If set, citations to files in the model output will be hyperlinked using the specified URI scheme so they can be ctrl/cmd-clicked from the terminal to open them.

For example, if the model output includes a reference such as `【F:/home/user/project/main.py†L42-L50】`, then this would be rewritten to link to the URI `vscode://file/home/user/project/main.py:42`.

Note this is **not** a general editor setting (like `$EDITOR`), as it only accepts a fixed set of values:

- `"vscode"` (default)
- `"vscode-insiders"`
- `"windsurf"`
- `"cursor"`
- `"none"` to explicitly disable this feature

Currently, `"vscode"` is the default, though Codex does not verify VS Code is installed. As such, `file_opener` may default to `"none"` or something else in the future.

## hide_agent_reasoning

Codex intermittently emits "reasoning" events that show the model's internal "thinking" before it produces a final answer. Some users may find these events distracting, especially in CI logs or minimal terminal output.

Setting `hide_agent_reasoning` to `true` suppresses these events in **both** the TUI as well as the headless `exec` sub-command:

```toml
hide_agent_reasoning = true   # defaults to false
```

## show_raw_agent_reasoning

Surfaces the model’s raw chain-of-thought ("raw reasoning content") when available.

Notes:

- Only takes effect if the selected model/provider actually emits raw reasoning content. Many models do not. When unsupported, this option has no visible effect.
- Raw reasoning may include intermediate thoughts or sensitive context. Enable only if acceptable for your workflow.

Example:

```toml
show_raw_agent_reasoning = true  # defaults to false
```

## model_context_window

The size of the context window for the model, in tokens.

In general, Codex knows the context window for the most common OpenAI models, but if you are using a new model with an old version of the Codex CLI, then you can use `model_context_window` to tell Codex what value to use to determine how much context is left during a conversation.

## model_max_output_tokens

This is analogous to `model_context_window`, but for the maximum number of output tokens for the model.

## project_doc_max_bytes

Maximum number of bytes to read from an `AGENTS.md` file to include in the instructions sent with the first turn of a session. Defaults to 32 KiB.

## tui

Options that are specific to the TUI.

```toml
[tui]
# More to come here
```

## Config reference

| Key | Type / Values | Notes |
| --- | --- | --- |
| `model` | string | Model to use (e.g., `gpt-5`). |
| `model_provider` | string | Provider id from `model_providers` (default: `openai`). |
| `model_context_window` | number | Context window tokens. |
| `model_max_output_tokens` | number | Max output tokens. |
| `approval_policy` | `untrusted` \| `on-failure` \| `on-request` \| `never` | When to prompt for approval. |
| `sandbox_mode` | `read-only` \| `workspace-write` \| `danger-full-access` | OS sandbox policy. |
| `sandbox_workspace_write.writable_roots` | array<string> | Extra writable roots in workspace‑write. |
| `sandbox_workspace_write.network_access` | boolean | Allow network in workspace‑write (default: false). |
| `sandbox_workspace_write.exclude_tmpdir_env_var` | boolean | Exclude `$TMPDIR` from writable roots (default: false). |
| `sandbox_workspace_write.exclude_slash_tmp` | boolean | Exclude `/tmp` from writable roots (default: false). |
| `disable_response_storage` | boolean | Required for ZDR orgs. |
| `notify` | array<string> | External program for notifications. |
| `instructions` | string | Currently ignored; use `experimental_instructions_file` or `AGENTS.md`. |
| `mcp_servers.<id>.command` | string | MCP server launcher command. |
| `mcp_servers.<id>.args` | array<string> | MCP server args. |
| `mcp_servers.<id>.env` | map<string,string> | MCP server env vars. |
| `mcp_servers.<id>.startup_timeout_ms` | number | Startup timeout in milliseconds (default: 10_000). Timeout is applied both for initializing MCP server and initially listing tools. |
| `model_providers.<id>.name` | string | Display name. |
| `model_providers.<id>.base_url` | string | API base URL. |
| `model_providers.<id>.env_key` | string | Env var for API key. |
| `model_providers.<id>.wire_api` | `chat` \| `responses` | Protocol used (default: `chat`). |
| `model_providers.<id>.query_params` | map<string,string> | Extra query params (e.g., Azure `api-version`). |
| `model_providers.<id>.http_headers` | map<string,string> | Additional static headers. |
| `model_providers.<id>.env_http_headers` | map<string,string> | Headers sourced from env vars. |
| `model_providers.<id>.request_max_retries` | number | Per‑provider HTTP retry count (default: 4). |
| `model_providers.<id>.stream_max_retries` | number | SSE stream retry count (default: 5). |
| `model_providers.<id>.stream_idle_timeout_ms` | number | SSE idle timeout (ms) (default: 300000). |
| `project_doc_max_bytes` | number | Max bytes to read from `AGENTS.md`. |
| `profile` | string | Active profile name. |
| `profiles.<name>.*` | various | Profile‑scoped overrides of the same keys. |
| `history.persistence` | `save-all` \| `none` | History file persistence (default: `save-all`). |
| `history.max_bytes` | number | Currently ignored (not enforced). |
| `file_opener` | `vscode` \| `vscode-insiders` \| `windsurf` \| `cursor` \| `none` | URI scheme for clickable citations (default: `vscode`). |
| `tui` | table | TUI‑specific options (reserved). |
| `hide_agent_reasoning` | boolean | Hide model reasoning events. |
| `show_raw_agent_reasoning` | boolean | Show raw reasoning (when available). |
| `model_reasoning_effort` | `minimal` \| `low` \| `medium` \| `high` | Responses API reasoning effort. |
| `model_reasoning_summary` | `auto` \| `concise` \| `detailed` \| `none` | Reasoning summaries. |
| `model_verbosity` | `low` \| `medium` \| `high` | GPT‑5 text verbosity (Responses API). |
| `model_supports_reasoning_summaries` | boolean | Force‑enable reasoning summaries. |
| `model_reasoning_summary_format` | `none` \| `experimental` | Force reasoning summary format. |
| `chatgpt_base_url` | string | Base URL for ChatGPT auth flow. |
| `experimental_resume` | string (path) | Resume JSONL path (internal/experimental). |
| `experimental_instructions_file` | string (path) | Replace built‑in instructions (experimental). |
| `experimental_use_exec_command_tool` | boolean | Use experimental exec command tool. |
| `responses_originator_header_internal_override` | string | Override `originator` header value. |
| `projects.<path>.trust_level` | string | Mark project/worktree as trusted (only `"trusted"` is recognized). |
| `tools.web_search` | boolean | Enable web search tool (alias: `web_search_request`) (default: false). |



--------

## Contributing

This project is under active development and the code will likely change pretty significantly.

**At the moment, we only plan to prioritize reviewing external contributions for bugs or security fixes.**

If you want to add a new feature or change the behavior of an existing one, please open an issue proposing the feature and get approval from an OpenAI team member before spending time building it.

**New contributions that don't go through this process may be closed** if they aren't aligned with our current roadmap or conflict with other priorities/upcoming features.

### Development workflow

- Create a _topic branch_ from `main` - e.g. `feat/interactive-prompt`.
- Keep your changes focused. Multiple unrelated fixes should be opened as separate PRs.
- Following the [development setup](#development-workflow) instructions above, ensure your change is free of lint warnings and test failures.

### Writing high-impact code changes

1. **Start with an issue.** Open a new one or comment on an existing discussion so we can agree on the solution before code is written.
2. **Add or update tests.** Every new feature or bug-fix should come with test coverage that fails before your change and passes afterwards. 100% coverage is not required, but aim for meaningful assertions.
3. **Document behaviour.** If your change affects user-facing behaviour, update the README, inline help (`codex --help`), or relevant example projects.
4. **Keep commits atomic.** Each commit should compile and the tests should pass. This makes reviews and potential rollbacks easier.

### Opening a pull request

- Fill in the PR template (or include similar information) - **What? Why? How?**
- Run **all** checks locally (`cargo test && cargo clippy --tests && cargo fmt -- --config imports_granularity=Item`). CI failures that could have been caught locally slow down the process.
- Make sure your branch is up-to-date with `main` and that you have resolved merge conflicts.
- Mark the PR as **Ready for review** only when you believe it is in a merge-able state.

### Review process

1. One maintainer will be assigned as a primary reviewer.
2. If your PR adds a new feature that was not previously discussed and approved, we may choose to close your PR (see [Contributing](#contributing)).
3. We may ask for changes - please do not take this personally. We value the work, but we also value consistency and long-term maintainability.
5. When there is consensus that the PR meets the bar, a maintainer will squash-and-merge.

### Community values

- **Be kind and inclusive.** Treat others with respect; we follow the [Contributor Covenant](https://www.contributor-covenant.org/).
- **Assume good intent.** Written communication is hard - err on the side of generosity.
- **Teach & learn.** If you spot something confusing, open an issue or PR with improvements.

### Getting help

If you run into problems setting up the project, would like feedback on an idea, or just want to say _hi_ - please open a Discussion or jump into the relevant issue. We are happy to help.

Together we can make Codex CLI an incredible tool. **Happy hacking!** :rocket:

### Contributor license agreement (CLA)

All contributors **must** accept the CLA. The process is lightweight:

1. Open your pull request.
2. Paste the following comment (or reply `recheck` if you've signed before):

   ```text
   I have read the CLA Document and I hereby sign the CLA
   ```

3. The CLA-Assistant bot records your signature in the repo and marks the status check as passed.

No special Git commands, email attachments, or commit footers required.

#### Quick fixes

| Scenario          | Command                                          |
| ----------------- | ------------------------------------------------ |
| Amend last commit | `git commit --amend -s --no-edit && git push -f` |

The **DCO check** blocks merges until every commit in the PR carries the footer (with squash this is just the one).

### Releasing `codex`

_For admins only._

Make sure you are on `main` and have no local changes. Then run:

```shell
VERSION=0.2.0  # Can also be 0.2.0-alpha.1 or any valid Rust version.
./codex-rs/scripts/create_github_release.sh "$VERSION"
```

This will make a local commit on top of `main` with `version` set to `$VERSION` in `codex-rs/Cargo.toml` (note that on `main`, we leave the version as `version = "0.0.0"`).

This will push the commit using the tag `rust-v${VERSION}`, which in turn kicks off [the release workflow](../.github/workflows/rust-release.yml). This will create a new GitHub Release named `$VERSION`.

If everything looks good in the generated GitHub Release, uncheck the **pre-release** box so it is the latest release.

Create a PR to update [`Formula/c/codex.rb`](https://github.com/Homebrew/homebrew-core/blob/main/Formula/c/codex.rb) on Homebrew.

### Security & responsible AI

Have you discovered a vulnerability or have concerns about model output? Please e-mail **security@openai.com** and we will respond promptly. 


------

## FAQ

### OpenAI released a model called Codex in 2021 - is this related?

In 2021, OpenAI released Codex, an AI system designed to generate code from natural language prompts. That original Codex model was deprecated as of March 2023 and is separate from the CLI tool.

### Which models are supported?

We recommend using Codex with GPT-5, our best coding model. The default reasoning level is medium, and you can upgrade to high for complex tasks with the `/model` command.

You can also use older models by using API-based auth and launching codex with the `--model` flag.

### Why does `o3` or `o4-mini` not work for me?

It's possible that your [API account needs to be verified](https://help.openai.com/en/articles/10910291-api-organization-verification) in order to start streaming responses and seeing chain of thought summaries from the API. If you're still running into issues, please let us know!

### How do I stop Codex from editing my files?

By default, Codex can modify files in your current working directory (Auto mode). To prevent edits, run `codex` in read-only mode with the CLI flag `--sandbox read-only`. Alternatively, you can change the approval level mid-conversation with `/approvals`.

### Does it work on Windows?

Running Codex directly on Windows may work, but is not officially supported. We recommend using [Windows Subsystem for Linux (WSL2)](https://learn.microsoft.com/en-us/windows/wsl/install). 


------


## Getting started

### CLI usage

| Command            | Purpose                            | Example                         |
| ------------------ | ---------------------------------- | ------------------------------- |
| `codex`            | Interactive TUI                    | `codex`                         |
| `codex "..."`      | Initial prompt for interactive TUI | `codex "fix lint errors"`       |
| `codex exec "..."` | Non-interactive "automation mode"  | `codex exec "explain utils.ts"` |

Key flags: `--model/-m`, `--ask-for-approval/-a`.

<!--
Resume options:

- `--resume`: open an interactive picker of recent sessions (shows a preview of the first real user message). Conflicts with `--continue`.
- `--continue`: resume the most recent session without showing the picker (falls back to starting fresh if none exist). Conflicts with `--resume`.

Examples:

```shell
codex --resume
codex --continue
```
-->

### Running with a prompt as input

You can also run Codex CLI with a prompt as input:

```shell
codex "explain this codebase to me"
```

```shell
codex --full-auto "create the fanciest todo-list app"
```

That's it - Codex will scaffold a file, run it inside a sandbox, install any
missing dependencies, and show you the live result. Approve the changes and
they'll be committed to your working directory.

### Example prompts

Below are a few bite-size examples you can copy-paste. Replace the text in quotes with your own task.

| ✨  | What you type                                                                   | What happens                                                               |
| --- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1   | `codex "Refactor the Dashboard component to React Hooks"`                       | Codex rewrites the class component, runs `npm test`, and shows the diff.   |
| 2   | `codex "Generate SQL migrations for adding a users table"`                      | Infers your ORM, creates migration files, and runs them in a sandboxed DB. |
| 3   | `codex "Write unit tests for utils/date.ts"`                                    | Generates tests, executes them, and iterates until they pass.              |
| 4   | `codex "Bulk-rename *.jpeg -> *.jpg with git mv"`                               | Safely renames files and updates imports/usages.                           |
| 5   | `codex "Explain what this regex does: ^(?=.*[A-Z]).{8,}$"`                      | Outputs a step-by-step human explanation.                                  |
| 6   | `codex "Carefully review this repo, and propose 3 high impact well-scoped PRs"` | Suggests impactful PRs in the current codebase.                            |
| 7   | `codex "Look for vulnerabilities and create a security review report"`          | Finds and explains security bugs.                                          |

### Memory with AGENTS.md

You can give Codex extra instructions and guidance using `AGENTS.md` files. Codex looks for `AGENTS.md` files in the following places, and merges them top-down:

1. `~/.codex/AGENTS.md` - personal global guidance
2. `AGENTS.md` at repo root - shared project notes
3. `AGENTS.md` in the current working directory - sub-folder/feature specifics

For more information on how to use AGENTS.md, see the [official AGENTS.md documentation](https://agents.md/).

### Tips & shortcuts

#### Use `@` for file search

Typing `@` triggers a fuzzy-filename search over the workspace root. Use up/down to select among the results and Tab or Enter to replace the `@` with the selected path. You can use Esc to cancel the search.

#### Image input

Paste images directly into the composer (Ctrl+V / Cmd+V) to attach them to your prompt. You can also attach files via the CLI using `-i/--image` (comma‑separated):

```bash
codex -i screenshot.png "Explain this error"
codex --image img1.png,img2.jpg "Summarize these diagrams"
```

#### Esc–Esc to edit a previous message

When the chat composer is empty, press Esc to prime “backtrack” mode. Press Esc again to open a transcript preview highlighting the last user message; press Esc repeatedly to step to older user messages. Press Enter to confirm and Codex will fork the conversation from that point, trim the visible transcript accordingly, and pre‑fill the composer with the selected user message so you can edit and resubmit it.

In the transcript preview, the footer shows an `Esc edit prev` hint while editing is active.

#### Shell completions

Generate shell completion scripts via:

```shell
codex completion bash
codex completion zsh
codex completion fish
```

#### `--cd`/`-C` flag

Sometimes it is not convenient to `cd` to the directory you want Codex to use as the "working root" before running Codex. Fortunately, `codex` supports a `--cd` option so you can specify whatever folder you want. You can confirm that Codex is honoring `--cd` by double-checking the **workdir** it reports in the TUI at the start of a new session.



---------


## Install & build

### System requirements

| Requirement                 | Details                                                         |
| --------------------------- | --------------------------------------------------------------- |
| Operating systems           | macOS 12+, Ubuntu 20.04+/Debian 10+, or Windows 11 **via WSL2** |
| Git (optional, recommended) | 2.23+ for built-in PR helpers                                   |
| RAM                         | 4-GB minimum (8-GB recommended)                                 |

### DotSlash

The GitHub Release also contains a [DotSlash](https://dotslash-cli.com/) file for the Codex CLI named `codex`. Using a DotSlash file makes it possible to make a lightweight commit to source control to ensure all contributors use the same version of an executable, regardless of what platform they use for development.

### Build from source

```bash
# Clone the repository and navigate to the root of the Cargo workspace.
git clone https://github.com/openai/codex.git
cd codex/codex-rs

# Install the Rust toolchain, if necessary.
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
rustup component add rustfmt
rustup component add clippy

# Build Codex.
cargo build

# Launch the TUI with a sample prompt.
cargo run --bin codex -- "explain this codebase to me"

# After making changes, ensure the code is clean.
cargo fmt -- --config imports_granularity=Item
cargo clippy --tests

# Run the tests.
cargo test
``` 


------
https://github.com/openai/codex/releases/tag/rust-v0.34.0

Releases rust-v0.34.0
0.34.0 Latest
@github-actions github-actions released this 3 days ago
· 48 commits to main since this release
 rust-v0.34.0
 0d2ceb1
#3436: hotfix for issue that prevented Codex from initializing external MCP servers

Merged PRs
[#2799] Persist model & reasoning changes (#2799)
[#3436] Make user_agent optional (#3436)
Assets
22
codex
sha256:e95e17f61449d7ef7c42de148b50df128ddff5904b63570f6c87e978ac452d5b
3.42 KB
3 days ago
codex-aarch64-apple-darwin.tar.gz
sha256:215eb4f74a7aa4aff6125506f766c0aeefd0a5716cefec951c980c7af70e558b
7.3 MB
3 days ago
codex-aarch64-apple-darwin.zst
sha256:06b150fa37b565f7dae36c3a44a24b31ea9983e9d343dd8c136cffe299848069
5.34 MB
3 days ago
codex-aarch64-pc-windows-msvc.exe.tar.gz
sha256:d16df098446e2de31ed2d479d5cf82803174b2c759e807f52c696fd9f6ed254c
7.54 MB
3 days ago
codex-aarch64-pc-windows-msvc.exe.zip
sha256:c7f53a2adbb75ede05d182ed17197406437932d9615d8af4b826c22ce7169e46
7.33 MB
3 days ago
codex-aarch64-pc-windows-msvc.exe.zst
sha256:d4c4ddb3d2e47d7a771fda4ff699d3b840dcf180b857b54f61f90e3967b9aa45
5.58 MB
3 days ago
codex-aarch64-unknown-linux-gnu.tar.gz
sha256:c2b98919c00ebcd29cbc1381eeba2699ee2c6fcac70aa438ae3e6a33f472f77e
7.55 MB
3 days ago
codex-aarch64-unknown-linux-gnu.zst
sha256:8b7faadd85a67e89c8e74eefab7c48e2b57910b43fbc805369678f854b1e175b
5.55 MB
3 days ago
codex-aarch64-unknown-linux-musl.tar.gz
sha256:e89d35480ce870e2d83d10b6f5a86411d728592f36544dad914c697c1802cfcc
9.56 MB
3 days ago
codex-aarch64-unknown-linux-musl.zst
sha256:b19a1bba543976670af93bec52dad581e58a4bc908c0c016fddd5ab6e108ca4e
7.37 MB
3 days ago
codex-npm-0.34.0.tgz
sha256:0d0a36202afd82488bade3e236451fc1684f5ad06bf3999fde517dc69a150e7c
52.1 MB
3 days ago
codex-x86_64-apple-darwin.tar.gz
sha256:2b2c111ef42c50d52c3c184cb27c4528542d9965a0cd5b4daa7754b79239b6c3
7.89 MB
3 days ago
codex-x86_64-apple-darwin.zst
sha256:2e5f100b0fd3fe1c24caf7de0195f96385ec99786d3fdf0ad38d57bb007f65c5
5.8 MB
3 days ago
codex-x86_64-pc-windows-msvc.exe.tar.gz
sha256:072486c4616f5387a51f5a0fd7c4e49e5bedaddfe116c617417e887d8f857ebc
8.19 MB
3 days ago
codex-x86_64-pc-windows-msvc.exe.zip
sha256:789563e58e6126de96329c8e154718409378831abcef3856c8b46527b20c08ac
7.92 MB
3 days ago
codex-x86_64-pc-windows-msvc.exe.zst
sha256:56a49da5af7188bd2368d8a5f8d176d5bee83e784cb71fef4c4de7ec568d86d6
6.09 MB
3 days ago
codex-x86_64-unknown-linux-gnu.tar.gz
sha256:70b7485cfcf3d6108c425699067d6f6946ac3d85a1299da94e8b70eb5a07028b
8.13 MB
3 days ago
codex-x86_64-unknown-linux-gnu.zst
sha256:600706b47a9be9e45ec2a88ea28b75c964028bf8b27db3677abb3671967a7007
6.01 MB
3 days ago
codex-x86_64-unknown-linux-musl.tar.gz
sha256:5715dc334947361555b7cef9062b26d6cd692dd6f64781cb2849137ebc7a8e59
10.1 MB
3 days ago
codex-x86_64-unknown-linux-musl.zst
sha256:438066ed81cd1d5ac575aafe0904eac37949d96882d3adf4fac0eca704e5e2e4
7.66 MB
3 days ago
Source code
(zip)
3 days ago
Source code
(tar.gz)
3 days ago


-------

## Sandbox & approvals

### Approval modes

We've chosen a powerful default for how Codex works on your computer: `Auto`. In this approval mode, Codex can read files, make edits, and run commands in the working directory automatically. However, Codex will need your approval to work outside the working directory or access network.

When you just want to chat, or if you want to plan before diving in, you can switch to `Read Only` mode with the `/approvals` command.

If you need Codex to read files, make edits, and run commands with network access, without approval, you can use `Full Access`. Exercise caution before doing so.

#### Defaults and recommendations

- Codex runs in a sandbox by default with strong guardrails: it prevents editing files outside the workspace and blocks network access unless enabled.
- On launch, Codex detects whether the folder is version-controlled and recommends:
  - Version-controlled folders: `Auto` (workspace write + on-request approvals)
  - Non-version-controlled folders: `Read Only`
- The workspace includes the current directory and temporary directories like `/tmp`. Use the `/status` command to see which directories are in the workspace.
- You can set these explicitly:
  - `codex --sandbox workspace-write --ask-for-approval on-request`
  - `codex --sandbox read-only --ask-for-approval on-request`

### Can I run without ANY approvals?

Yes, you can disable all approval prompts with `--ask-for-approval never`. This option works with all `--sandbox` modes, so you still have full control over Codex's level of autonomy. It will make its best attempt with whatever contrainsts you provide.

### Common sandbox + approvals combinations

| Intent                                  | Flags                                                                                  | Effect                                                                                  |
| --------------------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Safe read-only browsing                 | `--sandbox read-only --ask-for-approval on-request`                                            | Codex can read files and answer questions. Codex requires approval to make edits, run commands, or access network. |
| Read-only non-interactive (CI)          | `--sandbox read-only --ask-for-approval never`                                                 | Reads only; never escalates                                                                     |
| Let it edit the repo, ask if risky      | `--sandbox workspace-write --ask-for-approval on-request`                                      | Codex can read files, make edits, and run commands in the workspace. Codex requires approval for actions outside the workspace or for network access. |
| Auto (preset)                           | `--full-auto` (equivalent to `--sandbox workspace-write` + `--ask-for-approval on-failure`)     | Codex can read files, make edits, and run commands in the workspace. Codex requires approval when a sandboxed command fails or needs escalation. |
| YOLO (not recommended)                  | `--dangerously-bypass-approvals-and-sandbox` (alias: `--yolo`)                                 | No sandbox; no prompts                                                                          |

> Note: In `workspace-write`, network is disabled by default unless enabled in config (`[sandbox_workspace_write].network_access = true`).

#### Fine-tuning in `config.toml`

```toml
# approval mode
approval_policy = "untrusted"
sandbox_mode    = "read-only"

# full-auto mode
approval_policy = "on-request"
sandbox_mode    = "workspace-write"

# Optional: allow network in workspace-write mode
[sandbox_workspace_write]
network_access = true
```

You can also save presets as **profiles**:

```toml
[profiles.full_auto]
approval_policy = "on-request"
sandbox_mode    = "workspace-write"

[profiles.readonly_quiet]
approval_policy = "never"
sandbox_mode    = "read-only"
```

### Experimenting with the Codex Sandbox

To test to see what happens when a command is run under the sandbox provided by Codex, we provide the following subcommands in Codex CLI:

```
# macOS
codex debug seatbelt [--full-auto] [COMMAND]...

# Linux
codex debug landlock [--full-auto] [COMMAND]...
```

### Platform sandboxing details

The mechanism Codex uses to implement the sandbox policy depends on your OS:

- **macOS 12+** uses **Apple Seatbelt** and runs commands using `sandbox-exec` with a profile (`-p`) that corresponds to the `--sandbox` that was specified.
- **Linux** uses a combination of Landlock/seccomp APIs to enforce the `sandbox` configuration.

Note that when running Linux in a containerized environment such as Docker, sandboxing may not work if the host/container configuration does not support the necessary Landlock/seccomp APIs. In such cases, we recommend configuring your Docker container so that it provides the sandbox guarantees you are looking for and then running `codex` with `--sandbox danger-full-access` (or, more simply, the `--dangerously-bypass-approvals-and-sandbox` flag) within your container. 

-------

## Zero data retention (ZDR) usage

Codex CLI natively supports OpenAI organizations with [Zero Data Retention (ZDR)](https://platform.openai.com/docs/guides/your-data#zero-data-retention) enabled.


-------

## Codex open source fund

We're excited to launch a **$1 million initiative** supporting open source projects that use Codex CLI and other OpenAI models.

- Grants are awarded up to **$25,000** API credits.
- Applications are reviewed **on a rolling basis**.

**Interested? [Apply here](https://openai.com/form/codex-open-source-fund/).** 
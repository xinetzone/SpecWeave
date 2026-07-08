Your coding agent already knows the feature you just shipped. Plug miniTest in and it writes the tests too.

There are two ways in, and they can do the same things. Pick whichever fits your setup, or use both.

The CLI ships with a bundled agent skill. Once installed, your editor’s agent uses the same `minitest` commands you’d use in a shell, with the same understanding of [story shape](https://www.minitap.ai/docs/minitest/suite/anatomy), criteria rules, and dependencies.

### Beyond authoring

The CLI is also the right surface for scripts, local dev, and uploading manual builds:

```shellscript
# List the apps you can see
minitest apps list

# Upload a build
minitest --app myapp build upload ./path/to/build.ipa

# Start a run for one user story (waits until done)
minitest --app myapp run start "Sign up" --android-build 8f9c... --watch

# Start a run covering every user story
minitest --app myapp run all --ios-build 4e2b... --android-build 8f9c...
```

All commands accept `--json` for scripting. Target an app with `--app <id-or-name>` or `export MINITEST_APP_ID=...` once per shell.

For every command and flag, see [CLI commands](https://www.minitap.ai/docs/minitest/reference/cli-commands).

Open source at [github.com/minitap-ai/minitest-cli](https://github.com/minitap-ai/minitest-cli).

The MCP server gives your agent direct access to the miniTest backend. It works with **any MCP-compatible client**: Cursor, Claude Code, Windsurf, Cline, Continue, or anything else that speaks the Model Context Protocol.

### What your agent can do

## User stories

List, create, update, and delete user stories. Wire dependencies. Attach profiles and files.

## Runs

Create runs for a single story or the full suite. Poll for status, read per-criterion results.

## Config

Set profiles per app, update Mini’s memory, read the current app configuration.

## Docs

Search and read the miniTest docs without leaving the editor.

For every tool and its payload, see [MCP tools](https://www.minitap.ai/docs/minitest/reference/mcp-tools).

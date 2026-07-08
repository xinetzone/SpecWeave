These are the terms miniTest uses across the dashboard, the CLI, the MCP server, and this documentation. When the docs and the dashboard disagree, the docs win until the dashboard catches up.

| Term | What it means |
| --- | --- |
| **miniTest** | The product. Lowercase m, capital T. The CLI binary is `minitest` (all lowercase). |
| **Mini** | The AI agent that drives the device, authors user stories, and triages issues. Pronoun: “it”. |
| **Workspace** | The top-level container that holds apps, members, integrations, and billing. |
| **App** | A configured mobile app inside a workspace. |
| **User story** | A plain-English journey through the app, with acceptance criteria. Not “test”, “flow”, or “scenario”. |
| **Acceptance criterion** (pl. **criteria**) | A single observable condition inside a user story. Not “assertion”, “check”, or “step”. |
| **Suite** | All user stories for an app. |
| **Run** | One execution event. You click **Run tests**, N stories run together. Not “batch”. |
| **Build** | The `.ipa` or `.apk` artifact a run executes against. |
| **Verdict** | The outcome of a run or a story within a run: Passed, Warning, Failed, or Unprocessable. Not “result” or “status”. |
| **Status** | The lifecycle state of an issue (open, acknowledged, resolved). Distinct from verdict. |
| **Criticality** | The importance label on an issue: Critical, Warning, or Pass. Mini infers it at runtime. You can override it per issue when the inference doesn’t match your business reality. |
| **Issue** | A failed criterion that needs triage. Lives on the Issues tab. Not “failure” or “bug”. |
| **Suggestion** | A UX observation Mini flagged while running a story — something outside the acceptance criteria that looked off. Not “finding” or “recommendation”. |
| **Fix prompt** | The clipboard-ready block Mini produces for each failed criterion. Contains a root cause, steps to reproduce, and a suggested fix. |
| **Profile** | A named set of credentials (username, password, notes) attached to a user story. Mini uses it to sign in during the run. |
| **Mini’s memory** | Extra context about the app that Mini reads before every run. Set via the MCP server or the CLI. |
| **Test Configuration** | The per-app settings screen in the dashboard (profiles, env vars, Mini’s memory). Capitalize as a proper noun when referring to the screen; lowercase in flowing prose. |
| **Dashboard** | The webapp at [app.minitap.ai](https://app.minitap.ai/). |
| **Agent** | The AI driving the device. Synonym for Mini in technical contexts. |
| **CLI** | The `minitest` command-line tool. See [Cursor and Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude). |
| **MCP server** | The Model Context Protocol surface that Cursor, Claude Code, and other MCP clients connect to. |
| **MCP tools** | The individual calls exposed by the MCP server. See [MCP tools](https://www.minitap.ai/docs/minitest/reference/mcp-tools). |
| **PR check** | The GitHub status check posted on pull requests by the MiniTest GitHub App. |
| **MiniTest GitHub App** | The literal GitHub App name (Pascal case, no space). Only used when referring to the App you install on GitHub. |

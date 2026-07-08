Your suite is a list of user stories Mini runs against every build. [Mini maintains your suite](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite) for you most of the time, but the surfaces below stay open whenever you want to step in by hand.

Whichever surface you use, the [story shape](https://www.minitap.ai/docs/minitest/suite/anatomy) is the same — name, type, description, acceptance criteria, and optionally a profile or files.

The easiest place to start, and the only one where you can see the whole suite while you edit.

Go to **App → Stories** and click **New story**. The dialog covers everything:

- **Name** and **type** (Login, Checkout, etc. — or a custom type you define for this app).
- **Description** — one sentence about what the story validates.
- **Acceptance criteria** — one assertion per line. Hit Enter to add the next.
- Optionally bind a [profile](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles) or attach [files](https://www.minitap.ai/docs/minitest/suite/anatomy#files).
- Optionally declare dependencies — if the story needs another one to have passed first (e.g. checkout depends on sign-in).

Editing an existing story works the same way. Removing a criterion versions the change and auto-resolves any open issues tied to that criterion — see [Anatomy](https://www.minitap.ai/docs/minitest/suite/anatomy).

Good for quick edits without leaving the channel where you spotted the gap.

Mention Mini with the intent in plain English:

```text
@mini create test
```

Mini walks you through it with buttons and inputs: pick the app, name the story, list the criteria, confirm.

![Mini creating a user story in a Slack thread](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/slack-test-creation.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=6a24c7513a2e90a7f204a0fc1e20e5e7)

Mini creating a user story in a Slack thread

Same shape for editing or deleting:

```text
@mini edit test
@mini delete test
```

Handy when you’re reading a [triage](https://www.minitap.ai/docs/minitest/triage/issues) thread, realise the suite is missing a story for the bug you just acknowledged, and want to add one before you forget. The story lands in the dashboard the moment you confirm.

See [Mini in Slack](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#talking-to-mini) for the full intent surface.

Your coding agent already knows the feature you just shipped, so it can write the story for you. There are two ways to connect one to miniTest, and they can do the same things:

### Option 1 — The MCP server

Install the miniTest MCP server in your editor. The dashboard’s onboarding gives you the one-line command:

```shellscript
npx add-mcp https://testing-service.app.minitap.ai/mcp/ -g -n minitest
```

Your agent prompts you to authenticate on first use. From then on, ask it to write or edit stories in plain English and it routes through `create_user_story` / `update_user_story` after showing you the diff.

See the [MCP tools reference](https://www.minitap.ai/docs/minitest/reference/mcp-tools) for the full surface.

### Option 2 — The CLI with the bundled skill

Install the CLI, authenticate, and ask your agent the same way. The CLI ships with a bundled skill so your editor’s agent uses the same `minitest` commands you’d use in a shell.

See [Cursor and Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude) for the install steps and the full CLI tour.

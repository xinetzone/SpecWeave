The miniTest MCP server exposes a set of tools that your coding agent uses to browse apps, create and edit user stories, trigger runs, read results, and search the docs. This page documents every tool at the API level so you know what your agent has access to.

See [Cursor and Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude) for the install steps and the agent prompt.

## Tools

### Discovery

| Tool | Description |
| --- | --- |
| `get_user_apps` | Get all apps the authenticated user has access to. Use this first to discover valid `app_id` values required by other tools. |

### User stories

| Tool | Description |
| --- | --- |
| `list_user_stories` | List user stories for an application. Use `type_filter` to narrow to: `login`, `registration`, `checkout`, `onboarding`, `search`, `settings`, `navigation`, `form`, `profile`, or `other`. |
| `get_user_story` | Get a user story by ID, including its acceptance criteria. |
| `create_user_story` | Create a new user story with acceptance criteria. Each criterion is a plain-text assertion an AI agent verifies on-device. Criteria must be visually observable, so avoid backend-only assertions. Valid types: `login`, `registration`, `checkout`, `onboarding`, `search`, `settings`, `navigation`, `form`, `profile`, `other`. |
| `update_user_story` | Update an existing user story. Only the provided fields change. When `acceptance_criteria` is provided, the entire list is replaced. Also accepts `depends_on` to wire story dependencies (replace-all: pass `[]` to clear, omit to leave unchanged). |
| `delete_user_story` | Delete a user story and its associated acceptance criteria. |

### Runs

| Tool | Description |
| --- | --- |
| `create_run` | Create a story run for a user story and queue it for execution. Pass at least one of `ios_build_id`, `android_build_id`, or `run_web=true` to pick which targets execute. When `run_web=true`, the run uses the web targets configured on the app (web URL plus browser and viewport pairs). Use `get_run_status` to poll for completion. |
| `create_batch_runs` | Create story runs for **all** user stories of an app and queue them for execution. Pass at least one of `ios_build_id`, `android_build_id`, or `run_web=true`. Web runs source their targets from the app’s web configuration. |
| `get_run_status` | Get the current status of a story run (`pending`, `running`, `completed`, `failed`). |
| `get_run_results` | Get the acceptance criteria results for a completed story run. Returns each criterion’s pass/fail status with failure reasons, plus an overall summary. |

### Builds

| Tool | Description |
| --- | --- |
| `list_builds` | List builds for an application. Optionally filter by platform (`android` or `ios`). Builds are mobile only. Web runs have no builds; their URL, browser, and viewport come from the app’s settings. |
| `upload_build` | **Not yet supported via MCP.** Use the [minitest CLI](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude) instead: `minitest build upload <file>`. |

### Maintenance

| Tool | Description |
| --- | --- |
| `maintenance_check` | Acknowledge that tests have been reviewed for a commit. Call after making code changes, before opening or updating a PR. If the app has maintenance checks enabled, a GitHub Check Run flips to ✅. |

### App configuration

| Tool | Description |
| --- | --- |
| `set_app_test_config` | Configure a [profile](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles) for an app. Used at run time to provide login credentials to the agent. To set Mini’s memory (context), use `set_app_knowledge` instead. |
| `set_app_knowledge` | Set additional context about the app (test data, navigation patterns, app-specific behavior). Creates a new versioned prompt; previous versions are preserved. |
| `get_app_test_config` | Get test configuration for an app. Returns the config with decrypted credentials for use in test flows. |
| `delete_app_test_config` | Delete test configuration for an app. |

### Documentation

These two tools proxy the Mintlify-hosted public docs MCP.

| Tool | Description |
| --- | --- |
| `search_docs` | Semantic search across the public miniTest documentation. Call **before** generating a user story template or guessing how to trigger a run. Prefer “how to X” queries. |
| `read_docs` | Read the full content of miniTest docs pages. Use **after** `search_docs` when search snippets aren’t enough. Supports shell-like read-only queries (`rg`, `grep`, `ls`, `cat`, `head`). |

## Run-result payload

`get_run_results` returns:

```jsonc
{
  "run_id": "<uuid>",
  "status": "pending | running | completed | failed | cancelled",
  "summary": {
    "total":         <int>,
    "passed":        <int>,
    "failed":        <int>,
    "unprocessable": <int>
  },
  "results": [
    {
      "id":                   "<uuid>",
      "criterion_version_id": "<uuid>",
      "platform":             "ios | android | web",
      "browser":              "<str | null>",
      "viewport":             "<str | null>",
      "label":                "<str>",
      "status":               "success | failed | unprocessable | skipped",
      "success":              <bool>,
      "fail_reason":          "<str | null>",
      "rca_prompt":           "<str | null>"
    }
  ]
}
```

For mobile platforms, `browser` and `viewport` are `null` and `label` reads as `iOS` or `Android`. For web, `label` reads as `Chrome · Mobile`, `Firefox · Desktop`, and so on. The same three fields appear on each entry of the `platforms` array returned by `get_run_status`.

The MCP response intentionally does **not** include a video URL. The recording lives at the storage path referenced internally by the run; it’s rendered in the dashboard’s run-detail page. If you need video access from outside the dashboard, file a request.

## Authentication

The MCP server uses OAuth (PKCE). First call triggers a browser sign-in; the session is cached locally. There is no static API key.

This is the exhaustive reference. For the install steps and a quick tour, see [Cursor and Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude).

## Global

| Flag | Short | Default | Description |
| --- | --- | --- | --- |
| `--version` | `-v` | — | Print `minitest-cli <version>` and exit. |
| `--json` | — | off | Emit JSON to stdout; diagnostics go to stderr. |
| `--app <id-or-slug>` | — | `$MINITEST_APP_ID` | Target app. Required for every command except `auth`, `apps`, `flow-types`, `skill`, `upgrade`. |
| `--help` | — | — | Standard help. |

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 1 | General error (validation, bad args) |
| 2 | Authentication error |
| 3 | Network / API error |
| 4 | Resource not found |
| 5 | Build rejected as invalid (only `build upload`) |

## auth

Authentication management.

### minitest auth login

Run the OAuth 2.0 PKCE browser flow and save a session to `~/.minitest/credentials.json`. Opens a browser; waits up to two minutes.

### minitest auth logout

Delete the local credentials file.

### minitest auth status

Print the current auth state: method (`env_token` / `oauth` / `none`), user id, email, token expiry. Honors `--json`.

## apps

Read workspace + app metadata.

### minitest apps list

List all apps you can see.

### minitest apps create

Create a new app in a workspace. Prints the new app’s UUID to stdout.

| Flag | Required | Description |
| --- | --- | --- |
| `--name <str>` | yes | Human-readable app name. |
| `--tenant <id>` | no | Workspace UUID. Required only when you belong to more than one workspace. |
| `--description <str>` | no |  |
| `--slug <str>` | no | Auto-generated server-side if omitted. |
| `--icon <path>` | no | Path to a local image; uploaded as multipart. |

Example:

```shellscript
minitest apps create --name "My App" --tenant 3f0e... --icon ./icon.png
```

## user-story

User-story operations. All commands need `--app` or `MINITEST_APP_ID`.

### minitest user-story create

Create a user story.

| Flag | Required | Description |
| --- | --- | --- |
| `--name <str>` | yes |  |
| `--type <str>` | yes | Validated against backend types. Run `minitest flow-types list` to see them. |
| `--description <str>` | no |  |
| `--criteria <str>` | no | Acceptance criterion. Repeatable. |
| `--depends-on <id>` | no | Parent user-story ID. Repeatable. |

### minitest user-story list

Paginated list.

| Flag | Default | Description |
| --- | --- | --- |
| `--type <str>` | — | Filter by type. |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 | Max 100. |
| `--all` | off | Auto-paginate. |

### minitest user-story get <user-story-id>

Fetch a single story by UUID.

### minitest user-story update <user-story-id>

Partial update. At least one mutating flag is required.

| Flag | Description |
| --- | --- |
| `--name <str>` |  |
| `--type <str>` | Validated against backend types. |
| `--description <str>` |  |
| `--criteria <str>` | **Replace** the criteria set. Repeatable. |
| `--add-criteria <str>` | **Append** to the criteria set. Repeatable. Mutually exclusive with `--criteria`. |
| `--depends-on <id>` | **Replace** the dependency set. Repeatable. |
| `--remove-dependency <id>` | Subtract from current deps. Repeatable. Ignored with a warning if `--depends-on` is also passed. |

### minitest user-story delete <user-story-id>

Hard delete. `--force` is required.

## user-story-binding

Attach a profile and files to a story.

### minitest user-story-binding set-profile <user-story-id>

Bind or clear a test profile.

| Flag | Description |
| --- | --- |
| `--profile <id>` | Profile UUID. |
| `--clear` | Remove the binding. |

Exactly one of the two is required.

### minitest user-story-binding set-files <user-story-id>

Atomically replace the set of test files bound to a story.

| Flag | Description |
| --- | --- |
| `--file <id>` | Test-file UUID. Repeatable. |
| `--clear` | Replace with an empty set. |

Exactly one mode is required.

### minitest user-story-binding list-files <user-story-id>

| Flag | Default | Description |
| --- | --- | --- |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 50 | Max 100. |

## test-profile

App-scoped profiles (credentials the agent uses to sign in).

### minitest test-profile create

| Flag | Required | Description |
| --- | --- | --- |
| `--name <str>` | yes |  |
| `--username <str>` | no |  |
| `--password <str>` | no | Mutually exclusive with `--password-stdin`. |
| `--password-stdin` | no | Read password from stdin. |
| `--about <str>` | no | Free-text notes. |

Example:

```shellscript
echo "$PASS" | minitest test-profile create --name "QA user" --username qa@x.com --password-stdin
```

### minitest test-profile get <profile-id>

### minitest test-profile update <profile-id>

| Flag | Description |
| --- | --- |
| `--name <str>` |  |
| `--username <str>` |  |
| `--password <str>` | Mutually exclusive with `--password-stdin` and `--clear-password`. |
| `--password-stdin` | Read password from stdin. |
| `--clear-password` | Remove the stored password. |
| `--about <str>` | Pass empty string to clear. |

### minitest test-profile delete <profile-id>

`--force` is required.

### minitest test-profile list

List app-scoped profiles.

### minitest test-profile list-shared

List workspace-shared profiles (the ones under **Shared by Minitap** in the dashboard). Doesn’t need `--app`.

## test-file

App-scoped reference assets (images, docs, video, audio) bound to user stories. Upload cap: 25 MB.

### minitest test-file upload <path>

| Flag | Default | Description |
| --- | --- | --- |
| `--name <str>` | file basename |  |
| `--note <str>` | — |  |

MIME type is guessed from the extension.

### minitest test-file get <file-id>

### minitest test-file update <file-id>

At least one flag is required.

| Flag | Description |
| --- | --- |
| `--name <str>` |  |
| `--note <str>` | Mutually exclusive with `--clear-note`. |
| `--clear-note` |  |

### minitest test-file delete <file-id>

`--force` is required.

### minitest test-file list

| Flag | Default | Description |
| --- | --- | --- |
| `--kind <kind>` | — | One of `image`, `document`, `video`, `audio`, `other`. |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 | Max 100. |

## flow-types

### minitest flow-types list

Print every valid user-story type, one per line (JSON array with `--json`).

## app-knowledge

Read and update the per-app **Mini’s memory** prompt that grounds agent runs. Both subcommands require `--app` passed inline.

### minitest app-knowledge get

```shellscript
minitest app-knowledge get --app 3f0e...
```

### minitest app-knowledge update

| Flag | Required | Description |
| --- | --- | --- |
| `--app <id>` | yes |  |
| `--content <str>` | one of | Inline markdown. |
| `--content-file <path>` | one of | Path to a markdown file. |

```shellscript
minitest app-knowledge update --app 3f0e... --content-file ./app_knowledge.md
```

## build

### minitest build upload <file>

Upload a `.apk` or `.ipa`. The server validates the build for virtual-device compatibility before accepting it.

| Flag | Description |
| --- | --- |
| `--platform <ios\|android>` | Auto-detected from extension if omitted. |

iOS builds must be Simulator builds. Android builds must be x86\_64-compatible.

### minitest build list

| Flag | Default | Description |
| --- | --- | --- |
| `--platform <ios\|android>` | — | Filter. |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 |  |
| `--all` | off | Auto-paginate. |

## run

Story-run execution. All subcommands need `--app` or `MINITEST_APP_ID`. At least one of `--ios-build` / `--android-build` is required to start a run.

### minitest run start <user-story>

Start a run for one user story. `<user-story>` is either a UUID or a case-insensitive name match.

| Flag | Default | Description |
| --- | --- | --- |
| `--ios-build <id>` | — | iOS build UUID. |
| `--android-build <id>` | — | Android build UUID. |
| `--watch / --no-watch` | `--watch` | Poll every 2s until the run reaches a terminal state. |

### minitest run status <run-id>

| Flag | Default | Description |
| --- | --- | --- |
| `--watch / --no-watch` | `--no-watch` | If set and the run is non-terminal, poll every 2s. |

### minitest run list <user-story>

Historical runs for a story. `<user-story>` is a name or UUID.

| Flag | Default | Description |
| --- | --- | --- |
| `--status <str>` | — | One of `pending`, `running`, `completed`, `failed`, `cancelled`. |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 |  |
| `--all` | off | Auto-paginate. |

### minitest run cancel <run-id>

Cancel a pending or running story-run.

### minitest run all

Start a run covering every user story for the app. Fire-and-forget — prints the run ID and exits.

| Flag | Default | Description |
| --- | --- | --- |
| `--ios-build <id>` | — |  |
| `--android-build <id>` | — |  |

## batch

The CLI uses the term “batch” for a multi-story run (one click of **Run tests** in the dashboard = one batch).

### minitest batch list

| Flag | Default | Description |
| --- | --- | --- |
| `--status <str>` | — | Filter by status. Repeatable. |
| `--result <str>` | — | Filter by result. Repeatable. |
| `--commit-sha <str>` | — |  |
| `--user-story-id <id>` | — | Restrict to batches containing this story. |
| `--search <str>` | — | Free-text search. |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 | Max 100. |
| `--all` | off | Auto-paginate. |

### minitest batch get <batch-id>

Full batch payload with every story run.

### minitest batch cancel <batch-id>

Cancel the batch and every pending or running story-run in it.

## maintenance-check

### minitest maintenance-check <commit-sha>

Acknowledge that tests have been reviewed for a given commit. Used to gate CI on a “tests-are-up-to-date” status. The command runs directly on the group — there are no subcommands.

```shellscript
minitest --app myapp maintenance-check 0a1b2c3d4e5f...
```

## skill

### minitest skill

Fetch the latest agent skill for the CLI (the prompt that teaches AI coding agents how to drive it) and print it to stdout.

```shellscript
minitest skill > minitest-skill.md
```

## upgrade

### minitest upgrade

Self-update the CLI and refresh the agent skill. Detects whether you installed via Homebrew or `uv` and runs the right upgrade command, then reinstalls the skill if its content has changed.

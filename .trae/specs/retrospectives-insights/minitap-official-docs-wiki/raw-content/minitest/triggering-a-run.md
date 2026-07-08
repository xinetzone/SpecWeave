A run takes your suite (or part of it) and runs it against a build on virtual devices. There are four ways to start one; pick whichever fits how you work.

Click **Run tests** on any app page. A side panel walks you through two steps:

1. **Pick a build.** Use the latest build for the configured branch, pick a specific commit or build ID, upload a fresh `.apk` / `.ipa`, or paste a PWA URL.
2. **Pick the stories.** Run **all** of them (default) or narrow to a subset from a searchable list.

Click **Start run** and Mini queues it on the next available device. The dashboard’s Runs tab updates live.

Best for one-off checks before a demo, validating a fix you just pushed, or sanity-checking a build that came in from a third-party CI.

There are two ways to do it, both through `@mini`. There’s no slash command.

**Type the run inline.** Mention Mini with the app and the build tag:

```text
@mini run acme-checkout v1.4.2
```

Mini posts an ephemeral confirm with a 10-second cancel window, then fires. The heartbeat lands in the channel you configured for that app (see [Channel routing](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#channel-routing)).

**Or open the picker.** For a guided flow:

```text
@mini run all tests
```

Mini posts an interactive message walking you through app → build → stories → confirm.

Triggering from Slack requires your Slack user to be linked to a Minitap account. See [Linking your account](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#linking-your-account).

The path that powers [PR checks](https://www.minitap.ai/docs/minitest/integrations/github). Set this up once and Mini runs your suite on every PR: it builds the head commit, runs the stories, and posts the verdict back on the PR.

Setup is a workflow file in your repo that calls the **[`minitap-ai/minitest-trigger`](https://github.com/minitap-ai/minitest-trigger)** GitHub Action. The Action uploads the build (or asks Mini to build one) and starts the run, authenticated by the workflow’s GitHub OIDC token — no API key to manage.

```yaml
name: miniTest

on:
  pull_request:
    branches: [main]

jobs:
  run-suite:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # required for OIDC auth
      contents: read
    steps:
      - uses: minitap-ai/minitest-trigger@v1
        with:
          app-slug: my-app
```

Drop that file in `.github/workflows/`, push it to your default branch, and you’re done. The `MiniTest GitHub App` (see [GitHub integration](https://www.minitap.ai/docs/minitest/integrations/github)) must already be installed on the org — that’s what lets Mini post the verdict back to the PR.

The default config builds the head commit, runs every story, and posts a check + sticky comment on the PR. For every input — `run-ios`, `run-android`, `ios-build-path`, `android-build-path`, `user-story-types`, `tenant-id`, `cancel-previous-runs` — see [GitHub Action reference](https://www.minitap.ai/docs/minitest/reference/minitest-trigger-action).

### Required vs informational

The PR check is **informational by default**. To make Mini required to merge, enable `block_on_test_failures` in your workspace settings and add the check to **GitHub → Settings → Branches → Branch protection rules → Require status checks**. For everything the GitHub App posts on a PR — the sticky comment, the check run, the checkbox and slash-command triggers — see [GitHub integration](https://www.minitap.ai/docs/minitest/integrations/github).

### Re-running

- Toggle the **Run tests** checkbox in the sticky PR comment.
- Or post `/test` as a PR comment.
- Or click **Re-run** on the dashboard run report.

Two commands, depending on scope.

**One story:**

```shellscript
minitest run start <user-story-id> \
  --ios-build <build-id> \
  --android-build <build-id>
```

**The whole suite:**

```shellscript
minitest run all \
  --ios-build <build-id> \
  --android-build <build-id>
```

Both accept `--watch` to stream status to your terminal instead of printing the run ID and exiting. Sign in with `minitest auth login` once. See the [CLI reference](https://www.minitap.ai/docs/minitest/reference/cli-commands) for everything else.

See [Reading a run report](https://www.minitap.ai/docs/minitest/runs/run-report) for what to do with the result.

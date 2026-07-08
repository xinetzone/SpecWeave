miniTest talks to GitHub through a single GitHub App. Install it once per org and it covers every connected app in that org.

## Is connecting GitHub required?

Strictly speaking, no — you can test any app by uploading builds manually through the CLI. But skipping the GitHub connection means giving up a lot of what makes miniTest useful:

- [Automatic suite generation and maintenance](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite) from your codebase.
- Automatic builds on CI-triggered runs (see [Providing app builds](https://www.minitap.ai/docs/minitest/runs/builds)).
- Mini showing up on your PRs to tell you whether you can ship.

If you’re evaluating miniTest, you can skip GitHub today and add it later. If you’re using miniTest day to day, connect it.

## Install

**Workspace settings → Integrations → GitHub → Install**. The flow opens GitHub’s App install screen — pick the org and either grant **All repositories** or **Only selected repositories**.

![Workspace integrations settings showing a connected GitHub org](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/integrations-settings.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=f1502b6a2d8149112a28f229f7d8acc2)

Workspace integrations settings showing a connected GitHub org

## What you see on a PR

Mini only posts on PRs that target your app’s default branch (usually `main`) or a branch that matches your configured [release branch patterns](#when-mini-shows-up). Monorepo apps also require at least one changed file under the app’s source folder.

### The sticky comment

Mini posts one comment per PR. It introduces itself, lists every affected app with a **Run tests** checkbox, and waits for you to act — it never kicks off a run on its own.

Ticking a checkbox (or posting `@mini test <slug>` as a PR comment) fires a run. The comment edits in place as the run progresses, and when it finishes it becomes a full report: per-platform verdict, Critical and Warning buckets with expandable story cards, and a link back to the dashboard for the full timeline and video.

If you change the PR after the comment was posted — push a new commit, add an app — Mini edits the comment to match. No thread spam, no second comment.

### The check run

Every CI-triggered run also posts a GitHub check on the PR:

**Check name:** `Minitest (AppName)` — not visible in the project tree, but this is the name you’ll see in branch protection lists.

- **States:** queued → in progress → completed (success / failure / neutral).
- **Cancel** and **Bypass** buttons are available during the run and on terminal failures.

The check conclusion is **neutral by default** — Mini won’t block merges until you turn on blocking. To require it to pass, enable `block_on_test_failures` in your workspace settings, then add the check to **GitHub → Settings → Branches → Branch protection rules → Require status checks**.

## Triggering a run from a PR

Three paths, all producing the same run report:

### 1\. The CI Action (recommended)

**Why this path.** You control exactly when a run fires — on every push, only on PRs, on `release-*` tags, or any combination you want. You own the workflow file, so you decide the trigger conditions.

Add `minitap-ai/minitest-trigger@v1` to your `.github/workflows/*.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - uses: minitap-ai/minitest-trigger@v1
        with:
          app-slug: my-app
```

The Action authenticates via GitHub OIDC — no API key needed. The MiniTest GitHub App must be installed on the org before the first run. For every input and build-path example, see [GitHub Action reference](https://www.minitap.ai/docs/minitest/reference/minitest-trigger-action).

### 2\. The PR comment checkbox

Ticking the **Run tests** checkbox in Mini’s sticky comment fires a run for that app. No workflow file, no setup — the GitHub App handles the dispatch. Use this when you’re reviewing and want to confirm a fix without waiting for CI.

### 3\. The /test slash command

Post `@mini test <app-slug>` on the PR and Mini does the same thing as the checkbox. Works in the same comment or in any top-level PR comment.

## When Mini shows up

Mini decides whether to post a sticky comment on a PR using two rules — both configurable per app:

## Default branch

PRs targeting your app’s **default branch** (typically `main`) always get a comment for that app. This is the **source branch** you set when connecting the app to a repo.

## Release branch patterns

You can define **gitignore-style patterns** in **App Settings → CI** under `release_branch_patterns`. PRs targeting a branch that matches any pattern (e.g. `release/*`) get a comment even if the default branch is different.

If a PR matches neither (say it targets a feature branch), Mini stays quiet. The check run path via the CI Action still works regardless of branch.

Monorepo apps have one extra rule: at least one file in the PR must fall under the app’s configured source folder. PRs that only touch unrelated directories are skipped.

## Triggering from a tag

If you push a git tag matching your app’s configured tag pattern (set in **App Settings → CI** under `ci_tag_pattern`), Mini picks it up via the GitHub webhook and starts a run. No workflow file, no comment — purely for release-style triggers like `release-1.2.0`.

## Connecting an app to a repo

In each app’s **Settings → Source**, point at:

- **Repo** (`owner/name`) — auto-completes from the repos the App can see.
- **Branch** — the default branch. Determines which PRs get a sticky comment (see [When Mini shows up](#when-mini-shows-up)) and the base for tag-triggered runs.
- **Source folder** (optional) — subfolder for monorepos. See [Providing app builds](https://www.minitap.ai/docs/minitest/runs/builds).

## Removing the App

`GitHub → Settings → Applications → MiniTest → Configure → Uninstall`. miniTest will keep run history and configuration, but builds and PR checks will stop. Reinstalling restores everything.

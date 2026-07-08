The **[`minitap-ai/minitest-trigger`](https://github.com/minitap-ai/minitest-trigger)** GitHub Action is the CI surface for miniTest. It authenticates via GitHub OIDC, uploads your build (or asks Mini to build one), and starts the run — fire and forget. Results come back via a GitHub Check Run on the commit.

For the workflow setup walkthrough, see [Triggering a run → From CI](https://www.minitap.ai/docs/minitest/runs/triggering-a-run).

## Minimal usage

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
```

That’s enough. Mini builds your app for both platforms on the head commit, runs every story, and posts the verdict to the PR.

## Prerequisites

The workflow must have the `id-token: write` permission for OIDC authentication:

```yaml
permissions:
  id-token: write
```

And the `MiniTest GitHub App` must be installed on the org — see [GitHub integration](https://www.minitap.ai/docs/minitest/integrations/github).

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `app-slug` | Yes | — | The miniTest app slug. Find it in **App Settings → General**. |
| `run-ios` | No | `true` | Include the iOS lane. Mini builds the app when no `ios-build-path` is given. |
| `run-android` | No | `true` | Include the Android lane. Mini builds the app when no path is given. |
| `ios-build-path` | No | — | Pre-built iOS bundle, either a simulator `.app` directory or an `.ipa` file. |
| `android-build-path` | No | — | Pre-built Android `.apk`. Must target x86-64. |
| `user-story-types` | No | — | Comma-separated list of [story types](https://www.minitap.ai/docs/minitest/suite/anatomy) to run (e.g. `login,checkout`). |
| `run-web` | No | `false` | Include the web lane. For a web app linked to a GitHub repo, Mini builds and serves the commit this workflow runs on and tests against it, with no `web-url` needed. For a web app with only a configured URL, it tests that URL. See [Web runs](#web-runs). |
| `web-targets` | No | — | Explicit web targets, as a comma-separated list of `<browser>:<viewport>` specs (e.g. `chrome:desktop,safari:mobile`). Includes the web lane on its own. Set this or `run-web`, not both. |
| `web-url` | No | — | Per-run web URL, e.g. a PR preview deployment. When set, the web lane tests this URL instead of building the commit. Applies when `run-web` or `web-targets` is set. |
| `tenant-id` | No | — | Required only if the repo is linked to multiple workspaces. |
| `cancel-previous-runs` | No | `true` | Cancel in-flight CI runs on the same source branch when it matches a configured release pattern. See [Cancelling previous runs](#cancelling-previous-runs). |
| `api-url` | No | `https://testing-service.app.minitap.ai` | Override the API base URL. You won’t normally need this. |

## Outputs

| Output | Description |
| --- | --- |
| `batch-id` | The ID of the triggered run. |
| `status` | Initial status of the triggered run. |

## Build paths and requirements

If you don’t pass a build path, Mini builds your app for that platform on the triggering commit (using whatever’s configured in [Providing app builds](https://www.minitap.ai/docs/minitest/runs/builds)). If you pass a build path, the Action uploads that artifact instead of asking Mini to build.

### iOS

| Format | Notes |
| --- | --- |
| `.app` | Simulator bundle directory. Automatically packaged into `.ipa` before upload. |
| `.ipa` | Uploaded as-is. Must be a simulator build. |

A typical `xcodebuild` line for the simulator:

```shellscript
xcodebuild build \
  -scheme MyApp \
  -sdk iphonesimulator \
  -configuration Debug \
  -derivedDataPath ./build
# Output: ./build/Build/Products/Debug-iphonesimulator/MyApp.app
```

### Android

`.apk` only, and it must contain native libraries for `x86_64`. The Action inspects the APK and fails with a clear error if only `arm64-v8a` or `armeabi-v7a` are present.

Configure `app/build.gradle`:

```groovy
android {
  defaultConfig {
    ndk { abiFilters 'x86_64' }
  }
}
```

Then build:

```shellscript
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk
```

## Web runs

`run-ios`, `run-android`, and the web inputs each select a lane. Lanes are additive: you can run just the web lane, just one native lane, or any mix. Web targets point at a URL instead of an uploaded artifact, with one exception: a web app linked to a GitHub repo builds and serves the commit this workflow runs on. See [Building the commit](#building-the-commit).

There are two ways to include the web lane:

- **`run-web: true`** runs the app’s configured default web targets, set per app in the dashboard. This is the defaults marker: it expands to whatever browsers and viewports you set there. A repo-linked app runs them against the built commit; a URL-only app runs them against its configured web URL.
- **`web-targets`** runs an explicit list instead. Each spec is `<browser>:<viewport>`, comma-separated. Setting `web-targets` includes the web lane on its own.

Set `run-web` or `web-targets`, not both. One picks the app defaults, the other an explicit list.

A web app can be tested on a mobile device’s browser, so `<browser>:<viewport>` maps to a concrete target:

| Spec | Where it runs |
| --- | --- |
| `safari:mobile` | iOS device in Safari (mobile-web) |
| `chrome:mobile` | Android device in Chrome (mobile-web) |
| `chrome:desktop`, `firefox:desktop` | Desktop web |

The Action parses `<browser>:<viewport>` and the backend validates the combination.

Browser support is `chrome` and `firefox` for desktop, plus `safari` for iOS mobile-web. Desktop Safari (`safari:desktop`) is not a valid web target.

Each lane ignores nothing silently: `web-url` and `web-targets` apply only when the web lane is on, `ios-build-path` only when `run-ios` is on, `android-build-path` only when `run-android` is on. Passing a lane’s input while that lane is off is rejected, so a typo can’t quietly drop your build or URL.

### Building the commit

If your web app is linked to a GitHub repo (set in **App Settings**), `run-web: true` builds your frontend at the commit this workflow runs on, serves it in the test environment, and runs your web stories against that build. No `web-url` is required. This holds even if the app also has a configured web URL: the linked-repo lane tests the commit, not the deployment. Supply `web-url` only when you want to test a separately-deployed URL (e.g. a PR preview) instead of the commit.

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-web: true # builds and serves this commit for a repo-linked web app
```

### Per-run URL with web-url

The common CI case is testing a PR preview deployment. Set `web-url` to the deploy’s URL and it overrides the app’s configured web URL for that run:

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-web: true
    web-url: https://pr-142.preview.example.com
```

This runs the web lane against the preview URL, alongside whichever native lanes are enabled.

CI is one of two surfaces allowed to override web targets and the web URL per run; the other is the **Run tests** panel in the dashboard. The CLI, MCP tools, and Slack can pick the web lane but can’t override its targets or URL.

## Examples

### Default — Mini builds for both platforms

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
```

### iOS only

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-android: false
```

### Android only, with your own build

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-ios: false
    android-build-path: ./app/build/outputs/apk/debug/app-debug.apk
```

### Bring your own iOS build, let Mini build Android

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    ios-build-path: ./build/Build/Products/Debug-iphonesimulator/MyApp.app
```

### Restrict to specific story types

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    user-story-types: login,checkout,onboarding
```

### Web app, configured defaults

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    run-web: true
```

### Web app, explicit targets

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    web-targets: chrome:desktop,safari:mobile
    web-url: https://pr-142.preview.example.com
```

### Web app on mobile browsers

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    web-targets: safari:mobile,chrome:mobile
```

### Multi-workspace setup

```yaml
- uses: minitap-ai/minitest-trigger@v1
  with:
    app-slug: my-app
    tenant-id: tenant_abc123
```

## Cancelling previous runs

When you push repeatedly to the same release branch — reopening a release PR with a fix, for example — older runs that are still pending or running pile up. With `cancel-previous-runs: true` (the default), the server cancels in-flight runs that match the same source branch before starting the new one.

Cancellation is scoped:

- **Same source branch only** — matched on the PR head branch (`pull_request` events) or the branch ref for `push` / `workflow_dispatch` / `schedule` / `merge_group`.
- **Release branches only** — the branch must match one of the app’s configured release branch patterns (gitignore-style; configured per app in the dashboard).
- **CI-triggered only** — only runs started by this Action are cancelled. Dashboard, Slack, or CLI runs are untouched.

It’s a no-op for:

- Tag pushes (`refs/tags/*`).
- Branches that don’t match a configured release pattern.
- Events where the branch can’t be determined.

Opt out with `cancel-previous-runs: false`.

## How it works

1. **OIDC auth.** The Action requests a GitHub OIDC token scoped to the Minitap API. Nothing to manage on your side.
2. **Validate builds.** If you supplied any build paths, the Action checks the artifacts (simulator-only iOS, x86-64 Android).
3. **Upload builds.** Anything you supplied is uploaded to miniTest. `.app` bundles get packaged into `.ipa` first.
4. **Trigger the run.** For any enabled platform without a supplied build, Mini builds the app for the triggering commit. This includes the web lane for a repo-linked web app: Mini builds and serves the commit unless you point `web-url` at a deployed URL.
5. **Fire and forget.** The Action exits immediately. Results come back via the GitHub Check Run on the commit.

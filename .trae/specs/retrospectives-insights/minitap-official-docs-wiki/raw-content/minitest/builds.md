Every run uses a real build of your app, running on a virtual device. There are two ways to get a build to Mini, and you can mix them per app.

- You upload it

Connect your repo and Mini does the build for you. When a run needs a fresh artifact, it pulls the right commit, compiles for iOS and Android, and hands the binary to the test device.

Requires:

- The **MiniTest GitHub App** installed on the org. See [GitHub integration](https://www.minitap.ai/docs/minitest/integrations/github).
- The build env vars your app needs to compile (see below).

Monorepos are supported — point Mini at the subfolder that holds your mobile app in **App Settings → Builds**.

This is the path that powers [PR checks](https://www.minitap.ai/docs/minitest/runs/triggering-a-run): when a PR opens, Mini builds the head commit, runs the suite, and posts the verdict back on the PR.

For Expo apps, Mini supports **repack builds** — incremental rebuilds that reuse the native shell when only the JS bundle has changed. First build of the day is full; the rest are fast.

### Build env vars

Most mobile builds need at least one env var to compile cleanly: an API base URL, a Sentry DSN, a feature flag override. Mini stores them per app and injects them at build time.

Set them in **App Settings → Builds → Environment Variables**. Add, edit, or remove individual values. Changes take effect on the next build.

```text
API_URL=https://staging.example.com
SENTRY_DSN=https://abc@sentry.io/123
FEATURE_FLAG_CHECKOUT_V2=true
```

Values are encrypted at rest and only decrypted inside the build environment. They don’t appear in dashboard logs, run reports, or copies of the fix prompt.

Build the app yourself — on your laptop, on Bitrise, on Codemagic, wherever — and push the artifact with the [CLI](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude):

```shellscript
minitest build upload ./path/to/build.ipa
# or
minitest build upload ./path/to/app-debug.apk
```

The CLI prints a build ID you can target from a run. Best for one-off checks and for apps whose build pipeline lives outside GitHub.

Build env vars don’t apply here — your artifact already baked them in.

## Picking a build for a run

When you trigger a run from the dashboard, the build picker lets you:

- Use the **latest** build for the configured branch (default).
- Pick a **specific commit** or build ID.

CI-triggered runs always use the build produced by the triggering commit. There’s no manual picking when Mini is gating a PR.

## Web preview URLs

When you run a web build, Mini deploys it to a generated preview host you can open and share. The host looks like this:

```text
<preview_key>--<tenant_slug>.preview.minitap.ai
```

`<tenant_slug>` is your Workspace slug, which you’ll find in **Settings → General**. `<preview_key>` is derived per build, so each build you run gets its own host on `preview.minitap.ai`.

### The injected env var

The build automatically receives `MINITAP_PREVIEW_URL`, set to that preview URL. You don’t add this variable yourself. When you need the host inside your build config, reference the placeholder `{{MINITAP_PREVIEW_URL}}` and Mini fills it in at build time.

```text
MINITAP_PREVIEW_URL=https://<preview_key>--<tenant_slug>.preview.minitap.ai
```

### OAuth and allowed redirects

If your web app uses OAuth or any origin allow-list, preview builds need their host accepted. Add the wildcard domain below to your provider so every preview build authenticates without a per-build change:

```text
*--<tenant_slug>.preview.minitap.ai
```

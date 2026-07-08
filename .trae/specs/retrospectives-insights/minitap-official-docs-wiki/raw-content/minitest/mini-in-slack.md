Mini works as a real participant in your Slack workspace. Install it once and the things you’d normally do in the dashboard happen right in the channel where your team already works: kick off a run, triage a failed criterion, draft a new story.

Mini in Slack is a single integration, but it touches every part of the product. This page covers the install, the surfaces it adds, and the bits that only make sense in chat (channel routing, account linking, the run heartbeat).

## Installing

In the dashboard, go to **Workspace settings → Integrations → Slack** and click **Connect**. Slack walks you through the standard OAuth consent screen. Once you approve, Mini joins every public channel in the workspace automatically — paced over a few minutes to stay inside Slack’s rate limits. If you create a new public channel later, Mini joins that one too.

You don’t have to invite Mini into private channels. If you want it in one, run `/invite @mini` from inside the channel.

### Disconnecting

Same place: **Workspace settings → Integrations → Slack → Disconnect**. Mini leaves all channels, the per-app routing rules go away, and the heartbeat stops posting. Reconnecting later restores the OAuth grant; you’ll re-pick the per-app channels.

## Channel routing

Each app routes its run notifications to one Slack channel. Set it from **App Settings → Slack** in the dashboard: pick the channel, save. The bot validates the channel exists and that it can post there before saving.

When you set the channel for the first time, Mini posts a welcome message there. When you change it later, Mini posts a “moving to #new-channel” note in the old channel and starts using the new one. When you clear it, Mini posts a “going quiet” note and stops posting for that app entirely.

Mini still listens for `@mini` mentions in every channel it’s joined — channel routing only controls where the **outbound** notifications land, not where you can talk to it.

## Talking to Mini

Mini responds to `@mini` mentions in any channel it’s joined. There are no slash commands. For the full list of phrases Mini understands, see [Mini commands](https://www.minitap.ai/docs/minitest/reference/mini-commands).

### Triggering a run

Two forms:

```text
@mini run <app name> <build tag or version>
```

Mini fuzzy-matches the app name, resolves a build matching the tag, then posts an **ephemeral confirmation** with a 10-second `[Cancel] [Run now]` window before firing. If you don’t click, it auto-fires after 10 seconds.

```text
@mini run all tests
```

Opens an interactive picker: pick the app, pick the user stories (or “all”), pick the iOS / Android build, confirm. Use this when you want to narrow the run or you don’t remember the exact tag.

See [Triggering a run](https://www.minitap.ai/docs/minitest/runs/triggering-a-run) for the full picture across surfaces.

### Authoring user stories

```text
@mini create test
@mini edit test
@mini delete test
```

Each opens a multi-step flow: pick the app, pick the user story (for edit/delete), then enter the name, description, acceptance criteria. Useful in a triage thread when someone spots a missing scenario — you can capture it without leaving the conversation. See [Manually authoring user stories](https://www.minitap.ai/docs/minitest/suite/authoring) for the full mental model.

### Status

```text
@mini status
```

Mini replies with the latest verdict for the app. If your workspace has more than one app, it shows a picker first.

## The run heartbeat

Every run gets one **heartbeat message** posted in the app’s configured channel. Mini edits that single message in place as the run progresses — story completed, issue found, infra paused, retry started — so the channel doesn’t fill up. Edits are debounced to once every ten seconds to stay polite.

When the run finishes, Mini rewrites the heartbeat one last time with the final verdict. If every story passed, you get a green completion. If something failed, you get the breakdown with per-issue jump-links.

### Issue threads

When a run finds an issue, Mini replies in-thread on the heartbeat with the details: the criterion that failed, the criticality, the run report link, and an **embedded video clip** of the moment of failure. Three buttons let you triage without leaving Slack:

- **Acknowledge** — mark the issue as seen.
- **Not a bug** — opens a modal to capture why. The feedback flows back to Mini’s learning loop.
- **Resolved** — opens a modal to capture how it was fixed.

After triage, Mini swaps the action row for a status footer. A **Back to review** button is there if you change your mind.

### Cross-channel triggers

If you triggered a run from a channel other than the app’s configured one, Mini posts the heartbeat in the configured channel and drops a small permalink reply in the channel where you triggered it. That way you can follow the run from where the conversation started.

## Linking your account

The first time you trigger a run or triage an issue from Slack, Mini asks you to link your Slack identity to your Minitap account. Click the link in the ephemeral message; it opens the dashboard and finishes the link in one click. From then on, Slack actions are attributed to your Minitap user and respect your role.

Mini also matches Slack users to existing Minitap users by email at install time — if your Slack email and Minitap email match, you’re linked automatically.

## What lives where

| In Slack | In the dashboard |
| --- | --- |
| Trigger a run with `@mini run …` | Trigger a run with the **Run tests** button |
| See the heartbeat for every run | See the run report with full timeline + video |
| Triage issues with three buttons in-thread | Triage issues with full history + criticality override |
| Author/edit/delete user stories via `@mini` | Author/edit user stories with the full editor |
| `@mini status` for the latest verdict | The fleet view across every app |

Use Slack for quick, in-the-moment actions, and the dashboard when you need to dig into the detail.

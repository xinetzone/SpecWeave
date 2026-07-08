When a criterion fails, miniTest opens an **issue** in the **Issues** tab. One issue per failing criterion, deduplicated across runs so a single broken user story doesn’t fan out into N copies.

Triage works the same wherever you are — dashboard or Slack thread. State is shared across surfaces, so an action in one place updates the other instantly.

![Issues tab — left rail lists issues with criticality + age, right pane shows before/after, expected/actual, and suggestions](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/issues.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=707b37c57b46e7c11cabb74099bca15d)

Issues tab — left rail lists issues with criticality + age, right pane shows before/after, expected/actual, and suggestions

## Inside an issue

## Criterion

The exact wording that didn’t hold.

## Criticality

`Critical`, `Warning`, or `Pass`. Inferred by Mini from what it observed, and overridable per issue when the inference doesn’t match your business reality.

## Status

Where the issue is in the triage workflow below.

## Last seen

The most recent run where the issue reproduced.

## Evidence

A short clip of the failure plus a deep link to the [run report](https://www.minitap.ai/docs/minitest/runs/run-report) at the right moment.

## Fix prompt

The same paste-ready block from the run report, one click away.

## The triage actions

Every issue exposes three buttons. Pick one — that’s the whole loop.

## Acknowledge

You’ve seen it; nothing else to say yet. The issue stays open in the queue.

## Not a bug

Intentional change, flaky criterion, false positive. You’re asked for a short note explaining why it isn’t a bug. The issue stops counting against the app.

## Resolved

The underlying problem is fixed. You’re asked for feedback on what the fix was, and the next clean run closes it for real.

Every triaged issue keeps a **Back to review** button that returns it to the open queue if you change your mind.

Every note you write — on **Not a bug** or on **Resolved** — feeds [Mini’s memory](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite). Next time it sees something similar, it has your reasoning to draw on, so the same false positive doesn’t show up twice and the same fix patterns inform future suggestions.

## Overriding the criticality

Mini infers criticality from what it observed, but you know your product. If the inference is wrong, override it on the issue itself:

- A small-looking criterion that protects revenue (`Order total matches sum of items`) → bump to **Critical**.
- A serious-looking criterion that’s actually cosmetic (`A small "Beta" badge is shown`) → drop to **Warning**.

The override is sticky on that issue and reflected everywhere the issue appears.

## Where issues live

## In the dashboard

The **Issues** tab on every app. Left rail lists open issues by criticality and age, right pane shows the criterion, evidence, and the triage actions.

## In Slack

The same actions sit in the run heartbeat thread. Triage where the conversation already is — the dashboard updates the moment you click.

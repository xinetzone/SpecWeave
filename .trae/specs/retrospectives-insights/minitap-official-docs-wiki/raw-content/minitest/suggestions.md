While Mini runs your user stories, it sometimes notices things you didn’t ask it to check. Those become **suggestions**: a separate inbox from issues, optional to act on, that never blocks a release.

What ends up here is open-ended. It can be a small UI inconsistency, copy that reads oddly, or a product-level observation about how a feature actually behaves when it runs. There’s no fixed taxonomy. If Mini thinks something’s worth a second look, you’ll see it here.

## Suggestions vs. issues

## Issues

A failed acceptance criterion or a bug Mini discovered on its own. Tied to a user story, has a verdict. Triaged in [Issues](https://www.minitap.ai/docs/minitest/triage/issues).

## Suggestions

Something Mini noticed outside the acceptance criteria. No verdict, never blocking, lives in its own tab.

Both come from the same runs. Issues are the things that went wrong, whether you wrote a criterion for them or not. Suggestions are the things Mini volunteered.

## Where suggestions live

In the [dashboard](https://app.minitap.ai/), each app has a **Suggestions** tab in the sidebar. The page splits into three tabs:

## Proposal

New suggestions, waiting on your call. The sidebar badge counts these only.

## Not useful

Suggestions you’ve parked as not actionable. They stay visible here.

## Acknowledged

Read and accepted, but you’re not doing anything about it right now.

Suggestions don’t surface in run reports, PR comments, or Slack. The Suggestions tab is the only place they live.

## What’s on a suggestion card

Each card shows a short title, an optional description from Mini, and the user story it was observed in (or “No linked story” if Mini noticed it between stories). You also get an embedded video of the moment Mini noticed it, plus the platform and the last time the same observation came back on a run.

There’s no fix prompt on suggestions. They’re observations, not failures with a reproduction path.

## How a suggestion retires

When Mini stops noticing a suggestion across the stories that touch its part of the app, the suggestion goes away on its own. No action required from you.

Marking a suggestion as **Not useful** doesn’t suppress future observations. If Mini sees the same thing on a later run, the card stays in your Not useful tab with a fresh “last seen” time. It won’t pop back into Proposal, but it also won’t disappear until Mini stops noticing it.

## Fleet rollup

On the [apps page](https://app.minitap.ai/), each app shows a count of suggestions still in Proposal — a quick read on how much triage is open across your fleet. Filter and sort by it if you want to focus on the apps with the most untouched suggestions. The count never blocks anything.

![Mini, the miniTest AI QA engineer](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/meet-mini.svg?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=170c3b77d0045e1dc15f33202759a644)

Mini, the miniTest AI QA engineer

## This is Mini, your AI QA engineer.

Mini is the agent that runs your suite, starting with the first user story you write and staying with you through every release after that.

## Owning the suite

You won’t be the one keeping the suite in shape. Mini reads your codebase to draft the stories worth testing and [proposes new ones as your app grows](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite). It also learns from how you triage: every time you mark something as not-a-bug or fix an acceptance criterion, Mini puts that to use on the next run.

## Running on virtual devices

Every run happens on a virtual iOS or Android device. Mini [builds your app straight from GitHub](https://www.minitap.ai/docs/minitest/runs/builds), so you don’t have to manage artifacts, and it signs in with the [profile you’ve attached to each story](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles). For Google sign-in, it uses accounts that Minitap maintains for you.

## Surfacing what matters

When something breaks, Mini gives you enough to act on: a video of the device for the failed story, the exact criterion that failed, and [a fix prompt](https://www.minitap.ai/docs/minitest/runs/run-report#fix-prompt) you can paste into Cursor or Claude. When the device logs help explain the failure, Mini pulls those in too. Between them, you usually have what you need to reproduce the bug without guessing.

Mini also flags things you didn’t ask it to check: UX papercuts and broken edge cases it ran into while testing. Those show up as [suggestions](https://www.minitap.ai/docs/minitest/triage/suggestions), and it’s up to you whether any are worth your time.

## Where you’ll see Mini

## In the dashboard

The main surface for authoring stories, watching runs, and triaging issues.

## In Slack

Mini posts a live heartbeat for every run and lets you triage straight from a thread.

## On your pull requests

A miniTest check on every PR. Green means the suite passed on the build.

## From your IDE

Author and edit user stories from Cursor or Claude through the MCP server.

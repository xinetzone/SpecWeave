## 1\. Create your workspace

Sign up at [app.minitap.ai](https://app.minitap.ai/) and follow the onboarding: pick a workspace name, install the **MiniTest GitHub App** on the org that owns your mobile repo, then connect one app (name, icon, repo, branch).

![Onboarding — Create your app step with platforms, repo, and feature panel](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/onboarding-app.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=c5b663cb1ce719becd47c9bad62a1402)

Onboarding — Create your app step with platforms, repo, and feature panel

## 2\. Write your first user story

In the **User stories** tab, click **New story**. Describe the journey in plain English and let miniTest draft the acceptance criteria.

```text
Name: Sign in with email
Description: A returning user signs in and reaches the home screen.
```

Approve the proposed criteria. They should be things a person could verify just by looking at the screen — see [Acceptance criteria rules](https://www.minitap.ai/docs/minitest/suite/anatomy) for what holds up at runtime.

![User Stories tab — story list grouped by type on the left, editable acceptance criteria on the right](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/user-story.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=7d1025c57ec9b72ba4f095fb99133d1c)

User Stories tab — story list grouped by type on the left, editable acceptance criteria on the right

## 3\. Run it

Open your app’s **Runs** tab and click **New run**. Pick the latest build (or upload one via the [CLI](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)), select the story, and hit **Start**.

A few minutes later you get a green criterion list and a video of the agent driving your app. If something fails, the run page hands you a [fix prompt](https://www.minitap.ai/docs/minitest/runs/run-report#fix-prompt) ready for Cursor or Claude.

![Run report — per-story verdicts and per-criterion detail with video](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/run-report.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=8c8c21d5cb0448ee2d9b03370f2fa514)

Run report — per-story verdicts and per-criterion detail with video

## Next steps

- [Wire miniTest into GitHub Actions](https://www.minitap.ai/docs/minitest/runs/triggering-a-run) so every PR runs the suite.
- [Author stories from your IDE](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude) with the CLI or MCP server.
- [Attach a profile](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles) to user stories that need a signed-in user.

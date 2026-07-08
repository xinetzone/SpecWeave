A **user story** is a single journey through your app, written for a human reader. Mini uses it as both the script and the assertion list.

Most of the work below is something **[Mini handles for you](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite)**: writing criteria, splitting bundled assertions, retiring stale stories, wiring up dependencies. The two pieces that stay manual are **profiles** (Mini can’t guess your credentials) and **files** (Mini can’t generate the PDFs and photos your journeys upload). Read this page to understand the shape; don’t read it as a checklist you need to keep up to date.

## What’s in a user story

## Name

Short, action-led. `Sign in with email`. `Add item to cart`.

## Type

The category of journey — picks the icon and color, and groups stories in the list.

## Description

One sentence framing the user’s goal.

## Acceptance criteria

The observable conditions Mini will grade at runtime.

### Types

Built-in types cover most cases — `Login`, `Registration`, `Checkout`, `Onboarding`, `Search`, `Settings`, `Navigation`, `Form`, `Profile`, `Other`.

You can also create **custom types** from the type picker. A custom type carries a name, icon, color, and an optional usage prompt that gets injected into Mini’s context whenever a story of that type runs. Teams typically add ones like `Payment`, `Reservation`, or `Loyalty`.

Type is for categorization. It doesn’t auto-pick a profile or change how strictly Mini grades the story.

## Acceptance criteria

Each criterion is one observable condition, written as a short sentence in plain English. Mini plays the journey end-to-end and decides PASS or FAIL for each criterion based on what it observed.

```text
1. The home screen is displayed.
2. The "Cart" button shows a badge with "1".
3. Tapping "Checkout" opens the address form.
```

Three rules that hold up at runtime:

- **One condition per line.** If a step does two things, split it.
- **Talk like a user.** Refer to UI elements the way a user would, not by accessibility IDs.
- **Skip the typing steps.** When a profile is attached, write criteria about the post-login state (`The home screen for the signed-in user is displayed`) — Mini already has the credentials it needs to get there.

Editing a criterion versions it: existing issues stay tied to the version they were graded against, so your triage history doesn’t break when you fix the wording. Deleting a criterion auto-resolves its open issues.

## What you can attach

Beyond the four fields, three optional pieces shape how Mini runs a story.

A **profile** is a named identity Mini uses when a story needs to sign in. Attach one to the story and Mini uses it on every run.

Most apps need a handful — one for a free user, one for a pro user, one for an admin if the journey differs.

**Creating a profile**

Go to **App settings → Test Data → Profiles → New profile**. A profile has:

- **Name** — how you’ll refer to it (`Free user`, `Pro user`, `Admin`).
- **Username** — email, phone, or whatever the sign-in screen accepts.
- **Password** — encrypted at rest, never shown again, never echoed in run reports or Slack.
- **About this user** — free-form notes Mini reads as context (account state, entitlements, anything special).

You can also create profiles from your IDE with the [MCP server](https://www.minitap.ai/docs/minitest/reference/mcp-tools):

```text
Create a "Free user" profile: tester@example.com / ••••••
Attach the "Free user" profile to the "Sign in with email" story
```

**Sign in with Google**

If your app uses Google sign-in, you don’t need to provision your own test account. Minitap manages a set of shared Google accounts — they show up in the profile picker under **Shared by Minitap**. Attach one and Mini signs in with it on every run.

**One per role, not per person**

Use dedicated test users, not personal ones. Failed runs can leave accounts in odd states (half-finished checkouts, abandoned carts) you don’t want to clean up on a real user.

Files — for journeys that upload or attach content

Attach **files** when the journey needs to upload, attach, or reference user-provided content — a profile photo, a PDF receipt, a short audio clip.

Mini pre-loads the files onto the test device before the run starts. The agent then picks them up from the device’s gallery, Files app, or document picker the same way a real user would.

Supported kinds: images, documents, video, audio.

Attach files from the story detail in the dashboard, or via the MCP server when authoring from your IDE.

Dependencies — for stories that need a setup story to pass first

A story can depend on other stories. When a parent story fails, its dependents are skipped on that run rather than re-running a journey you already know is broken. There’s no point checking checkout if sign-in is down.

Set dependencies from the story detail. The full graph shows up on the dependencies view.

## Where to author

When you need to author by hand — most often for profiles and files — see [Authoring user stories](https://www.minitap.ai/docs/minitest/suite/authoring) for the three surfaces (Cursor or Claude, Slack, dashboard) and when to use each.

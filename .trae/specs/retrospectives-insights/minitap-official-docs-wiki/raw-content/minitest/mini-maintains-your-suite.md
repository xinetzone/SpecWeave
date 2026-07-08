A test suite is easy to write and hard to keep honest. Your app keeps moving, and the suite has to move with it.

**Mini’s self-maintenance** is what keeps the two in sync. Mini reads your codebase, generates the first version of the suite, and keeps it current as you ship. Add a feature and it drafts a story for it. Remove one and the story retires. Reshape a screen and it rewrites the criteria to match.

**GitHub integration is required.** Self-maintenance reads your repo to detect changes. Without the [GitHub integration](https://www.minitap.ai/docs/minitest/integrations/github) active and pointed at the right repo, Mini has nothing to watch.

## What it covers

## Microscopic drift

A renamed button, a tweaked label, a reordered form. The story stays; criteria are rewritten to match what’s on screen now.

## Macroscopic drift

A whole feature removed, a new journey shipped. Stories are added or retired.

## Connective tissue

Dependencies between stories get wired automatically. Existing profiles get linked to the journeys that need them.

## How it works

Mini watches what lands on the **default branch** (`main` in most cases). When the diff is meaningful, it updates the suite in the background: it drafts new stories, retires stale ones, and rewrites criteria to match the new UI.

You don’t trigger it, and you don’t review every change. You just keep shipping.

## What stays manual

Two things Mini can’t infer from code alone:

## New profiles

If a new journey needs a new identity (a `Pro user` to test a paywall, an `Admin` for a settings screen), you’ll be prompted to provide the credentials. Existing profiles get linked automatically.

## Device files

Photos to upload, PDFs to attach, audio to play back — anything that lives outside your repo. You attach those by hand.

Both can be done from the [dashboard, your IDE, or Slack](https://www.minitap.ai/docs/minitest/suite/authoring).

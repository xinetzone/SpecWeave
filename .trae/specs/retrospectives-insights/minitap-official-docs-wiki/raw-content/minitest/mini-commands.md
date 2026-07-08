Mini responds to `@mini` mentions in any channel it has joined. There are no slash commands. You can phrase things naturally — Mini uses an LLM to classify intent, with a keyword fallback when no API key is configured.

See [Mini in Slack](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack) for the install, channel routing, and the run heartbeat.

## Run commands

### Trigger a tagged run

```text
@mini run <app> <build or tag>
```

The build token must contain a digit (so `v1.2.3` matches but plain words don’t). Mini fuzzy-matches the app name, resolves a build matching the tag, then posts an ephemeral confirmation with a 10-second window:

- **Run now** fires immediately.
- **Cancel** aborts.
- No click? Auto-fires after 10 seconds.

Requires a [linked Slack account](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#linking-your-account).

Alternate phrasings: `kick off <app> <tag>`, `trigger <app> build <tag>`, `start <app> on tag <tag>`.

### Run all tests (interactive picker)

```text
@mini run all tests
```

Opens a multi-step picker in-thread:

1. Pick the app (skipped if Mini can guess from your message).
2. Pick user stories — all or a subset.
3. Pick the iOS and/or Android build.
4. Confirm.

Mini posts a status card and updates it in place as the run progresses.

Alternate phrasings: `run tests`, `test all`, `execute tests`.

### Check the latest verdict

```text
@mini status
```

Mini replies with the latest run verdict for the app. If the workspace has more than one app and Mini can’t guess which one you mean, it shows a dropdown first.

Alternate phrasings: `verdict`, `latest run`, `what's the latest`.

### Retry a run

```text
@mini retry run
```

Coming soon. Today, use `@mini run all tests` to start a fresh run.

## Authoring commands

### Create a user story

```text
@mini create test
```

Mini walks through each field in order:

1. Pick the app (skipped if guessable).
2. Type the story name.
3. Type the acceptance criteria (one per line).
4. Review the summary, then **Create** or **Cancel**.

The story lands in the dashboard the moment you confirm.

Alternate phrasings: `new test`, `add test`.

### Edit a user story

```text
@mini edit test
```

Same shape as create, but Mini pre-fills the current name and criteria so you only change what you need:

1. Pick the app.
2. Pick the user story from a dropdown.
3. Edit the name.
4. Edit the criteria.

Submitting the criteria saves immediately (no separate confirm step).

Alternate phrasings: `modify test`, `update test`, `change test`.

### Delete a user story

```text
@mini delete test
```

1. Pick the app.
2. Pick the user story.
3. Confirm deletion — **Delete** or **Cancel**.

Permanent. The story and its acceptance criteria are removed.

Alternate phrasings: `remove test`.

## App commands

### Create an app

```text
@mini create app
```

1. Type the app name.
2. Type a description (optional).
3. Pick GitHub repos to link (checkbox list from your GitHub App installations), or skip.
4. If you linked more than one repo, pick the source (build) repo.
5. Review the summary, then **Create** or **Cancel**.

Alternate phrasings: `new app`, `add app`.

## When Mini doesn’t understand

If Mini can’t classify your message, it replies with a short help card listing the available commands. The card is posted as a thread reply, not an ephemeral, so the rest of the channel can see it too.

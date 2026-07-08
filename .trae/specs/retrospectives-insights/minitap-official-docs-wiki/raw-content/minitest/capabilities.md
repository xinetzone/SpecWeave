The honest answer to “will this work for my app?”

## What Mini can do

## Drive any iOS or Android app

Real builds running on cloud emulators. Taps, swipes, scrolls, types, waits, dismisses system dialogs, accepts permissions, recovers from unexpected screens. If a human can navigate it on a phone, Mini can.

## Author the suite for you

Once GitHub is connected, [Mini reads your repository](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite) to draft the initial suite, add stories as features ship, retire stories whose features are gone, and rewrite criteria when screens change. Profiles and uploaded device files stay manual.

## Build the app for you

Connect GitHub and Mini builds the app on its own infrastructure — no separate CI workflow needed for test builds. Or keep your existing workflow and upload the artifact yourself. Both paths feed the same run engine. See [Providing app builds](https://www.minitap.ai/docs/minitest/runs/builds).

## Run from anywhere you already work

[CI](https://www.minitap.ai/docs/minitest/runs/triggering-a-run), the [dashboard](https://www.minitap.ai/docs/minitest/runs/triggering-a-run), [Slack](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack), the [CLI](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude), and [Cursor or Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude). A run triggered from Slack lands in the same Issues tab as a run triggered from CI.

## Produce a fix prompt, not just a bug report

When something fails, Mini delivers the criterion that didn’t hold, a video of the moment of failure, and a [fix prompt](https://www.minitap.ai/docs/minitest/runs/run-report#fix-prompt) you can paste into Cursor or Claude. Device logs come along when they help explain what happened.

## Triage from Slack or the dashboard

Acknowledge, mark as not-a-bug, mark as resolved — same actions, same state, regardless of surface. The Issues tab is the canonical view, but most triage happens in the Slack thread where the issue first surfaced.

## Override criticality per issue

Mini infers criticality at runtime, but you have the final word. Override it per issue when the default doesn’t match your business reality.

## Catch regressions you didn't write tests for

[Suggestions](https://www.minitap.ai/docs/minitest/triage/suggestions) surface things that look wrong but aren’t tied to any acceptance criterion — visual regressions, copy changes, broken navigation. They show up in the Suggestions tab in the dashboard.

## Navigate OS surfaces

Mini can open the Settings app, accept notification prompts, toggle permissions, switch to another app (like a browser for OAuth) and return via deep link, control network conditions to test under slow connectivity, and pull device logs into the run report.

## What’s on the way

## Scheduled runs

Cron-style scheduling. Today the workaround is a GitHub Action that pushes a tag on a schedule.

## Hardware features

Cloud emulators handle most flows. Support for camera, biometrics, and push notifications is coming.

## Retry from Slack

The `@mini retry` command is stubbed. Today, use the dashboard’s **Re-run** button or re-trigger from CI.

## What Mini can’t do today

Real limits in the current product. Some are temporary, some are permanent.

Hardware sensors and physical input

- **Microphone.** Mini can’t speak into the mic or pipe audio in. Voice-driven flows are out of scope.
- **Camera.** Mini can’t inject a specific image into the camera. QR scanning or document photographing needs a different approach.
- **Biometrics.** Touch ID / Face ID prompts can be dismissed, but Mini can’t enroll or authenticate a real biometric.
- **Bluetooth, NFC, motion sensors.** Anything requiring a physical device beyond touch input.

Outside the app

- **External browsers.** Mini stays in your app. If sign-in opens Safari/Chrome and bounces back via deep link, that works. Living in the browser doesn’t.
- **Email and SMS verification.** Mini can read the last code from a fixed email address on the profile (for sign-up flows). It can’t open a real inbox, click an arbitrary link, or read SMS.

Operating system surfaces

- **VPN configuration, Bluetooth pairing, and similar multi-step system flows** that go beyond your app’s scope.

Test architecture

- **Networking shims.** Mini drives the actual app talking to your actual backend. No intercepted network calls, no injected responses, no mocked services.
- **Time travel.** Mini can’t set the device clock. “What happens on January 1st” needs to be triggered on January 1st.
- **Concurrent users.** One run, one user. Multi-user scenarios need separate sequential runs.

Platforms

- **Web apps in a desktop browser.** The product targets native mobile. Mini can drive a PWA installed on a phone, but not a website opened on a laptop.
- **Tablet-specific layouts.** Mini runs on phone-sized emulators. iPad and large-screen tablet UIs aren’t covered.
- **Watch and TV apps.** Out of scope.

## What’s not on the roadmap

To keep expectations clear:

- Unit tests and integration tests of your code. Use your existing tooling.
- Load testing and performance benchmarks. Mini runs a handful of devices, not a fleet.
- Security testing and penetration testing.
- A general-purpose mobile RPA platform. Mini is built for QA, not for automating real user workflows.

If something on your wishlist isn’t listed here, ask. The roadmap moves fast.

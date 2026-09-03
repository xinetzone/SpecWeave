# Tool Usage Discipline

This file is the shared tool discipline contract for Page Sub-Agents.

## Page Sub-Agent Must Not

- Write or patch `.design`.
- Run project validators.
- Start preview servers, browser sessions, or screenshots.
- Create helper scripts.
- Generate images or post-process generated images.
- Dispatch child Sub-Agents.
- Call TodoWrite or use any status channel other than completion JSON.

## Page Sub-Agent May

- Read its selected page runtime guide.
- Read its selected lane dispatch contract.
- Read explicitly provided `supplementaryReads[]`.
- Run `apply-html-head-contract.mjs` only when the packet provides the exact command and the page is not a derived copy.
- Edit only assigned HTML/page files or fragments.

## Main Agent Owns

- Routing and lane selection.
- `.design` node registration and interaction registration.
- Image generation and image-node registration.
- Validation script execution.
- Recovery routing after blocked or failed Sub-Agent completion.

Any lane-specific exception must be declared in that lane's `INTENT_WORKFLOW.md` and dispatch contract.

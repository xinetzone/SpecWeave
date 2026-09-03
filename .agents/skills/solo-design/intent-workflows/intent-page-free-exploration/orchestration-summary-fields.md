---
lane: free_exploration
contract: orchestration-summary-fields
---

# Free Exploration Summary Fields

Write `project.resolvedLane`, `project.intentProfile`, `project.contextReadScope`, `project.cssPreflightEvidence`, `project.dispatchPreflightManifest[]`, `project.styleContinuityAnchors`, and `pages[].qualityRisks`.

Free exploration may leave restore and Library fields empty, and validators must not treat those empty fields as restore or Library failures.

For multi-page/stateful/tabbed/closed-loop requests, also write `project.pageCompletenessGate`. It records expected pages, states, interactions, and navigation affordances. Page completion reports must map these rows to `done`, `reduced-scope`, or `blocked`; unresolved missing rows cannot be silently ignored.

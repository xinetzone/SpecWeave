---
lane: free_exploration
contract: dispatch
---

# Free Exploration Dispatch Contract

Required fields: `intentProfile`, `resolvedLane=free_exploration`, `contextEnvelope`, `supplementaryReads[]`, `cssPreflightEvidence`, `fillHtmlHeadCommand`, and page slice fields from `shared-runtime/agent-dispatch-runtime/lane-dispatch-index.md`.

Forbidden fields: Library identity, restore evidence, high-fidelity visual checkpoints, and graphic layout-static assertions.

For multi-page, stateful, tabbed, or closed-loop UI requests, the packet must include a compact `pageCompletenessGate`:

```json
{
  "expectedPages": ["home", "create-task", "analytics"],
  "requiredStates": ["empty", "filled", "completed"],
  "requiredInteractions": ["tab-switch", "primary-submit", "archive-flow"],
  "requiredNavigation": ["bottom-nav", "back-or-close"],
  "missingAllowed": []
}
```

Completion JSON must report each `pageCompletenessGate` row as `done`, `reduced-scope`, or `blocked`. A missing required page/state/interaction must be repaired or explicitly reduced before final validation.

For task-driven, multi-step, or information-complete pages, the packet must include `defaultDeliverableVisibility` when user-required content could otherwise be hidden behind JS state:

```json
{
  "applies": true,
  "requiredVisibleRegions": [
    {
      "htmlSrc": "pages/example.html",
      "selector": "#required-region",
      "label": "required user-facing region",
      "source": "user requirement"
    }
  ],
  "hiddenAllowed": []
}
```

Required user-facing regions must be visible in the default delivered HTML. Do not satisfy core requirements only through `display:none`, `hidden`, `visibility:hidden`, `opacity-0`, or JS-only reveal flows. Optional modals, hover-only states, and transient overlays may be hidden only when listed in `hiddenAllowed[]` with a reason.

`supplementaryReads[]` is the only mechanism for extra read scope. Each row must include `{path, reason, ownerLane}`. Paths may reference this lane, `shared-runtime/`, `delivery-quality/`, or declared `visual-experience/` rules only; cross-lane `intent-workflows/<other-lane>/` reads are invalid.

`build-page-dispatch-manifest.mjs` owns `project.readScopeLedger[]` writes. The Main Agent supplies `supplementaryReads[]`; it must not hand-write ledger rows. The ledger is a declared-read audit, not a tool-call trace; actual misuse still requires runtime discipline and external trace/evaluation evidence.

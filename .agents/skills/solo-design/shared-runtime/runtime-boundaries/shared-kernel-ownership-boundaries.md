---
owner: shared-runtime
purpose: define which rules may live in the shared page rendering kernel
---

# Shared Kernel Ownership Boundaries

This file is the ownership contract for `shared-runtime/agent-dispatch-runtime/shared-page-rendering-kernel.md`.

## Shared Runtime Owns

- Page Sub-Agent tool discipline that is invariant across all lanes.
- HTML head management and deterministic command handoff.
- `.design` ownership boundaries: Main Agent owns canvas metadata, Sub-Agent owns HTML/page fragments only.
- Common completion JSON fields and failure response shape.
- Generic render-safety constraints that apply to every page runtime guide.

## Intent Workflow Owns

- Lane routing and lane selection.
- Library identity, token fidelity, component conformance, and UI Kit details.
- Restore evidence, visual checkpoint requirements, and source-authority rules.
- Variant, redesign, existing edit, graphic layout, and bitmap-first business semantics.
- Lane-specific delivery evidence and repair policy.

## Rule

If a rule is not true for every Page Sub-Agent lane, it must live under the owning `intent-workflows/<intent-...>/` directory or `delivery-quality/`, not in the shared kernel.

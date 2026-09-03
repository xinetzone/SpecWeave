---
lane: library_bound
runtime: page-sub-agent
---

# Library-Bound Page Runtime

Use this page runtime guide for Library-bound page generation. It extends `shared-runtime/agent-dispatch-runtime/shared-page-rendering-kernel.md` with strict Library identity, token, component, and UI Kit fidelity requirements.

Read `design-library-ingestion.md`, `design-token-fidelity-rules.md`, `component-conformance-rules.md`, and `icon-source-priority-rules.md` before writing page HTML.

Completion JSON inherits the shared kernel shape, including the full `toolDisciplineEvidence` object with `todoWriteUsed=false`, `previewStarted=false`, `validationScriptsRunBySubAgent=false`, `helperScriptsCreated=false`, and `imagesGeneratedBySubAgent=false`.

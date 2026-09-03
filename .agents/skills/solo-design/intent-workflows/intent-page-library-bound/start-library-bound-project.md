# Create Project — Library-Bound Strict Path

Use this workflow when an active Design Library exists:

- user-selected Design Library
- existing `.design.config.designLibrary`
- selected/current project Library identity
- explicit Library path or Library metadata in context

This path optimizes for fidelity to the Library. Do not apply free-explore fast-path shortcuts here.

## Non-Negotiable Scope Guard

- Do not use `start-free-exploration-project.md`.
- Do not use `start-complex-project-build.md` for Library identity, token reference, component plan, or UI Kit fidelity.
- Do not use `free-exploration-page-runtime.md`.
- Do not downgrade token, component, UI Kit, or Library identity issues to soft warnings.
- Do not fabricate token names, component structures, or component variants.

## Required Library Extraction

The Main Agent extracts Library context once, then passes compact packets to page Sub-Agents:

1. Resolve `libraryIdentity`: `name`, `id`, `version`, `scope`, `path`, `versionSource`.
2. Read Library `SKILL.md` and `README.md` for essentials and caveats.
3. Read `css.json` when present for structured token understanding.
4. Read component index (`components/_evidence/index.json` or `components/index.json`) and UI Kit plan when present.
5. Resolve each planned component to `previewFile`, `contractFile`, and optional `debugFile`.
6. Store the Library identity in both `.design.config.designLibrary` and `runtime-orchestration-summary.json.designSource.libraryIdentity`.

After extraction, rely on the distilled cache. Do not repeatedly read full Library source files.

## Library Context Cache

```json
{
  "operatingMode": "library-bound",
  "libraryIdentity": {"name": "...", "version": "...", "path": "..."},
  "brandPrefix": "...",
  "cssPath": "...",
  "actualTokenNameReference": [],
  "designDecisionSummary": "...",
  "componentIndexSummary": [],
  "uiKitSummary": "...",
  "allowedComponents": [],
  "forbiddenInventedComponents": []
}
```

## Library-Bound Page Packet

Each page Sub-Agent receives only the current page packet plus resolved component files:

```json
{
  "nodeId": "...",
  "htmlSrc": "pages/example.html",
  "brandPrefix": "...",
  "actualTokenNameReference": ["only relevant tokens"],
  "componentPlan": [
    {"slug": "button", "previewFile": "...", "contractFile": "..."}
  ],
  "uiKitPath": "...",
  "tokenFidelity": "strict"
}
```

Sub-Agent obligations stay strict:

- Read every planned `previewFile` first when present.
- Read each planned `contractFile` as semantic supplement.
- Read UI Kit when provided.
- Use only tokens from Actual Token Name Reference / Library token data.
- Use Tailwind utilities plus Library CSS variables; do not write custom component CSS.
- Report `componentsRead` and `extraComponentsRead`.

## Library-Bound Head Contract

Library-bound pages consume the Design Library head/token contract, not the free-explore fallback token model.

- Use `{libraryPath}/colors_and_type.css` as the `apply-html-head-contract.mjs` CSS source.
- Preserve Library CSS variables, component CSS inclusion mode, icon mask infrastructure, and `config.designLibrary` identity.
- Require `@theme inline` and `semantic-token-fallback` only when the generated page or Library component usage relies on Tailwind semantic classes such as `bg-card`, `text-foreground`, `border-border`, or `ring-primary`.
- Do not add project-local free-explore aliases such as generated `--color-background`, `--color-primary`, or state token scales when the Library already defines its own token namespace. If a semantic bridge is needed, derive it from Library tokens or `css.json`, not from invented fallback values.
- Do not downgrade missing Library CSS, component CSS, token reference, or icon asset issues to free-explore soft warnings.

## Validation Semantics

Library-bound validation is stricter than free-explore:

- Library identity mismatch is blocking.
- Token fabrication is blocking.
- Missing planned component reads are blocking.
- UI Kit path ignored when provided is blocking.
- Free-explore soft warning rules do not apply to Library-bound mode.

Style/aesthetic rules are fallback only where Library evidence is silent. Library always wins over aesthetics.

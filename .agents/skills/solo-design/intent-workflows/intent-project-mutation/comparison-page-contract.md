# Comparison Page Contract

Existing project mutations are add-first by default.

## Default

When a current page, selected element, xpath, source page, or existing `.design` project is available, requests to modify, improve, optimize, add, redesign, adjust, or create a state must create a new comparison page that preserves the source context.

The source page remains unchanged unless the user explicitly asks for an in-place edit.

## In-Place Edit Gate

Set `inPlaceEditAllowed: true` only when the user says the equivalent of:

- directly modify current page
- overwrite original page
- replace current page
- do not create a new page
- no comparison page

Selection alone is never an in-place signal.

## Required Summary Fields

Existing edit summary records must include:

- `sourcePageId`
- `sourceHtmlSrc`
- `derivationType: "comparison-page" | "explicit-in-place"`
- `inPlaceEditAllowed`
- `sourceProjectLaneHeritage` when the source project has Library, restore, or graphic-layout constraints

## Validation Implications

- Comparison pages must keep visible source-page anchors such as shell, navigation, main layout, and style continuity.
- Pages with `supersedesPageId` must trigger Version Convergence in `intent-workflows/intent-project-complex-build/interaction-wiring-plan.md`.
- Library-bound source heritage inherits token/reference checks; restore source heritage must not break existing restore evidence.

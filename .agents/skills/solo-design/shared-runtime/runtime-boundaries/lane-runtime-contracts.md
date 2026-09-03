# Intent Router

This file is the shared lane boundary contract for `solo-design`. Runtime routing starts in `SKILL.md` route priority, then loads exactly one lane `INTENT_WORKFLOW.md`. Maintainers use this file to audit lane boundaries, compatibility rules, density classification summaries, and graphic strategy boundaries.

## Route Order

Evaluate in this order:

1. Existing project vs new project.
2. `intentProfile.caseFamily`.
3. `intentProfile.sourceType` or `graphicStrategy` when relevant.
4. `operatingMode` based on active Design Library identity.
5. Complexity guard: free-fast vs complex.

Do not merge rules from multiple workflow branches after routing.

## Intent Family

| Family | Trigger | Route |
| --- | --- | --- |
| `restore_1to1` | Explicit "1:1", clone, replicate, pixel-perfect, exact restoration, high-fidelity reconstruction, or eval metadata `image_restore_1to1` / `url_restore_1to1` | New project: `intent-workflows/intent-page-restore-1to1/start-restore-1to1-project.md`; existing project: `intent-workflows/intent-project-mutation/edit-existing-project.md` restore path |
| `graphic_design` | Image generation itself is the deliverable, or the request asks for any bitmap-first generated visual asset: final picture, poster, banner, KV, cover, invitation, social card, PPT cover, one-pager, manual/document visual, static promo material, illustration, product/portrait image, transparent-background asset, cutout, etc. | Choose `bitmap-first` or `layout-static` |
| `library_bound` | User-selected Library, existing `.design.config.designLibrary`, Library path, `componentPlan`, or `actualTokenNameReference` | `intent-workflows/intent-page-library-bound/start-library-bound-project.md` for new project; matching edit path for existing project |
| `free_exploration` | Open-ended UI/page/app/site creation with no restoration target and no active Library | `intent-workflows/intent-page-free-exploration/start-free-exploration-project.md` when guard passes; otherwise `intent-workflows/intent-project-complex-build/start-complex-project-build.md` |

## Source Type For Restore

`restore_1to1` is one behavior family. Image and URL differ only in evidence collection.

| SourceType | Detection | Visual authority |
| --- | --- | --- |
| `image` | Screenshot/image attachment only | Provided screenshot/image |
| `url` | URL only | Browser full-page screenshot |
| `image+url` | Screenshot/image plus URL | Screenshot/image first; URL supplements copy/nav/section inventory |

## Graphic Strategy

| Strategy | Use when | Route |
| --- | --- | --- |
| `bitmap-first` | Image generation is the requested output, visual impact is primary, no editable DOM/text requirement; includes short-copy poster/banner/KV/cover/social card and any generated image asset regardless of style or format | Invoke `Skill: solo-graphic-generation`, then stop the current workflow |
| `layout-static` | PPT, one-pager, manual/document redesign, long copy, exact text hierarchy, tables, multi-section information layout | `intent-workflows/intent-project-complex-build/start-complex-project-build.md` |

Route away from bitmap-first when the user asks for UI/UX pages, DOM layout, interactions, page flow, exact editable text layers, post-generation copy correction, or any 1:1 UI/page restoration.

Before selecting `bitmap-first`, apply a text controllability check. If exact readable information is core to success — price, date, venue, activity rules, course schedule, comparison table, legal copy, brand copy, dense body copy, PPT/page copy, one-pager/manual content, or any text the user expects to edit/correct later — choose `layout-static`. Use image generation only for background, illustration, atmosphere, or hero imagery in that case.

## Existing Project Default

When an existing design project, current page, selected page, selected element, xpath, `design_page`, or current canvas focus is available, treat it as source context only by default.

- Default: create a new comparison page via `intent-workflows/intent-project-mutation/edit-existing-project.md`.
- In-place edit is allowed only when the user explicitly says overwrite / replace current / directly modify / do not create a new page.
- Selection is never an in-place signal.
- Exception: any request or workflow step that generates and keeps an image asset is a canvas asset addition, not a comparison-page edit. Invoke `Skill: solo-graphic-generation` and stop the current workflow; that skill owns size confirmation, generation, and registration of every kept image as a `type: "image"` node in the existing `.design` file. Only skip canvas placement when the user explicitly says file-only, download-only, do not add to canvas, or do not place in the design project.

## New Project Routing

| Condition | Workflow |
| --- | --- |
| `restore_1to1` | `intent-workflows/intent-page-restore-1to1/start-restore-1to1-project.md` |
| `graphic_design + bitmap-first` | Invoke `Skill: solo-graphic-generation`, then stop |
| active Design Library | `intent-workflows/intent-page-library-bound/start-library-bound-project.md` |
| no Library and free-fast guard passes | `intent-workflows/intent-page-free-exploration/start-free-exploration-project.md` |
| long PRD, multi-device, multi-style, fragment mode, complex interaction-state expansion, layout-static graphic, or generation-tree orchestration | `intent-workflows/intent-project-complex-build/start-complex-project-build.md` |

## Free-Fast Guard

Use free-fast only when all are true:

- no active Design Library
- not restore
- not image-only graphic
- not layout-static graphic
- not multi-device
- not long PRD requiring full page planning
- not a complex generation-tree task

Stateful and chart pages may still use free-fast when covered by `start-free-exploration-project.md`.

## When To Use This Contract

- routing is ambiguous after this compact router
- graphic asset details such as aspect ratio or prompt construction are needed
- density classification is needed
- Library restraint detection is needed
- pre-execution preparation details are needed
- an existing-project edge case is not covered above

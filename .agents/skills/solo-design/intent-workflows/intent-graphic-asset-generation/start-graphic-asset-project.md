# Create Image Project Workflow

## Goal

Generate bitmap-first images quickly, then register every generated image directly on the Design Canvas without HTML. This workflow is the early static graphic asset branch inside `solo-design`; it must be selected before normal HTML/page workflows when image generation itself is the deliverable or the user's intent is bitmap-first.

## Step 1 — Classify Request

Read `shared-runtime/runtime-boundaries/lane-runtime-contracts.md` and confirm this is a static bitmap-first graphic asset request. Any image-generation prompt qualifies for this workflow when the generated image itself is the deliverable and the request does not require editable DOM/text.

Stop and route away when:

- The user asks for UI/UX pages, app screens, components, interactions, or web layouts.
- The user explicitly asks for editable text layers, DOM-based text correction, or post-generation copy editing.
- The user asks for PPT pages, one-pagers, manuals/documents, long-form copy layout, tables, or other static deliverables whose success depends on exact editable typography and information hierarchy. Route these `graphic_design` requests to the `layout-static` HTML/page workflow.
- The user asks to restore a UI/page/screenshot/site 1:1. Route to `restore_1to1`; image-only output is forbidden for UI/page restoration.
- The user wants a reusable Design Library or token/component system.

If the request is actionable, continue without asking. Ask at most one question only when the subject or aspect ratio is impossible to infer.

When an existing project or current canvas is available, this workflow runs in append mode by default: generate the requested asset into that project's `assets/` directory and add a new image node to the existing `.design`. Do not create a separate file-only deliverable unless the user explicitly says not to place it on the canvas, file-only, download-only, or do not add it to the design project.

Canvas-first invariant: every successful image generation that is kept as a file or artifact must become a `type: "image"` node in `.design`. This includes final images, intermediate images that remain useful, generated alternatives, and images produced for later page use. The image's style, format, subject, or background treatment does not change this rule.

## Graphic Strategy Gate — Text Controllability

Before continuing as `bitmap-first`, write a compact gate decision in the Main Agent's working notes. If the gate resolves to `layout-static`, stop this workflow immediately and route to the HTML/page workflow selected by `SKILL.md route priority`.

```json
{
  "graphicStrategyGate": "bitmap-first | layout-static",
  "textCriticality": "low | medium | high",
  "copyDensity": "none | short | medium | dense",
  "coreInfoTypes": ["title", "price", "date", "venue", "rules", "table", "legal", "brand"],
  "bitmapFirstAllowed": true,
  "layoutStaticRequired": false,
  "graphicStrategyRoutingReason": "short evidence from user request"
}
```

Routing rules:

| Condition | Strategy |
| --- | --- |
| Short title/slogan only, visual impact is primary, user did not request editable text | `bitmap-first` |
| Image generation itself is the requested output, with no editable text requirement | `bitmap-first` |
| Price, date, venue, activity rules, course schedule, comparison table, legal copy, or brand copy must be exact | `layout-static` |
| PPT page, one-pager, manual/document redesign, dense copy, or multi-section information hierarchy | `layout-static` |
| User asks to edit/correct text after generation, preserve text layers, or control DOM typography | `layout-static` |
| Image model is only needed for background, illustration, atmosphere, or hero visual while text must remain exact | `layout-static` with image assets as support visuals |

If `textCriticality === "high"` or `copyDensity === "dense"`, `layoutStaticRequired` must be `true`. Do not rely on image generation to carry exact information that users or evaluators will read.

When rerouting to `layout-static`, the receiving HTML/page workflow must write `project.deliverableCompletenessChecklist` before dispatch. Missing required pages/assets, copy blocks, core information types, or source material coverage blocks final validation.

## Step 2 — Plan Assets

Determine:

- Project display name in the user's language.
- Graphic strategy: must be `bitmap-first`. If the strategy is `layout-static`, stop and reroute before generating images.
- `graphicStrategyGate` fields: `graphicStrategyGate`, `textCriticality`, `copyDensity`, `coreInfoTypes`, `bitmapFirstAllowed`, `layoutStaticRequired`, and `graphicStrategyRoutingReason`.
- Asset count.
- Asset title for each image.
- Filename for each image.
- Output extension for each image: preserve any user-specified supported format; otherwise use `.jpg` for ordinary raster output.
- Intended aspect ratio or nearest generation size.
- Required visible text/copy from the user request.
- Information hierarchy: primary text, secondary text, required callout/price/date, and any copy that must stay visible.
- Composition intent: focal subject, foreground/background relationship, and publish format.
- Visual direction per image.

Default asset count is 1. For variants, keep each direction distinct in composition, palette, or visual metaphor; do not generate near-duplicates.

## Step 3 — Create Project Skeleton

For a new image-only deliverable, create:

```text
<designProjectPath>/
├── <project-name>.design
└── assets/
```

Do not create `pages/`, `partials/`, `theme/`, or `colors_and_type.css`.

Initialize `.design` only after at least one image generation succeeds, so no broken or empty canvas file is produced.

For append mode in an existing project, reuse the existing project root and `assets/` directory. Do not create a second `.design` file. After generation succeeds, append new image nodes to the existing `.design` while preserving all existing page/image nodes and config.

## Step 4 — Generate Images

Generate each planned image directly into `assets/`.

Rules:

- Run independent image generations in parallel when possible.
- Retry a failed image at most once.
- If an image still fails, omit it from `.design`.
- If every image fails, stop and report that no canvas asset was produced.
- If `GenerateImage` returns success, accept the image. A small development-preview overlay added by the generation platform is expected and should not trigger prompt retries; final exported images are expected to be clean.
- If the user reports an embedded source-site mark, platform UI, creator tag, or corner label that is part of the image content, generate a replacement once with the source-mark avoidance wording below. Do not crop, resize, erase, or otherwise post-process the image.
- If the replacement still has a mark, do not keep retrying or present it as final; route to the HTML/page branch for controlled editable composition or report that clean image-only generation is blocked by the image service.
- Use the source-mark avoidance wording below in every prompt.
- Preserve all user-specified output semantics such as format, background treatment, subject completeness, crop, lighting, material, and composition. These are valid subject/composition constraints, not optional style hints.
- Do not add extra text-negative constraints; static graphic assets may need generated text.
- Do not include watermark-related negative prompt phrases such as `no watermark`, `no watermask`, `no logo`, `no signature`, or AI-generated-label wording.

Prompt template:

```text
{deliverable type}, {subject/business context}, {required visible text/copy when provided}, {audience or occasion}, {composition}, {visual style}, {color/material/lighting}, {aspect intent}, {user-specified output requirements such as format/background/crop/completeness when provided}, high quality, production-ready graphic design, clean unbranded final artwork, no platform UI, no source website frame, no gallery page, no creator tag, no corner label, only the requested poster text
```

For exact user-specified style references, preserve the user's style words directly unless they conflict with safety or output validity.

## Step 5 — Write `.design`

After successful image files exist for a new image-only deliverable, write one `.design` file with only image nodes.

Template:

```json
{
  "data": [
    {
      "id": "image-001",
      "title": "<semantic title>",
      "type": "image",
      "version": 1,
      "createdAt": 1782990000000,
      "devMetadata": {
        "imageSrc": "assets/<filename>.jpg"
      },
      "canvasData": {
        "x": 0,
        "y": 0
      }
    }
  ],
  "config": {
    "autoLayout": true,
    "deviceType": "freeSize",
    "projectName": "<project display name>"
  }
}
```

For an existing project or current canvas, append nodes instead:

1. Read the existing `.design`.
2. Find the largest `image-NNN`.
3. Append one image node per newly generated asset.
4. Preserve all existing page/image nodes, interactions, config, and existing canvas ordering.
5. Write the file once.

## Step 6 — Generation Summary File

Write `generation-summary.json` for internal continuity and skill version provenance:

```json
{
  "skillProvenance": {
    "name": "solo-design",
    "version": "2026.07.06.8",
    "version_source": "skill-release-manifest.json",
    "runtime_skill_dir": "{SKILL_DIR}",
    "recorded_at": "ISO-8601 timestamp"
  },
  "operation": "create-image-project",
  "assetCount": 1,
  "assets": [
    {
      "filename": "launch-key-visual.jpg",
      "title": "发布会主视觉",
      "deliverableType": "KV",
      "intendedAspect": "landscape 16:9",
      "status": "generated"
    }
  ]
}
```

Before writing the summary, read `{SKILL_DIR}/skill-release-manifest.json`; if unavailable, set `version: null`, `version_source: "unknown"`, and `read_status: "missing"`.

The summary file is not user-facing and is not required for canvas rendering.

## Step 7 — Validate

Run:

```bash
node {SKILL_DIR}/shared-runtime/deterministic-tooling/validate-graphic-asset-design.mjs <design-project-path>
```

Validation failure is blocking. Fix missing registrations, invalid node fields, or broken image references before finishing.

## Completion

Final response:

- Use the user's language.
- Do not include absolute paths or manual links.
- Say the static visual asset has been generated and validated.
- If some variants failed, mention only that successful directions were kept.

# Reference Material Handling (Main Agent — Pre-Execution Preparation)

> **When to read**: During Pre-Execution Preparation, when the user's message contains **any non-text reference material** — screenshots, images, URLs, ZIP files, HTML files, or other attached artifacts. This file defines how to analyze and integrate these materials into the standard workflow.
>
> **Positioning**: This file extends `SKILL.md route priority` and `shared-runtime/runtime-boundaries/lane-runtime-contracts.md` pre-execution preparation guidance. After completing reference material analysis, route to the appropriate workflow (create-project router, edit-project, etc.) as normal.
>
> **Quick routing**: style-reference-only scenarios → read "Reference Material Detection" + the relevant type-specific analysis section (Screenshot Steps 1–4 / URL Steps 1–3 / ZIP Steps 1–4) only; high-fidelity replication intent → additionally read "Screenshot High-Fidelity Replication" (SR-1~SR-5) for screenshots or "High-Fidelity Replication Mode" + Steps 2.4/2.5 for URLs.
>
> **Restore isolation**: When high-fidelity replication is active, do not read or route through the free-exploration workflow. The source material is the visual authority; free-fast creative recipes and soft-warning semantics are irrelevant and create context pollution.

---

## Reference Material Detection

During Pre-Execution Preparation, scan the user's message for reference materials:

| Material Type | Detection Signal | Priority |
|---------------|-----------------|----------|
| Screenshot / Image | Image attachment in conversation (png/jpg/webp) | Analyze first |
| URL | `http://` or `https://` link in message text | Fetch & analyze |
| ZIP / Archive | File attachment with `.zip`, `.rar`, `.7z` extension | Extract & analyze |
| HTML file | File attachment with `.html` extension | Read & analyze |
| PDF / Document | File attachment with `.pdf`, `.docx` extension | Extract text content |

**Multiple materials**: When user provides multiple reference types simultaneously (e.g., screenshot + URL + text), process them in the priority order above, then synthesize findings.

---

## Screenshot / Image Reference Analysis

### Step 1 — Determine Reference Intent

| User Expression | Intent | Downstream Behavior |
|-----------------|--------|---------------------|
| "基于这个设计..." / "在这个基础上..." / "这是现有的页面" | **Reconstruct + Extend** | Extract layout structure → create as initial page → add new pages per requirements |
| "参考这个风格" / "类似这种感觉" / "like this style" | **Style Extraction** | Extract visual parameters only → feed into brand CSS generation |
| "重新设计这个" / "redesign this" | **Full Redesign** | Extract content structure → apply new design direction |
| "复刻这个" / "replicate" / "clone" / "照着做一样的" | **High-Fidelity Replication** | Extract layout + content + style with maximum precision → see High-Fidelity Replication Mode below |
| 手绘草图/线框图（手写笔迹、白板照片、低保真 wireframe、Balsamiq 输出） | **Layout Extraction Only** | Extract spatial arrangement and content blocks only; skip Color/Typography/Density analysis → derive style separately in Step 1 |
| No explicit intent qualifier | **Default: Style Extraction** | Extract dominant visual traits → confirm intent via AskUserQuestion if ambiguous |

### Step 2 — Visual Analysis (Multi-modal)

Extract the following design elements from the screenshot:

| Dimension | What to Extract | How to Express |
|-----------|----------------|----------------|
| **Color Palette** | Dominant colors (background, primary, accent, text) | HEX values, e.g., "background: #F5F7FA, primary: #2563EB" |
| **Layout Structure** | Section arrangement, grid columns, spacing rhythm | Descriptive: "hero-split-left-image, 3-col feature grid, full-width CTA band" |
| **Typography Style** | Font weight contrast, size hierarchy, serif vs sans | "Large bold heading + light body, sans-serif, high contrast hierarchy" |
| **Component Patterns** | Card style, button shape, navigation type | "Rounded cards with shadow, pill buttons, sticky top navbar" |
| **Density & Whitespace** | Compact vs generous, content-to-space ratio | "Generous whitespace, ~40% content density" |
| **Visual Tone** | Overall feeling | Map to the selected lane's design tone taxonomy |

### Step 2a — Low-Fidelity Input Override

When Intent is "Layout Extraction Only" (hand-drawn sketch / wireframe detected):

**Detection signals** (any 1 sufficient):
- Image contains hand-drawn lines, irregular shapes, handwriting
- Image has < 3 distinct colors (typically black/white/gray only)
- Image shows placeholder text ("Lorem", "xxx", boxes with X)
- Image background is whiteboard/paper texture

**Modified extraction** — only extract these dimensions:

| Dimension | What to Extract |
|-----------|----------------|
| **Section arrangement** | Top-to-bottom section order (e.g., "nav → hero → 3-col grid → footer") |
| **Content blocks** | What each section contains (text block, image placeholder, button, form) |
| **Relative proportions** | Approximate width ratios (e.g., "sidebar 1/4, main 3/4") |
| **Hierarchy** | Which elements are emphasized (larger, circled, starred) |

**Skip entirely**:
- Color Palette extraction (would produce meaningless "black/white")
- Typography Style extraction (handwriting ≠ design intent)
- Component Patterns extraction (sketch shapes ≠ UI component specs)
- Density & Whitespace measurement (sketch spacing ≠ final spacing intent)

**Downstream**: After layout extraction, proceed to Step 1 (Style Selection) in create-project — the user has communicated *what* to build but NOT *how it looks*. Style must still be determined through normal inquiry or user context.

### Step 3 — Synthesis into Design Constraints

Convert extracted elements into actionable design constraints:

```
Extracted Design Constraints from Reference Image:
  - Color direction: {palette description}
  - Layout pattern: {structure description}
  - Typography: {font style description}
  - Component language: {shape/shadow/border description}
  - Density: {spacing/whitespace description}
  - Tone: {one of: brutally minimal | maximalist dense | luxury/refined | etc.}
```

This constraint set replaces the normal "style inquiry" step in `start-complex-project-build.md` Step 1. The user has already communicated their style preference through the reference image — do not ask again unless the image is too ambiguous to extract clear direction.

### Step 4 — Handle "Reconstruct + Extend" Intent

When the user provides a screenshot of an **existing design they want to build upon**:

1. **Reconstruct the existing page** as the first page in the new project:
   - Use extracted layout structure as the primary layout guide for that page's Sub-Agent
   - Pass the screenshot analysis as additional context: "This page must closely match the reference screenshot layout"
   - Content from the screenshot (visible text, section names) should be preserved
2. **Generate additional pages** per user requirements:
   - New pages inherit the design constraints extracted from the reference
   - Maintain visual consistency with the reconstructed first page
3. **[IMPORTANT]** Do NOT ask "should I replicate this exactly?" — the user provided it as a reference; faithful reconstruction is the default expectation

---

## Screenshot High-Fidelity Replication (when Intent = "High-Fidelity Replication" and source is screenshot)

> **When to activate**: Step 1 classifies intent as "High-Fidelity Replication" AND the reference is a screenshot/image (not a URL). This section replaces the generic Steps 2–4 above with a pixel-precise extraction flow.

### SR-1 — Pixel-Level Structural Extraction

For each visible UI region in the screenshot, extract **exact structural properties** (not just patterns):

| Extraction Target | What to Capture | Example Output |
|-------------------|----------------|----------------|
| **Container hierarchy** | Whether regions use wrapper cards or are flush/edge-to-edge; exact nesting depth | "Sidebar: flush to viewport edge, no wrapper card, no border-radius, no extra padding" |
| **Spacing values** | Exact padding/margin/gap (estimate in px from visual proportions) | "Sidebar-to-content gap: ~0px (no gap), section internal padding: ~16px" |
| **Border & radius** | Per-component border-radius, border width, border color | "Cards: radius 12px, no border, subtle shadow; Input: radius 8px, 1px border #E5E7EB" |
| **Background layers** | Solid vs gradient vs transparent per region | "Sidebar: transparent (no distinct background), main content: #FFFFFF" |
| **Width ratios** | Proportional width of each column/region | "Sidebar: ~22% viewport width, main content: ~78%" |
| **Alignment & positioning** | Flush vs centered, sticky vs scrollable, absolute vs flow | "Sidebar: fixed/sticky, full viewport height; Header: sticky top" |

**[CRITICAL] Structural precision over aesthetic generalization.** Do NOT output "rounded cards with shadow" — output "border-radius: 12px, box-shadow: 0 1px 3px rgba(0,0,0,0.1), padding: 16px 20px".

### SR-2 — Component-Level Inventory

Enumerate **every distinct UI component** visible in the screenshot with its exact rendering:

```
Component Inventory:
━━━━━━━━━━━━━━━━━━━
1. Sidebar navigation
   - Container: flush, no wrapper card, full height
   - Section headers: font-weight 600, ~13px, color #374151
   - List items: ~14px, color #6B7280, indent 16px per level
   - Active indicator: filled circle ● vs outlined circle ○
   - Bottom user badge: avatar 32px + username + "Pro" pill badge

2. Showcase cards (×3, horizontal row)
   - Layout: equal-width grid, gap ~16px
   - Card container: radius 12px, border 1px #E8E8E8, no shadow
   - Image area: top portion, aspect ratio ~16:10, radius 8px (inner)
   - Image CONTENT: [see SR-3 for embedded image description]
   - Title: bold ~15px, below image, left-aligned
   - Description: regular ~13px, color #6B7280, 1-2 lines

3. Input area
   - Container: radius 12px, border 1px #E5E7EB, padding 16px
   - Placeholder text: "描述你的设计需求，生成专业的页面原型。"
   - Bottom toolbar: icon row (具体 icons) + model selector + action buttons
   ...
━━━━━━━━━━━━━━━━━━━
```

### SR-3 — Embedded Image Content Description (for Image Generation)

When the screenshot contains images/thumbnails inside UI components (e.g., card thumbnails, hero images), extract **what is actually depicted** inside each image:

| Image Location | Describe Actual Visible Content | DO NOT |
|---------------|-------------------------------|--------|
| Card 1 thumbnail | "UI mockup showing a webpage with text 'Create an awesome...' and browser-like layout with warm brown/cream color scheme" | ❌ Generic "website design" |
| Card 2 thumbnail | "Dark UI showing a sneaker e-commerce app mockup with product cards and 'Build a sneaker e-commerce mini app' text overlay" | ❌ Generic "e-commerce product" |
| Card 3 thumbnail | "Food/vegetable photography showing fresh produce with green/earth tones, lifestyle composition" | ❌ Generic "food image" |

**Output format for image generation** (to be used in Step 2.5b):

```
Embedded Image Replication Plan:
  | Position | Visible Content Description (for prompt) | Aspect Ratio | Style Notes |
  |----------|-------------------------------------------|--------------|-------------|
  | Card 1 | UI design mockup with warm cream/brown tones, showing website layout with headline text, professional design tool screenshot aesthetic | 16:10 | Warm, muted, professional |
  | Card 2 | Dark-themed e-commerce app UI mockup showing sneaker product cards, modern mobile app aesthetic | 16:10 | Dark, modern, tech |
  | Card 3 | Fresh vegetables and produce photography, natural lighting, lifestyle food composition, green/earth tones | 16:10 | Natural, fresh, editorial |
```

**[CRITICAL]** For replication, image generation prompts must describe the **content and composition visible in the source image**, not category keywords. The goal is visual similarity to what the user sees in the original.

**[CRITICAL]** Large embedded image regions are mandatory image assets. If the reference page shows a product photo, hero media, CAD/model viewport, poster subject, thumbnail group, or illustration occupying a major visual area, add it to the image generation/reuse plan. Do not ask the page Sub-Agent to approximate that region with SVG shapes, icon glyphs, emoji, empty gray blocks, or abstract color geometry.

**[RULE]** When embedded images clearly show complex UI screenshots that cannot be faithfully regenerated (e.g., full app UIs, data dashboards, code editors), mark them as:
- `status: "approximate"` — generated image will approximate the visual tone and composition but cannot replicate exact UI elements
- Add to Sub-Agent context: "Image at {position} is an approximation of a UI screenshot. Use similar color palette and composition but exact content match is not expected."

### SR-4 — Text & Icon Precision

Extract every piece of visible text and icon with exact placement:

| Element | Extract |
|---------|---------|
| **All visible text** | Exact wording, including button labels, placeholders, headers, badges |
| **Icon identity** | Describe icon shape/meaning (e.g., "paperclip attachment icon", "smiley emoji icon", "link chain icon") — Sub-Agent must use semantically matching icons |
| **Badge/tag content** | Exact text and visual style ("BETA" badge: uppercase, small, gray background) |
| **Interactive state indicators** | Hover/active/selected visual cues visible in screenshot |

### SR-5 — Output: Screenshot Replication Constraints Document

Produce a combined document with all SR-1 through SR-4 findings:

```
Screenshot High-Fidelity Replication Constraints:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: User-provided screenshot
Quality criterion: viewer cannot distinguish output from original at a glance

Structural Blueprint:
  - [Full SR-1 output]

Component Inventory:
  - [Full SR-2 output]

Embedded Image Replication Plan:
  - [Full SR-3 output]

Text & Icon Precision:
  - [Full SR-4 output]

Visual Spec Excerpt (for Sub-Agent):
  - Colors: {exact HEX values observed}
  - Spacing: {estimated px values for key gaps}
  - Typography: {font sizes, weights, line-heights}
  - Layout: {exact section structure with container properties}
  - Effects: {shadows, borders, gradients}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

This document feeds into:
- `start-complex-project-build.md` Step 1 (replaces style inquiry entirely)
- `start-complex-project-build.md` Step 2.5 (embedded image planning drives image generation prompts for non-restore complex pages)
- Sub-Agent dispatch (Visual Spec Excerpt + Structural Blueprint replace aesthetics)

**[FORBIDDEN]** In Screenshot High-Fidelity mode:
- Extracting only high-level patterns ("rounded cards, generous whitespace") — extract pixel values
- Using generic image generation keywords when source shows specific content
- Guessing structural details — if a region is ambiguous, describe what's visible and note uncertainty
- Asking the user style questions — the screenshot IS the complete style reference

---

## URL Reference Analysis

### Step 1 — Determine URL Intent

| User Expression | Intent | Action |
|-----------------|--------|--------|
| "参考这个网站的风格" / "style like this site" | **Style Reference** | Fetch → extract visual parameters only |
| "重新设计这个网站" / "redesign this" | **Full Redesign** | Fetch → extract content + structure → redesign |
| "做一个类似 XXX 的网站" / "build something like XXX" | **Functional Reference** | Fetch → extract page structure + feature patterns |
| "复刻这个网站" / "replicate this site" / "clone this site" / "照着做" | **High-Fidelity Replication** | Fetch → extract layout + content + style with maximum precision |
| Bare URL with no qualifier | **Default: Style + Structure Reference** | Fetch → extract both; confirm intent if ambiguous |

### Step 2 — Fetch and Analyze

**Navigation method**: When visiting sub-pages of a reference URL:
- [PREFERRED] Use `browser_navigate` with the full URL directly (construct from base URL + href path)
- [FORBIDDEN] Using `browser_click` on navigation links — click targets may be dynamically rendered or outside the viewport, causing CDP "Could not compute box model" errors
- Construct sub-page URLs from the navigation href values extracted during homepage analysis

1. **Prefer browser screenshot analysis when visual fidelity matters**: For "reference this site style", "redesign this website", or any request where first-screen visual appearance matters, open the URL in a browser tool and capture desktop/mobile screenshots when available.
2. **Use WebFetch** to retrieve the URL content as a structural/content supplement.
3. **If browser or fetch succeeds**: Extract from the screenshot and/or HTML:
   - First-screen visual hierarchy and responsive differences
   - Page section structure (what sections exist, in what order)
   - Navigation patterns (how many pages, what hierarchy)
   - Color scheme (from CSS variables, inline styles, or dominant colors)
   - Component patterns (card layouts, form styles, button shapes)
   - Content structure (what types of content: text, images, videos, data)
4. **If browser and fetch both fail** (auth required, blocked, timeout):
   - Inform user: "Unable to access this URL directly. Could you provide a screenshot instead?"
   - If user has also provided text description, proceed with text-based flow
   - Do NOT retry more than once

### Step 2.4 — Replication Scope Confirmation (when user requests "all pages" / "full site")

> **Trigger**: Intent = "High-Fidelity Replication" AND user uses open-ended scope words ("所有页面", "全站", "所有子页面", "全部复刻", "all pages", "entire site", "full site").

**Flow**:

1. After completing Step 2 (Fetch & Analyze) and extracting the homepage navigation structure:
2. List all discovered independent sub-pages (in navigation order)
3. Use AskUserQuestion to confirm scope:
   - "I found N independent pages in the site navigation: [page list]."
   - Option A: Replicate all (≤ 6 pages: execute directly; > 6 pages: auto-batch)
   - Option B: Prioritize core pages (user selects subset)
   - Option C: Other (user specifies)

4. Batching strategy (when confirmed pages > 6):
   - Batch 1: Homepage + user-prioritized pages (≤ 6 pages) → generate full project
   - Batch 2: After Batch 1 completes, inform user: "Core pages are done. You can extend with remaining pages by saying 'add [page name] pages'."
   - Each batch independently executes create-project or edit-project workflow

5. **Does NOT modify the max 6 pages hard limit** (see `delivery-quality/long-requirement-intake-rules.md` §Page Cap Table) — that limit still applies in Step 2.5. This step's purpose is to let the user consciously scope or acknowledge batching.

**[FORBIDDEN]** Triggering this step when user has NOT used open-ended scope words (e.g., user provides a single URL without saying "all pages" → proceed normally without asking)

### Step 2.5 — Multi-page Discovery (when user requests "all sub-pages")

When the user requests reconstructing all sub-pages of a site:

1. **First-pass analysis** (from the homepage screenshot/HTML):
   - Extract all navigation links and their URLs
   - Classify each link by pattern:
     | Pattern | Action |
     |---------|--------|
     | Same-domain path (e.g., /enterprise, /pricing) | Candidate for navigate |
     | External URL (e.g., https://docs.xxx.com) | Skip — external site |
     | Anchor link (e.g., #features) | Skip — same page section |
     | Known SPA redirect patterns (/docs → external docs) | Skip |

2. **Navigate only confirmed independent pages** (max 6):
   - After navigating, if the page title matches the homepage title AND the URL was not in the original navigation href, classify as "redirect" and skip analysis
   - [FORBIDDEN] navigating > 6 sub-pages (diminishing returns; see `delivery-quality/long-requirement-intake-rules.md` §Page Cap Table)
   - [FORBIDDEN] navigating URLs that return to the homepage (detected by identical page title)

3. **Early termination**: If 2 consecutive navigates produce redirects, stop exploring remaining URLs and proceed with confirmed pages only.

### Step 3 — Map to Design Constraints

Same output format as Screenshot Step 3 above. Feed into brand CSS generation / style selection.

**URL as competitor reference** (e.g., "参考小红书"): Use the selected lane's competitor-reference analysis framework to extract differentiating visual DNA and avoid treating the reference as a reconstruction target.

### High-Fidelity Replication Mode

When the user's intent is classified as **High-Fidelity Replication** ("复刻", "replicate", "clone", "照着做一样的"):

**Key principle**: Layout precision and content fidelity take absolute priority over creative freedom.

| Dimension | Standard Reference Mode | High-Fidelity Replication Mode |
|-----------|------------------------|-------------------------------|
| Layout | Extract patterns → reinterpret | **Match layout grid, section order, proportions exactly** |
| Content | Use as inspiration | **Preserve all visible text and hierarchy** |
| Color | Extract palette → may adjust | **Match exact color values** |
| Typography | Extract style family | **Match exact font choices and size hierarchy** |
| Creative freedom | High | **Minimal — only deviate where source is technically impossible to replicate** |

### Unified Restore Source Model

`restore_1to1` is one behavior family. Image, URL, and image+URL are source collection variants, not separate quality standards.

| `sourceType` | When | Visual Authority | Supplementary Evidence |
| --- | --- | --- | --- |
| `image` | Screenshot/image attachment only | Provided screenshot/image | User text |
| `url` | URL only | Browser full-page screenshot | WebFetch, browser snapshot, navigation inventory |
| `image+url` | Screenshot/image plus URL | Provided screenshot/image | URL for section inventory, copy, nav, responsive hints |

When `sourceType === "image+url"`, do not let the live URL override the attached screenshot's visual layout, colors, density, or component proportions. The URL can fill missing text/structure only.

Before dispatch, write `runtime-orchestration-summary.json.project.sourceAuthorityLock`:

```json
{
  "visualAuthority": "user-screenshot | provided-image | full-page-screenshot",
  "contentSupplement": "url | browser-snapshot | extracted-copy | none",
  "browserObservationRole": "targeted-verification-only",
  "mayOverrideVisualAuthority": false,
  "lockedBeforeDispatch": true
}
```

This lock is the runtime source of truth. Later browser, URL, or WebFetch observations can supplement copy, navigation, and section inventory, but cannot override locked layout, color rhythm, density, typography hierarchy, component proportions, or fine detail.

### Restoration Contract Lite (Mandatory)

Before any Sub-Agent dispatch, produce a compact `Restoration Contract Lite`. This replaces open-ended style guidance and must be stored in `runtime-orchestration-summary.json`.

```json
{
  "sourceType": "image | url | image+url",
  "sourceAuthority": "screenshot | url-full-page-screenshot | screenshot-primary-url-supplement",
  "sourceAuthorityLock": {
    "visualAuthority": "user-screenshot | provided-image | full-page-screenshot",
    "contentSupplement": "url | browser-snapshot | extracted-copy | none",
    "browserObservationRole": "targeted-verification-only",
    "mayOverrideVisualAuthority": false,
    "lockedBeforeDispatch": true
  },
  "targetViewport": "desktop | mobile | tablet | freeSize",
  "similarityFreeze": [
    "first-screen composition",
    "primary background and color rhythm",
    "header/navigation or app chrome structure",
    "core component proportions",
    "information density"
  ],
  "contentToPreserve": ["section/order/copy summary"],
  "sourceRegionCoverage": [
    {
      "sourceRegion": "header / hero / sidebar / card grid / table / bottom nav",
      "regionGroup": "first-screen | middle-section | footer-bottom | outer-frame | device-shell | inner-screen | primary-object",
      "priority": "high | medium | low",
      "mustPreserve": "layout/color/text/component/detail to preserve",
      "targetPageSection": "where it will be rebuilt",
      "mappedStatus": "mapped | intentionally-deviated | unmapped",
      "allowedDeviation": "brand-safe copy/logo replacement, technical limit, or none"
    }
  ],
  "largeVisualRegionPlan": [
    {
      "id": "lvr-01",
      "measuredSourceFactId": "msf-focal-01",
      "regionGroup": "primary-object",
      "assetStrategy": "source-crop | provided-asset | generated-asset | explicit-deviation",
      "targetAssetPath": "assets/hero-product.png",
      "allowedDeviation": null
    }
  ],
  "allowedDeviationList": ["brand/logo/copy replacements explicitly requested by user"]
}
```

Blocking rules:

- `similarityFreeze` must contain 3-5 concrete visual anchors. Keep it compact; do not paste a long raw analysis.
- Every `high` and `medium` priority `sourceRegionCoverage` row must be `mapped` or `intentionally-deviated` with an explicit reason. Any `unmapped` high/medium row blocks dispatch.
- Every high-priority `focal-object` measured fact must map to `largeVisualRegionPlan[]`, an `assetPlanId`, or an explicit allowed deviation. If the source contains a large product image, device shell, CAD canvas, hero media, or primary object, do not replace it with abstract CSS/SVG blocks.
- The contract is a page slice input. Sub-Agents receive only the rows relevant to their target page plus shared global anchors.
- If the user asks not to copy Logo or brand copy, preserve layout, density, color rhythm, and component proportions; replace only the protected brand asset/copy.

### Restore Visual Checkpoints (Mandatory)

`similarityFreeze` is only a compact anchor summary. The enforceable restore contract is `restoreVisualCheckpoints`, stored in `runtime-orchestration-summary.json.project.restoreVisualCheckpoints` and sliced into each `RestorePagePacket`.

```json
[
  {
    "id": "vc-01",
    "priority": "high | medium | low",
    "sourceObservation": "exact observed visual fact from the source",
    "targetImplementation": "how it must be rebuilt in HTML/CSS",
    "tolerance": "none | small spacing variance | approximate icon acceptable",
    "region": "header | hero | card | table | bottom-nav | modal | sidebar | form"
  }
]
```

Rules:

- Produce 8-12 checkpoints before dispatch; at least 5 must be `high`.
- Cover viewport/canvas, first-screen structure, background/color rhythm, typography hierarchy, spacing density, core component proportions, navigation/app chrome, and at least one fine-detail component.
- Each checkpoint must be executable. Vague taste descriptions such as "premium", "overall similar", or "keep advanced feeling" are invalid.
- For `sourceType: "image"`, checkpoints come from the attached screenshot/image only; do not browse or fetch to reinterpret the visual authority.
- For `sourceType: "url"`, checkpoints come from the full-page screenshot first; WebFetch and browser snapshot can only fill copy, navigation, and section inventory.
- For `sourceType: "image+url"`, the screenshot remains visual authority and URL evidence is supplementary.

### Reference Capture Evidence (Mandatory, No Extra Tool Calls)

Before any high-fidelity Sub-Agent dispatch, record the source capture that already happened in `runtime-orchestration-summary.json.project.referenceCaptureEvidence`.

```json
{
  "sourceType": "image | url | image+url",
  "sourceAuthority": "screenshot | url-full-page-screenshot | screenshot-primary-url-supplement",
  "providedImagePath": "absolute path or null",
  "fullPageScreenshotEvidence": "absolute path, browser screenshot artifact, or tool-result reference",
  "viewportScreenshotEvidence": "absolute path, browser screenshot artifact, tool-result reference, or null",
  "browserSnapshotSections": ["header", "hero", "below-fold"],
  "webFetchStatus": "success | failed | not-needed",
  "visualSpecExcerptLength": 0,
  "captureBlockingReason": null
}
```

Efficiency rules:

- This evidence records existing capture only. Do not take an extra screenshot, run an extra browser pass, or run validation just to fill this object.
- For `sourceType: "url"`, `fullPageScreenshotEvidence` is required. It may be a file path, screenshot artifact id, or explicit tool-result reference. If it is missing, stop with `captureBlockingReason: "missing full-page screenshot for URL high-fidelity restore"` instead of continuing as a same-domain redesign.
- For `sourceType: "image"`, the provided image is sufficient visual authority; leave URL fields null.
- For `sourceType: "image+url"`, the screenshot remains visual authority. URL fetch/snapshot only fills missing copy, section inventory, and navigation.
- `visualSpecExcerptLength` must be greater than 0 before dispatch. The excerpt must be inline in the Task query; do not pass only a path to a visual-analysis file.

### [FORBIDDEN] Reference Screenshot as Final Body

In high-fidelity UI/page restoration, the final page must be rebuilt as editable HTML/CSS components. It is forbidden to make the source screenshot/reference image the dominant page body via a single `<img>` or background image and call that restoration complete.

Allowed:
- Source images as small thumbnails, product/media content, or explicitly requested image assets.
- Cropped/source assets inside specific media regions when the original page truly contains images.
- Generated or reused image assets for large media regions extracted in SR-3; the rebuilt UI stays editable, but genuine image content remains image content.

Forbidden:
- `<img src="../assets/reference-*.png">` or equivalent occupying the main UI/page body.
- A full-page screenshot used as a CSS `background-image` to simulate a restored UI.
- Replacing visible UI controls, navigation, tables, cards, chips, status bars, FABs, or form rows with a flat image.

If exact reconstruction is technically impossible, record the limitation in `allowedDeviationList`; do not hide it by embedding the screenshot.

**Replication workflow adjustments**:

1. **Full-Page Screenshot Capture** (URL targets — [MANDATORY] first step, cannot be skipped):
   - Navigate to the target URL using `browser_navigate`
   - [MANDATORY] Immediately call `browser_take_screenshot` with `fullPage: true` to capture the **entire scrollable page** as a single image
   - This screenshot is your **primary visual reference** — use your vision capabilities to analyze it in detail
   - If the page is very long, also take a viewport-only screenshot (`fullPage: false`) for the hero/first-screen at higher detail
   - **Multi-segment snapshot rule**: After the initial `browser_snapshot`, if the snapshot returns < 15 interactive refs, the page likely has below-fold content not captured. Execute `browser_scroll` (direction: "down", amount: "page") + another `browser_snapshot` to capture additional sections. Repeat until no new content is found (max 3 scrolls).
   - **Folded region detection**: Compare WebFetch text content volume (section count) vs snapshot ref count. If the ratio is > 3:1, treat as a long page and enforce multi-segment capture.
   - **[FORBIDDEN]** Proceeding to design extraction without first capturing a full-page screenshot
   - **[FORBIDDEN]** Relying solely on WebFetch text for below-fold layout — visual structure must come from screenshots/snapshots
   - Do not add extra capture passes beyond the rules above only to populate `referenceCaptureEvidence`; it is a record of this mandatory capture, not a new workflow step.
   - **Exception for `sourceType=image+url`**: if the user-provided screenshot already defines the target visual state, do not spend extra browser work trying to override it. Capture/fetch the URL only as needed for missing section inventory, copy, or navigation.

2. **Vision-Based Design Extraction** (analyze the screenshot with your multimodal capabilities):
   - From the full-page screenshot, visually extract and document:
     - **Color palette**: Background color(s), primary accent, text colors, gradient directions — describe as HEX values or precise color names
     - **Layout structure**: Section count, column arrangements, hero layout (centered/split/full-bleed), content max-width proportion, spacing rhythm between sections
     - **Typography hierarchy**: Relative heading sizes (h1 vs h2 vs body ratio), font weight contrast, serif vs sans-serif, letter-spacing characteristics
     - **Component patterns**: Card styles (rounded? shadow? border?), button shapes (pill/rounded/square), navigation style (sticky? transparent?)
     - **Visual effects**: Gradients, glassmorphism, dark/light theme, image treatments, animation hints (parallax indicators, hover states)
   - Produce a **"Visual Spec Excerpt"** (≤ 2000 chars) from your visual analysis — this is structured design intelligence, not raw code
   - This excerpt is **MANDATORY** in the Sub-Agent "Reference Material Context" for replication tasks
   - **[FORBIDDEN]** Dispatching Sub-Agent for replication without a non-empty "Visual Spec Excerpt" in Reference Material Context

3. **Content Extraction** (MANDATORY): From `browser_snapshot` (with `compact: false`) + WebFetch results, extract and preserve:
   - Section inventory (top-to-bottom order): e.g., "announcement bar → nav → hero (split layout) → 4-feature tabs → partner logos → footer"
   - Key copy per section: exact headings, subheadings, CTA labels, navigation items
   - This becomes the authoritative "Content to Preserve" field in the Design Constraints Document — Sub-Agents use it verbatim, not as inspiration
   - Cross-validate content with the screenshot to ensure nothing is missed (dynamic content, image alt text, etc.)

4. **Brand CSS generation**: Derive colors and fonts directly from your screenshot visual analysis (do not ask user for style preferences — the source IS the style). Map observed colors to CSS custom properties.

5. **Page Cap override**: For replication, cap is raised to match the actual source page count (up to 8 pages; see `delivery-quality/long-requirement-intake-rules.md` §Page Cap Table)

6. **Sub-Agent instruction**: Pass explicit directive along with the Visual Spec Excerpt: "This is a high-fidelity replication. Match the reference layout precisely. Creative deviation is forbidden unless technically necessary. The Visual Spec Excerpt contains exact design parameters extracted from the original — use them as hard constraints, not suggestions."

7. **Quality criterion**: Success = "a viewer cannot easily distinguish the output from the original at a glance"

7a. **Similarity Freeze Checklist**: Before dispatch, write 3-5 frozen anchors from the source into the contract: first-screen composition, primary background/color rhythm, header/app chrome, core component proportions, and information density. Sub-Agent completion must report how each anchor was preserved.

8. **Navigation & Wiring Extraction** (High-Fidelity only):
   - Extract ALL navigation links from header/footer of the source site
   - Classify each link as:
     | Link Type | Action |
     |-----------|--------|
     | Internal anchor (`#section`) | Register as `dom-id` for potential wiring; ensure corresponding section has matching `id` attribute |
     | Subpage (`/pricing`, `/blog`) | Register primary business-flow links in `wiringPlan`; register global nav, footer nav, secondary CTAs, breadcrumbs, and skip links in `hiddenInteractionPlan` with `hideEdge: true` |
     | External (different domain) | Keep `href` as-is, no wiring needed |
   - For each section with a visible heading, add an `id` attribute matching the nav anchor (e.g., `<section id="features">`)
   - This enables future multi-page expansion without re-analyzing the source site

---

## ZIP / File Attachment Analysis

### Step 1 — Extract and Inventory

Extract archives only through a safe, bounded process:

| Safety Rule | Requirement |
|-------------|-------------|
| Temp directory | Extract to a unique temporary directory, never into the project root directly |
| Path traversal | Reject entries with absolute paths, `..`, or paths escaping the temp directory |
| Symlinks | Reject symlink entries |
| Size limits | Enforce max file count, max total uncompressed size, and max single-file size |
| Cleanup | Delete temporary extraction files after copying approved assets into `assets/` |

Do not use `unzip -o` directly on untrusted input without these checks.

### Step 2 — Classify Contents

| File Type Found | Action |
|-----------------|--------|
| `.html` files | Read content → extract layout structure, content, and styles |
| `.css` files | Read → extract design tokens (colors, fonts, spacing) |
| Image files (`.png`, `.jpg`, `.svg`) | Copy to project `assets/` for reuse |
| `.json` / data files | Read → understand content structure |
| Other (`.psd`, `.fig`, `.sketch`) | Inform user: "Cannot process {format} directly. Please export as HTML or provide screenshots." |

### Step 3 — Determine Integration Strategy

| ZIP Content Pattern | Strategy |
|--------------------|----------|
| Complete HTML pages + CSS + images | **Import as base**: Use HTML content as initial pages; extract CSS as design constraints; copy images to assets/ |
| Single HTML page + requirements for more | **Reconstruct + Extend**: Import as first page; generate additional pages matching the style |
| Only images / design assets | **Asset reuse**: Copy to `assets/`; proceed with normal create-project flow |
| Mixed / unclear structure | **Analyze best effort**: Extract whatever design constraints are available; proceed with normal flow |

### Step 3.5 — Source Asset Inventory

When files are copied from reference material into the project, produce an inventory that the owning project workflow later merges into its asset preparation phase:

```
Source Asset Inventory:
  | Copied asset path | Original source | Semantic description | Preferred page/section | Reuse priority |
  |-------------------|-----------------|----------------------|------------------------|----------------|
  | assets/hero-photo.jpg | zip:/images/hero.jpg | Warm lifestyle hero image | Home / Hero | high |
```

Page Sub-Agents receive only the rows relevant to their page plus shared assets.

### Step 4 — HTML Import (when applicable)

When ZIP contains usable HTML files:

1. Read each HTML file, extract:
   - The `<main>` content structure (sections, components, copy)
   - CSS variables / inline styles → map to brand CSS constraints
   - Image references → check if corresponding images exist in ZIP
2. These HTML files become the **reference implementation** for the Sub-Agents:
   - Pass relevant HTML content as "Current page content" in the Sub-Agent dispatch
   - Sub-Agents adapt the content to the project's brand CSS system (Tailwind + CSS variables)
   - Original structure and content are preserved; only the styling system is adapted

---

---

## Multiple Reference Sources (N ≥ 2 same-type references)

> **When to apply**: User provides 2+ URLs or 2+ screenshots from *different sources* (different apps/sites) as references simultaneously.

### Step 1 — Classify Each Source's Role

For each reference source, determine which design dimension it primarily contributes:

| Dimension | Identification Signal | Example |
|-----------|----------------------|---------|
| **Layout** | User says "布局参考 X" / "layout like X" / source has distinctive page structure | "参考小红书的瀑布流布局" |
| **Style** | User says "风格像 X" / "颜色像 X" / source has distinctive visual treatment | "配色参考 Apple" |
| **Function** | User says "功能参考 X" / "交互像 X" / source has distinctive feature patterns | "功能参考 Notion 的 block editor" |
| **Content** | User says "内容结构像 X" / source provides reference for information architecture | "信息架构参考 Airbnb" |
| **Unspecified** | Bare URL/image with no qualifier | See resolution below |

### Step 2 — Resolve Unspecified Sources

When user provides N sources without per-source role assignment:

| Count | Resolution Strategy |
|-------|-------------------|
| 2 sources | Analyze both; extract **Visual DNA** from each; let user choose primary via AskUserQuestion: "These two references have different styles — which one should I prioritize for visual direction?" (max 1 question) |
| 3+ sources | **Synthesize** — extract top 2 distinctive traits from each source; build a composite Design Constraints document that cherry-picks the most coherent combination. Do NOT ask user to assign roles (too many questions). Instead, state chosen combination in progress update. |

### Step 3 — Composite Design Constraints

Produce a single merged Design Constraints document (same format as standard output):

```
Reference Source Synthesis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sources analyzed: {N} references
Role assignment:
  - Layout from: {source A} — {brief reason}
  - Style from: {source B} — {brief reason}
  - Function from: {source C} — {brief reason}

Merged Design Constraints:
  - Color direction: {from style source}
  - Layout patterns: {from layout source}
  - Component patterns: {from function source}
  - Typography: {from style source}
  - Tone: {synthesized}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Anti-Patterns

| Forbidden | Correct |
|-----------|---------|
| Averaging all sources' colors into a muddy blend | Pick one source's palette as dominant, use others for accent |
| Asking user 3+ questions to clarify each source's role | Analyze and synthesize; state your reasoning; proceed |
| Ignoring sources that are harder to analyze | Give each source proportional attention |

---

## Mixed Input Handling (Multiple Material Types)

When user provides multiple reference types simultaneously:

### Priority Resolution

| Combination | Resolution |
|-------------|-----------|
| Screenshot + Text requirements | Screenshot provides design direction; text provides functional/content requirements. **Text takes priority for what to build; screenshot for how it looks** |
| URL + "redesign" text | URL provides current state; text provides redesign direction. **Build per text requirements, extract baseline from URL** |
| ZIP + additional requirements | ZIP provides existing implementation; text describes additions/changes. **Reconstruct from ZIP, then apply changes per text** |
| Screenshot + URL + text | Screenshot + URL together inform design direction (cross-reference); text defines requirements. **Synthesize visual direction from both references** |

### Conflict Resolution

When reference materials conflict with explicit text requirements:

- **Text requirements always win** for functional/content decisions
- **Reference materials inform** visual/style decisions unless text explicitly overrides
- If conflict is unclear → use AskUserQuestion to clarify (max 1 question, multiple-choice)

---

## Output: Design Constraints Document

After analyzing all reference materials, the Main Agent produces a structured constraints summary that replaces or augments the normal style selection step:

```
Reference Material Analysis Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source(s): {screenshot | URL | ZIP | combination}
Intent: {reconstruct+extend | style-reference | full-redesign | functional-reference}

Design Constraints Extracted:
  - Color direction: {description + specific HEX if identifiable}
  - Layout patterns: {section structure description}
  - Typography: {font style characteristics}
  - Component language: {card/button/nav patterns}
  - Density: {whitespace/spacing feel}
  - Tone: {Design Thinking Framework tone label}

Content to Preserve (if reconstruct/extend):
  - Existing pages: {list of pages from reference}
  - Key content: {section names, copy, data to retain}

Content to Preserve (MANDATORY for High-Fidelity Replication — omit only for non-replication intents):
  - Section inventory (top-to-bottom): {e.g., "announcement bar → nav → hero (split: title left, visual right) → 4-feature tabs → partner logos → footer"}
  - Key copy per section: {e.g., "Hero title: 'Ship Faster with TRAE', subtitle: 'Understand. Execute. Deliver.', CTA: 'TRAE SOLO Web' / 'Download TRAE SOLO'"}
  - Navigation items: {e.g., "Products | SOLO Web | Download | Docs | Pricing"}

Visual Spec Excerpt (MANDATORY for High-Fidelity Replication — omit only for non-replication intents):
  - Colors: {exact HEX values for bg, text, accent, border, gradient stops}
  - Spacing: {section padding, content max-width, gap rhythm}
  - Typography: {h1-h6 sizes, weights, line-heights, font-family}
  - Layout: {section count, grid structure, hero layout type}
  - Effects: {gradients, shadows, border-radius, key animations}

Source Asset Inventory (if assets were extracted/copied):
  - {copied asset path, original source, semantic description, preferred page/section, reuse priority}

Additional Requirements (from text):
  - New pages needed: {list}
  - New features: {list}
  - Modifications: {list}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

This document is then used by:
- `start-complex-project-build.md` Step 1 (replaces style inquiry when reference provides clear direction)
- `edit-existing-project.md` Step 1 (informs current state analysis)
- Brand CSS generation (color/typography decisions feed directly)
- Sub-Agent dispatch (layout patterns passed as additional context)

---

## [FORBIDDEN] Reference Material Anti-Patterns

| Forbidden Behavior | Correct Approach |
|-------------------|-----------------|
| Ignoring reference materials and asking "what style do you want?" | Analyze materials first; only ask if analysis is inconclusive |
| Spending >3 tool calls analyzing a single screenshot | Extract key design elements in one analytical pass |
| Fetching a URL more than once | One fetch attempt; if fails, ask for screenshot |
| Attempting to render/open image files with Read tool | Images are analyzed via multi-modal vision; text-based Read will fail |
| Creating scripts to parse/process reference HTML | Read and extract manually; no ad-hoc scripts (per SKILL.md forbidden rules) |
| Asking user to re-provide materials in different format | Work with what's provided; only ask for alternatives when format is truly unprocessable |

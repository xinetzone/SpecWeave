## Step 2.5 — Image Pre-generation → Dispatch sub-tasks in parallel

> **Core Principle: Images first, pages use them later.** Before generating any HTML pages, generate all required image assets in parallel. This way page generation Sub-Agents can directly reference existing images without needing to call image generation tools themselves, greatly improving page generation speed and image consistency.

### 2.5a — Plan Image Inventory (Main Agent)

1. **Classify image necessity by role instead of page-level image quotas**:

   | Image Role | Generation Rule | Quality Priority |
   |------------|-----------------|------------------|
   | `critical-hero` | Generate or reuse for brand home, campaign landing, product showcase, and other pages whose first impression depends on a real visual | Must not be removed for speed; if generation fails, record `status: "degraded"` and use approved CSS degradation |
   | `shared-brand` | Generate at most 1-2 project-wide brand visuals that can be reused across pages | Prefer shared style consistency over unique images per page |
   | `supporting-content` | Generate only when the section's meaning depends on an image, such as product proof, venue, food, vehicle, person, or report visual | Reuse closest existing/shared image before generating |
   | `decorative` | Do not generate by default | Use typography, icons, surface, spacing, and subtle same-hue texture instead |

   **Large visual area rule**: if an image/media slot occupies a major part of the hero, first screen, product card, reference layout, or visual story, it is never `decorative`. Classify it as `critical-hero` or `supporting-content`, then generate or reuse a real image asset before page generation. Do not let page Sub-Agents replace large image regions with SVG drawings, icon glyphs, emoji, empty blocks, wireframe placeholders, or colored geometry.

2. **Apply default allocation rules**:
   - `showcase`: default 1 `critical-hero`; add at most 1 `supporting-content` only when content semantics require it
   - `information-dense`: default 0 images; generate/reuse 1 only for avatar/product/report evidence
   - `task-driven`: default 0-1 images; usually only success/confirmation/explanation screens need one
   - New generated image hard cap: `min(pageCount + 1, 6)`; copied/reused reference assets do not count toward this cap
   - Existing ZIP/URL/reference assets with matching semantics must be reused before any new generation

3. **For each planned image, specify only**:
   - Owning page
   - Role (one of: `critical-hero` | `shared-brand` | `supporting-content` | `decorative`)
   - Section type (one of: `hero` | `feature` | `detail` | `testimonial` | `background` | `product`)
   - Target filename (e.g., `hero-main.jpg`, `feature-collaboration.jpg`) — must follow Asset file naming rules in `shared-runtime/design-artifact-formats/design-project-file-format.md` (semantic kebab-case, no numeric prefixes or suffixes)
   - Initial status (`planned`, `reused`, `generated`, or `degraded`)

After planning, update `{designProjectPath}/runtime-orchestration-summary.json.assets[]` and each page's `imagePlan`.

> **Prompt construction is formulaic** — the Main Agent does not need to compose free-form creative descriptions. Each image prompt is assembled from the formula in Step 2.5b below.

### 2.5b — Dispatch image generation sub-tasks in parallel

> **Image Acceptance Rule (SSOT — applies to ALL image generation/operations in this skill; `edit-existing-project.md` and other workflows reference this section)**
>
> The `GenerateImage` platform adds a small overlay watermark in development preview. This is **expected platform behavior** — final exported images are watermark-free after export.
>
> - [CRITICAL] If GenerateImage returns success → image is **unconditionally accepted**. Do NOT inspect, re-read, re-generate, or delete it.
> - [FORBIDDEN] Reading generated image files to "verify quality" (binary files cannot be meaningfully read)
> - [FORBIDDEN] Adding "no watermark", "no logo", or "no signature" to prompts (these phrases prime watermark-related reasoning and trigger hallucinated concerns)
> - [FORBIDDEN] Re-generating, deleting, or replacing images due to perceived watermark/quality issues
> - [FORBIDDEN] Degrading to SVG/CSS-only fallback or removing imagePlan when GenerateImage succeeded
> - [FORBIDDEN] Skipping a planned large visual media asset and asking page Sub-Agents to approximate it with SVG/icon/emoji/placeholder geometry
> - [FORBIDDEN] Reasoning about whether generated images "might have watermarks" — you cannot see image content; accept tool confirmation at face value

All images to be generated are dispatched as independent sub-tasks, **in the same round in parallel** to Sub-Agents. Format for each image generation sub-task:

```
Task: Generate image asset "{section type} for {page name}"
Output: {designProjectPath}/assets/{image-filename}.jpg
Tool discipline:
  - Do not call TodoWrite. Sub-Agent completion JSON is the only status channel.
  - Do not create helper scripts.
  - Do not start preview servers or browser sessions.
  - Do not run project validation scripts.
  - Do not write or modify .design.
Input data:
  - Image generation prompt (assembled from formula):
    "{project business theme}, {page business scenario}, {section type} image, {style keywords from brand CSS (e.g., warm tones / cool minimal / earthy organic)}, high quality, professional photography, no text, no typography, no letters, no words"
  - Target file path: {designProjectPath}/assets/{image-filename}.jpg
  - Owning page: {page name}
  - Image role: {critical-hero|shared-brand|supporting-content}
  - Section type: {hero|feature|detail|testimonial|background|product}
Note:
  - Prompt follows the formula above — Main Agent fills in the bracketed variables; no free-form description needed
  - Must follow visual-experience/visual-experience-guidelines.md §5 Imagery "Image generation prompt construction rules" for lighting/composition constraints
  - Save directly after generation, [FORBIDDEN] to post-process
  - Decorative images are not generated by default; do not create image tasks with role `decorative`
```

### 2.5c — Consolidate image resource list

After all image sub-tasks complete, the Main Agent consolidates the complete image resource list in the `assets/` directory (including filename, role, semantic description, owning page, and status), updates `runtime-orchestration-summary.json`, and passes only the current page's images plus shared assets to each Sub-Agent in Step 3.

If Step 0.5 extracted reusable assets from screenshots/URLs/ZIP/HTML references, merge them into the same inventory before dispatch:

| Source | Merge Rule |
|--------|-----------|
| ZIP / HTML image assets | Copy into `assets/`, preserve source mapping, and prefer reuse before generating new images |
| Screenshot-derived visual elements | Record as visual constraints; only copy actual attached files when available |
| URL assets | Reuse only when legally and technically available as local files; otherwise treat as visual reference only |

The final per-page "Available image resources" table must include both generated images and copied reference assets, filtered to the target page plus shared assets.

### 2.5c-1 — Asset Integrity Verification (Main Agent)

After downloading/copying assets (whether from image generation, URL download, or ZIP extraction), verify each file before proceeding:

| Check | Threshold | Action on Failure |
|-------|-----------|-------------------|
| File size | < 1 KB | Likely a redirect page or error response; retry with explicit `-L` flag or alternate URL |
| File format | Cannot be identified as image by extension + magic bytes (e.g., file starts with `<!DOCTYPE` or `<html`) | Mark as `degraded`; do not pass to Sub-Agent as valid image |
| HTTP status | Non-200 after redirect following | Mark as `degraded` |

**Retry strategy**:
1. First retry: Add explicit `Accept: image/*` header and follow all redirects (`curl -L`)
2. Second retry: If original URL has signed/expiring parameters (`x-expires`, `x-signature`), skip retry — these are time-limited CDN links that may have expired
3. After 2 failed retries: Mark asset as `degraded`, record failure reason in `runtime-orchestration-summary.json.assets[]`, pass `fallbackAllowed: true` to Sub-Agent for the affected section

**[FORBIDDEN]** Passing a < 1KB file or a non-image file (HTML redirect page) as a valid image resource to Sub-Agents.

### 2.5d — Register every asset as an image node in `.design` (Main Agent, [REQUIRED])

> **[REQUIRED]** After all image sub-tasks complete (and before dispatching Step 3 page generation), the Main Agent **must append one `type: "image"` node into `.design` `data` array for every file produced under `assets/`**. Without this step, image assets only live inside HTML `<img>` tags and never surface as independent cards on the canvas, which contradicts gate invariant #6 of `SKILL.md`.

Procedure (all in a single Main Agent pass, do not delegate to Sub-Agents):

1. **List `assets/` directory**: enumerate every file produced in Step 2.5b (and any pre-existing reusable assets that were carried into Step 2.5c's resource list).
2. **Skip non-image files**: only register files with image extensions (`.jpg` / `.jpeg` / `.png` / `.gif` / `.webp` / `.svg`). Other files (e.g. fonts, data) are not registered.
3. **Exemption**: files under `assets/icons/**` (Design Library icon assets for CSS mask rendering) are NOT registered as `.design` image nodes. Only register files directly under `assets/` (not in subdirectories).
4. **Build one image node per asset** using the "Image Node" spec in `shared-runtime/design-artifact-formats/design-project-file-format.md` (the SSOT for the node field template, `image-NNN` 3-digit project-wide id counter starting from `001`, and the semantic-title rule: title is a meaningful description in the user's language, never a mechanical Title Case conversion of the filename).
5. **Append at the end of `data`**: read current `.design`, append all new image nodes after the existing nodes (theme + page skeletons from Step 2), write back once. Do not modify any existing node.
6. **Skip validation here**: HTML pages are still empty at this stage, so `validate-design-file-format.mjs` check #10 will fail. Full validation is handled by Step 4.
7. **Quick integrity check** (lightweight, not full validation): After writing `.design`, re-read it and verify:
   - `data` array length = expected total (page skeleton count from Step 2 + image node count from this step)
   - The last N entries (where N = number of images registered) all have `type: "image"`
   - No duplicate `id` values exist across all nodes

   If mismatch → re-execute step 4 (re-append image nodes from the gap). **[FORBIDDEN]** proceeding to Step 3 with a mismatched `.design` file.

> **[FORBIDDEN]**
> - Delegating image node registration to page generation Sub-Agents (breaks the "Main Agent exclusively manages `.design`" invariant).
> - Selectively registering only "primary" images and dropping decorative ones — every file in `assets/` (that matches an image extension) becomes a node.
> - Reusing the same `id` across image nodes; ID counter is project-wide unique.

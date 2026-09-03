---
lane: complex_html_page
contract: dispatch
---

# Complex Page Dispatch Contract

Required fields: current phase, current page/tree slice, `generationTree`, the current page's `dispatchPreflightManifest` row, page metadata, design source, CSS preflight evidence, and interaction tables.

Only pass the current page or current tree slice to a Page Sub-Agent. Do not pass the full `dispatchPreflightManifest[]` array into an individual page task.

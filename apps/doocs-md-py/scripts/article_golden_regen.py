"""TR-9 端到端文章渲染黄金夹具重新生成器。

用上游 doocs/md v2.1.0 的 Node 端真实模块复刻 mcp-server buildRenderedOutput：
- initRenderer / renderMarkdown / postProcessHtml（含真实 isomorphic-dompurify）
- cssVariables.ts / cssProcessor.ts / config-options.ts（原样 TS，strip-types 直跑）
- 四份真实主题 CSS（shared/configs/theme-css）

产出 tests/golden/article_expected_<name>.html，并立即与 Python build_rendered_output
做归一化 DOM 对拍。输入定义（markdown + options）见 tests/golden/article_cases.json。

前置环境同 scripts/golden_regenerate.py（WSL openKylin-3.0 + rootless podman
+ localhost/node:22-alpine，上游检出 d:/AI/.chaos/libs/md）。

普通 pytest 运行不依赖 Node——夹具文件已入库。

用法：
    python scripts/article_golden_regen.py            # 重生成 + DOM 对拍
    python scripts/article_golden_regen.py --no-check
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = APP_ROOT / "tests" / "golden"
CASES_JSON = GOLDEN_DIR / "article_cases.json"
WORK = APP_ROOT / ".temp-article"
WSL_WORK = "/mnt/d/AI/apps/doocs-md-py/.temp-article"
UPSTREAM = "/mnt/d/AI/.chaos/libs/md/packages"
UPSTREAM_CSS = "/d/AI/.chaos/libs/md/packages/shared/src/configs/theme-css"

PACKAGE_JSON = """{
  "name": "article-harness",
  "type": "module",
  "private": true,
  "dependencies": {
    "entities": "^8.1.0",
    "fflate": "0.8.3",
    "highlight.js": "11.11.1",
    "isomorphic-dompurify": "^4.5.0",
    "js-yaml": "5.4.3",
    "marked": "18.1.0"
  }
}
"""

HARNESS_TS = r"""// TR-9 对拍 harness：逐行复刻 packages/mcp-server/src/render-article.ts
// buildRenderedOutput，CSS/配置/渲染全部使用上游真实模块。
import process from 'node:process'
import fs from 'node:fs'
import { initRenderer } from './core/renderer/renderer-impl.ts'
import { renderMarkdown, postProcessHtml } from './core/utils/markdownHelpers.ts'
import { processCSS } from './core/cssProcessor.ts'
import { generateCSSVariables, generateHeadingStyles } from './core/cssVariables.ts'
import { defaultRenderOptions } from './core/config-options.ts'

// SSR 占位基线（同 TR-7.2）：fetch 立即失败、querySelector 返回 null。
;(globalThis).fetch = async () => ({ ok: false, status: 599, text: async () => '' })
;(globalThis).document = { querySelector: () => null }

const CSS_DIR = process.env.UPSTREAM_CSS
function loadCSSFile(filename) {
  return fs.readFileSync(`${CSS_DIR}/${filename}`, 'utf-8')
}
const baseCSSContent = loadCSSFile('base.css')
const themeMap = {
  default: loadCSSFile('default.css'),
  grace: loadCSSFile('grace.css'),
  simple: loadCSSFile('simple.css'),
}

function escapeStyleContent(css) {
  // 与上游 render-article.ts:43 逐字：模板串中 \\ 求值为单个反斜杠
  return css.replace(/<\/style/gi, `<\\/style`)
}

function normalizeHeadingStyles(input) {
  if (!input)
    return undefined
  const normalized = {}
  for (const [level, style] of Object.entries(input)) {
    if (style && style !== 'default')
      normalized[level] = style
  }
  return Object.keys(normalized).length > 0 ? normalized : undefined
}

const chunks = []
for await (const chunk of process.stdin) chunks.push(chunk)
const payload = JSON.parse(chunks.join(''))

const outputs = payload.cases.map((c) => {
  const input = c.options || {}
  const d = defaultRenderOptions
  const pick = (v, k) => (v ?? d[k])

  const theme = pick(input.theme, 'theme')
  const renderer = initRenderer({
    isMacCodeBlock: pick(input.isMacCodeBlock, 'isMacCodeBlock'),
    isShowLineNumber: pick(input.isShowLineNumber, 'isShowLineNumber'),
    citeStatus: pick(input.citeStatus, 'citeStatus'),
    countStatus: pick(input.countStatus, 'countStatus'),
    themeMode: pick(input.themeMode, 'themeMode'),
    legend: pick(input.legend, 'legend'),
  })

  const { html: baseHtml, readingTime } = renderMarkdown(c.markdown, renderer)
  const processedHtml = postProcessHtml(baseHtml, readingTime, renderer)
  const { yamlData } = renderer.parseFrontMatterAndContent(c.markdown)

  const headingStyles = normalizeHeadingStyles(input.headingStyles)
  const cssConfig = {
    primaryColor: pick(input.primaryColor, 'primaryColor'),
    fontFamily: pick(input.fontFamily, 'fontFamily'),
    fontSize: pick(input.fontSize, 'fontSize'),
    lineHeight: pick(input.lineHeight, 'lineHeight'),
    blockSpacing: pick(input.blockSpacing, 'blockSpacing'),
    linkColor: pick(input.linkColor, 'linkColor'),
    blockquoteBackground: pick(input.blockquoteBackground, 'blockquoteBackground'),
    isUseIndent: pick(input.isUseIndent, 'isUseIndent'),
    isUseJustify: pick(input.isUseJustify, 'isUseJustify'),
    headingStyles,
  }

  const variablesCSS = generateCSSVariables(cssConfig)
  const headingStylesCSS = generateHeadingStyles(cssConfig)
  const themeCSS = themeMap[theme] || themeMap.default
  // 与 render-article.ts:118、150 一致：先 ?? 默认主题 URL，再决定是否抓取
  const codeBlockTheme = pick(input.codeBlockTheme, 'codeBlockTheme')
  const hljsCSS = codeBlockTheme ? c.hljs : ''
  const customCSS = escapeStyleContent(input.customCSS?.trim() ?? '')

  let mergedCSS = [
    variablesCSS,
    baseCSSContent,
    themeCSS,
    headingStylesCSS,
    hljsCSS,
    customCSS,
  ].filter(Boolean).join('\n\n')
  mergedCSS = processCSS(mergedCSS)

  return { name: c.name, html: `<style>\n${mergedCSS}\n</style>\n${processedHtml}` }
})

process.stdout.write(JSON.stringify(outputs))
"""

UTILS_SHIM = "export * from './utils/basicHelpers.ts'\n"

SVG_CACHE_SHIM = """export class LRUMap<V> {
  private readonly map = new Map<string, V>()
  private readonly maxSize: number
  constructor(maxSize: number = 50) { this.maxSize = maxSize }
  get(key: string): V | undefined {
    if (!this.map.has(key)) return undefined
    const value = this.map.get(key)
    this.map.delete(key)
    this.map.set(key, value)
    return value
  }
  set(key: string, value: V): void {
    if (this.map.has(key)) this.map.delete(key)
    else if (this.map.size >= this.maxSize) {
      const oldest = this.map.keys().next().value
      if (oldest !== undefined) this.map.delete(oldest)
    }
    this.map.set(key, value)
  }
  get size(): number { return this.map.size }
  clear(): void { this.map.clear() }
}
export function createSVGCache(maxSize: number = 50): LRUMap<string> {
  return new LRUMap<string>(maxSize)
}
"""

# 仅保留 plaintext 语法（对齐 Python T5 契约：REGISTERED_LANGUAGES={plaintext}，
# 其余语言 pending + plaintext 转义，语法着色登记 contract-differences）。
LANGUAGES_PRUNE = r"""
sed -i -E "/from 'highlight\.js\/lib\/languages\/(bash|css|javascript|json|markdown|python|shell|typescript|xml)'/d" "$W/core/utils/languages.ts"
sed -i -E "/^  (bash|css|javascript|json|markdown|python|shell|typescript|xml),$/d" "$W/core/utils/languages.ts"
"""

SETUP_BASH = """set -euo pipefail
W=%(w)s
U=%(u)s
rm -rf "$W/core"
mkdir -p "$W/core/extensions" "$W/core/utils" "$W/core/types" "$W/core/renderer"
cd "$U/core/src"
for f in extensions/*.ts; do
  case "$f" in
    *".test.ts") ;;
    *) cp "$f" "$W/core/extensions/" ;;
  esac
done
for f in basicHelpers scan asyncDiagramState mathDetection mathjax svgCache front-matter markdownHelpers languages; do
  cp "utils/$f.ts" "$W/core/utils/"
done
cp types/*.ts "$W/core/types/"
cp renderer/renderer-impl.ts "$W/core/renderer/renderer-impl.ts"
cp theme/cssVariables.ts "$W/core/cssVariables.ts"
cp theme/cssProcessor.ts "$W/core/cssProcessor.ts"
cp "$U/mcp-server/src/config-options.ts" "$W/core/config-options.ts"
cp "$U/shared/src/utils/readingTime.ts" "$W/core/reading-time.ts"
cp "$W/_shims/utils.ts" "$W/core/utils.ts"
cp "$W/_shims/svgCache.ts" "$W/core/utils/svgCache.ts"
%(prune)s
cd "$W/core"
# 真实 highlight.js（core + plaintext 语法），不替换 hljs；'../utils/languages'
# 保持原样，由下一轮 sed 补 .ts 指向真实 languages.ts
sed -i "s#@md/shared/utils/readingTime#../reading-time.ts#; s#from '../extensions'#from '../extensions/index'#" renderer/renderer-impl.ts
find . -name '*.ts' -print0 | xargs -0 sed -i -E "s#from '(\\.\\.?/[^']+)'#from '\\1.ts'#g"
find . -name '*.ts' -print0 | xargs -0 sed -i 's#\\.ts\\.ts#.ts#g'
podman run --rm --network slirp4netns -e UPSTREAM_CSS=%(css)s -v /mnt/d:/d -v "$W:/w" -w /w localhost/node:22-alpine \
  sh -c "[ -d node_modules/highlight.js ] || npm install --no-audit --no-fund --silent; node --experimental-strip-types harness-article.ts < article_payload.json > article_js.json"
""" % {"w": WSL_WORK, "u": UPSTREAM, "css": UPSTREAM_CSS, "prune": LANGUAGES_PRUNE}

CAMEL_TO_SNAKE = {
    "theme": "theme",
    "primaryColor": "primary_color",
    "fontFamily": "font_family",
    "fontSize": "font_size",
    "lineHeight": "line_height",
    "blockSpacing": "block_spacing",
    "linkColor": "link_color",
    "blockquoteBackground": "blockquote_background",
    "legend": "legend",
    "isMacCodeBlock": "is_mac_code_block",
    "isShowLineNumber": "is_show_line_number",
    "citeStatus": "cite_status",
    "countStatus": "count_status",
    "themeMode": "theme_mode",
    "isUseIndent": "is_use_indent",
    "isUseJustify": "is_use_justify",
    "headingStyles": "heading_styles",
    "codeBlockTheme": "code_block_theme",
    "customCSS": "custom_css",
}


def run_wsl_bash(script: str) -> subprocess.CompletedProcess[str]:
    wsl = Path(os.environ["WINDIR"]) / "System32" / "wsl.exe"
    return subprocess.run(
        [str(wsl), "-d", "openKylin-3.0", "-e", "bash", "-lc", script],
        text=True,
        capture_output=True,
        timeout=900,
    )


def load_cases() -> dict:
    spec = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    for case in spec["cases"]:
        if "markdown" not in case:
            case["markdown"] = (GOLDEN_DIR / case["file"]).read_text(encoding="utf-8")
    return spec


def python_render(case: dict, hljs_fixture: str) -> str:
    sys.path.insert(0, str(APP_ROOT / "src"))
    from doocs_md_py.render.article import (
        RenderArticleInput,
        build_rendered_output,
    )

    options = {
        CAMEL_TO_SNAKE[key]: value
        for key, value in case.get("options", {}).items()
    }
    result = build_rendered_output(
        RenderArticleInput(markdown=case["markdown"], **options),
        code_css_fetcher=lambda url: hljs_fixture,
    )
    return result.html


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-check", action="store_true")
    args = parser.parse_args()

    spec = load_cases()

    shim_dir = WORK / "_shims"
    shim_dir.mkdir(parents=True, exist_ok=True)
    (WORK / "package.json").write_text(PACKAGE_JSON, encoding="utf-8")
    (WORK / "harness-article.ts").write_text(HARNESS_TS, encoding="utf-8")
    (shim_dir / "utils.ts").write_text(UTILS_SHIM, encoding="utf-8")
    (shim_dir / "svgCache.ts").write_text(SVG_CACHE_SHIM, encoding="utf-8")
    (WORK / "article_payload.json").write_text(
        json.dumps(
            {"cases": [{"name": c["name"], "markdown": c["markdown"],
                        "options": c.get("options", {}), "hljs": spec["hljs_fixture"]}
                       for c in spec["cases"]]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    proc = run_wsl_bash(SETUP_BASH)
    if proc.returncode != 0:
        print("NODE HARNESS FAILED")
        print(proc.stdout[-4000:])
        print(proc.stderr[-4000:])
        return 1

    outputs = {item["name"]: item["html"]
               for item in json.loads((WORK / "article_js.json").read_text(encoding="utf-8"))}

    for case in spec["cases"]:
        expected = outputs[case["name"]]
        target = GOLDEN_DIR / f"article_expected_{case['name']}.html"
        target.write_text(expected, encoding="utf-8")
        print(f"regenerated: {target.name} ({len(expected)} chars)")

    if args.no_check:
        return 0

    sys.path.insert(0, str(APP_ROOT / "src"))
    from doocs_md_py.render.domcompare import dom_equal

    failed = False
    for case in spec["cases"]:
        expected = (GOLDEN_DIR / f"article_expected_{case['name']}.html").read_text(
            encoding="utf-8"
        )
        actual = python_render(case, spec["hljs_fixture"])
        ok, message = dom_equal(expected, actual)
        print(f"{case['name']}: {'DOM EQUAL' if ok else 'DOM DIFFER'}")
        if not ok:
            failed = True
            print(message[:4000])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

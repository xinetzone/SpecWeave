"""TR-7.2 黄金夹具重新生成器。

用上游 doocs/md v2.1.0 的 Node 端 initRenderer 渲染 tests/golden/complex_doc.md，
把输出锁定为 tests/golden/complex_doc.expected.html，并立即与 Python 实现做
归一化 DOM 对拍。

前置环境（仅重新生成时需要）：
- WSL 发行版 openKylin-3.0 + rootless podman；
- 镜像 localhost/node:22-alpine（Node 22，--experimental-strip-types）；
- 上游源码检出在 d:/AI/.chaos/libs/md（HEAD 见规格 contract-differences）。

普通 pytest 运行不依赖本脚本与 Node 环境——夹具文件已入库。

用法：
    python scripts/golden_regenerate.py            # 重生成 + DOM 对拍
    python scripts/golden_regenerate.py --no-check # 仅重生成
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_MD = APP_ROOT / "tests" / "golden" / "complex_doc.md"
FIXTURE_HTML = APP_ROOT / "tests" / "golden" / "complex_doc.expected.html"
WORK = APP_ROOT / ".temp-node-comp"
WSL_MNT = "/mnt/d/AI/apps/doocs-md-py/.temp-node-comp"
UPSTREAM = "/mnt/d/AI/.chaos/libs/md/packages"

PACKAGE_JSON = """{
  "name": "comp-harness",
  "type": "module",
  "private": true,
  "dependencies": {
    "entities": "^8.1.0",
    "fflate": "0.8.3",
    "js-yaml": "5.4.3",
    "marked": "18.1.0"
  }
}
"""

HARNESS_TS = """// TR-7.2 对拍 harness：直接使用上游 initRenderer（完整 renderer + 全扩展，SSR 占位路径）。
import process from 'node:process'
import { initRenderer } from './core/renderer/renderer-impl.ts'

const renderer = initRenderer({})

// SSR 基线：PlantUML inlineSvg 路径会 fire-and-forget fetch + document 占位替换。
// 强制其占位路径：fetch 立即失败、querySelector 返回 null。
;(globalThis).fetch = async () => ({
  ok: false,
  status: 599,
  text: async () => '',
})
;(globalThis).document = {
  querySelector: () => null,
}

const chunks = []
for await (const chunk of process.stdin) chunks.push(chunk)
const cases = JSON.parse(chunks.join(''))
const outputs = cases.map((md) => {
  const html = renderer.renderMarkdownToHtml(md)
  return html.replace(/<br\\s*\\/?>\\s*(?=<span class="katex-inline)/gi, '')
})
process.stdout.write(JSON.stringify(outputs))
"""

UTILS_SHIM = "export * from './utils/basicHelpers.ts'\n"

SVG_CACHE_SHIM = """// strip-types 不支持 TS 参数属性，手写等价 LRU shim。
export class LRUMap<V> {
  private readonly map = new Map<string, V>()
  private readonly maxSize: number

  constructor(maxSize: number = 50) {
    if (maxSize < 1) {
      throw new RangeError(`LRUMap maxSize must be >= 1, got ${maxSize}`)
    }
    this.maxSize = maxSize
  }

  get(key: string): V | undefined {
    if (!this.map.has(key)) {
      return undefined
    }
    const value = this.map.get(key)
    if (value === undefined) {
      return undefined
    }
    this.map.delete(key)
    this.map.set(key, value)
    return value
  }

  set(key: string, value: V): void {
    if (this.map.has(key)) {
      this.map.delete(key)
    }
    else if (this.map.size >= this.maxSize) {
      const oldestKey = this.map.keys().next().value
      if (oldestKey !== undefined) {
        this.map.delete(oldestKey)
      }
    }
    this.map.set(key, value)
  }

  get size(): number {
    return this.map.size
  }

  clear(): void {
    this.map.clear()
  }
}

export function createSVGCache(maxSize: number = 50): LRUMap<string> {
  return new LRUMap<string>(maxSize)
}
"""

LANGUAGES_SHIM = """// 综合文档不含代码围栏，高亮子系统仅需模块可加载。
export const COMMON_LANGUAGES = {}
export function highlightAndFormatCode() {
  return ''
}
"""

HLJS_SHIM = """const hljs = {
  registerLanguage() {},
}
export default hljs
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
for f in basicHelpers scan asyncDiagramState mathDetection mathjax svgCache front-matter; do
  cp "utils/$f.ts" "$W/core/utils/"
done
cp types/*.ts "$W/core/types/"
cp renderer/renderer-impl.ts "$W/core/renderer/renderer-impl.ts"
cp "$U/shared/src/utils/readingTime.ts" "$W/core/reading-time.ts"
cp "$W/_shims/utils.ts" "$W/core/utils.ts"
cp "$W/_shims/svgCache.ts" "$W/core/utils/svgCache.ts"
cp "$W/_shims/languages.ts" "$W/core/languages-shim.ts"
cp "$W/_shims/hljs.ts" "$W/core/hljs-shim.ts"
cd "$W/core"
sed -i "s#@md/shared/utils/readingTime#../reading-time.ts#; s#highlight.js/lib/core#../hljs-shim.ts#; s#'../utils/languages'#'../languages-shim.ts'#; s#from '../extensions'#from '../extensions/index'#" renderer/renderer-impl.ts
find . -name '*.ts' -print0 | xargs -0 sed -i -E "s#from '(\\.\\.?/[^']+)'#from '\\1.ts'#g"
find . -name '*.ts' -print0 | xargs -0 sed -i 's#\\.ts\\.ts#.ts#g'
podman run --rm --network slirp4netns -v "$W:/w" -w /w localhost/node:22-alpine \
  sh -c "[ -d node_modules/entities ] || npm install --no-audit --no-fund --silent; node --experimental-strip-types harness-golden.ts < golden_cases.json > golden_js.json"
""" % {"w": WSL_MNT, "u": UPSTREAM}


def run_wsl_bash(script: str) -> subprocess.CompletedProcess[str]:
    wsl = Path(os.environ["WINDIR"]) / "System32" / "wsl.exe"
    return subprocess.run(
        [str(wsl), "-d", "openKylin-3.0", "-e", "bash", "-lc", script],
        text=True, capture_output=True, timeout=600,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-check", action="store_true", help="仅重生成，不做 DOM 对拍")
    args = parser.parse_args()

    if not FIXTURE_MD.exists():
        print(f"missing fixture: {FIXTURE_MD}", file=sys.stderr)
        return 2

    shim_dir = WORK / "_shims"
    shim_dir.mkdir(parents=True, exist_ok=True)
    (WORK / "package.json").write_text(PACKAGE_JSON, encoding="utf-8")
    (WORK / "harness-golden.ts").write_text(HARNESS_TS, encoding="utf-8")
    (shim_dir / "utils.ts").write_text(UTILS_SHIM, encoding="utf-8")
    (shim_dir / "svgCache.ts").write_text(SVG_CACHE_SHIM, encoding="utf-8")
    (shim_dir / "languages.ts").write_text(LANGUAGES_SHIM, encoding="utf-8")
    (shim_dir / "hljs.ts").write_text(HLJS_SHIM, encoding="utf-8")

    doc = FIXTURE_MD.read_text(encoding="utf-8")
    (WORK / "golden_cases.json").write_text(
        json.dumps([doc], ensure_ascii=False), encoding="utf-8"
    )

    proc = run_wsl_bash(SETUP_BASH)
    if proc.returncode != 0:
        print("NODE HARNESS FAILED")
        print(proc.stdout[-4000:])
        print(proc.stderr[-4000:])
        return 1

    outputs = json.loads((WORK / "golden_js.json").read_text(encoding="utf-8"))
    FIXTURE_HTML.write_text(outputs[0], encoding="utf-8")
    print(f"regenerated: {FIXTURE_HTML} ({len(outputs[0])} chars)")

    if args.no_check:
        return 0

    sys.path.insert(0, str(APP_ROOT / "src"))
    from doocs_md_py.render import init_renderer
    from doocs_md_py.render.domcompare import dom_equal
    from doocs_md_py.render.extensions.katex import strip_break_before_inline_katex

    actual = strip_break_before_inline_katex(
        init_renderer().render_markdown_to_html(doc)
    )
    ok, message = dom_equal(outputs[0], actual)
    if ok:
        print("DOM EQUAL")
        return 0
    print("DOM DIFFER")
    print(message)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

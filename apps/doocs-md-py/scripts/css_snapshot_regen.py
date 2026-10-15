"""TR-9 CSS 字面黄金快照重新生成器。

直接用 Node 22 --experimental-strip-types 执行上游无依赖纯 TS 模块
cssVariables.ts / cssProcessor.ts，把一组固定输入的输出固化到
tests/golden/css_snapshot.json，供 tests/render/test_css.py 对拍。

上游两模块仅含 type-only import（strip-types 直接擦除），无需 npm 安装。

用法：
    python scripts/css_snapshot_regen.py
"""

import json
import os
import subprocess
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
TARGET = APP_ROOT / "tests" / "golden" / "css_snapshot.json"
WORK = APP_ROOT / ".temp-css"
WSL_WORK = "/mnt/d/AI/apps/doocs-md-py/.temp-css"
# 容器内 D 盘挂载于 /d（非 /mnt/d）
CONTAINER_OUT = "/d/AI/apps/doocs-md-py/tests/golden/css_snapshot.json"

# 与 .temp 生成器逐字（上游 HEAD 1bdad48）
GEN_MJS = r"""// TR-9 CSS golden 快照：直跑上游 cssVariables.ts/cssProcessor.ts
import { writeFileSync, readFileSync } from "node:fs"
import {
  generateCSSVariables,
  generateHeadingStyles,
} from "/d/AI/.chaos/libs/md/packages/core/src/theme/cssVariables.ts"
import { processCSS } from "/d/AI/.chaos/libs/md/packages/core/src/theme/cssProcessor.ts"

const variableCases = [
  { name: "defaults", input: {
      primaryColor: "#0F4C81", fontFamily: "Sans, serif", fontSize: "16px",
      lineHeight: "1.75", blockSpacing: "1", linkColor: "#576b95",
      blockquoteBackground: "default", isUseIndent: false, isUseJustify: false } },
  { name: "fallbacks-when-empty", input: {
      primaryColor: "#333", fontFamily: "Mono", fontSize: "14px",
      lineHeight: undefined, blockSpacing: undefined, linkColor: undefined,
      blockquoteBackground: undefined, isUseIndent: undefined, isUseJustify: undefined } },
  { name: "custom-blockquote-indent-justify", input: {
      primaryColor: "#abc", fontFamily: "Serif", fontSize: "17px",
      lineHeight: "2", blockSpacing: "1.2", linkColor: "inherit",
      blockquoteBackground: "#f5f5f5", isUseIndent: true, isUseJustify: true } },
  { name: "empty-blockquote-bg", input: {
      primaryColor: "#000", fontFamily: "X", fontSize: "16px",
      blockquoteBackground: "" } },
]

const headingCases = [
  { name: "presets", input: { h1: "color-only", h2: "border-bottom", h3: "border-left" } },
  { name: "default-and-custom-skipped", input: { h1: "default", h2: "custom", h3: "color-only" } },
  { name: "empty-string-skipped", input: { h1: "", h4: "border-left" } },
  { name: "all-default", input: { h1: "default", h2: "default" } },
  { name: "undefined", input: undefined },
]

const defaultCss = readFileSync(
  "/d/AI/.chaos/libs/md/packages/shared/src/configs/theme-css/default.css", "utf-8")

const processCases = [
  { name: "var-basic", input: ":root{--a:red}x{color:var(--a)}" },
  { name: "var-fallback-used", input: "x{color:var(--missing, blue)}" },
  { name: "var-fallback-nested-parens", input: "x{color:var(--miss, rgb(1, 2, 3))}" },
  { name: "var-resolved-wins-over-fallback", input: ":root{--a:red}x{color:var(--a, blue)}" },
  { name: "var-nested-resolution", input: ":root{--a:var(--b);--b:green}x{color:var(--a)}" },
  { name: "var-unresolved-kept", input: "x{color:var(--never-defined)}" },
  { name: "calc-add", input: "x{width:calc(10px + 2px)}" },
  { name: "calc-sub", input: "x{width:calc(10px - 3px)}" },
  { name: "calc-mul-unit", input: "x{width:calc(2 * 4px)}" },
  { name: "calc-div-upstream-nan", input: "x{width:calc(8px / 2)}" },
  { name: "calc-rounding", input: "x{width:calc(1px / 3)}" },
  { name: "calc-unitless-add", input: "x{width:calc(1 + 2)}" },
  { name: "calc-unmatched-kept", input: "x{width:calc(10px + 2em)}" },
  { name: "default-theme-full", input: defaultCss },
]

const snapshot = {
  generated_by: "Node 22 + upstream cssVariables.ts/cssProcessor.ts @ 1bdad48",
  variables: variableCases.map((c) => ({
    name: c.name, input: c.input, expected: generateCSSVariables(c.input) })),
  headings: headingCases.map((c) => ({
    name: c.name, input: c.input,
    expected: generateHeadingStyles({ headingStyles: c.input }) })),
  process: processCases.map((c) => ({
    name: c.name, input: c.input, expected: processCSS(c.input) })),
}

writeFileSync(process.env.OUT, JSON.stringify(snapshot, null, 2), "utf-8")
"""


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "gen-snapshot.mjs").write_text(GEN_MJS, encoding="utf-8")
    wsl = Path(os.environ["WINDIR"]) / "System32" / "wsl.exe"
    proc = subprocess.run(
        [
            str(wsl), "-d", "openKylin-3.0", "-e", "bash", "-lc",
            f"podman run --rm --network slirp4netns -v /mnt/d:/d "
            f"-e OUT={CONTAINER_OUT} "
            f"-v '{WSL_WORK}':/w -w /w localhost/node:22-alpine "
            f"node --experimental-strip-types gen-snapshot.mjs",
        ],
        text=True,
        capture_output=True,
        timeout=300,
    )
    if proc.returncode != 0:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        return 1
    data = json.loads(TARGET.read_text(encoding="utf-8"))
    print(
        f"regenerated: {TARGET} "
        f"(variables={len(data['variables'])}, headings={len(data['headings'])}, "
        f"process={len(data['process'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

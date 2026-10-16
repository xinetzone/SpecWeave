"""横向滑动图片块扩展。

upstream: packages/core/src/extensions/slider.ts（markedSlider）。
语法：<![alt1](url1),![alt2](url2)>，独占一行；输出微信兼容的横滑 section 结构。
"""

import re

# upstream: slider.ts:17
_SLIDER_RE = re.compile(r"^<(!\[.*?\]\(.*?\)(?:,!\[.*?\]\(.*?\))*)>")
_IMAGE_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")


def slider_block(state, startLine: int, endLine: int, silent: bool) -> bool:
    if state.is_code_block(startLine):
        return False
    pos = state.bMarks[startLine] + state.tShift[startLine]
    maximum = state.eMarks[startLine]
    line_text = state.src[pos:maximum].strip()
    if not line_text.startswith("<!["):
        return False
    match = _SLIDER_RE.match(line_text)
    if not match or match.end() != len(line_text):
        return False
    if silent:
        return True
    state.line = startLine + 1
    token = state.push("horizontal_slider", "", 0)
    token.map = [startLine, state.line]
    token.content = match.group(1)
    return True


def render_slider(tokens, idx, options, env) -> str:
    """upstream: slider.ts:28-65（字面模板照搬）。"""
    text = tokens[idx].content
    images = []
    for img in _IMAGE_RE.findall(text):
        images.append({"src": img[1] or "", "alt": img[0] or ""})

    if not images:
        return ""

    image_html = "".join(
        '<section style="display: inline-block; width: 100%; margin-right: 0;'
        ' vertical-align: top;">'
        f'<img src="{img["src"]}" alt="{img["alt"]}" title="{img["alt"]}" '
        'style="width: 100%; height: auto; border-radius: 4px; vertical-align: top;"/>'
        '<p style="margin-top: 5px; font-size: 14px; color: #666; text-align: center; '
        f'white-space: normal;">{img["alt"]}</p>'
        "</section>"
        for img in images
    )

    return (
        '\n            <section style="box-sizing: border-box; font-size: 16px;">\n'
        '              <section data-role="outer" style="font-family: 微软雅黑; font-size: 16px;">\n'
        '                <section data-role="paragraph" style="margin: 0px auto; box-sizing: border-box; width: 100%;">\n'
        '                  <section style="margin: 0px auto; text-align: center;">\n'
        '                    <section style="display: inline-block; width: 100%;">\n'
        '                      <!-- WeChat-compatible horizontal scroll image container -->\n'
        '                      <section style="overflow-x: scroll; -webkit-overflow-scrolling: touch; white-space: nowrap; width: 100%; text-align: center;">\n'
        f"                        {image_html}\n"
        "                      </section>\n"
        "                    </section>\n"
        "                  </section>\n"
        "                </section>\n"
        "              </section>\n"
        '              <p style="font-size: 14px; color: #999; text-align: center; margin-top: 5px;"><<< 左右滑动看更多 >>></p>\n'
        "            </section>\n"
        "          "
    )


def register_slider(md) -> None:
    md.block.ruler.before("paragraph", "horizontal_slider", slider_block)
    md.renderer.rules["horizontal_slider"] = render_slider

"""MCP 静态选项字面值资产。

upstream: packages/mcp-server/src/config-options.ts（11 组选项 + 代码块主题）
          packages/shared/src/configs/ai-service-options.ts（serviceOptions）
          packages/shared/src/constants/ai-config.ts（DEFAULT_SERVICE_ENDPOINT）
          packages/mcp-server/src/index.ts（explain_extensions / get_renderer_options 文案）

转录规则：键序、文案、空串 ``desc``、模型名大小写均与 TS 源逐字一致；
派生值（``author``、hljs URL）在 tools.py 的 payload 构造器中还原。
"""

DEFAULT_SERVICE_ENDPOINT = "https://proxy-ai.doocs.org/v1"

# upstream: config-options.ts:10-22
COLOR_OPTIONS = (
    {"value": "#0F4C81", "label": "经典蓝", "desc": "稳重冷静"},
    {"value": "#009874", "label": "翡翠绿", "desc": "自然平衡"},
    {"value": "#FA5151", "label": "活力橘", "desc": "热情活力"},
    {"value": "#FECE00", "label": "柠檬黄", "desc": "明亮温暖"},
    {"value": "#92617E", "label": "薰衣紫", "desc": "优雅神秘"},
    {"value": "#55C9EA", "label": "天空蓝", "desc": "清爽自由"},
    {"value": "#B76E79", "label": "玫瑰金", "desc": "奢华现代"},
    {"value": "#556B2F", "label": "橄榄绿", "desc": "沉稳自然"},
    {"value": "#333333", "label": "石墨黑", "desc": "内敛极简"},
    {"value": "#A9A9A9", "label": "雾烟灰", "desc": "柔和低调"},
    {"value": "#FFB7C5", "label": "樱花粉", "desc": "浪漫甜美"},
)

# upstream: config-options.ts:24-28
THEME_OPTIONS = (
    {"value": "default", "label": "经典", "desc": ""},
    {"value": "grace", "label": "优雅", "desc": "@brzhang"},
    {"value": "simple", "label": "简洁", "desc": "@okooo5km"},
)

# upstream: config-options.ts:30-46
FONT_FAMILY_OPTIONS = (
    {
        "label": "无衬线",
        "value": (
            "-apple-system-font,BlinkMacSystemFont, Helvetica Neue, PingFang SC, "
            "Hiragino Sans GB , Microsoft YaHei UI , Microsoft YaHei ,Arial,sans-serif"
        ),
        "desc": "字体123Abc",
    },
    {
        "label": "衬线",
        "value": (
            "Optima-Regular, Optima, PingFangSC-light, PingFangTC-light, 'PingFang SC', "
            "Cambria, Cochin, Georgia, Times, 'Times New Roman', serif"
        ),
        "desc": "字体123Abc",
    },
    {
        "label": "等宽",
        "value": "Menlo, Monaco, 'Courier New', monospace",
        "desc": "字体123Abc",
    },
)

# upstream: config-options.ts:48-54
FONT_SIZE_OPTIONS = (
    {"label": "14px", "value": "14px", "desc": "更小"},
    {"label": "15px", "value": "15px", "desc": "稍小"},
    {"label": "16px", "value": "16px", "desc": "推荐"},
    {"label": "17px", "value": "17px", "desc": "稍大"},
    {"label": "18px", "value": "18px", "desc": "更大"},
)

# upstream: config-options.ts:56-62
LINE_HEIGHT_OPTIONS = (
    {"label": "1.5", "value": "1.5", "desc": "紧凑"},
    {"label": "1.65", "value": "1.65", "desc": "稍紧"},
    {"label": "1.75", "value": "1.75", "desc": "推荐"},
    {"label": "1.9", "value": "1.9", "desc": "稍松"},
    {"label": "2.05", "value": "2.05", "desc": "宽松"},
)

# upstream: config-options.ts:64-70
BLOCK_SPACING_OPTIONS = (
    {"label": "0.75×", "value": "0.75", "desc": "紧凑"},
    {"label": "0.9×", "value": "0.9", "desc": "稍紧"},
    {"label": "1×", "value": "1", "desc": "推荐"},
    {"label": "1.15×", "value": "1.15", "desc": "稍松"},
    {"label": "1.35×", "value": "1.35", "desc": "宽松"},
)

# upstream: config-options.ts:72-76
LINK_COLOR_OPTIONS = (
    {"label": "微信蓝", "value": "#576b95", "desc": "默认"},
    {"label": "主题色", "value": "var(--md-primary-color)", "desc": "跟随主题色"},
    {"label": "正文色", "value": "inherit", "desc": "与正文一致"},
)

# upstream: config-options.ts:78-82
BLOCKQUOTE_BACKGROUND_OPTIONS = (
    {"label": "跟随主题", "value": "default", "desc": "默认"},
    {"label": "无背景", "value": "transparent", "desc": "透明"},
    {
        "label": "主题色",
        "value": "color-mix(in srgb, var(--md-primary-color) 8%, transparent)",
        "desc": "主题色浅底",
    },
)

# upstream: config-options.ts:84-91
LEGEND_OPTIONS = (
    {"label": "title 优先", "value": "title-alt", "desc": ""},
    {"label": "alt 优先", "value": "alt-title", "desc": ""},
    {"label": "只显示 title", "value": "title", "desc": ""},
    {"label": "只显示 alt", "value": "alt", "desc": ""},
    {"label": "文件名", "value": "filename", "desc": ""},
    {"label": "不显示", "value": "none", "desc": ""},
)

# upstream: config-options.ts:95-101
HEADING_STYLE_OPTIONS = (
    {"label": "默认", "value": "default", "desc": ""},
    {"label": "主题色文字", "value": "color-only", "desc": ""},
    {"label": "下边框", "value": "border-bottom", "desc": ""},
    {"label": "左边框", "value": "border-left", "desc": ""},
    {"label": "自定义", "value": "custom", "desc": ""},
)

# upstream: index.ts:252
HEADING_LEVELS = ("h1", "h2", "h3", "h4", "h5", "h6")

# upstream: ai-service-options.ts:4-365（21 个内置服务，键序 value/label/endpoint/models）
AI_SERVICE_OPTIONS = (
    {
        "value": "default",
        "label": "内置服务",
        "endpoint": DEFAULT_SERVICE_ENDPOINT,
        "models": (
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-Coder-7B-Instruct",
            "Qwen/Qwen2-7B-Instruct",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "THUDM/GLM-Z1-9B-0414",
            "THUDM/GLM-4-9B-0414",
            "internlm/internlm2_5-7b-chat",
            "qwen/qwen3-30b-a3b:free",
            "qwen/qwen3-8b:free",
            "qwen/qwen3-14b:free",
            "qwen/qwen3-32b:free",
            "qwen/qwen3-235b-a22b:free",
            "tngtech/deepseek-r1t-chimera:free",
            "thudm/glm-z1-9b:free",
            "thudm/glm-z1-32b:free",
            "thudm/glm-4-9b:free",
            "thudm/glm-4-32b:free",
            "microsoft/mai-ds-r1:free",
            "arliai/qwq-32b-arliai-rpr-v1:free",
            "nvidia/llama-3.3-nemotron-super-49b-v1:free",
            "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
            "meta-llama/llama-4-maverick:free",
            "meta-llama/llama-4-scout:free",
            "deepseek/deepseek-v3-base:free",
            "qwen/qwen2.5-vl-3b-instruct:free",
            "qwen/qwen2.5-vl-32b-instruct:free",
        ),
    },
    {
        "value": "deepseek",
        "label": "DeepSeek",
        "endpoint": "https://api.deepseek.com",
        "models": (
            "deepseek-v4-pro",
            "deepseek-v4-flash",
            "deepseek-chat",
            "deepseek-reasoner",
        ),
    },
    {
        "value": "openai",
        "label": "OpenAI",
        "endpoint": "https://api.openai.com/v1",
        "models": (
            "gpt-5.5",
            "gpt-5.4",
            "gpt-5.4-mini",
            "gpt-5.4-nano",
            "gpt-5-mini",
            "gpt-5-nano",
            "o3",
            "o3-mini",
            "o4-mini",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
        ),
    },
    {
        "value": "google",
        "label": "Google Gemini",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": (
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
        ),
    },
    {
        "value": "xai",
        "label": "xAI Grok",
        "endpoint": "https://api.x.ai/v1",
        "models": (
            "grok-4",
            "grok-3",
            "grok-3-mini",
            "grok-3-fast",
            "grok-2",
            "grok-2-vision-1212",
        ),
    },
    {
        "value": "mistral",
        "label": "Mistral AI",
        "endpoint": "https://api.mistral.ai/v1",
        "models": (
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
            "codestral-latest",
            "ministral-8b-latest",
            "ministral-3b-latest",
            "pixtral-large-latest",
        ),
    },
    {
        "value": "openrouter",
        "label": "OpenRouter",
        "endpoint": "https://openrouter.ai/api/v1",
        "models": (
            "openai/gpt-5.4",
            "anthropic/claude-sonnet-4-6",
            "anthropic/claude-opus-4-8",
            "google/gemini-2.5-pro",
            "google/gemini-2.5-flash",
            "deepseek/deepseek-v4-pro",
            "deepseek/deepseek-v4-flash",
            "meta-llama/llama-4-maverick",
            "x-ai/grok-3",
            "mistralai/mistral-large-latest",
            "qwen/qwen3-235b-a22b",
        ),
    },
    {
        "value": "groq",
        "label": "Groq",
        "endpoint": "https://api.groq.com/openai/v1",
        "models": (
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ),
    },
    {
        "value": "qwen",
        "label": "通义千问",
        "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": (
            "qwen3-max",
            "qwen3-plus",
            "qwen3-flash",
            "qwen-max-latest",
            "qwen-plus-latest",
            "qwen-turbo-latest",
            "qwen-long",
            "qwen-vl-max-latest",
            "qwen-vl-plus-latest",
            "qwen-coder-plus-latest",
            "qwen-coder-turbo-latest",
            "qwen2.5-72b-instruct",
            "qwen2.5-32b-instruct",
            "qwen2.5-14b-instruct",
            "qwen2.5-7b-instruct",
            "qwen2.5-coder-32b-instruct",
            "qwen2.5-coder-7b-instruct",
            "deepseek-v3",
            "deepseek-r1",
        ),
    },
    {
        "value": "hunyuan",
        "label": "腾讯混元",
        "endpoint": "https://api.hunyuan.cloud.tencent.com/v1",
        "models": (
            "hunyuan-turbos-latest",
            "hunyuan-t1-latest",
            "hunyuan-pro",
            "hunyuan-turbo",
            "hunyuan-standard-256k",
            "hunyuan-standard-32K",
            "hunyuan-standard",
            "hunyuan-lite",
            "hunyuan-code",
            "hunyuan-vision",
            "hunyuan-role",
            "hunyuan-functioncall",
            "hunyuan-turbo-vision",
        ),
    },
    {
        "value": "doubao",
        "label": "火山方舟",
        "endpoint": "https://ark.cn-beijing.volces.com/api/v3",
        "models": (
            "doubao-seed-1-6-250615",
            "doubao-seed-1-6-flash-250615",
            "doubao-1-5-thinking-pro-250415",
            "doubao-1-5-thinking-pro-m-250415",
            "doubao-1-5-pro-256k-250115",
            "doubao-1-5-pro-32k-250115",
            "doubao-1-5-lite-32k-250115",
            "doubao-1-5-vision-pro-250328",
            "doubao-1-5-vision-lite-250315",
            "deepseek-v3-250324",
            "deepseek-r1-250120",
            "kimi-k2-250711",
        ),
    },
    {
        "value": "siliconflow",
        "label": "硅基流动",
        "endpoint": "https://api.siliconflow.cn/v1",
        "models": (
            "deepseek-ai/DeepSeek-V3.2",
            "deepseek-ai/DeepSeek-R1",
            "deepseek-ai/DeepSeek-V3",
            "Qwen/Qwen3-235B-A22B",
            "Qwen/Qwen3-32B",
            "Qwen/Qwen3-30B-A3B",
            "Qwen/Qwen3-14B",
            "Qwen/Qwen3-8B",
            "THUDM/GLM-Z1-32B-0414",
            "THUDM/GLM-4-32B-0414",
            "THUDM/GLM-4-9B-0414",
            "Qwen/QwQ-32B",
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "Qwen/Qwen2.5-Coder-7B-Instruct",
            "Pro/deepseek-ai/DeepSeek-R1",
            "Pro/deepseek-ai/DeepSeek-V3",
            "internlm/internlm2_5-20b-chat",
            "internlm/internlm2_5-7b-chat",
        ),
    },
    {
        "value": "302ai",
        "label": "302.AI",
        "endpoint": "https://api.302.ai/v1",
        "models": (
            "gpt-5.4",
            "gpt-5.4-mini",
            "gpt-4.1",
            "gpt-4o",
            "gpt-4o-mini",
            "o3",
            "o4-mini",
            "claude-sonnet-4-6",
            "claude-opus-4-8",
            "claude-haiku-4-5-20251001",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "deepseek-v4-pro",
            "deepseek-v4-flash",
            "grok-3",
            "grok-3-mini",
        ),
    },
    {
        "value": "bigmodel",
        "label": "智谱 AI",
        "endpoint": "https://open.bigmodel.cn/api/paas/v4",
        "models": (
            "glm-4.7",
            "glm-4.7-flashx",
            "glm-4.7-flash",
            "glm-4.6",
            "glm-4.5-air",
            "glm-4.5-airx",
            "glm-4-long",
            "glm-4-flash-250414",
            "glm-4-flashx-250414",
        ),
    },
    {
        "value": "baichuan",
        "label": "百川智能",
        "endpoint": "https://api.baichuan-ai.com/v1",
        "models": (
            "Baichuan4-Turbo",
            "Baichuan4-Air",
            "Baichuan4",
            "Baichuan3-Turbo-128k",
            "Baichuan3-Turbo",
        ),
    },
    {
        "value": "lingyiwanwu",
        "label": "零一万物",
        "endpoint": "https://api.lingyiwanwu.com/v1",
        "models": (
            "yi-lightning",
            "yi-large",
            "yi-medium",
            "yi-spark",
        ),
    },
    {
        "value": "moonshot",
        "label": "月之暗面",
        "endpoint": "https://api.moonshot.cn/v1",
        "models": (
            "kimi-k2.7-code",
            "kimi-k2.7-code-highspeed",
            "kimi-k2.6",
            "kimi-k2.5",
            "moonshot-v1-128k-vision-preview",
            "moonshot-v1-32k-vision-preview",
            "moonshot-v1-8k-vision-preview",
            "moonshot-v1-128k",
            "moonshot-v1-32k",
            "moonshot-v1-8k",
        ),
    },
    {
        "value": "minimax",
        "label": "MiniMax",
        "endpoint": "https://api.minimaxi.com/v1",
        "models": (
            "MiniMax-M2.5",
            "MiniMax-M2.5-highspeed",
            "MiniMax-M2.1",
            "MiniMax-M2.1-highspeed",
            "MiniMax-Text-01",
            "abab6.5s-chat",
            "abab6.5g-chat",
            "abab6.5t-chat",
        ),
    },
    {
        "value": "stepfun",
        "label": "阶跃星辰",
        "endpoint": "https://api.stepfun.com/v1",
        "models": (
            "step-2-16k",
            "step-2-mini",
            "step-1-8k",
            "step-1-flash",
        ),
    },
    {
        "value": "ernie",
        "label": "百度千帆",
        "endpoint": "https://qianfan.baidubce.com/v2",
        "models": (
            "ernie-4.5-turbo-128k",
            "ernie-4.5-turbo-32k",
            "ernie-4.5-8k-preview",
            "ernie-4.0-turbo-128k",
            "ernie-4.0-turbo-8k",
            "ernie-4.0-8k",
            "ernie-speed-pro-128k",
            "ernie-speed-128k",
            "ernie-lite-pro-128k",
            "ernie-lite-8k",
            "ernie-tiny-8k",
        ),
    },
    {
        "value": "custom",
        "label": "自定义兼容 OpenAI API 的服务",
        "endpoint": "",
        "models": (),
    },
)

# upstream: index.ts:333-398（explain_extensions 的 extensions 数组，逐字含顺序）
EXTENSION_DOCS = (
    {
        "name": "KaTeX Math",
        "description": "Inline and block LaTeX math expressions rendered via KaTeX.",
        "inlineExample": "$E = mc^2$",
        "blockExample": "$$\n\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}\n$$",
    },
    {
        "name": "Mermaid Diagrams",
        "description": "Sequence, flowchart, Gantt, class, and other diagrams via Mermaid.js.",
        "example": "```mermaid\ngraph TD\n  A --> B\n```",
    },
    {
        "name": "PlantUML",
        "description": "UML diagrams rendered via PlantUML (output as inline SVG).",
        "example": "```plantuml\n@startuml\nAlice -> Bob: hello\n@enduml\n```",
    },
    {
        "name": "Callout Alerts",
        "description": (
            "Styled alert/callout blocks via blockquote ([!TYPE]) or container (::: type) "
            'syntax. An optional custom title can follow the type on the same line, e.g. '
            '"::: theorem Pythagorean Theorem" or "> [!IMPORTANT] 必读". '
            "Built-in types carry their own color/icon — GFM: note, tip, info, important, "
            "warning, caution; Obsidian-style: abstract, summary, tldr, todo, success, done, "
            "question, help, faq, failure, fail, missing, danger, error, bug, example, quote, "
            "cite; Academic: theorem, lemma, corollary, proposition, definition, axiom, "
            'postulate, assumption, proof, remark. Any other name (including non-ASCII, e.g. '
            '"::: 推论") renders with a neutral fallback style using the name as the title. '
            "Bodies support full Markdown and KaTeX math."
        ),
        "example": (
            "> [!NOTE] 自定义标题\n> This is a note.\n\n::: theorem 勾股定理\n"
            "$a^2 + b^2 = c^2$\n:::\n\n::: 推论\n任意名称都会渲染为方框。\n:::"
        ),
    },
    {
        "name": "Footnotes",
        "description": "Standard Markdown footnotes collected and rendered at the document bottom.",
        "example": "Some text[^1]\n\n[^1]: footnote body",
    },
    {
        "name": "Ruby Annotations",
        "description": "East Asian ruby (furigana) annotations above text.",
        "example": "{漢字|かんじ}",
    },
    {
        "name": "Table of Contents",
        "description": "Auto-generated TOC inserted with the [toc] marker.",
        "example": "[toc]",
    },
    {
        "name": "Infographic",
        "description": "Styled infographic blocks powered by @antv/infographic.",
        "example": "```infographic\n...\n```",
    },
    {
        "name": "Markup Highlighting",
        "description": "Inline markup: ==highlight==, ++underline++, ~wavy line~ and ^superscript^.",
        "example": "==highlighted text== ++underlined++ ~wavy~ x^2^",
    },
    {
        "name": "Emoji",
        "description": "GitHub-style emoji shortcodes. Unknown names stay literal.",
        "example": "Ship it :rocket: :tada:",
    },
    {
        "name": "Slider",
        "description": "Horizontal scroll slider blocks for narrow viewports.",
        "example": "<<< slide content >>>",
    },
)

# upstream: index.ts:409-429（get_renderer_options 的 options 表，键序 name/type/default/description）
RENDERER_OPTION_DOCS = (
    {
        "name": "theme",
        "type": "'default' | 'grace' | 'simple'",
        "default": "default",
        "description": "Visual theme.",
    },
    {
        "name": "primaryColor",
        "type": "string (hex)",
        "default": "#0F4C81",
        "description": "Primary accent color via --md-primary-color.",
    },
    {
        "name": "fontFamily",
        "type": "string",
        "default": "system sans-serif stack",
        "description": "CSS font-family. See list_fonts.",
    },
    {
        "name": "fontSize",
        "type": "string (px)",
        "default": "16px",
        "description": "Base font size. See list_font_sizes.",
    },
    {
        "name": "lineHeight",
        "type": "string (unitless)",
        "default": "1.75",
        "description": "Body line height. See list_spacing_options.",
    },
    {
        "name": "blockSpacing",
        "type": "string (unitless)",
        "default": "1",
        "description": "Multiplier for the theme's vertical block margins. See list_spacing_options.",
    },
    {
        "name": "linkColor",
        "type": "string (colour)",
        "default": "#576b95",
        "description": "Link colour. See list_color_options.",
    },
    {
        "name": "blockquoteBackground",
        "type": "string (colour)",
        "default": "default",
        "description": (
            'Blockquote background; "default" keeps the theme\'s own. See list_color_options.'
        ),
    },
    {
        "name": "legend",
        "type": "'title-alt' | 'alt-title' | 'title' | 'alt' | 'filename' | 'none'",
        "default": "alt",
        "description": "Image caption format.",
    },
    {
        "name": "isMacCodeBlock",
        "type": "boolean",
        "default": False,
        "description": "macOS-style code block title bar.",
    },
    {
        "name": "isShowLineNumber",
        "type": "boolean",
        "default": False,
        "description": "Line numbers in code blocks.",
    },
    {
        "name": "citeStatus",
        "type": "boolean",
        "default": False,
        "description": "Links as footnote-style citations.",
    },
    {
        "name": "countStatus",
        "type": "boolean",
        "default": False,
        "description": "Prepend reading-time estimate.",
    },
    {
        "name": "themeMode",
        "type": "'light' | 'dark'",
        "default": "light",
        "description": "Diagram colour mode.",
    },
    {
        "name": "isUseIndent",
        "type": "boolean",
        "default": False,
        "description": "Paragraph first-line indent.",
    },
    {
        "name": "isUseJustify",
        "type": "boolean",
        "default": False,
        "description": "Justified paragraph text.",
    },
    {
        "name": "headingStyles",
        "type": "object",
        "default": "{}",
        "description": "Per-level heading styles. See list_heading_styles.",
    },
    {
        "name": "codeBlockTheme",
        "type": "preset url enum",
        "default": "github.min.css",
        "description": "highlight.js preset from list_code_block_themes.",
    },
    {
        "name": "customCSS",
        "type": "string",
        "default": "''",
        "description": "User custom CSS appended last.",
    },
)

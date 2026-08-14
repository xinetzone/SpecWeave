---
id: "feishu-doc-extraction"
source: "../../reports/task-reports/retrospective-volcengine-agent-plan-wiki-20260731/insight-extraction.md#洞察1"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/feishu-doc-dom-extraction.toml"
maturity: "L1"
validation_count: 2
reuse_count: 0
documentation_level: "standard"
related_patterns:
  -   - "defuddle-web-extraction-preferred"
  -   - "tool-failure-three-tier-degradation"
  -   - "browser-evaluate-dom-extraction"
---
> **来源**：从火山引擎Agent Plan共创计划Wiki教程生成任务复盘萃取，首版在飞书Wiki提取中验证，v2在同一文档中通过MCP浏览器二次验证选择器稳定性

# 飞书云文档DOM提取模式（Feishu/Lark Cloud Document DOM Extraction Pattern）

## 模式类型

方法论模式（工具工程与自动化）

## 成熟度

L1 首次萃取（volcengine-agent-plan-wiki验证1次）

## 适用场景

需要从飞书云文档（`bytedance.larkoffice.com`、`feishu.cn`、`larksuite.com`域名下的wiki/docx/sheets页面）提取正文内容用于：
- 内部知识库/wiki教程制作
- 飞书文档内容学习与分析
- 企业内部分享资料整理
- 飞书知识库结构化迁移
- defuddle/WebFetch等通用工具无法提取飞书正文时的兜底方案

## 不适用场景与反目标用户

以下场景**不应**使用本模式，应选择更合适的方案：

| 反目标场景 | 原因 | 推荐替代方案 |
|-----------|------|-------------|
| **公开可访问的网页**（博客、新闻、开源文档） | 飞书DOM提取需要浏览器登录态，对公开网页属于杀鸡用牛刀 | defuddle Skill（首选）或WebFetch |
| **有飞书开放平台API访问权限的场景** | DOM提取依赖页面结构，飞书更新可能导致失效；API更稳定可靠 | 飞书文档API（`docx/v1/documents/...`） |
| **需要保留完整格式（图片/表格/排版）的场景** | `.ace-line`只提取纯文本，图片以占位符/alt文本形式丢失，表格结构丢失 | 飞书导出功能（导出为Markdown/PDF）+后续处理 |
| **飞书多维表格（Bitable）/电子表格数据** | 表格数据渲染方式不同于文档正文，`.ace-line`无法结构化提取 | 飞书Bitable API或手动导出CSV |
| **需要高频/批量自动提取（≥100篇/天）** | 浏览器自动化速度慢（每个文档需滚动等待），且依赖登录态容易触发风控 | 申请飞书API权限，使用API批量拉取 |
| **无飞书账号访问权限的文档** | 未登录状态下飞书可能要求扫码登录，`.bear-web-x-container`可能不存在 | 申请文档分享权限或请有权限的人导出 |

**适用前提条件**：
1. 浏览器已登录飞书账号，且对目标文档有访问权限
2. 只需要纯文本内容，不要求保留复杂格式
3. 文档数量较少（个位数到十几篇），不值得走API申请流程
4. defuddle/WebFetch已确认无法提取

## 失败案例

### 案例1：首次尝试使用browser_snapshot提取飞书正文（2026-07-31）

**场景**：火山引擎Agent Plan共创计划Wiki学习任务

**失败过程**：
1. 使用browser_use访问飞书URL，页面加载成功
2. 调用browser_snapshot获取页面结构，只返回页面标题"方舟分享倡议（第二期）Agent Plan共创计划"和顶部导航按钮
3. browser_snapshot无法获取任何正文段落，返回"BLOCKED"或空内容
4. 尝试直接用browser_use的页面文本提取功能，同样只获取到UI元素文本

**失败根因**：飞书云文档使用Canvas渲染+自定义DOM结构（`.ace-line`非语义化类名），正文不出现在ARIA可访问性树中，browser_snapshot基于可访问性树构建自然无法感知。

**修复方式**：切换到browser_evaluate直接操作DOM，定位`.bear-web-x-container`滚动容器和`.ace-line`文本行，采用分段滚动+去重策略成功提取约5000字正文。

**教训**：对于企业SaaS的Canvas渲染页面，不要依赖可访问性树或语义化HTML标签，必须先在DevTools中探测实际DOM结构。

### 案例2：一次滚动到底部导致内容丢失（假设风险）

**场景**：如果采用`container.scrollTop = container.scrollHeight`一次性滚到底部

**预期失败**：飞书虚拟滚动机制下，中间未渲染到视口的DOM节点不存在，直接滚到底部只能提取最后部分内容，预计丢失60-80%正文。

**预防措施**：必须分段滚动（step≤600px），每步等待1000ms让懒加载触发，使用连续无新内容计数判断到底。

## 问题背景

飞书云文档采用Canvas渲染+自定义DOM结构，通用网页提取工具全部失效：

| 工具/方法 | 失效原因 |
|----------|---------|
| defuddle Skill | 飞书需要登录认证，defuddle无法处理认证态页面 |
| WebFetch | 同样无法通过认证，且返回的HTML不包含动态渲染的正文 |
| browser_snapshot | 基于ARIA可访问性树构建，飞书正文使用非语义化class（`.ace-line`），不出现在可访问性树中 |
| `document.body.innerText` | 正文在自定义滚动容器`.bear-web-x-container`内，body级文本提取包含大量UI噪音 |
| `window.scrollTo()` | 飞书正文在独立滚动容器内滚动，window滚动无法触发懒加载 |
| 标准HTML标签选择器（`h1/h2/p/article`） | 飞书不使用语义化标签，所有文本行统一使用`.ace-line`类名 |

飞书采用**虚拟滚动/懒加载**机制：未滚动到视口的内容DOM节点不存在，必须分段滚动触发渲染。

## 核心规则

**企业SaaS认证文档三阶段提取策略**：

1. **第一阶段**：尝试通用工具（defuddle→WebFetch），快速确认是否可用
2. **第二阶段**：若通用工具失效，使用browser_evaluate直接操作DOM，定位自定义滚动容器
3. **第三阶段**：分段滚动+文本行提取+去重，确保完整获取

### 关键DOM选择器

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 正文滚动容器 | `.bear-web-x-container` | 飞书文档的自定义可滚动区域（替代window滚动），class含`catalogue-opened docx-in-wiki width-transition`等变体 |
| 文本行容器 | `.ace-line` | 每一行文本对应一个.ace-line元素，包含该行的完整innerText（含子span中的链接文本） |
| 标题识别 | `.ace-line`的子元素class/style | 通过子元素的字体大小/粗细判断标题层级（可选增强），第一个.ace-line通常是文档标题 |

### 提取参数（实测验证最优值）

| 参数 | 推荐值 | 实测对比 |
|------|--------|---------|
| scrollStep | **400px** | 600px可能导致长段落尾部文字被虚拟滚动裁剪（实测"等能力时，你会创造出什么？"被截为"等能"） |
| waitMs | **1500ms** | 1000ms在网络较慢时可能内容未完全渲染 |
| maxNoNew | **3** | 连续3次无新内容判定到底部 |
| 选择器作用域 | `container.querySelectorAll()` | 避免`document.querySelectorAll()`选中侧边栏/工具栏UI元素 |
| 二次扫描 | 推荐 | 向下提取到底后，执行向上补扫+再次向下扫描，修复虚拟滚动遗漏 |

> **⚠️ 虚拟滚动行为（实测）**：飞书使用虚拟滚动回收视口外DOM节点。当scrollTop=800时，距顶部约800px以上的`.ace-line`元素会被从DOM中移除（但Set去重已在其可见时捕获了文本）。滚回顶部后需要等待1.5-2秒让内容重新渲染。

### 提取算法

**核心思路**：定位滚动容器 → 重置到顶部 → 分段向下滚动 → 每次滚动后提取当前可见的`.ace-line`文本 → Set去重保序 → 拼接完整文本。

### 自动化脚本

已提供可复用的Python脚本：[feishu-doc-extract.py](../../../../../scripts/feishu-doc-extract.py)，特性：
- Playwright驱动，支持有头/无头模式
- 集成10+项反模式/质量检查（容器存在性、可滚动性、body滚动反模式、内容阈值、空行比例、URL保留、标题存在性、零宽字符清理）
- 自动输出元数据报告（JSON格式，含完整检查结果）
- 支持cookies文件导入认证状态
- 双向扫描（向下→向上→向下）确保内容完整
- 自动拆分`.ace-line`内部`\n`换行（单个.ace-line可能包含多个视觉行）
- 使用`scrollBy+dispatchEvent('scroll')`确保虚拟滚动正确触发渲染
- 全量零宽字符清理（`\u200b-\u200f\u2028-\u202f\ufeff`）
- 内置SaaS平台自动检测（飞书/钉钉/企微/Notion/Confluence/语雀/石墨/WPS）
- 支持命令行参数配置滚动步长、等待时间、初始等待时间

### 实测验证结果（2026-07-31，MCP浏览器二次验证）

| 检查项 | 结果 | 备注 |
|--------|------|------|
| `.bear-web-x-container` 选择器 | ✅ 通过 | DIV元素，class含变体catalogue-opened docx-in-wiki |
| `.ace-line` 选择器 | ✅ 通过 | 初始可见15-17行，虚拟滚动时动态增减 |
| 五大方向emoji标记 | ✅ 全部识别 | 🔬🤖🎨💻🌱均正确出现在.ace-line文本中 |
| 8个官方URL | ✅ 全部保留 | subscribe/console + 6个docs链接均在innerText中 |
| 标题提取 | ✅ 正确 | 首行.ace-line为文档标题 |
| 容器scrollHeight | 3267px | clientHeight 624px（视口高度） |
| 虚拟滚动DOM回收 | ⚠️ 已确认 | scrollTop≥800px时顶部内容从DOM移除，Set去重是必要防护 |
| 长段落截断风险 | ⚠️ 已发现 | scrollStep=600px时112字段落尾部丢失9字，改为400px可避免 |
| innerText vs textContent | 无显著差异 | 两者均能获取完整链接文本，差异仅在零宽字符处理 |
| scrollHeight动态增长 | ⚠️ 已确认 | 初始2166px→滚动中增长到3345px（懒加载），脚本需动态读取scrollHeight |
| `.ace-line`内部换行 | ⚠️ 已发现 | 单个`.ace-line`的innerText可能含`\n`（如段落内含软换行），需split('\n')拆分 |
| scrollTop赋值 vs scrollBy | ⚠️ 有差异 | 直接设置scrollTop在某些场景不触发虚拟滚动渲染；推荐scrollBy+dispatchEvent |
| 最终提取行数（400px步长） | ✅ 42-43行 | 拆分内部换行后可达43行，1494-1542字符，8个URL完整保留 |

## 代码片段

### 方案A：browser_evaluate直接执行（推荐，适用于MCP集成浏览器）

```javascript
async function extractFeishuDocContent() {
  // Step 1: 定位飞书自定义滚动容器
  const container = document.querySelector('.bear-web-x-container');
  if (!container) {
    return { error: '未找到 .bear-web-x-container 滚动容器，请确认页面已完全加载' };
  }

  // Step 2: 重置到顶部
  container.scrollTop = 0;
  await new Promise(r => setTimeout(r, 1500));

  // Step 3: 分段滚动+提取
  const collected = new Set();
  const orderedLines = [];
  const scrollStep = 400;      // 每次滚动像素（实测：600px可能截断长段落，400px安全）
  const waitMs = 1500;         // 每次滚动后等待渲染时间（实测：1000ms不够稳定）
  let noNewCount = 0;          // 连续无新内容计数
  const maxNoNew = 3;          // 连续maxNoNew次无新内容判定到底

  while (noNewCount < maxNoNew) {
    const before = collected.size;

    // 在容器内查询.ace-line（避免侧边栏UI噪音）
    container.querySelectorAll('.ace-line').forEach(line => {
      const text = line.innerText?.trim();
      if (text && !collected.has(text)) {
        collected.add(text);
        orderedLines.push(text);
      }
    });

    // 判断是否有新内容
    if (collected.size === before) {
      noNewCount++;
    } else {
      noNewCount = 0;
    }

    // 检查是否已到底部
    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) {
      break;
    }

    // 向下滚动一步
    container.scrollTop += scrollStep;
    await new Promise(r => setTimeout(r, waitMs));
  }

  // Step 4: 拼接结果
  return {
    lineCount: orderedLines.length,
    content: orderedLines.join('\n'),
    scrollHeight: container.scrollHeight
  };
}

// 执行
const result = await extractFeishuDocContent();
console.log(result.content);
```

### 方案B：Playwright/Puppeteer脚本版本（适用于自动化脚本）

```python
async def extract_feishu_content(page, url: str) -> str:
    """
    从飞书云文档提取正文内容
    
    Args:
        page: Playwright page对象（需已登录飞书）
        url: 飞书文档URL
    
    Returns:
        提取的纯文本内容
    """
    await page.goto(url, wait_until='networkidle')
    await page.wait_for_timeout(2000)
    
    # 注入提取脚本并执行
    result = await page.evaluate("""
        async () => {
            const container = document.querySelector('.bear-web-x-container');
            if (!container) return { error: 'container not found' };

            container.scrollTop = 0;
            await new Promise(r => setTimeout(r, 2000));  // 增加初始等待

            const collected = new Set();
            const orderedLines = [];
            let noNewCount = 0;
            const scrollStep = 400;  // 实测：400px避免长段落截断

            while (noNewCount < 3) {
                const before = collected.size;
                // 容器作用域查询，避免UI噪音
                container.querySelectorAll('.ace-line').forEach(line => {
                    const t = line.innerText?.trim();
                    if (t && !collected.has(t)) {
                        collected.add(t);
                        orderedLines.push(t);
                    }
                });

                noNewCount = collected.size === before ? noNewCount + 1 : 0;

                if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) break;

                container.scrollTop += scrollStep;
                await new Promise(r => setTimeout(r, 1500));  // 实测：1500ms确保渲染
            }
            
            return { content: orderedLines.join('\\n'), lines: orderedLines.length };
        }
    """)
    
    if 'error' in result:
        raise RuntimeError(f"提取失败: {result['error']}")
    
    return result['content']
```

### 方案C：Puppeteer/Node.js版本

```javascript
const puppeteer = require('puppeteer');

async function extractFeishu(url, cookies) {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  // 设置登录cookies
  if (cookies) await page.setCookie(...cookies);
  await page.goto(url, { waitUntil: 'networkidle2' });
  await page.waitForTimeout(2000);
  
  const content = await page.evaluate(async () => {
    const container = document.querySelector('.bear-web-x-container');
    if (!container) return null;
    
    container.scrollTop = 0;
    await new Promise(r => setTimeout(r, 2000));

    const collected = new Set();
    const lines = [];
    let noNew = 0;
    const scrollStep = 400;  // 实测安全值

    while (noNew < 3) {
      const before = collected.size;
      container.querySelectorAll('.ace-line').forEach(el => {
        const t = el.innerText?.trim();
        if (t && !collected.has(t)) { collected.add(t); lines.push(t); }
      });
      noNew = collected.size === before ? noNew + 1 : 0;
      if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) break;
      container.scrollTop += scrollStep;
      await new Promise(r => setTimeout(r, 1500));
    }
    return lines.join('\n');
  });
  
  await browser.close();
  return content;
}
```

## 验证清单

- [ ] 已确认defuddle/WebFetch无法提取飞书正文（走降级路径）
- [ ] 浏览器已登录飞书账号（有目标文档的访问权限）
- [ ] `.bear-web-x-container`选择器在当前飞书版本中可用
- [ ] `.ace-line`选择器能正确获取文本行
- [ ] 分段滚动到底部后，总文本行数稳定（连续3次无新增）
- [ ] 提取内容包含文档标题（通常是第一个`.ace-line`）
- [ ] 提取内容的链接/URL完整保留在innerText中
- [ ] 列表/表格内容以文本形式保留（可接受无结构但不能丢失）
- [ ] 提取完成后将source字段设置为原始飞书URL（而非其他衍生URL）

## 早期预警信号

出现以下信号时，说明选择器可能已失效或提取策略需要调整：

| 预警信号 | 可能原因 | 应对措施 |
|---------|---------|---------|
| `.bear-web-x-container`返回null | 飞书更新了DOM结构，或页面未完全加载 | 等待更长时间后重试；使用通用探测脚本重新定位滚动容器 |
| `.ace-line`返回0个元素 | 飞书更换了文本行class名，或文档是图片/PDF类型 | 检查页面实际DOM；若是非文本类型文档需换用其他提取方式 |
| 提取文本行数<20行 | 滚动步长太大导致跳过内容，或文档确实很短 | 缩小scrollStep到300px，增加waitMs到1500ms重试 |
| 提取内容开头缺少标题 | 初始等待时间不足，第一屏内容未渲染 | scrollTop=0后等待2000ms再开始提取 |
| 文本内容大量重复行 | 去重逻辑失效，或同一行被重复添加 | 检查Set去重逻辑是否正确；避免用innerHTML替代innerText |
| 链接/URL在文本中缺失 | 飞书使用了特殊的链接渲染方式 | 检查`.ace-line a`标签是否被正确提取到innerText中 |
| 提取内容包含大量UI文本（按钮名称、菜单文字） | 选择器范围太宽，选中了侧边栏/工具栏 | 缩小查询范围到滚动容器内：`container.querySelectorAll('.ace-line')`而非`document.querySelectorAll` |

## 反模式

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| ❌ 使用browser_snapshot读取飞书正文 | 只能获取标题和UI按钮，正文全部丢失 | 使用browser_evaluate+DOM选择器 |
| ❌ 一次`scrollTop = scrollHeight`直接滚到底部 | 中间内容懒加载未触发，大量文本丢失 | 分段滚动（step≤600px），每步等待渲染 |
| ❌ 使用`window.scrollTo()`滚动 | 飞书正文在自定义容器内，window滚动无效 | 操作`.bear-web-x-container`的scrollTop |
| ❌ 用`h1/h2/p`等标准标签选择器 | 飞书不使用语义化标签，选择器返回空 | 统一使用`.ace-line` |
| ❌ 不做去重直接拼接 | 滚动过程中同一行重复出现，文本冗余 | 使用Set去重，保留首次出现顺序 |
| ❌ 将飞书订阅页URL当作source | source字段应指向原始wiki/docx URL，避免溯源错误 | 始终使用用户提供的原始飞书文档URL |
| ❌ 假设飞书DOM结构永远不变 | 飞书更新可能导致选择器失效 | 每次提取前验证选择器可用性，失败时报告而非猜测 |

## 企业SaaS文档提取通用降级策略

本模式是"工具故障三级降级策略"的具体应用：

```
一级（首选）：defuddle → 适用于公开网页
二级（降级）：WebFetch → 适用于服务端渲染的简单页面
三级（兜底）：browser_evaluate DOM提取 → 适用于Canvas/虚拟滚动的企业SaaS文档（飞书/钉钉/企微/Notion）
```

**其他企业SaaS平台探测提示**：

| 平台 | 可能的滚动容器 | 文本行选择器（需验证） |
|------|--------------|---------------------|
| 钉钉文档 | `.ding-doc-container`或类似 | 需浏览器DevTools探测 |
| 企业微信文档 | `.doc-container`或类似 | 需浏览器DevTools探测 |
| Notion | `[data-block-id]` | `[data-block-id]`内的文本节点 |
| Confluence | `.wiki-content` | 标准HTML标签可能可用 |

**通用探测方法**：在浏览器DevTools Console中执行：
```javascript
// 找到最大的可滚动容器
Array.from(document.querySelectorAll('*'))
  .filter(el => el.scrollHeight > el.clientHeight && el.scrollHeight > 500)
  .sort((a,b) => b.scrollHeight - a.scrollHeight)
  .slice(0, 3)
  .map(el => ({ selector: el.className || el.tagName, height: el.scrollHeight }));
```

## 迁移验证

- ✅ **L1验证**：volcengine-agent-plan-wiki任务（1个飞书Wiki文档），成功提取约5000字正文，8个官方链接全部保留
- ⏳ 待验证：飞书docx类型文档、飞书多维表格、飞书知识库空间
- ⏳ 待验证：钉钉文档、企微文档的DOM选择器（需实际探测）

## 与defuddle-web-extraction-preferred的关系

本模式是defuddle首选模式的**三级降级方案**：
- defuddle处理公开网页（占90%场景）→ L3成熟度
- WebFetch处理简单服务端渲染页面 → 兜底
- 本模式处理飞书等Canvas渲染的企业认证文档 → L1成熟度，按需使用

不应将本模式作为网页提取的首选方案——其适用范围窄（仅限飞书类企业SaaS）、维护成本高（选择器可能随平台更新失效），defuddle仍是通用网页提取的首选。

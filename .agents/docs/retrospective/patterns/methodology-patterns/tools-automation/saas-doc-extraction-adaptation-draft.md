# 企业SaaS云文档DOM提取适配方案（草案）

> **状态**：草案 v0.1（飞书已验证，其他平台待实测验证）
> **创建日期**：2026-07-31
> **基础模式**：[feishu-doc-dom-extraction.md](../../patterns/methodology-patterns/tools-automation/feishu-doc-dom-extraction.md)

## 一、背景与目标

飞书云文档DOM提取模式（feishu-doc-extraction）已通过2次实测验证，证明了"定位自定义滚动容器+分段滚动+文本行选择器+Set去重"策略对Canvas渲染企业文档的有效性。本方案将该策略扩展到其他主流企业SaaS云文档平台。

## 二、企业云文档共性挑战

所有企业SaaS云文档平台普遍存在以下技术特征，导致通用提取工具（defuddle/WebFetch/browser_snapshot）失效：

| 共性特征 | 影响 | 应对策略 |
|---------|------|---------|
| **Canvas/WebGL渲染正文** | DOM中无语义化HTML标签，标准选择器失效 | 探测自定义class名的文本行容器 |
| **虚拟滚动/懒加载** | 未滚动到的区域DOM节点不存在 | 分段滚动+等待渲染 |
| **自定义滚动容器** | window.scrollTo()无效 | 定位平台特定的overflow:auto容器 |
| **登录认证墙** | defuddle/WebFetch无认证态无法访问 | 浏览器自动化（Playwright/MCP）+ cookies |
| **非语义化class命名** | class名可能是hash/编译产物，跨版本不稳定 | 多候选选择器+运行时探测降级 |
| **零宽字符/特殊Unicode** | innerText中包含\u200b等不可见字符 | .trim() + replace(/[\u200b-\u200f\u2028-\u202f\ufeff]/g, '') |
| **侧边栏/工具栏UI噪音** | document级查询会混入菜单文本 | 容器作用域查询（container.querySelectorAll） |

## 三、平台适配矩阵

### 3.1 已验证平台

| 平台 | 域名特征 | 滚动容器选择器 | 文本行选择器 | 成熟度 |
|------|---------|--------------|------------|--------|
| **飞书/Lark** | `bytedance.larkoffice.com`, `feishu.cn`, `larksuite.com` | `.bear-web-x-container` | `.ace-line` | L1（2次验证） |

### 3.2 待验证平台（选择器假设，需实测）

> ⚠️ 以下选择器为基于平台技术栈推测的**候选方案**，未经实测验证。实际DOM结构可能完全不同。

#### 钉钉文档（DingTalk Docs）

| 属性 | 推测值 | 验证方法 |
|------|--------|---------|
| 域名 | `alidocs.dingtalk.com`, `dingtalk.com` | URL匹配 |
| 技术栈推测 | React + Slate.js或自研编辑器 | DevTools检查 |
| **候选滚动容器** | `.document-container`, `.editor-container`, `.doc-scroll-container`, `[class*="doc-container"]`, `[class*="editor-scroll"]` | 通用探测脚本 |
| **候选文本行** | `.ding-doc-line`, `.editor-line`, `.ace-line`（可能复用飞书方案？）, `[data-line]`, `p`, `.block-content` | 容器内探测 |
| 认证方式 | 钉钉扫码/账号密码登录 | Playwright持久化context |
| 预期虚拟滚动 | 是（钉钉文档为长文档优化，大概率使用虚拟滚动） | 滚动测试 |
| **反模式预警** | 钉钉文档可能使用iframe嵌套编辑器 | 需frame检测 |

#### 企业微信文档（WeCom Docs / 腾讯文档企业版）

| 属性 | 推测值 | 验证方法 |
|------|--------|---------|
| 域名 | `doc.weixin.qq.com`, `work.weixin.qq.com` | URL匹配 |
| 技术栈推测 | 腾讯文档内核（Canvas或WebKit渲染） | DevTools检查 |
| **候选滚动容器** | `.editor-main`, `.sheet-main`, `.docx-container`, `[class*="reader-container"]`, `[class*="page-container"]` | 通用探测脚本 |
| **候选文本行** | `.text-line`, `.para-element`, `.editor-paragraph`, `[class*="paragraph"]`, `[data-block-id]` | 容器内探测 |
| 认证方式 | 企业微信扫码登录 | Playwright持久化context |
| 预期虚拟滚动 | 是（腾讯文档有虚拟滚动实现） | 滚动测试 |
| **反模式预警** | 腾讯文档可能将内容渲染在canvas标签中而非DOM | 需检测canvas.toDataURL或OCR兜底 |

#### 语雀（Yuque）

| 属性 | 推测值 | 验证方法 |
|------|--------|---------|
| 域名 | `yuque.com`, `yuque.antfin.com` | URL匹配 |
| 技术栈推测 | 语雀文档编辑器（语义化HTML较友好） | DevTools检查 |
| **候选滚动容器** | `.ne-viewer-body`, `.doc-content`, `.article-content`, `#content` | 通用探测脚本 |
| **候选文本行** | 语义化标签（`h1-h6`, `p`, `li`, `table`）可能可用 | 优先试语义化选择器 |
| 认证方式 | 语雀账号/支付宝登录 | Playwright/cookies |
| 预期虚拟滚动 | 部分（长文可能有，短文可能无） | 检查scrollHeight vs clientHeight |
| **反模式预警** | 语雀的公开文档可能可直接用defuddle提取 | 先尝试defuddle再降级 |

#### 石墨文档（Shimo）

| 属性 | 推测值 | 验证方法 |
|------|--------|---------|
| 域名 | `shimo.im` | URL匹配 |
| **候选滚动容器** | `.document-editor`, `.editor-scroll`, `.sheet-container`, `[class*="editor-wrapper"]` | 通用探测脚本 |
| **候选文本行** | `.docx-line`, `.cell-content`, `.paragraph`, `[class*="block"]` | 容器内探测 |
| 认证方式 | 石墨账号登录 | Playwright |

#### WPS/KDocs（金山文档）

| 属性 | 推测值 | 验证方法 |
|------|--------|---------|
| 域名 | `kdocs.cn`, `wps.cn`, `doc.wps.cn` | URL匹配 |
| **候选滚动容器** | `.kdocs-container`, `.wps-doc-container`, `[class*="document-container"]` | 通用探测脚本 |
| **候选文本行** | `.kdocs-para`, `.wps-paragraph`, `.text-run` | 容器内探测 |
| **特殊注意** | WPS可能使用WebAssembly渲染，DOM中可能只有canvas | 需检测canvas兜底 |

#### Notion

| 属性 | 已知/推测 | 验证方法 |
|------|---------|---------|
| 域名 | `notion.site`, `notion.so` | URL匹配 |
| **已知滚动容器** | `.notion-frame`, `.notion-page-content` | 较高可信度 |
| **已知文本行** | `[data-block-id]` | Notion使用data-block-id标记每个块 |
| 认证方式 | Notion账号/Google登录 | Playwright |
| 备注 | Notion的DOM相对规范，data-block-id选择器稳定 | 优先测试此方案 |

#### Confluence（Atlassian）

| 属性 | 已知/推测 | 验证方法 |
|------|---------|---------|
| 域名 | `atlassian.net`, 自建confluence域名 | URL匹配 |
| **候选滚动容器** | `.wiki-content`, `.content-container`, `#main-content` | Confluence通常语义化较好 |
| **候选文本行** | 标准HTML标签（`h1-h6`, `p`, `li`, `td`）可能可用 | 优先试语义化选择器 |
| 备注 | Confluence服务端渲染比例高，可能可用WebFetch直接提取 | 先尝试WebFetch/defuddle |

## 四、通用容器探测脚本

当遇到未知平台或选择器失效时，使用以下通用探测脚本自动定位滚动容器和文本行：

```javascript
/**
 * 企业SaaS文档通用DOM探测脚本
 * 在浏览器DevTools Console或browser_evaluate中执行
 * 返回最可能的滚动容器和文本行选择器
 */
function detectDocStructure() {
  // Step 1: 找出所有高度大于视口的可滚动容器
  const viewportHeight = window.innerHeight;
  const scrollables = Array.from(document.querySelectorAll('*'))
    .filter(el => {
      const style = window.getComputedStyle(el);
      const isScrollable = style.overflowY === 'auto' || style.overflowY === 'scroll';
      const hasContent = el.scrollHeight > el.clientHeight + 100;
      const isBigEnough = el.clientHeight > viewportHeight * 0.3; // 至少占视口30%
      const isNotBody = el !== document.body && el !== document.documentElement;
      return isScrollable && hasContent && isBigEnough && isNotBody;
    })
    .sort((a, b) => b.scrollHeight - a.scrollHeight)
    .slice(0, 5)
    .map(el => ({
      selector: buildSelector(el),
      tag: el.tagName.toLowerCase(),
      className: (el.className || '').toString().substring(0, 80),
      scrollHeight: el.scrollHeight,
      clientHeight: el.clientHeight,
      childCount: el.children.length,
      textLength: el.innerText?.length || 0
    }));

  // Step 2: 对每个候选容器，探测最可能的文本行选择器
  const containers = scrollables.map(c => {
    const el = document.querySelector(c.selector) || findElementByClass(c.className);
    if (!el) return { ...c, lineSelectors: [] };

    // 候选文本行选择器策略
    const lineSelectorStrategies = [
      '[class*="line"]',     // 类名含line
      '[class*="ace-"]',     // 飞书ace-line类
      '[class*="para"]',     // paragraph
      '[class*="block"]',    // block element
      '[data-block-id]',     // Notion风格
      '[data-line]',         // 行号标记
      'p',                    // 段落
      'div[class]',           // 有class的div
    ];

    const lineSelectors = lineSelectorStrategies
      .map(sel => {
        try {
          const nodes = el.querySelectorAll(sel);
          if (nodes.length < 3) return null;
          // 检查这些节点是否包含有意义的文本
          const textNodes = Array.from(nodes).filter(n => (n.innerText?.trim() || '').length > 2);
          const avgLen = textNodes.reduce((s, n) => s + n.innerText.trim().length, 0) / Math.max(textNodes.length, 1);
          return {
            selector: sel,
            count: nodes.length,
            textNodeCount: textNodes.length,
            avgTextLength: Math.round(avgLen),
            sample: textNodes[0]?.innerText?.trim()?.substring(0, 60) || ''
          };
        } catch (e) { return null; }
      })
      .filter(Boolean)
      .sort((a, b) => b.textNodeCount - a.textNodeCount);

    return { ...c, lineSelectors: lineSelectors.slice(0, 5) };
  });

  return {
    url: location.href,
    title: document.title,
    viewportHeight,
    bodyScrollHeight: document.body.scrollHeight,
    bodyTextLength: document.body.innerText?.length || 0,
    detectedContainers: containers,
    recommendation: containers[0] ? {
      containerSelector: containers[0].selector,
      bestLineSelector: containers[0].lineSelectors[0]?.selector || null,
      confidence: containers[0].textLength > 500 ? 'high' : containers[0].textLength > 100 ? 'medium' : 'low'
    } : null
  };
}

function buildSelector(el) {
  // 构建一个尽量精确的CSS选择器
  if (el.id) return '#' + el.id;
  if (el.className && typeof el.className === 'string') {
    const classes = el.className.split(/\s+/).filter(c => c && !c.startsWith('vue-') && !c.startsWith('react-'));
    if (classes.length > 0) return '.' + classes.slice(0, 2).join('.');
  }
  return el.tagName.toLowerCase();
}

function findElementByClass(className) {
  if (!className) return null;
  const firstClass = className.split(/\s+/)[0];
  return firstClass ? document.querySelector('.' + firstClass) : null;
}

// 执行探测
const result = detectDocStructure();
console.log(JSON.stringify(result, null, 2));
return result;
```

## 五、适配实施路线图

### Phase 1：基础设施完善（当前）
- [x] 飞书模式沉淀与验证（feishu-doc-extraction, L1）
- [x] 飞书自动化提取脚本（feishu-doc-extract.py）
- [x] 通用探测脚本设计
- [ ] 多平台候选选择器调研（本草案）

### Phase 2：重点平台验证（按需）
在遇到以下平台文档时，执行DOM探测验证：
- [ ] 钉钉文档：访问一个公开的钉钉文档，运行探测脚本，验证/修正候选选择器
- [ ] 企微/腾讯文档：同上
- [ ] 语雀：先试defuddle，无效时DOM探测
- [ ] Notion：验证`[data-block-id]`选择器
- 每个平台验证后更新本方案的选择器表，沉淀为独立pattern（`dingtalk-doc-extraction`等）

### Phase 3：统一多平台提取脚本
- [ ] 扩展feishu-doc-extract.py为通用saas-doc-extract.py
- [ ] 集成平台自动检测（detect_saas_platform()已预留接口）
- [ ] 统一的反模式检查框架
- [ ] 选择器自动降级（A→B→C→通用探测）
- [ ] 提取质量评分系统

### Phase 4：高级特性
- [ ] cookies持久化（一次登录，多次使用）
- [ ] 批量文档提取（URL列表文件）
- [ ] 图片/附件下载支持
- [ ] 结构化输出（Markdown，而非纯文本）
- [ ] 表格识别与结构化导出

## 六、反模式统一检查清单（跨平台）

所有平台的提取脚本均应包含以下检查：

| # | 检查项 | 检查方法 | 预警条件 |
|---|--------|---------|---------|
| 1 | 容器存在性 | 选择器查询返回非null | 返回null → 报错+建议运行探测脚本 |
| 2 | 容器可滚动 | scrollHeight > clientHeight | 不可滚动 → 警告（内容可能无需滚动） |
| 3 | 初始文本行数 | querySelectorAll返回数量 | <3 → 警告（选择器可能不正确） |
| 4 | 最小内容阈值 | 提取后字符数/行数 | <10行或<200字符 → 警告 |
| 5 | URL保留率 | 正则匹配URL数量 | 页面链接>0但文本中无URL → 警告 |
| 6 | 空行比例 | 空行/总行数 | >50% → 警告（选择器匹配到装饰元素） |
| 7 | 标题存在性 | 前5行是否有短文本（<30字） | 无标题 → 提示 |
| 8 | 双向扫描一致性 | 向下+向上提取行数差异 | 差异>20% → 自动二次扫描 |
| 9 | 选择器作用域 | 使用container.querySelectorAll | 使用document.querySelectorAll → 代码审查拦截 |
| 10 | 零宽字符清理 | innerText后replace处理 | 包含\u200b等 → 自动清理 |

## 七、风险与注意事项

1. **class名版本风险**：企业SaaS平台的class名（如`.ace-line`）是编译产物，可能随产品更新而变化。脚本必须包含选择器失效的明确错误提示和降级路径。
2. **法律合规**：自动化提取企业文档内容需确保有访问权限，不得用于绕过权限控制或爬取非授权内容。
3. **平台反爬**：频繁自动化访问可能触发平台风控机制（验证码、IP封禁）。建议控制访问频率，添加合理延迟。
4. **Canvas兜底**：如果平台使用纯Canvas渲染（DOM中无文本节点），则DOM提取方案完全失效，需转向OCR或截图方案。
5. **iframe嵌套**：部分平台（如钉钉）可能将编辑器放在iframe中，需要先切换frame context再执行选择器查询。

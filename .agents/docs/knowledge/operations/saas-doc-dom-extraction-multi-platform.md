---
id: saas-doc-dom-extraction-multi-platform
title: SaaS云文档DOM提取多平台适配方案
source:
  - lib/saas_doc_extractor/ (v1.0, 已验证飞书)
  - feishu-doc-extract.py (2026-07-31 飞书实测)
tags:
  - web-automation
  - dom-extraction
  - virtual-scroll
  - anti-pattern
created: 2026-04-15
verified: feishu=✓, dingtalk=○, wecom=○
---

# SaaS云文档DOM提取多平台适配方案

## 1. 概述

基于飞书云文档实测验证的DOM提取模式（虚拟滚动+反模式检查+双向扫描），封装为通用
`SaasDocExtractor` 框架，通过 `PlatformConfig` 配置驱动支持多平台扩展。
本文档对比飞书（已验证）、钉钉（候选）、企微（候选）三个平台的DOM结构差异与适配策略。

## 2. 核心提取模式（飞书实测验证）

所有平台共用以下核心机制：

| 机制 | 说明 | 飞书参数 |
|------|------|----------|
| 分段滚动 | 避免一次到底导致虚拟滚动截断 | 400px/步 |
| 等待渲染 | 每步后等待虚拟列表渲染 | 1500ms |
| 双向扫描 | 向下→向上→向下三扫，防DOM回收遗漏 | 默认开启 |
| scrollBy+dispatchEvent | 手动触发scroll事件确保虚拟列表响应 | 必需 |
| 容器作用域查询 | querySelectorAll限定在滚动容器内，避免UI噪音 | 必需 |
| 去重保序 | Set去重+Ordered List保序，处理虚拟滚动DOM回收 | 必需 |
| JS端预处理 | innerText拆分`\n`软换行、清理零宽字符 | 必需 |
| 11项反模式检查 | 提取前5项+提取后6项 | 必需 |

### 11项反模式检查清单

| # | 阶段 | 检查项 | 失败表现 |
|---|------|--------|----------|
| 1 | 前 | 容器存在性 | container_exists=False → 硬错误 |
| 2 | 前 | 容器可滚动性 | scrollHeight≤clientHeight → warning |
| 3 | 前 | body滚动反模式 | body可滚动但平台预期容器滚动 → warning |
| 4 | 前 | 初始行数≥3 | 0行→warning, <3行→warning |
| 5 | 后 | 最小行数≥10 | 内容过短 → warning |
| 6 | 后 | 最小字符数≥200 | 内容过短 → warning |
| 7 | 后 | 标题存在 | 未提取到标题 → warning |
| 8 | 后 | URL保留度检测 | 页面有链接但文本无URL → warning |
| 9 | 后 | 空行比例≤30% | 空行过多说明选择器误配 → warning |
| 10 | 后 | 零宽字符残留 | JS端清理后仍有残留 → warning |
| 11 | 后 | 选择器有效性 | lines>0且content>50字符 | 通过标记 |

## 3. 三平台DOM结构对比

### 3.1 对比矩阵

| 维度 | 飞书（已验证✓） | 钉钉（候选○） | 企微/腾讯文档（候选○） |
|------|----------------|--------------|---------------------|
| **域名** | bytedance.larkoffice.com, feishu.cn, larksuite.com | alidocs.dingtalk.com, docs.dingtalk.com | doc.weixin.qq.com, docs.qq.com, work.weixin.qq.com |
| **滚动容器** | `.bear-web-x-container` (class含catalogue-opened/docx-in-wiki变体) | `.doc-scroll-container` (候选) / `.canvas-container` / `.ne-viewer` | `.dui-dialog-scroll__container` (候选) / `.qz-editor-container` / `.reader-container` |
| **文本行选择器** | `.ace-line` | `.doc-line` / `.text-run` / `.ne-viewer-line` / `p.ne-paragraph` | `.text-render` / `.paragraph-render` / `.dui-text` / `.qz-text` |
| **行内软换行** | `.ace-line` innerText含`\n`，需split | 待验证：钉钉ne-viewer可能类似 | 待验证：腾讯文档可能使用`<br>` |
| **渲染引擎** | 自研ace编辑器 | ne-viewer (自研canvas-like) | 腾讯文档自研渲染（可能含Shadow DOM） |
| **虚拟滚动** | ✓（scrollTop≥800px顶部DOM回收） | ✓（推测，但阈值待实测） | ✓（推测） |
| **scrollHeight行为** | 动态增长（懒加载，初始2166px→滚动中3345px+） | 待实测 | 待实测 |
| **body可滚动** | ✗（反模式） | 待验证 | 待验证 |
| **初始渲染等待** | 2000ms（首屏） | 建议2500ms（候选） | 建议2500ms（候选） |
| **URL保留方式** | innerText内直接包含链接文本 | 待验证：可能需读取`a[href]`属性 | 待验证：可能需特殊处理 |
| **Shadow DOM** | ✗ | 待验证 | ⚠️ 高概率使用dui组件的Shadow DOM |
| **verified标记** | True | False（待实测） | False（待实测） |

### 3.2 关键差异分析

#### 差异1：渲染引擎不同
- **飞书**：DOM-based渲染，`.ace-line`为普通DOM元素，innerText直接可用
- **钉钉**：ne-viewer引擎可能采用Canvas或混合渲染，DOM中可能只保留当前视口文本
  - 适配策略：初始尝试`.doc-line`/`.text-run`，若行数为0尝试`.ne-viewer-line`/`p.ne-paragraph`
  - 风险：ne-viewer可能使用Canvas绘制文本，DOM不可查询 → 需要OCR或降级策略

#### 差异2：企微的Shadow DOM问题
- 企微文档使用dui组件库，部分内容可能封装在Shadow DOM中
- **影响**：标准`querySelector`无法穿透Shadow DOM
- **适配策略**：
  1. 先尝试常规选择器
  2. 若初始行数为0，注入JS穿透Shadow Root：
     ```js
     // 伪代码：穿透Shadow DOM收集文本
     function collectFromShadowRoots(root) {
       const lines = [];
       root.querySelectorAll('.text-render, .dui-text, .qz-text')
         .forEach(el => lines.push(el.innerText));
       root.querySelectorAll('*').forEach(el => {
         if (el.shadowRoot) lines.push(...collectFromShadowRoots(el.shadowRoot));
       });
       return lines;
     }
     ```
  3. 在`PlatformConfig`中增加`uses_shadow_dom: bool`标记，extractor根据标记决定是否使用Shadow DOM穿透逻辑

#### 差异3：URL保留方式不同
- **飞书**：`.ace-line` innerText直接包含URL文本（如`参考https://example.com`）
- **钉钉**：链接可能以`<a>`标签存在但innerText只保留显示文本，需额外读取`href`属性
- **企微**：可能使用卡片链接（非文本URL），需要特殊提取
- **适配策略**：在`_scroll_collect`的JS中，增加可选的链接提取步骤：
  ```js
  // 钉钉/企微适配：额外提取a[href]的href属性
  if (platform.extract_hrefs) {
    c.querySelectorAll('a[href]').forEach(a => {
      const href = a.getAttribute('href');
      if (href && href.startsWith('http')) lines.push(href);
    });
  }
  ```

#### 差异4：滚动事件触发方式
- **飞书**：`scrollBy`+`dispatchEvent('scroll')`有效
- **钉钉**：可能需要`wheel`事件模拟真实滚动，或使用`Element.scrollTop = xxx`直接设置
- **企微**：腾讯文档可能监听`scroll`事件但使用passive listener，`dispatchEvent`可能无效
- **适配策略**：在`PlatformConfig`中增加`scroll_method: str`字段：
  - `"scrollBy_dispatch"`（默认，飞书模式）
  - `"scrollTop_set"`（直接设置scrollTop属性）
  - `"wheel_event"`（模拟wheel事件）
  - 实测后确定各平台最优方法

## 4. 适配实施路线图

### Phase 1：钉钉验证（预计1-2小时）
1. 用浏览器打开任意alidocs.dingtalk.com文档
2. DevTools中验证：
   - 滚动容器选择器：执行`document.querySelector('.doc-scroll-container')`检查
   - 文本行选择器：容器下执行`.querySelectorAll('.doc-line').length`检查行数
   - 虚拟滚动：向下滚动后检查DOM节点数是否稳定（视口+缓冲区）
   - scrollHeight变化：记录初始和滚动后的scrollHeight
3. 使用`feishu-doc-extract.py --platform dingtalk -v <url>`实测
4. 根据实际DOM更新DINGTALK_CONFIG的选择器和参数
5. 设置`verified=True`

### Phase 2：企微验证（预计2-3小时）
1. 打开doc.weixin.qq.com文档
2. 重点检查：
   - 是否存在Shadow DOM（DevTools中看#shadow-root标记）
   - 滚动容器是document.body还是内部div
   - 文本节点是否有自定义class
3. 若有Shadow DOM，需要扩展extractor支持Shadow DOM穿透
4. 在`PlatformConfig`中添加`uses_shadow_dom: bool`和`shadow_root_selector: str`字段
5. 实测并更新WECOM_CONFIG
6. 设置`verified=True`

### Phase 3：通用化增强
根据实测中发现的共性问题，考虑：
- 增加`scroll_method`配置项
- 增加`extract_hrefs`配置项
- 增加`uses_shadow_dom`配置项
- 扩展`SaasDocExtractor`的JS模板以支持这些变体

## 5. PlatformConfig扩展字段建议

当前`PlatformConfig`已覆盖基本需求，实测钉钉/企微后可能需要新增：

```python
@dataclass
class PlatformConfig:
    # ...现有字段...

    # 扩展字段（待实测后激活）
    uses_shadow_dom: bool = False        # 是否使用Shadow DOM封装
    shadow_root_selector: str = ""      # Shadow Root宿主选择器
    scroll_method: str = "scrollBy"     # scrollBy|scrollTop|wheel
    extract_hrefs: bool = False         # 是否需要额外提取a[href]属性
    text_source: str = "innerText"      # innerText|textContent|shadow_pierce
    auth_required_hint: str = ""        # 认证提示文案
```

## 6. 测试策略

- **单元测试**（已完成64个）：覆盖text_cleaner、platforms、models、anti_patterns、extractor（mock page）
- **集成测试**（Phase 1/2完成后添加）：使用Playwright打开真实钉钉/企微文档，端到端验证
- **反模式回归测试**：新增平台时必须通过11项反模式检查
- **MockPage扩展**：为钉钉/企微创建专用MockPage子类，模拟其特殊DOM行为

## 7. 相关文件

| 文件 | 职责 |
|------|------|
| [lib/saas_doc_extractor/__init__.py](../mdi/generated/case1/__init__.py) | 公共API导出 |
| [lib/saas_doc_extractor/models.py](../../../scripts/lib/saas_doc_extractor/models.py) | PlatformConfig/ExtractionResult/AntiPatternReport数据模型 |
| [lib/saas_doc_extractor/platforms.py](../../../scripts/lib/saas_doc_extractor/platforms.py) | 8个平台配置注册表 |
| [lib/saas_doc_extractor/text_cleaner.py](../../../scripts/lib/saas_doc_extractor/text_cleaner.py) | 零宽字符清理/行拆分/URL提取 |
| [lib/saas_doc_extractor/anti_patterns.py](../../../scripts/lib/saas_doc_extractor/anti_patterns.py) | 11项反模式检查逻辑 |
| [lib/saas_doc_extractor/extractor.py](../../../scripts/lib/saas_doc_extractor/extractor.py) | 核心提取器（PageProtocol协议+SaasDocExtractor） |
| [feishu-doc-extract.py](../../../scripts/feishu-doc-extract.py) | CLI入口（已重构为多平台通用） |
| [tests/test_saas_doc_extractor.py](../../../scripts/tests/test_saas_doc_extractor.py) | 64个单元测试（mock驱动） |

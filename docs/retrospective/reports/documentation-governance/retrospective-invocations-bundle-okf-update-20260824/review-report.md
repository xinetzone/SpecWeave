---
type: Report
title: invocations bundle 对抗性审查报告
description: 对 awesome-okf-xs doc/bundles/build/tooling/invocations 全部 22 文件的引用与 vendor 4.1.0 源码逐项对账，识别确定性漂移/疑似漂移/无问题
tags: [invocations, adversarial-review, bundle, drift, okf]
generated: { by: "process:seven-concepts-v", at: "2026-08-24T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-24" }
sources:
  - id: facts
    resource: /facts.md
  - id: vendor
    resource: file:///d:/spaces/SpecWeave/external/libs/tools/pyinvoke/invocations/invocations
---

# invocations bundle 对抗性审查报告

> 阶段2（对抗性审查）产物。信源：`facts.md`（v4.1.0 事实基线）+ vendor 源码实际行内容。
> 验证方法：每个模块名/任务名/函数签名/配置键在 vendor 源码 Grep/Read 逐项核对。

## 1. 审查范围

`projects/awesome-okf-xs/doc/bundles/build/tooling/invocations/` 共 22 文件：
- 根：`index.md`、`log.md`（2）
- concepts：`00-introduction` ~ `10-composition-patterns` + `index.md`（12）
- examples：`basic-usage`/`custom-release-flow`/`file-watch-auto-test`/`multi-site-docs`/`test-install-verification` + `index.md`（6）
- references：`index.md` + `invocations-source.md`（2）

## 2. 结论摘要

| 类别 | 数量 | 说明 |
|------|:----:|------|
| 确定性漂移 | 2 | 路径错误 1、伪造配置键 1 |
| 疑似漂移 | 1 | 单数/复数书写不一致（prose 层） |
| 无问题 | 19 | 核心 API 引用全部与 vendor 一致 |

无虚构 API（未发现类似 PyInvoke 虚构 `Response` 类的问题）；文档任务名/函数签名/参数默认值整体高度忠实于源码。

## 3. 确定性漂移

### D1 — references/invocations-source.md L47：源码位置路径错误

- **位置**：`references/invocations-source.md` 第 47 行
- **原文**：`external/libs/pyinvoke/invocations/`
- **真实值**：`external/libs/tools/pyinvoke/invocations/invocations/`（经 py314 `invocations.__file__` 实测确认）
- **影响**：指向不存在的目录，读者/工具按此路径无法定位 vendor 源码
- **处理**：Task 3 修正路径

### D2 — concepts/05-packaging-release.md L269：伪造配置键 `packaging.find_opts`

- **位置**：`concepts/05-packaging-release.md` L269（`ns.configure` 的 `packaging` 配置块内）
- **原文**：`"find_opts": "",  # find 命令额外选项`
- **证据**：
  - `invocations/packaging/release.py` 全文 **无** `find_opts` 读取
  - `find_opts` 实际属于 `checks.blacken`（`invocations/checks.py` 读取 `c.config.get("blacken", {})` 的 `find_opts`）
  - [concepts/02-checks-formatting.md#L72-L77](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/build/tooling/invocations/concepts/02-checks-formatting.md#L72-L77) **正确**地将 `find_opts` 归入 `blacken` 配置，反证 05 误写
- **影响**：误导读者以为 release 支持 `packaging.find_opts`；按此配置不生效
- **处理**：Task 4 从 `packaging` 配置块移除 `find_opts`

## 4. 疑似漂移

### S1 — concepts/06-ci-automation.md L166：`ci.sudo.group` 单数书写

- **位置**：`concepts/06-ci-automation.md` L166（"注意事项" prose）
- **原文**：`通过配置 ci.sudo.group 适配其他 CI 环境`
- **证据**：vendor 配置键为 `ci.sudo.groups`（复数，见 `invocations/ci.py` `ns.configure`）
- **影响**：低（prose 层描述性提及，非可执行代码）
- **处理**：Task 4 顺手修正为 `ci.sudo.groups`

## 5. 逐文件核对记录（无问题项）

| 文件 | 核对结论 |
|------|---------|
| references/invocations-source.md | 模块清单、公开导出模式、watch 签名均与 vendor 一致（**仅 L47 路径漂移**） |
| concepts/00-introduction | 模块→CLI 命令映射准确 |
| concepts/01-getting-started | release 任务清单（all/build/prepare/publish/push/status/test-install/upload）、`docs.www.build` 命名空间嵌套准确 |
| concepts/02-checks-formatting | blacken 签名/默认值/别名 format、`find_opts` 归属 `blacken` 正确 |
| concepts/03-testing-pytest | pytest/test/watch_tests/count_errors 均存在并准确 |
| concepts/04-docs-sphinx | build 参数表、clean/browse/doctest/tree、多站点 `_site(name)`→`sites/{name}`、watch 正则全部实测一致 |
| concepts/05-packaging-release | status 三组件/枚举值、分支类型检测、prepare/build/publish/test_install/upload/push 流程准确（**仅 L269 find_opts 漂移**） |
| concepts/06-ci-automation | make_sudouser/sudo_run/make_sshable 及默认配置 user==invoker/password==secret/groups==[sudo,circleci] 准确（**仅 L166 单复数**） |
| concepts/07-utilities-watchers | confirm/tmpdir/in_ci/watch 三层 API、BaseException 容错准确 |
| concepts/08-vendorize | 参数表、PyPI sdist 下载流程、`git_url: pass` 未实现说明准确 |
| concepts/09-autodoc-sphinx | TaskDocumenter/objtype/directivetype/setup(app) 准确 |
| concepts/10-composition-patterns | （架构模式类，无具体 API 漂移） |
| examples/basic-usage | 模块收集/预配置 Collection 命名准确 |
| examples/custom-release-flow | `from invocations.packaging.release import status/prepare/publish/push` 均真实存在 |
| examples/file-watch-auto-test | watch 用法准确 |
| examples/multi-site-docs | docs/www 子集合 + `packaging.package`/`tests.package` 配置准确 |
| examples/test-install-verification | `build`/`get_archives`/`_find_package` 均真实存在，`test-install` CLI 名正确 |
| index.md / log.md / concepts/index.md / examples/index.md / references/index.md | 导航与链接正常 |

## 6. 处理建议（Task 3/4）

1. Task 3：修正 `references/invocations-source.md` L47 路径 → `external/libs/tools/pyinvoke/invocations/invocations/`；并在 frontmatter `sources` 新增本地 vendor 信源条目（满足 checklist 阶段3），上传 `verified` 字段
2. Task 4：移除 `05-packaging-release.md` L269 的 `packaging.find_opts`；修正 `06-ci-automation.md` L166 为 `ci.sudo.groups`；更新受影响文档 `verified` 字段
3. Task 5：log.md 追加本轮审查与更新记录
4. Task 8：按 checklist.md 逐项打勾并以 `git diff` 核对落盘
---
title: "CLI命令参考"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/reference/cli-commands"
date: "2026-07-07"
tags: ["minitest", "cli", "command-line", "命令行", "参考"]
summary: "miniTest CLI命令的完整参考文档，包括全局标志、认证、应用管理、用户故事、配置文件、测试文件、构建和运行命令。"
---

> 来源：https://www.minitap.ai/docs/minitest/reference/cli-commands

# CLI命令参考

这是详尽的参考文档。有关安装步骤和快速介绍，请参阅[Cursor和Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)。

## 全局标志

| 标志 | 缩写 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--version` | `-v` | — | 打印`minitest-cli <version>`并退出。 |
| `--json` | — | off | 将JSON输出到stdout；诊断信息转到stderr。 |
| `--app <id-or-slug>` | — | `$MINITEST_APP_ID` | 目标应用。除`auth`、`apps`、`flow-types`、`skill`、`upgrade`外，每个命令都必需。 |
| `--help` | — | — | 标准帮助。 |

### 退出码

| 代码 | 含义 |
| --- | --- |
| 0 | 成功 |
| 1 | 一般错误（验证、参数错误） |
| 2 | 认证错误 |
| 3 | 网络/API错误 |
| 4 | 资源未找到 |
| 5 | 构建被拒绝为无效（仅`build upload`） |

## auth（认证）

认证管理。

### minitest auth login

运行OAuth 2.0 PKCE浏览器流程并将会话保存到`~/.minitest/credentials.json`。打开浏览器；最多等待两分钟。

### minitest auth logout

删除本地凭据文件。

### minitest auth status

打印当前认证状态：方法（`env_token` / `oauth` / `none`）、用户ID、邮箱、令牌过期时间。支持`--json`。

## apps（应用）

读取工作区和应用元数据。

### minitest apps list

列出您可以看到的所有应用。

### minitest apps create

在工作区中创建新应用。将新应用的UUID打印到stdout。

| 标志 | 必需 | 说明 |
| --- | --- | --- |
| `--name <str>` | 是 | 人类可读的应用名称。 |
| `--tenant <id>` | 否 | 工作区UUID。仅当您属于多个工作区时必需。 |
| `--description <str>` | 否 |  |
| `--slug <str>` | 否 | 如果省略则在服务器端自动生成。 |
| `--icon <path>` | 否 | 本地图片路径；作为multipart上传。 |

示例：

```shellscript
minitest apps create --name "My App" --tenant 3f0e... --icon ./icon.png
```

## user-story（用户故事）

用户故事操作。所有命令都需要`--app`或`MINITEST_APP_ID`。

### minitest user-story create

创建用户故事。

| 标志 | 必需 | 说明 |
| --- | --- | --- |
| `--name <str>` | 是 |  |
| `--type <str>` | 是 | 根据后端类型验证。运行`minitest flow-types list`查看它们。 |
| `--description <str>` | 否 |  |
| `--criteria <str>` | 否 | 验收标准。可重复。 |
| `--depends-on <id>` | 否 | 父用户故事ID。可重复。 |

### minitest user-story list

分页列表。

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--type <str>` | — | 按类型过滤。 |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 | 最大100。 |
| `--all` | off | 自动分页。 |

### minitest user-story get <user-story-id>

通过UUID获取单个故事。

### minitest user-story update <user-story-id>

部分更新。至少需要一个变更标志。

| 标志 | 说明 |
| --- | --- |
| `--name <str>` |  |
| `--type <str>` | 根据后端类型验证。 |
| `--description <str>` |  |
| `--criteria <str>` | **替换**标准集。可重复。 |
| `--add-criteria <str>` | **追加**到标准集。可重复。与`--criteria`互斥。 |
| `--depends-on <id>` | **替换**依赖集。可重复。 |
| `--remove-dependency <id>` | 从当前依赖中减去。可重复。如果同时传递`--depends-on`则被忽略并带有警告。 |

### minitest user-story delete <user-story-id>

硬删除。需要`--force`。

## user-story-binding（用户故事绑定）

将配置文件和文件附加到故事。

### minitest user-story-binding set-profile <user-story-id>

绑定或清除测试配置文件。

| 标志 | 说明 |
| --- | --- |
| `--profile <id>` | 配置文件UUID。 |
| `--clear` | 移除绑定。 |

两者必须恰好选其一。

### minitest user-story-binding set-files <user-story-id>

原子替换绑定到故事的测试文件集。

| 标志 | 说明 |
| --- | --- |
| `--file <id>` | 测试文件UUID。可重复。 |
| `--clear` | 替换为空集。 |

恰好需要一种模式。

### minitest user-story-binding list-files <user-story-id>

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 50 | 最大100。 |

## test-profile（测试配置文件）

应用范围的配置文件（代理用于登录的凭据）。

### minitest test-profile create

| 标志 | 必需 | 说明 |
| --- | --- | --- |
| `--name <str>` | 是 |  |
| `--username <str>` | 否 |  |
| `--password <str>` | 否 | 与`--password-stdin`互斥。 |
| `--password-stdin` | 否 | 从stdin读取密码。 |
| `--about <str>` | 否 | 自由文本备注。 |

示例：

```shellscript
echo "$PASS" | minitest test-profile create --name "QA user" --username qa@x.com --password-stdin
```

### minitest test-profile get <profile-id>

### minitest test-profile update <profile-id>

| 标志 | 说明 |
| --- | --- |
| `--name <str>` |  |
| `--username <str>` |  |
| `--password <str>` | 与`--password-stdin`和`--clear-password`互斥。 |
| `--password-stdin` | 从stdin读取密码。 |
| `--clear-password` | 移除存储的密码。 |
| `--about <str>` | 传递空字符串清除。 |

### minitest test-profile delete <profile-id>

需要`--force`。

### minitest test-profile list

列出应用范围的配置文件。

### minitest test-profile list-shared

列出工作区共享的配置文件（仪表板中**Shared by Minitap**下的那些）。不需要`--app`。

## test-file（测试文件）

应用范围的参考资产（图片、文档、视频、音频）绑定到用户故事。上传上限：25 MB。

### minitest test-file upload <path>

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--name <str>` | 文件基名 |  |
| `--note <str>` | — |  |

MIME类型从扩展名猜测。

### minitest test-file get <file-id>

### minitest test-file update <file-id>

至少需要一个标志。

| 标志 | 说明 |
| --- | --- |
| `--name <str>` |  |
| `--note <str>` | 与`--clear-note`互斥。 |
| `--clear-note` |  |

### minitest test-file delete <file-id>

需要`--force`。

### minitest test-file list

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--kind <kind>` | — | `image`、`document`、`video`、`audio`、`other`之一。 |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 | 最大100。 |

## flow-types（流程类型）

### minitest flow-types list

打印每个有效的用户故事类型，每行一个（使用`--json`时为JSON数组）。

## app-knowledge（应用知识）

读取和更新每个应用的**Mini记忆**提示，用于接地代理运行。两个子命令都需要内联传递`--app`。

### minitest app-knowledge get

```shellscript
minitest app-knowledge get --app 3f0e...
```

### minitest app-knowledge update

| 标志 | 必需 | 说明 |
| --- | --- | --- |
| `--app <id>` | 是 |  |
| `--content <str>` | 二选一 | 内联markdown。 |
| `--content-file <path>` | 二选一 | markdown文件路径。 |

```shellscript
minitest app-knowledge update --app 3f0e... --content-file ./app_knowledge.md
```

## build（构建）

### minitest build upload <file>

上传`.apk`或`.ipa`。服务器在接受之前验证构建的虚拟设备兼容性。

| 标志 | 说明 |
| --- | --- |
| `--platform <ios\|android>` | 如果省略则从扩展名自动检测。 |

iOS构建必须是Simulator构建。Android构建必须兼容x86_64。

### minitest build list

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--platform <ios\|android>` | — | 过滤。 |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 |  |
| `--all` | off | 自动分页。 |

## run（运行）

故事运行执行。所有子命令都需要`--app`或`MINITEST_APP_ID`。启动运行至少需要`--ios-build` / `--android-build`之一。

### minitest run start <user-story>

为一个用户故事启动运行。`<user-story>`是UUID或不区分大小写的名称匹配。

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--ios-build <id>` | — | iOS构建UUID。 |
| `--android-build <id>` | — | Android构建UUID。 |
| `--watch / --no-watch` | `--watch` | 每2秒轮询一次，直到运行达到终端状态。 |

### minitest run status <run-id>

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--watch / --no-watch` | `--no-watch` | 如果设置且运行非终端，每2秒轮询。 |

### minitest run list <user-story>

一个故事的历史运行。`<user-story>`是名称或UUID。

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--status <str>` | — | `pending`、`running`、`completed`、`failed`、`cancelled`之一。 |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 |  |
| `--all` | off | 自动分页。 |

### minitest run cancel <run-id>

取消待处理或正在运行的故事运行。

### minitest run all

启动覆盖应用每个用户故事的运行。即发即弃 — 打印运行ID并退出。

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--ios-build <id>` | — |  |
| `--android-build <id>` | — |  |

## batch（批次）

CLI使用术语"batch"表示多故事运行（在仪表板中点击一次**Run tests** = 一个batch）。

### minitest batch list

| 标志 | 默认值 | 说明 |
| --- | --- | --- |
| `--status <str>` | — | 按状态过滤。可重复。 |
| `--result <str>` | — | 按结果过滤。可重复。 |
| `--commit-sha <str>` | — |  |
| `--user-story-id <id>` | — | 限制为包含此故事的批次。 |
| `--search <str>` | — | 自由文本搜索。 |
| `--page <int>` | 1 |  |
| `--page-size <int>` | 20 | 最大100。 |
| `--all` | off | 自动分页。 |

### minitest batch get <batch-id>

包含每个故事运行的完整批次payload。

### minitest batch cancel <batch-id>

取消批次及其中每个待处理或正在运行的故事运行。

## maintenance-check（维护检查）

### minitest maintenance-check <commit-sha>

确认已针对给定提交审查了测试。用于在"测试最新"状态上门禁CI。该命令直接在组上运行 — 没有子命令。

```shellscript
minitest --app myapp maintenance-check 0a1b2c3d4e5f...
```

## skill（技能）

### minitest skill

获取CLI的最新代理技能（教导AI编码代理如何驱动它的提示）并打印到stdout。

```shellscript
minitest skill > minitest-skill.md
```

## upgrade（升级）

### minitest upgrade

自更新CLI并刷新代理技能。检测您是通过Homebrew还是`uv`安装的，并运行正确的升级命令，然后如果技能内容已更改则重新安装。

---

> **下一章**：[术语表 →](03-glossary.md)

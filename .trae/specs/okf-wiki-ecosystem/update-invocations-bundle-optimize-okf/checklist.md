# Checklist

## 阶段 1：源头复基线
- [x] 版本确认为 4.1.0（pyproject.toml）
- [x] 真实模块清单完整记录，且明确**无** `packaging/version.py`
- [x] facts.md 事实零推测、每条标注 vendor 源码路径
- [x] Task 函数签名/参数默认值/配置键路径均来自真实源码

## 阶段 2：对抗性审查
- [x] 全部 22 文件已遍历，收集引用清单
- [x] 每个引用的模块名/任务名/参数在 vendor 源码 Grep 验证通过或标记为漂移
- [x] 漂移项已定位到具体文件+行，审查报告输出到 spec 目录

## 阶段 3：更新 bundle
- [x] references/invocations-source.md 模块清单与真实源码一致
- [x] 已新增指向本地 vendor 源码路径的信源条目
- [x] 引用 `packaging/version.py` 的文档已修正为真实模块名（仅 log.md 历史记录提及，已由 facts.md/08-24 记录澄清）
- [x] 受影响文档 `verified` 字段已更新（references + 05 + 06）
- [x] log.md 已追加审查与更新记录
- [x] 交叉链接无断裂（无 `../` 风格、指向存在的文件）

## 阶段 4：项目优化
- [x] tasks.py 存在，含 `build`/`clean` 任务，`invoke build` 等价 sphinx-build 命令
- [x] pyproject.toml doc 依赖含 `invoke` 与 `invocations==4.1.0`
- [x] CI pages.yml 使用任务化命令入口（`invoke build`）
- [x] `invoke build` 本地运行成功产出 `_build/html/index.html`
- [x] `invoke clean` 本地运行生效

## 阶段 5：验证与沉淀
- [x] "修复即闭环"：以 `git diff`/磁盘核对所有变更已真实落盘
- [x] 模式文档含触发场景/核心步骤/反模式（≥5）/迁移验证
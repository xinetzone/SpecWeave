# Tasks

- [x] Task 1: 梳理两份仓库的层级定位与职责边界
  - [x] SubTask 1.1: 提取并记录两份仓库的入口文件与目录结构（README、pyproject/requirements、scripts、核心目录）
  - [x] SubTask 1.2: 基于仓库元数据与构建入口，给出“主从/并列外部依赖/子模块/拷贝引入”等关系判定与依据

- [x] Task 2: 双向扫描代码调用与技术依赖关系（含证据链）
  - [x] SubTask 2.1: 在 `home-assistant/core` 内检索 `tuya-openclaw` / `openclaw` / `tuya-smart-control` 等关键符号与潜在引用路径
  - [x] SubTask 2.2: 在 `tuya-openclaw-skills` 内检索 `homeassistant.*` / `hass` / `Home Assistant` 等关键符号与潜在引用路径
  - [x] SubTask 2.3: 输出检索策略、命中统计、代表性命中点（若为 0 命中则记录“未发现”证据）

- [x] Task 3: 梳理 Home Assistant Core 内与 Tuya 相关的核心能力/组件
  - [x] SubTask 3.1: 定位并总结 `homeassistant/components/tuya/` 的依赖声明、核心模块与数据流关键点
  - [x] SubTask 3.2: 判断这些能力是否可被 `tuya-openclaw-skills` 复用（直接依赖 vs 仅可作为参考实现）

- [x] Task 4: 分析版本管理、构建打包与发布协作关系
  - [x] SubTask 4.1: 提取两份仓库的 Git 形态信息（是否独立仓库、remote、分支/HEAD 形态等）
  - [x] SubTask 4.2: 总结两份仓库的构建/打包入口与依赖安装方式，判定是否存在绑定发布或独立迭代

- [x] Task 5: 输出《关系说明文档》并完成可追溯性自检
  - [x] SubTask 5.1: 在本 spec 目录产出 `relationship-report.md`，包含：依赖拓扑图、核心交互流程图、关联点清单、证据链与复现步骤
  - [x] SubTask 5.2: 自检 Mermaid 可渲染、所有关键结论可通过“复现步骤”验证，且引用不包含本地绝对链接（file:///）

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 1
- Task 5 depends on Task 2
- Task 5 depends on Task 4

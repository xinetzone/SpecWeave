# Tasks

- [x] Task 0: 明确最小闭环边界与适用假设
  - [x] SubTask 0.1: 明确闭环的“最小设备形态”假设（如：Linux 开发板/SoC IPC、带 Wi-Fi、具备音视频采集输入）
  - [x] SubTask 0.2: 明确闭环的“最小移动端形态”假设（优先使用 Tuya Smart/Smart Life 官方 App 完成绑定与控制）
  - [x] SubTask 0.3: 明确闭环的“最小云侧形态”假设（Tuya IoT 平台 + 云项目 + IPC 产品 PID）

- [x] Task 1: 编写《Tuya IPC 最小闭环跑通路径》知识库文档
  - [x] SubTask 1.1: 写清楚端-云-手机闭环架构与数据流（含 Mermaid 依赖关系图）
  - [x] SubTask 1.2: 输出前置准备清单（账号/产品创建/授权材料/工具链/依赖版本）
  - [x] SubTask 1.3: 输出全流程步骤（每步包含：操作节点、依赖条件、验收标准、排查方向）
  - [x] SubTask 1.4: 明确 5 个核心功能节点（配网、音视频、绑定、控制、事件）并给出最小实现与验证方法
  - [x] SubTask 1.5: 输出最小闭环验收总表（勾选式）

- [x] Task 2: 更新知识库索引与可发现性
  - [x] SubTask 2.1: 在 `docs/knowledge/README.md` operations 分类登记新文档入口
  - [x] SubTask 2.2: 若索引为脚本生成，执行索引生成脚本并确认新条目可检索

- [x] Task 3: 自检一致性与可执行性
  - [x] SubTask 3.1: 对照 checklist.md 逐项核验文档信息无缺漏（尤其是依赖条件与验收标准）
  - [x] SubTask 3.2: 抽样选择 2-3 个关键步骤进行“可执行性”审阅（操作节点是否可按文档直接执行）

# Task Dependencies

- Task 1 依赖 Task 0 完成（边界与假设明确后才能保证步骤不跑偏）
- Task 2 依赖 Task 1 完成（文档文件存在后才能登记索引）
- Task 3 依赖 Task 1、Task 2 完成（内容与入口齐备后再做自检）

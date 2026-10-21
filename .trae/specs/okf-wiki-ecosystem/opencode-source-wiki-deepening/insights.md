---
type: spec
source: "facts.md"
---

# I 阶段洞察与知识地图

## 洞察一：配置优先级属于消费链，而非通用深合并对象

- **陈述**：本快照把来源顺序与领域消费分开；同一个 entries 序列由不同插件转化为技能、指令和压缩设置。
- **证据**：F-115～F-122。
- **反常识**：看到 global/project/settings 文件不能仅靠“最后配置覆盖一切”解释；字段选取、技能同 ID 覆盖、指令组合各有独立语义。
- **行动**：先定位 discovery 来源，再找领域插件的消费循环，最后核对 Session 状态；异常定位按此顺序逐层记录。

## 洞察二：执行环境复用不等于预算与校验自动生效

- **陈述**：codemode 复用 prepared runtime，逐次新建执行状态；可选预算必须显式接线，输入校验取决于 schema 形态。
- **证据**：F-123～F-130。
- **反常识**：解释器不是宿主 eval，但不能据此断言进程级隔离；有 limits 类型也不表示 Core 已传入；JSON Schema 呈现不表示运行时解码。
- **行动**：审读工具执行时并列检查 runtime 生命周期、make 参数、decodeInput、hooks 与输出裁剪，避免把局部限制写成整体安全保证。

## 洞察三：扩展信息、加载许可和运行生命周期是不同契约

- **陈述**：Schema 的插件信息是可见契约；Core module policy 与 activation 决定加载；Scope/cleanup 承载释放。
- **证据**：F-131～F-135。
- **反常识**：Info 的 active/failed 不能独立说明重载顺序；重新排列失败插件也不一定触发相同 revision 重试。
- **行动**：从公共 Schema 入手，追到 module → activation → hook → finalizer，独立区分 pending、failed 和健康 fallback。

## 洞察四：“完成”必须标注是哪一层的确认

- **陈述**：TUI 写成功后更新状态；App 先变状态后延迟写；Desktop ACK 返回 revision 后还有 SQLite write-behind。
- **证据**：F-136～F-140。
- **反常识**：响应式状态更新、RPC resolve 或某层 flush resolve 都不能通用地等价为数据已持久保存；失败排队仍可能存在。
- **行动**：对每端画出调用顺序（用文字轨迹即可），标记确认点与失败归属；排查先问“哪一层返回成功”，再找更下层的写入证据。

## 洞察五：可复现路径与交付路径都需要显式失败边界

- **陈述**：simulation 控制请求流，recorder 回放固定交互；云端 proxy/统计/对象服务与 updater 则各自处理不同的失败与确认。
- **证据**：F-141～F-151。
- **反常识**：终端 JSONL 不是 HTTP cassette；CI auto replay 不是所有模式禁网；public proxy 源码不证明计费正确；更新 ready 不是 installed。
- **行动**：分别选择模型驱动、HTTP匹配、终端时间线的验证对象；读云端与更新时记录代理响应、统计重试、etag保护、暂存与安装交接，不替未读代码或未运行环境作保证。

## 增量知识地图

| 文件 | 新事实覆盖 | 前置与读者 |
|---|---|---|
| concepts/10-config-context-resolution.md | F-115～F-122 | 先读旧包地图05；上下文配置学习者入口 |
| concepts/11-codemode-runtime-boundaries.md | F-123～F-130 | 建议先读工具07；工具与解释器开发者 |
| concepts/12-plugin-contract-lifecycle.md | F-131～F-135 | 先读API08；扩展开发者 |
| concepts/13-product-state-persistence.md | F-136～F-140 | 先读产品09；客户端与持久化排查 |
| concepts/14-simulation-record-replay.md | F-141～F-146 | 建议先读会话06；测试与验证学习者 |
| concepts/15-cloud-update-boundaries.md | F-147～F-151 | 先读产品09，再读回放14；工程边界收束 |
| examples/03-state-and-replay-reading-lab.md | F-136～F-151 | 先读13～15；静态源码核验练习，不是运行脚本 |

E 第一批仅创建 references/source-deepening-2.0.32.md，随后创建 spec/facts-deepening-2.0.32.md 与 spec/insights-deepening-2.0.32.md，再分批写概念与导读；各级 index 最后更新。
G2 自验：五组四元组齐全；六主题均映射到概念，新增编号不覆盖旧文件。TR-5.2=3/3，有前置、读者分层和静态验证导读。

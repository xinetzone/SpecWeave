# remote 消息通信生态 OKF Wiki - 验证清单

## 目录结构
- [ ] bundles/messaging/ 目录存在
- [ ] messaging/index.md 存在且含 type: category frontmatter 和 okf_version: "0.2"
- [ ] 4 个知识束目录（libzmq/cppzmq/pyzmq/dramatiq）均存在
- [ ] 每个知识束含 concepts/、examples/、references/、spec/ 四个子目录
- [ ] 每个知识束含根 index.md（type: bundle + okf_version: "0.2"）和 log.md
- [ ] 每个子目录（concepts/examples/references）含 index.md（无 frontmatter）

## R 阶段事实质量
- [ ] 每个知识束 spec/facts.md 存在
- [ ] facts.md 中每条事实有编号 F-xxx
- [ ] 每条事实标注源码文件路径与行号
- [ ] 事实中无"用于"/"目的是"/"设计为"等推断性表述
- [ ] libzmq ≥60 条事实，cppzmq ≥30 条，pyzmq ≥45 条，dramatiq ≥45 条
- [ ] 核心模块全覆盖（libzmq: ctx/socket_base/session_base/pipe/zmtp_engine/io_thread/poller/msg/mailbox；cppzmq: zmq.hpp/zmq_addon.hpp；pyzmq: sugar/_future/asyncio/backend/auth/eventloop/green/devices；dramatiq: actor/broker/worker/message/middleware/encoder/results/cli/watcher）

## I 阶段洞察质量
- [ ] 每个知识束 spec/insights.md 存在
- [ ] 每个洞察含四要素：陈述、证据（引用 F-xxx）、反常识点、行动建议
- [ ] 知识地图明确 concepts 文档列表及每篇覆盖的 F-xxx 范围
- [ ] 设计了学习路径（从入门到高级）

## E 阶段文档生成
- [ ] references/ 信源文件先于 concepts/ 生成（信源先行）
- [ ] libzmq: concepts/ ≥12 篇，references/ ≥6 篇，examples/ ≥3 篇
- [ ] cppzmq: concepts/ ≥5 篇，references/ ≥2 篇，examples/ ≥2 篇
- [ ] pyzmq: concepts/ ≥7 篇，references/ ≥4 篇，examples/ ≥2 篇
- [ ] dramatiq: concepts/ ≥7 篇，references/ ≥4 篇，examples/ ≥2 篇
- [ ] 每批生成 ≤7 个文件
- [ ] index.md 在所有内容文档定稿后最后生成
- [ ] 概念文档按 NN-kebab-case.md 编号命名
- [ ] 中文正文，英文技术术语首次出现括号注释
- [ ] 代码块标注语言（c++/python/bash 等）
- [ ] 每个概念文档结尾有"相关概念"章节

## Frontmatter 合规
- [ ] 每个非保留 .md 文件含可解析 YAML frontmatter
- [ ] 每个 frontmatter 含非空 type 字段
- [ ] 概念/示例/信源文档含 title、description、tags、sources、generated、verified、status、stale_after
- [ ] 根 index.md 含 okf_version: "0.2"
- [ ] 子目录 index.md 无 frontmatter
- [ ] sources 字段指向存在的 references/ 文件和具体源码路径

## V 阶段 API 真实性
- [ ] 文档中引用的每个 C++ 类名/函数名在 libzmq/cppzmq 源码中 Grep 命中
- [ ] 文档中引用的每个 Python 类名/方法名在 pyzmq 源码中 Grep 命中
- [ ] 文档中引用的每个 Python 类名/方法名在 dramatiq 源码中 Grep 命中
- [ ] 代码示例中的 API 调用签名与源码一致
- [ ] 无虚构 API（0 个未命中引用）

## 链接完整性
- [ ] 所有 `/` 开头的 bundle-relative 内部链接目标文件存在
- [ ] 无 `../` 相对路径链接
- [ ] 无 `file:///` 绝对路径链接
- [ ] 各 index.md 列出的文档链接均有效
- [ ] 概念文档间的"相关概念"链接有效

## 分组与根索引
- [ ] messaging/index.md 含 4 个知识束概览表（含概念/示例/信源计数）
- [ ] messaging/index.md 含生态关系图（libzmq 核心 → cppzmq/pyzmq 绑定 → dramatiq 上层任务队列）
- [ ] messaging/index.md 含推荐学习路径
- [ ] bundles/index.md 新增 messaging 分组条目
- [ ] bundles/index.md total_bundles 计数 +4
- [ ] bundles/index.md groups 计数 +1
- [ ] bundles/index.md 分组导航表和分组详情均含 messaging 章节

## 安全与边界
- [ ] 未修改 external/libs/remote/ 下任何源码文件
- [ ] 未修改 projects/awesome-okf-xs/.agents/ 下任何规范文件
- [ ] pyzmq 教程为原创教育内容，非向 pyzmq 上游贡献

# Checklist

## 覆盖完整性
- [x] `external/libs/rust-lang/` 下全部 3 个子文件夹（rust/cargo/rfcs）各有对应 bundle 与事实清单
- [x] rust 仓库覆盖：编译器流水线各阶段 crate、标准库 core/alloc/std 分层、bootstrap 构建系统均有概念文档

## G1-R 阶段：事实零推测
- [x] facts-rust.md / facts-cargo.md / facts-rfcs.md 中事实编号连续（133/144/177 条），每条含源码路径，无"用于/目的是/设计为"等推断性表述（三子代理独立自检通过）

## G2-I 阶段：洞察四元组
- [x] insights.md 中每条洞察含陈述、证据（F-xxx 引用）、反常识、行动四要素（12 条），并有知识地图与学习路径设计（454 事实 100% 映射）

## G3-E 阶段：生成纪律
- [x] 三个 bundle 均满足：references/ 先于 concepts/ 生成，各级 index.md 最后生成，每批 concepts/ 文档数 ≤7 文件
- [x] 每个 bundle 根 index.md 含 `okf_version: "0.2"` frontmatter 与 `{toctree}`；log.md 存在；子目录 index.md 无 frontmatter
- [x] 所有内容文档 frontmatter 含 type/title/description/tags/generated/verified/status/stale_after/sources，sources 指向已存在的信源文件
- [x] 概念文档中文撰写，英文术语首次出现括号注释，`##` 分节，结尾有"相关概念"，交叉链接为 `/` 开头 bundle-relative 路径

## G4-V 阶段：验证与质量门
- [x] 文档中引用的 rustc_* crate 名、struct、方法、配置键、RFC 编号经 Grep 源码验证存在，零虚构 API（~112 验证点，15 类计数虚构全部修复，验证报告见各 V 子任务产出）
- [x] 所有交叉链接指向存在的文件，无断裂（无 `../`、无 `file:///`）
- [x] awesome-okf-xs 内 `invoke gates.toctrees`：rust 域零问题（过滤验证）；全仓报 52 处不可达全部位于 containers/ 域，系并行任务存量问题，不在本 spec 范围
- [x] awesome-okf-xs 内 `invoke gates.utf8` 通过（5601 文件 UTF-8 无 BOM）
- [x] `external/libs/rust-lang/` 源码零修改（全程只读）

## 根索引与元数据
- [x] `bundles/index.md` 更新：含 rust 域导航行、mermaid 生态图与入门路径 rust 节点、toctree 含 rust/index；frontmatter 计数与磁盘自洽（268 束/32 组/13 域——含并行 protobuf 任务贡献，rust 自身 +3 束/+1 组/+1 域）
- [x] `rust/index.md` 域索引存在且含三个 bundle 的学习路径表与 toctree

## G5-C 阶段：模式沉淀
- [x] 超大规模 monorepo 分层采样经验已沉淀（`.trae/specs/rust-lang-okf-wiki/patterns.md`：2 模式、6 反模式）
- [x] tasks.md 全部勾选，spec 三件套齐备（另含 facts×3、insights、patterns）

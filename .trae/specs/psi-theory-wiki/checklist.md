# Ψhē 理论体系 OKF Wiki 教程 - 验证清单

## 结构与规范

- [x] CP-1: `bundles/psi/` 目录存在，含 `index.md`（带 `okf_version: "0.2"` frontmatter）
- [x] CP-2: 4 个知识束子目录（psi-core/psi-math/psi-universe/godgpt）均存在
- [x] CP-3: 每个知识束含 `index.md`、`log.md`、`concepts/`、`examples/`、`references/`
- [x] CP-4: 子目录 `index.md`（concepts/examples/references 下的）不含 frontmatter
- [x] CP-5: 文件命名使用 kebab-case 英文，无中文文件名
- [x] CP-6: 每个概念文档 500-5000 字符

## Frontmatter 合规

- [x] FM-1: 所有非 index.md 文件含可解析的 YAML frontmatter
- [x] FM-2: 每个 frontmatter 含非空 `type` 字段
- [x] FM-3: 每个概念文档含 `title`、`description`、`tags`
- [x] FM-4: 每个文档含 `generated: { by: ..., at: ... }`
- [x] FM-5: 每个文档含 `verified: { by: "process:seven-concepts-v", at: ... }`
- [x] FM-6: 每个文档含 `status: draft`（首次生成）
- [x] FM-7: 每个文档含 `stale_after` 日期
- [x] FM-8: 每个文档含 `sources` 列表，每个 source 有 `id`、`resource`、`title`

## 信源与溯源

- [x] SR-1: references/ 文件先于 concepts/ 文件生成（信源先行）
- [x] SR-2: 每个知识束的 references/ 下有 ≥2 个信源文件
- [x] SR-3: 信源文件 `type: Reference`，含有效 URL 或本地路径
- [x] SR-4: 概念文档的 sources[].resource 指向的 references 文件实际存在
- [x] SR-5: 三个网站 URL（godgpt.fun、dw.cash、math.dw.cash）均在 references 中登记
- [x] SR-6: 本地路径（external/dao/AllTheory/）在 references 中登记

## 内容准确性

- [x] CA-1: ψ=ψ(ψ) 核心方程在 psi-core 中准确表述
- [x] CA-2: 塌缩（Collapse）、回声（Echo）、观察者等核心概念定义与源材料一致
- [x] CA-3: psi-math 中 RH 证明结构反映 math.dw.cash 的实际内容
- [x] CA-4: psi-universe 中三大公理和 XOR-SHIFT 操作层级准确
- [x] CA-5: universe 维度谱系（D0-D∞）与源文件分类一致
- [x] CA-6: GodGPT 产品信息（功能、定价、法律）与 godgpt.fun 一致
- [x] CA-7: 无虚构的 API、术语、公式或定理名称
- [x] CA-8: 理论体系的"思想实验"免责声明在 references 中保留

## 交叉链接

- [x] CL-1: 所有 `/` 开头的 bundle-relative 链接目标文件存在
- [x] CL-2: 无 `../` 相对路径（统一使用 `/` 开头路径）
- [x] CL-3: 无 `file:///` 绝对路径
- [x] CL-4: 每个概念文档结尾有 `## 相关概念` 章节
- [x] CL-5: 跨知识束链接使用正确路径（如 `/psi-core/concepts/00-psi-equation.md`）

## Index 完整性

- [x] IX-1: 每个知识束根 index.md 列出所有 concepts、examples、references 文件
- [x] IX-2: concepts/index.md 列出所有概念文档
- [x] IX-3: index.md 中列出的文件均实际存在
- [x] IX-4: 无遗漏的概念文档（所有生成的 .md 文件都在某个 index 中列出）
- [x] IX-5: `bundles/psi/index.md` 分组索引列出 4 个知识束

## 总索引更新

- [x] TI-1: `bundles/index.md` 分组导航表含 psi 分组行
- [x] TI-2: `bundles/index.md` 分组详情含 psi 的 4 个知识束条目
- [x] TI-3: total_bundles 和 groups 计数已更新
- [x] TI-4: psi 分组链接指向正确路径

## 生成纪律

- [x] GD-1: 分批生成，每批 ≤ 7 个内容文件
- [x] GD-2: references/ 在 concepts/ 之前生成
- [x] GD-3: index.md 在所有内容文件之后最后生成
- [x] GD-4: 所有文档使用中文撰写
- [x] GD-5: 英文术语首次出现时有括号注释
- [x] GD-6: 数学公式使用 LaTeX 格式（`$` 或 `$$`）

## 内容覆盖度

- [x] CV-1: psi-core 覆盖 ≥8 个核心概念（方程/塌缩/回声/观察者/语言/现实/元递归/统一）
- [x] CV-2: psi-math 覆盖 ≥6 个数学主题（theory_psi/CST/RH/坍缩数学/常数/ZFC）
- [x] CV-3: psi-universe 覆盖 ≥6 个主题（公理/操作/递归/维度/本体论/信息场）
- [x] CV-4: godgpt 覆盖 ≥4 个主题（定位/功能/商业/法律）
- [x] CV-5: 17 部 alltheory 著作在 psi-core 中均有提及或覆盖
- [x] CV-6: universe 的 778 个理论文件在 psi-universe 中按学科分类概览

# 打印与分发指引（Print & Distribution Guide）

> **配套**：[`TEACHER-GUIDE.md`](TEACHER-GUIDE.md) 第〇节 | [`SETUP-CHECKLIST.md`](SETUP-CHECKLIST.md)
> **用途**：告诉教师"哪几份要打印、给学生哪几份、怎么转 PDF"。
> **耗时**：首次 10 分钟；后续复用同一批 PDF 即可。

---

## 一、先看这个：五份文件该怎么用

教师包共 5 份文档，**只有 1 份需要每组分发**：

| 文件 | 给谁 | 份数 | 处理方式 |
|---|---|---|---|
| [`SCORING-SHEET.md`](SCORING-SHEET.md) | **每小组 1 份** | **N 组** | ✅ **必须打印**（教师边评边填） |
| [`TEACHER-GUIDE.md`](TEACHER-GUIDE.md) | 教师本人 | 1 | 打印或存平板/手机随时查 |
| [`SETUP-CHECKLIST.md`](SETUP-CHECKLIST.md) | 教师本人 | 1 | **开课前**打印勾选，用完可归档 |
| [`FAQ.md`](FAQ.md) | 教师本人 | 1 | 打印或旁置（课堂应急翻查） |
| [`S7-FIELD-CAPTURE-SPEC.md`](S7-FIELD-CAPTURE-SPEC.md) | 教师本人 | — | ⏸ **暂不用打印**（前置条件：真实课程跑完一轮） |

> 🎯 **一句话**：**只打印评分表，份数 = 小组数**。其余四份教师自用。
>
> ⚠️ **不要把手册（`handbook/`）当答案发**——它是学生用的，学生自己看。
> 教师如需对照，直接打开 `handbook/task-N-*.md` 即可。

---

## 二、怎么转成 PDF（3 种方式，任选）

### 方式 A：浏览器打印（最简，推荐）

1. 用 VS Code / Typora / 任意 Markdown 预览器打开 `.md`
2. `Ctrl+P`（macOS `Cmd+P`）→ 目标选 **"另存为 PDF"**
3. 关键设置：
   - **纸张**：A4
   - **边距**：默认
   - **勾选**「背景图形」（否则 `- [ ]` 勾选框可能不显示）
   - **缩放**：`默认` 或 `适合页面`

> 💡 **VS Code 用户**：装 `Markdown Preview Enhanced` 插件，
> 命令面板 → `Markdown Preview Enhanced: Chrome (Puppeteer) → PDF`，排版更整齐。

### 方式 B：pandoc 批量转（多份一起转）

> ⚠️ **先说结论**：pandoc 转 PDF **需要先装 LaTeX**（`xelatex`）。
> 多数机房没有装，因此**下面这条 PDF 命令在多数环境会失败**。
> 若你不确定装没装，**跳过方式 B，直接用方式 A**。

```bash
# ⚠️ 前置条件：已安装 LaTeX（xelatex 在 PATH 中）。未装则报 "xelatex not found"
cd teacher
for f in SCORING-SHEET.md TEACHER-GUIDE.md SETUP-CHECKLIST.md FAQ.md; do
  pandoc "$f" -o "${f%.md}.pdf" --pdf-engine=xelatex -V CJKmainfont="Microsoft YaHei"
done
```

**没有 LaTeX？用 HTML 中转（无需任何额外依赖，已实测可用）**：

```bash
cd teacher
for f in SCORING-SHEET.md TEACHER-GUIDE.md SETUP-CHECKLIST.md FAQ.md; do
  pandoc "$f" -o "${f%.md}.html" --standalone --metadata title="教师材料"
done
# 然后用浏览器打开 .html → Ctrl+P → 另存为 PDF（即方式 A）
```

> ✅ HTML 中转这条路径**已实测通过**（pandoc 3.8，无需 LaTeX）。
> 它把 pandoc 的优点（批量、保留表格结构）和方式 A 的优点（不需 LaTeX）合在一起。

### 方式 C：不转 PDF，直接共享盘发 `.md`

若学生的编辑器/浏览器能渲染 Markdown（VS Code、Typora、GitHub 网页），
**直接把 `.md` 发出去也可以**——教师打印评价表用纸质，学生看手册用电子版，
两不冲突。

---

## 三、打印时的格式注意

| 文档 | 注意点 |
|---|---|
| **`SCORING-SHEET.md`** | ⚠️ **档 C 的班级请打印第五节的"折半版"**，不是标准版 |
| `SCORING-SHEET.md` §六 | 现场答辩记录表在**第六节**，可与主表同页打印或单独抽页 |
| `SETUP-CHECKLIST.md` | 全是 `- [ ]` 勾选框 —— **必须勾选"背景图形"**，否则框可能不渲染 |
| `TEACHER-GUIDE.md` | 较长（384 行），建议**双面打印**或只打"课时编排"章节 |

> 📌 **为什么要特意说明"勾选背景图形"**：Markdown 的 `- [ ]` 在浏览器打印时
> 属于**背景渲染**范畴，若"背景图形"未勾选，打印结果可能只剩空行——
> 教师会以为文件坏了。**请打印前先打一张试印页确认**。

---

## 四、分发清单（开课前对照打勾）

- [ ] `SCORING-SHEET.md` 已打印 **N 份**（N = 小组数），并按档位选对版本
- [ ] `SETUP-CHECKLIST.md` 已打印 1 份，开课前逐项勾选完毕
- [ ] `TEACHER-GUIDE.md` 已备好（纸质或电子）
- [ ] `FAQ.md` 已备好（课堂应急）
- [ ] 学生手册（`handbook/`）**未混入**教师材料 —— 确认没把它当答案发出去
- [ ] 若走内网/离线档：`handbook/shots/` 中的示意图已确认可离线打开

---

## 五、为什么不提供 DOCX / PPT

本方案**刻意不产出**教师 DOCX 与 PPT（见 [`../spec.md`](../spec.md) 第三节 Non-Goals）。理由：

| 质疑 | 回答 |
|---|---|
| "DOCX 不是更通用吗？" | 教师包是**表格 + 勾选框**结构，Markdown 打印/导出 PDF 均已满足；换成 DOCX 是**零收益变更** |
| "Word 里能改啊" | 需要改就直接改 `.md`（纯文本，比 Word 更容易版本化），或用 pandoc 随时转 |
| "那 PPT 呢？" | `handbook/task-7-showcase.md` 里的"路演 PPT"是**学生提交物**，不是教师材料 |
| "维持两份格式不行吗？" | **不行**——一份内容两种格式，改一处漏一处，这是本项目 R8–R12 反复抓到的缺陷类型 |

> 🎯 **判据（可迁移）**：**交付物的形态由使用场景决定，不由格式偏好决定。**
> 动手转换之前先问：**现在这份东西，教师打开 PDF 打印一下，能用吗？**
> 能用就不转。

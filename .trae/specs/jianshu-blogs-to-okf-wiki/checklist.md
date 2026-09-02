# Checklist

## 阶段 0/1：信源采集与事实登记（R 阶段）

- [ ] 三个简书连载（nb/46194813、nb/40234132、nb/47487870）全部文章正文已抓取并保存至 `.trae/specs/jianshu-blogs-to-okf-wiki/raw/`
- [ ] `facts.md` 已登记编号事实（F-xxx），每条标注来源 URL 与内容时点，零推测（无"用于/目的是"类推断词）

## 阶段 2：洞察与知识地图（I 阶段）

- [ ] `insights.md` 含各 notebook 核心洞察（陈述/证据/反常识/行动四元组）
- [ ] 束结构与放置已确定：networkx/pillow 入 `jishu/data/pydata/`，dev/autonomous 为新分组
- [ ] 每束 concepts/examples/references 文档清单与学习路径已设计

## 阶段 3：批量生成（E 阶段）

- [ ] matplotlib 束已扩展（补齐事件处理、patches/path、分形示例），其 index/log 已同步
- [ ] networkx 束已生成（节点与边、路径绘制、DAG 画神经网络、布局样式）
- [ ] pillow 束已生成（图像基础、缩放合成、ImageDraw 绘制、图像特效）
- [ ] dev 分组已生成（git/github/opensource 三束 + 组 index）
- [ ] autonomous 分组已生成（autoware/ros2/dds/ecosystem 四束 + 组 index）
- [ ] 所有文档遵循 OKF v0.2 frontmatter；子目录 index.md 不含 frontmatter；交叉链接用 `/` 开头路径
- [ ] 每束含 `log.md`；references/ 信源登记先行；单批生成 ≤7 文件

## 阶段 4：索引对账与独立验证（V 阶段）

- [ ] `jishu/data/pydata/index.md`、`jishu/index.md`、`doc/bundles/index.md` 已同步（表 + toctree + 计数）
- [ ] `invoke gates.all` 三门全绿（utf8 / toctrees / bundles）
- [ ] `sphinx-build` 零错误零警告
- [ ] 计数断言验证通过（"X 篇/个/束"类陈述经 Glob/Grep 独立复核）
- [ ] 过时内容现状校正已抽查标注（2020 年时点 + 当前版本差异说明，有信源依据）

## 阶段 5：原子提交（C 阶段）

- [ ] 已检查 `.git/MERGE_HEAD` 与并行会话暂存区（yixue/tcm、medicine 等未被触碰）
- [ ] 暂存集经 `git diff --cached --name-only` 核对，仅含本任务文件
- [ ] 提交信息为 Conventional Commits 中文主体；存在竞态时已停止并如实报告

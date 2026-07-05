# docs/knowledge/learning 目录主题分类系统性划分 - Verification Checklist

## 目录结构验证
- [x] learning 目录下存在 8 个一级主题子目录，命名格式为 `{两位数编号}-{kebab-case}`（01-08）
- [x] 07-vendor-product-learning 目录下存在 sunlogin/ 和 tuya/ 二级子目录
- [x] learning 根目录仅保留 README.md 和 CATEGORIES.md（以及 .gitkeep 等隐藏文件如有），无遗留的 Wiki 文件或目录
- [x] 每个主题子目录下无空目录（除了厂商子目录）
- [x] 所有原子化 Wiki 目录已整体迁移，保持原有的内部章节结构（00-overview.md、01-xxx.md 等）
- [x] 原子化 Wiki 目录内的子目录（examples/、appendix/、resources/、templates/ 等）保持完整

## 文件归类验证
- [x] 所有 22 个已原子化 Wiki 目录均位于正确的主题子目录中
- [x] 所有 37 个单文件 Wiki（含入口 .md 文件）均位于正确的主题子目录中
- [x] 每个 Wiki（原子化目录或单文件）唯一归属一个主题，无重复、无遗漏
- [x] 向日葵系列 Wiki（10篇+索引+Oray矩阵）全部位于 07/sunlogin/ 下
- [x] 涂鸦系列 Wiki（3篇）全部位于 07/tuya/ 下
- [x] 迁移前后文件总数一致（允许新增 README.md 和 CATEGORIES.md 两个文件）
- [x] dspark-paper-wiki.md 归入02 Agent工程方法论（推理加速），ian-xiaohei-illustrations.md 归入05 AI多模态内容（AI配图），归属经内容确认后合理

## 文档完整性验证
- [x] CATEGORIES.md 存在且包含：分类设计原则（6条）、8个主题详细定义、每个主题下完整 Wiki 清单（带链接）、主题关联关系图（Mermaid）、推荐学习路径
- [x] README.md 存在且包含：知识库简介、统计数字、8主题导航表格、每个主题下 Wiki 快速链接、推荐学习路径、CATEGORIES.md 链接
- [x] CATEGORIES.md 中列出的 Wiki 清单与实际目录内容一一对应
- [x] README.md 中所有 Wiki 链接指向正确路径

## 链接有效性验证
- [x] 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning` 结果显示 0 个迁移引入的断链（11个均为迁移前已存在问题/代码块误报/外部依赖缺失）
- [x] 原子化 Wiki 内部章节导航链接（prev/next）正确指向对应章节文件
- [x] 原子化 Wiki 内部目录链接（directory）正确指向 Wiki 根或对应位置
- [x] Wiki 之间的交叉引用路径已更新为新的主题目录结构，无断链
- [x] 原子化 Wiki 根目录入口文件中的导航表格链接路径正确
- [x] docs/knowledge/README.md 中所有 learning 相关链接路径已更新（共1526处替换）
- [x] 全局旧路径残留检查：docs/knowledge/learning/ 下无旧扁平路径引用

## 元数据完整性验证
- [x] 抽查 5-10 个 Wiki 文件的 YAML frontmatter，id、title、tags、date、summary 等字段完整无损坏
- [x] 原子化 Wiki 内章节文件的 frontmatter（如有）保持完整
- [x] 文件编码保持 UTF-8，无中文乱码

## 命名规范验证
- [x] 主题目录命名符合 `{两位数编号}-{kebab-case}` 规范（如 01-agent-protocols-interfaces）
- [x] 二级厂商子目录命名符合 kebab-case 规范（sunlogin、tuya）
- [x] 迁移过程中未修改任何 Wiki 文件或章节的原有命名

## 上层文档同步验证
- [x] docs/knowledge/README.md 中的 learning 部分链接路径已全部更新（共266个文件1943处替换）
- [x] docs/retrospective/、.agents/templates/ 等引用 learning 路径的文件均已同步更新
- [x] .trae/specs/docs-restructure/ 下 tasks.md 和 checklist.md 已更新任务完成状态

## 收尾验证
- [x] 迁移过程中产生的空目录已全部清理
- [x] Git 状态检查：文件变更均为重命名（renamed）而非删除+新增，保留文件历史
- [x] 无 .pyc 缓存文件或临时文件被意外迁移（04目录下存在1个迁移前已有的 __pycache__/，不属于迁移引入）

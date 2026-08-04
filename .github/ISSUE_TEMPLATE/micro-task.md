---
name: ✨ 微任务：随时可做的小改进
about: 不需要讨论、直接可以做的微任务清单——修复错别字、断链、注释等
title: "[微任务] "
labels: ["good first issue", "help wanted", "documentation"]
assignees: []
---

## 🎉 微任务随时可做！

以下任务**不需要先开Issue讨论**，直接Fork→修改→提交PR即可：

| 任务类型 | 具体示例 | 修改位置 | 预计耗时 | PR标题示例 |
|---------|---------|---------|---------|-----------|
| **🔤 修复错别字** | 文档中的错字、语法错误、标点问题、多字/漏字 | `.agents/docs/` 下任意 `.md` 文件 | 5-10分钟 | `docs: fix typo in xxx.md` |
| **🔗 修复断链** | Markdown中引用的相对路径404、锚点失效 | 包含错误链接的 `.md` 文件 | 10-15分钟 | `fix: correct link to xxx in yyy.md` |
| **📝 补充注释** | Python脚本中缺少docstring的函数、难以理解的逻辑缺少行内注释 | `.agents/scripts/` 下的 `.py` 文件 | 10-20分钟 | `docs: add docstring for xxx function` |
| **🌐 改进翻译/表达** | 中英文术语翻译不统一、句子不通顺、表达不自然 | 任意 `.md` 文件 | 10-20分钟 | `docs: improve wording in xxx section` |
| **🧪 添加测试用例** | 为现有函数补充边界情况测试、补充缺失的测试 | `.agents/scripts/tests/` | 20-30分钟 | `test: add edge case tests for xxx` |
| **🐛 报告Bug** | 使用中遇到的问题，详细记录复现步骤 | 本Issue | 10分钟 | —— |

### 🚀 提交方式

1. **Fork** 本仓库
2. **修改** 对应的文件
3. **提交PR**，标题使用上方表格中的格式
4. **等待** 维护者审查（承诺48小时内回复）

> 💡 **第一次贡献？** 不用担心！阅读 [CONTRIBUTING.md](https://github.com/xinetzone/SpecWeave/blob/main/CONTRIBUTING.md) 的"首次贡献指南"章节，你可以在PR中写"这是我的第一次开源贡献"，我们会特别耐心地帮助你。

### ✅ 提交前检查

- [ ] 我的修改 ≤20行
- [ ] 运行了 `python .agents/scripts/check-links.py --path <修改的文件>` 确认链接有效
- [ ] 没有提交密钥/令牌/密码（pre-commit hook会自动检测）
- [ ] PR标题遵循 Conventional Commits 格式（`docs:` / `fix:` / `test:` 等）

---

> **微任务原则**：小改进持续积累 > 大改进一次性完成。每一个错别字修复都是有价值的贡献！

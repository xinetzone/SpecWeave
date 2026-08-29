---
id: p2-15-npm-github-release-guide
title: npm monorepo 包发布与 GitHub Release 操作流程
source: d:\spaces\chaos\daoApps\DaoMind\.trae\RELEASE-SUMMARY-2.0.0.md
source_type: file
category: operations
tags:
  - npm
  - github
  - release
  - pnpm
  - monorepo
  - deployment
archive_status: archived
archive_priority: P2
created_at: 2026-08-02T12:10:00Z
updated_at: 2026-08-02T12:15:00Z
version: v0.1.0
reviewer: chaos-coordinator
review_notes: approved - 运维操作流程完整，故障排查实用，分类准确
summary: TypeScript monorepo 项目使用 pnpm 工作区发布 npm 包并创建 GitHub Release 的完整操作流程与故障排查指南
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p2-15-npm-github-release-guide.md
archived_at: 2026-08-02T04:07:52Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T04:07:52Z archived from d:\spaces\chaos\.agents\knowledge\temp\operations\p2-15-npm-github-release-guide.md to D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p2-15-npm-github-release-guide.md
---

# npm monorepo 包发布与 GitHub Release 操作流程

## 发布前检查清单

- [ ] 所有包版本号已统一更新
- [ ] 代码构建成功（`pnpm build`）
- [ ] Lint 检查通过（0 errors, 0 warnings）
- [ ] 测试通过
- [ ] Git tag 已创建并推送到远程
- [ ] 代码已推送到目标分支

## npm 发布流程

### 1. 登录准备

```bash
# 登录 npm
npm login

# 验证登录状态
npm whoami
```

**权限确认**：确保拥有组织（如 @daomind、@modulux）的发布权限。

### 2. 预演发布（强烈推荐）

```bash
# 预演发布，查看将要发布什么
pnpm publish --access public -r --dry-run

# 检查每个包的 package.json 配置
for pkg in packages/*/package.json; do
  echo "=== $(dirname $pkg) ==="
  cat $pkg | grep -E '"name"|"version"|"main"|"types"|"exports"'
done
```

### 3. 正式发布（pnpm 工作区方式）

```bash
# 在项目根目录执行
pnpm build

# 发布所有包到 npm（公开访问）
pnpm publish --access public -r --no-git-checks

# 或发布到 beta 标签
pnpm publish --access public -r --tag beta --no-git-checks
```

### 发布参数说明

| 参数 | 说明 |
|------|------|
| `--access public` | 公开发布（scoped 包默认私有） |
| `-r` / `--recursive` | 递归发布所有工作区包 |
| `--no-git-checks` | 跳过 git 状态检查 |
| `--tag <tag>` | 发布到指定标签（默认 latest） |
| `--dry-run` | 预演发布，不实际上传 |

### 4. 验证发布

```bash
# 查看包信息
npm view @daomind/nothing
npm view @daomind/anything

# 安装测试
npm install @daomind/nothing@2.0.0
```

在线验证：https://www.npmjs.com/package/@your-scope/package-name

## GitHub Release 创建流程

### 方式一：GitHub 网页（推荐）

1. 访问 Releases 页面：`https://github.com/<owner>/<repo>/releases/new`
2. 选择已推送的 tag（如 v2.0.0）和目标分支
3. 填写 Release 标题和描述
4. 勾选 "Set as the latest release"
5. 点击 "Publish release"

### 方式二：GitHub CLI

```bash
# 登录 GitHub
gh auth login

# 创建 Release
gh release create v2.0.0 \
  --title "Release 2.0.0 - 重大更新" \
  --notes-file .trae/RELEASE-2.0.0.md \
  --target main
```

Release 描述建议包含：
- 版本信息与发布日期
- 重大变更（Breaking Changes）说明
- 新功能列表
- 迁移指南
- 测试验证结果

## 常见问题与故障排查

### 问题 1：权限错误

```
Error: You do not have permission to publish "@scope/package"
```

**解决方案**：
- 确认已登录正确的 npm 账号
- 联系组织管理员添加发布权限
- 或使用正确的 scope/组织名

### 问题 2：版本已存在

```
Error: You cannot publish over the previously published versions
```

**解决方案**：
- 更新版本号（如 2.0.0 → 2.0.1）
- 或使用不同 tag（如 `--tag next`）
- 注意：npm 不允许重复发布同一版本

### 问题 3：包名冲突

```
Error: Package name too similar to existing package
```

**解决方案**：
- 使用 scoped 包名（@scope/package-name）
- 选择更独特的包名

## 发布后工作

1. **更新文档**：README 安装说明、使用示例
2. **发布公告**：GitHub Release 说明、社区宣传
3. **监控**：npm 下载量、Issue 反馈
4. **后续规划**：收集反馈，规划下一版本

## monorepo 发布注意事项

1. **版本一致性**：确保所有相互依赖的包版本正确
2. **构建顺序**：先构建被依赖的包
3. **发布顺序**：从底层包到上层应用包依次发布
4. **Git tag**：tag 应对应整个 monorepo 的版本节点
5. **Changelog**：记录每个包的变更历史

---

**来源参考**：
- 发布总结：[RELEASE-SUMMARY-2.0.0.md](file:///d:/spaces/chaos/daoApps/DaoMind/.trae/RELEASE-SUMMARY-2.0.0.md)
- npm 发布指南：[publish-to-npm.md](file:///d:/spaces/chaos/daoApps/DaoMind/.trae/publish-to-npm.md)
- GitHub Release 指南：[create-github-release.md](file:///d:/spaces/chaos/daoApps/DaoMind/.trae/create-github-release.md)

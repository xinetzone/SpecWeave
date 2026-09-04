# Checklist

## 壳文件归一化（M1/M2）

- [x] rules/ 下 9 个壳文件均符合统一模板：仅含 frontmatter、一句话定位、导航表，无与分册重复的正文
- [x] 每个壳文件的导航表条目与对应子目录实际文件一一对应，链接全部可达
- [x] stage-guardrails-guide.md 仅含单一 frontmatter 块，重复块已删除（另发现并修复 spec-version-control.md、spec-writing-guide.md 同类问题）
- [x] alternatives-guide.md 的映射表处置已明确（分册已覆盖等价内容，映射表已移除）

## 权限主题收敛（M3）

- [x] worlds/collaboration/permissions.md 中无与 teams/permission-system.md 重复的模型定义正文，以引用指针替代
- [x] permissions.md 保留工作区场景的扩展差异内容，语义完整

## 模板治理（M4/M5）

- [x] Task 1 归档清单中每个文件均有判定依据记录（最终归档 2 个：new-user-first-quota-onboarding.md、saas-pricing-quickref.md；基线候选中 2 个经核验为真模板予以保留）
- [x] 归档文件已迁移至 templates/archive/，原位置无残留（git mv，rename 保留历史）
- [x] templates/README.md 含归档清单与准入标准两节
- [x] 4 处复盘模板入口均有指向对比表的互链指针

## 索引与链接（M6）

- [x] rules/README.md、capability-registry（含分册）、AGENTS.md、context-routing.md 中受影响条目已同步核验（壳文件路径未变、归档文件本不在索引中，无需改写）
- [x] check-links 验证：rules/ 与 worlds/ 全绿；本次变更零新增断链（templates/ 剩余 16 个断链均为既有问题，指向 docs/ 缺失文件或 example-wiki 占位，无一指向本次移动文件；全仓过滤确认无指向 archive/ 的断链）

## 范围与边界

- [x] 未修改 scripts/、skills/ 的 SKILL.md、commands/ 正文、projects/、vendor/、docs/（git status 核对确认）
- [x] 未执行 git commit
- [x] modules/ 与 brand/ 仅在 spec 开放问题中登记，未做处理

## 独立审查

- [x] Task 7 独立审查结论为 pass（8 个检查点全部 PASS，无需修复项；附带观察：归档文件 TOML 镜像未随迁，当前三层 ../ 路径依赖现有布局可达，已记录）

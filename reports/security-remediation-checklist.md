# 敏感信息防泄露安全整改建议清单

> 基于本次敏感信息脱敏审计（2026-07-08），结合项目已有数据安全规范体系，提出以下分层防御整改建议。建议按优先级分阶段落地。

---

## 一、立即整改（P0 — 本周内完成）

### 1.1 将敏感信息扫描集成到 CI 门禁流水线

- [ ] 在 [ci-check.ps1](file:///d:/spaces/SpecWeave/.agents/scripts/ci-check.ps1) 中新增第14步：敏感信息扫描
  - 命令：`python .agents/scripts/check-sensitive-info.py --only-severity high`
  - 退出码1（HIGH风险）时阻断流水线，退出码2（MEDIUM）仅警告
  - bash版本 [ci-check.sh](file:///d:/spaces/SpecWeave/.agents/scripts/ci-check.sh) 同步添加
- [ ] 验证：当前扫描 HIGH=0，CI 应通过

### 1.2 配置 Git pre-commit 钩子（本地防护第一道门）

- [ ] 创建 `.git/hooks/pre-commit` 钩子脚本：
  ```bash
  #!/bin/sh
  python .agents/scripts/check-sensitive-info.py --only-severity high --path .
  if [ $? -ne 0 ]; then
    echo "❌ 检测到高风险敏感信息，请脱敏后再提交"
    echo "   可运行 python .agents/scripts/check-sensitive-info.py --fix 自动修复"
    exit 1
  fi
  ```
- [ ] 将钩子脚本模板放入 `.agents/scripts/hooks/pre-commit`，在项目初始化文档中说明启用方式

### 1.3 补充 `.gitignore` 遗漏的敏感文件模式

- [x] `.env.*` 环境文件 + `!.env.example` 白名单（已完成）
- [x] 证书密钥文件 `*.pem`、`*.key`、`*.p12`（已完成）
- [ ] 补充：`*.jks`、`*.keystore`、`*.kdbx`（KeePass数据库）、`*.pfx`、`id_*`（SSH私钥）、`*.ovpn`（VPN配置）
- [ ] 补充：`*.log`（日志文件，防止意外记录敏感信息）、`*.bak`、`*.tmp`
- [ ] 补充：IDE敏感配置：`.idea/workspace.xml`、`.vscode/settings.json`（如果含本地路径）

---

## 二、短期整改（P1 — 2周内完成）

### 2.1 环境变量与密钥管理规范

- [ ] 项目根目录创建 `.env.example` 模板文件，列出所有必需的环境变量（不含真实值）
- [ ] 编写文档：[docs/knowledge/best-practices/](file:///d:/spaces/SpecWeave/docs/knowledge/best-practices/) 下新增 `secrets-management.md`，内容包括：
  - 禁止硬编码的密钥类型清单（API Key、密码、Token、数据库连接串）
  - 环境变量注入方式（本地开发用 `.env.local`，生产部署用密钥管理服务）
  - Python代码示例：使用 `os.environ.get()` 或 `python-dotenv` 读取配置
  - 错误处理：密钥缺失时的友好报错（不要在错误信息中泄露其他配置）
- [ ] 审查现有代码中所有 `password=`、`secret=`、`api_key=`、`token=` 赋值，确保值来自环境变量

### 2.2 日志安全规范

- [ ] 检查所有日志输出（`print()`、`logging` 模块调用），确保：
  - 不打印完整的手机号/邮箱/身份证号（如需调试，使用脱敏函数）
  - 不打印 Authorization 头、Cookie、Session ID
  - 不打印完整的数据库连接串（密码部分必须掩码）
  - 异常堆栈中不暴露文件系统路径（用户目录部分替换为 `<USER_HOME>`）
- [ ] 在日志工具封装中提供 `mask_sensitive()` 工具函数，复用脱敏规则

### 2.3 文档与注释安全规范

- [ ] 文档编写规范补充：示例代码中使用 `138****5678`、`user@example.com`、`sk-xxxx` 等占位符
- [ ] 文档中如需展示真实内网IP/配置，需标记为"示例"上下文（代码块上方有"示例""example"等关键词），或在该行添加 `<!-- nosec -->`（Markdown）、`# nosec`（代码）注释
- [ ] 禁止在 Markdown 链接、图片src中硬编码带认证token的URL（如 `https://api.example.com?token=xxx`）

### 2.4 测试数据安全

- [ ] 单元测试/集成测试中禁止使用真实个人信息，必须使用：
  - 手机号：`13800138000`（运营商测试号段）、`138****5678`（已脱敏格式）
  - 邮箱：`test@example.com`、`user@test.org`
  - 人名：`测试用户`、`John Doe`
  - API密钥：`sk-xxxxxxxxxxxxxxxxxxxxxxxx`（x占位）
- [ ] 测试用例中如需构造敏感字符串，使用字符串拼接（如 `'sk-' + 'x'*32`），避免被检测工具误报

---

## 三、中期整改（P2 — 1个月内完成）

### 3.1 CI/CD 流水线增强

- [ ] GitHub Actions workflow [sensitive-info-scan.yml](file:///d:/spaces/SpecWeave/.github/workflows/sensitive-info-scan.yml) 增强：
  - 增加 `--json` 输出，将结果上传为 CI artifact
  - 对 PR 新增/修改的文件进行增量扫描（而非全量），缩短反馈时间
  - 配置扫描失败时自动评论 PR，标注具体文件和行号
- [ ] 在 `repo-check.py all` 命令中集成敏感信息扫描，作为 repo 合规检查的一部分
- [ ] 建立基线机制：首次全量扫描后，后续CI只阻断新增的 HIGH 风险项（存量问题纳入技术债跟踪）

### 3.2 密钥轮换与历史清理

- [ ] **审计 Git 历史**：使用 `git log -p -S "sk-"`、`git log -p -S "password"` 等命令排查历史提交中是否有已提交的密钥
  - 如果发现已泄露的密钥，**必须立即轮换**（仅仅删除文件是不够的，Git历史中仍可恢复）
  - 如需彻底清除历史中的敏感数据，使用 `git filter-repo` 工具重写历史（注意：需要强制推送，协调团队）
- [ ] 检查当前所有配置的第三方API密钥是否有效，对疑似泄露的密钥执行轮换
- [ ] 建立密钥轮换制度：每90天轮换一次生产环境密钥

### 3.3 脱敏工具库沉淀

- [ ] 将脱敏规则从 [sensitive_info.py](file:///d:/spaces/SpecWeave/.agents/scripts/lib/checks/sensitive_info.py) 中的 `fix_func` 提取为可复用的 `lib/security/masking.py` 模块
- [ ] 提供通用脱敏函数供业务代码和日志使用：
  - `mask_phone(phone: str) -> str`：138****5678
  - `mask_email(email: str) -> str`：a***b@domain.com
  - `mask_id_card(id: str) -> str`：110***********1234
  - `mask_path(path: str) -> str`：替换用户目录为 `<USER_HOME>`
  - `mask_jwt(token: str) -> str`：只保留前10位+...+后10位
- [ ] 编写单元测试，覆盖率 ≥90%

### 3.4 数据分类分级落地

参照 [.agents/rules/data-security/data-classification/](file:///d:/spaces/SpecWeave/.agents/rules/data-security/data-classification/) 规范：
- [ ] 梳理项目中涉及的数据资产，按 L1（公开）/L2（内部）/L3（敏感）/L4（绝密）分级
- [ ] 对 L3/L4 数据（个人信息、密钥、支付信息）在存储、传输、日志三个环节落实加密/脱敏
- [ ] 在代码审查Checklist中增加"数据分类是否正确标注"检查项

---

## 四、长期治理（P3 — 持续进行）

### 4.1 检测规则持续迭代

- [ ] 建立误报反馈机制：开发人员遇到误报时，通过在代码行加 `# nosec` + 注释说明原因
- [ ] 定期（每季度）审查 nosec 标记的使用情况，清理不必要的豁免
- [ ] 根据新出现的敏感信息模式（如新的云服务商密钥格式）更新正则规则
- [ ] 考虑引入熵检测（entropy analysis）：识别高熵字符串（随机度高的字符串很可能是密钥/Token），减少对正则的依赖

### 4.2 安全意识培训

- [ ] 新成员 onboarding 文档中加入"敏感信息处理规范"章节
- [ ] 每半年组织一次数据安全意识培训，覆盖：
  - 什么是敏感信息（列举项目中出现过的真实案例）
  - 如何正确使用环境变量和密钥管理
  - 发现敏感信息泄露后的应急响应流程
- [ ] 代码审查培训：Reviewer 必须检查 PR 中是否有硬编码敏感信息

### 4.3 应急响应预案

参照 [.agents/rules/data-security/incident-response/](file:///d:/spaces/SpecWeave/.agents/rules/data-security/incident-response/) 规范：
- [ ] 明确敏感信息泄露事件的分级标准和响应SLA
- [ ] 建立密钥泄露应急处理流程：
  1. 立即轮换被泄露的密钥/密码
  2. 评估泄露范围（哪些系统受影响、数据是否可被利用）
  3. 清除 Git 历史中的敏感数据
  4. 编写事后复盘报告，更新检测规则防止同类问题
- [ ] 指定安全负责人（Security Champion），负责安全问题的协调和跟进

---

## 五、快速自查命令参考

```bash
# 全量扫描（日常使用）
python .agents/scripts/check-sensitive-info.py

# 自动修复可脱敏项
python .agents/scripts/check-sensitive-info.py --fix

# 仅检查高风险项（CI使用）
python .agents/scripts/check-sensitive-info.py --only-severity high

# JSON格式输出（CI artifact）
python .agents/scripts/check-sensitive-info.py --json --output report.json

# 扫描指定目录
python .agents/scripts/check-sensitive-info.py --path ./apps/my-app

# 排除额外目录
python .agents/scripts/check-sensitive-info.py --exclude temp,build,dist
```

---

## 六、nosec 标记使用指南

在确认为示例/测试数据且无法通过上下文自动识别时，可在代码行尾添加 nosec 标记跳过检测：

| 语言/格式 | 标记方式 | 示例 |
|-----------|---------|------|
| Python/Shell/YAML | `# nosec` | `api_key = "sk-test-xxxx"  # nosec 这是文档示例` |
| JavaScript/TypeScript/C/Java | `// nosec` | `const key = "sk-test-xxxx"; // nosec` |
| C/Java 块注释 | `/* nosec */` | `/* nosec */ const key = "sk-test-xxxx";` |
| HTML/Markdown | `<!-- nosec -->` | `邮箱：test@example.com <!-- nosec -->` |
| Mermaid 图表 | `%% nosec` | `%% nosec` |
| SQL/Lua | `-- nosec` | `-- nosec` |

> ⚠️ **nosec 使用原则**：
> 1. 必须在 nosec 后添加注释说明为什么这是安全的（如"文档示例"、"公开测试key"、"脱敏后的值"）
> 2. 禁止滥用 nosec 来隐藏真实的敏感信息
> 3. 每季度审计 nosec 标记，清理不必要的豁免

---

## 附录：本次审计处理记录

| 处理项 | 数量 | 说明 |
|--------|------|------|
| 检测并修复真实个人路径 | 4处 | `<USER_HOME>\...` → 已替换为占位符 |
| 误报优化迭代 | 6轮 | 从520项告警降到6项LOW，误报率降低98.8% |
| 文档示例添加nosec | 8处 | 内网IP示例添加标记 |
| 公开邮箱保留 | 6处 | support@minitap.ai 为企业公开支持邮箱，不脱敏 |
| .gitignore规则完善 | 22行新增 | 覆盖环境文件、密钥、证书、凭证、数据库文件 |
| CI集成 | 1个workflow | GitHub Actions 高风险扫描 |
| 单元测试 | 52个 | 覆盖10类敏感信息检测+误报控制+自动修复 |

---
生成时间：2026-07-08
关联报告：[sensitive-info-sanitization-report.md](file:///d:/spaces/SpecWeave/reports/sensitive-info-sanitization-report.md)

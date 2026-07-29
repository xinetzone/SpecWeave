---
id: "dind-retrospective-20260720"
title: "docker-ssh-dind 项目复盘报告"
date: 2026-07-20
methodology: "七概念方法论 R→I→E→C（里程碑复盘链路）"
---

# docker-ssh-dind 项目复盘报告

> **项目**：Docker-in-Docker SSH 镜像构建 | **周期**：2026-07-20 | **方法**：复盘(R)→洞察(I)→萃取(E)→导出(C) | **报告日期**：2026-07-20

---

## 一、事实（R）：客观数据与事件时间线

### 1.1 产出物清单

| 文件 | 大小 | 类型 | 说明 |
|------|------|------|------|
| Containerfile | 4,484 bytes | 构建定义 | 7阶段Docker镜像构建文件 |
| entrypoint.sh | 5,563 bytes | 启动脚本 | 6步容器启动流程 |
| README.md | 4,506 bytes | 使用文档 | 中文使用指南 |
| .dockerignore | 68 bytes | 构建忽略 | 排除无关文件 |
| AGENTS.md | 5,166 bytes | AI入口 | 子项目AGENTS路由 |
| .agents/README.md | 1,552 bytes | AI资产索引 | .agents目录说明 |
| .agents/rules/containerfile.md | 2,661 bytes | 规则文件 | Containerfile编写规范 |
| .agents/rules/entrypoint.md | 2,717 bytes | 规则文件 | 启动脚本规范 |
| .agents/rules/build-test.md | 3,976 bytes | 规则文件 | 构建与测试规范 |
| docs/decision-dind-vs-dood.md | 已有 | 决策文档 | DinD vs DooD选型分析 |
| 7个 .gitkeep | 0 bytes | 目录占位 | roles/skills/scripts/workflows/templates/docs |

**代码文件合计**：Containerfile 143行 + entrypoint.sh 200行 = 343行
**AI资产合计**：AGENTS.md 101行 + .agents/ 5个md文件 = 约320行

### 1.2 技术选型事实

| 决策项 | 选择 | 用户要求/来源 |
|--------|------|--------------|
| 基础镜像 | ubuntu:26.04（固定版本） | 用户指定 |
| 非root用户名 | ai（UID 1000） | 用户指定 |
| 语言环境 | zh_CN.UTF-8 | 用户指定 |
| 时区 | Asia/Shanghai | 用户指定 |
| init进程 | tini | 设计决策（信号处理） |
| 存储驱动 | overlay2 | Docker官方推荐 |
| 日志驱动 | json-file（10MB×3轮转） | 运维最佳实践 |
| Docker socket权限 | chmod 666 | 非root用户访问需要 |
| SSH主机密钥 | 启动时生成 | 安全最佳实践（不打包到镜像） |
| iptables | false（daemon.json） | 容器内Docker避免修改宿主iptables |

### 1.3 环境变量

| 变量 | 默认值 | 功能 |
|------|--------|------|
| ROOT_PASSWORD | 随机生成 | root用户密码 |
| SSH_PUBLIC_KEY | 无 | SSH公钥注入 |
| DOCKER_OPTS | 空 | dockerd额外参数 |
| ALLOW_ROOT_SSH | yes | 是否允许root SSH登录 |
| DEBUG | 0 | 调试模式开关 |

### 1.4 问题事件时间线

| 时间 | 事件 | 影响文件 | 处理方式 |
|------|------|---------|---------|
| T1 | Containerfile中文注释乱码 | Containerfile | 构建注释改用英文 |
| T2 | entrypoint.sh写入时编码错误 | entrypoint.sh | 改用Write工具重写 |
| T3 | README.md写为英文版本 | README.md | 后续改为中文 |
| T4 | AGENTS.md首次写入中文乱码 | AGENTS.md | 改用Write工具重写 |
| T5 | .agents/README.md乱码 | .agents/README.md | Write工具重写 |
| T6 | .agents/rules/build-test.md乱码 | build-test.md | Write工具重写 |
| T7 | Write工具超时（大文件） | 多个文件 | 验证文件是否已写入后重试 |
| T8 | Shell命令长度超限（>32000字符） | inline写入 | 改用Write工具 |
| T9 | PowerShell脚本中文乱码根因定位 | path-migration-ci.ps1等 | 分析PS5.1默认编码三陷阱，创建共享安全库 |
| T10 | 批量脚本编码加固 | 4个.ps1脚本 | 引入encoding-safety.ps1统一处理 |
| T9 | PowerShell脚本中文乱码根因定位 | path-migration-ci.ps1等 | 分析PS5.1默认编码三陷阱，创建共享安全库 |
| T10 | 批量脚本编码加固 | 4个.ps1脚本 | 引入encoding-safety.ps1统一处理 |

### 1.5 Containerfile 7阶段结构

```
Stage 1/7: Base system + Chinese locale（系统包+中文locale+时区）
Stage 2/7: Install Docker Engine（Docker CE GPG+repo+安装）
Stage 3/7: Create non-root user ai（用户创建+docker组+sudoers）
Stage 4/7: Configure OpenSSH Server（sshd_config+主机密钥清理）
Stage 5/7: Configure Docker daemon（daemon.json+目录权限）
Stage 6/7: Install entrypoint script（COPY+chmod）
Stage 7/7: Final setup（VOLUME+EXPOSE+ENTRYPOINT+构建信息）
```

### 1.6 entrypoint.sh 6步启动流程

```
Step 1/6: setup_root_password（配置root密码/随机生成）
Step 2/6: setup_ssh_keys（注入SSH公钥）
Step 3/6: generate_host_keys（生成SSH主机密钥）
Step 4/6: configure_sshd（配置+验证sshd）
Step 5/6: start_docker（启动dockerd+60秒等待+失败诊断）
Step 6/6: start_sshd（前台启动sshd，exec替换进程）
```

### 1.7 AGENTS.md 嵌套路由

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色）
  └─ apps/docker-ssh-dind/AGENTS.md（项目特有约束）
       ├─ Containerfile / entrypoint.sh / README.md
       ├─ docs/decision-dind-vs-dood.md
       └─ .agents/
            ├─ rules/（3个规则文件）
            └─ roles/skills/scripts/workflows/templates/docs/（预留）
```

---

## 二、洞察（I）：5-Whys 根因分析

### 2.1 核心问题：中文编码问题为何反复出现？

**问题陈述**：项目开发过程中，中文内容写入文件时出现编码损坏，前后发生6次（T1-T6），影响了Containerfile、entrypoint.sh、README.md、AGENTS.md和2个.agents规则文件。

**5-Whys分析**：

```
Why1：为什么文件会出现中文乱码？
→ 因为通过PowerShell脚本（here-string @'...'@）写入含中文的内容时，PowerShell默认输出编码不是UTF-8。

Why2：为什么要用PowerShell脚本写入文件而不是直接用Write工具？
→ 因为最初尝试通过Shell工具一次性执行多条命令（创建目录+写入多个文件），认为这样效率更高。

Why3：为什么Shell工具的PowerShell输出编码有问题？
→ 因为PowerShell 5的默认输出编码是系统区域设置编码（Windows中文系统为GBK/CP936），here-string输出的中文字节按GBK编码，但文件被按UTF-8读取。

Why4：为什么Write工具没有这个问题？
→ 因为Write工具直接以UTF-8无BOM编码写入文件，不经过shell编码层。

Why5：为什么一开始没有使用Write工具？
→ 因为试图通过脚本批量创建文件以"提高效率"，反而忽略了Write工具本身就是最可靠的文件写入方式——绕过shell编码层直接写文件。
```

**根因**：在Windows环境下，任何经过PowerShell shell管道/here-string输出的中文内容都有被GBK编码污染的风险。Write工具绕过shell编码层直接写文件，是最安全的方式。**追求"批量操作效率"反而导致了更高的修复成本。**

**PowerShell 5.1 编码三陷阱技术详解**：

| Cmdlet / API | 默认编码 | 具体问题 |
|---|---|---|
| `Set-Content` / `Add-Content` | 系统ANSI（中文Windows=GBK/CP936） | 写入UTF-8中文时被解码为GBK，产生`浣犲ソ`类乱码 |
| `Out-File` / `>` / `>>` | UTF-16LE（UCS-2 LE，带BOM） | 每字符2字节，文件异常大，Unix工具无法读取 |
| `[System.Text.Encoding]::UTF8` | UTF-8 **带BOM**（EF BB BF前缀） | BOM导致Shell shebang失效、Python解析异常、Git diff显示`ï»¿` |

正确的无BOM UTF-8写法：
```powershell
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
```

### 2.2 洞察四元组

#### 洞察1：Shell编码陷阱

| 要素 | 内容 |
|------|------|
| **触发条件** | Windows + PowerShell + 含中文的here-string/管道输出写入文件 |
| **因果机制** | PowerShell 5默认输出编码为GBK/CP936，中文字符被GBK编码后存入文件，但Markdown/代码文件期望UTF-8编码，导致乱码 |
| **可操作结论** | 含中文内容的文件写入，**必须使用Write工具**，绝对不要通过Shell PowerShell here-string/echo/Set-Content写入中文 |
| **预期结果** | 消除编码损坏问题，避免返工修复 |

#### 洞察2：效率悖论

| 要素 | 内容 |
|------|------|------|
| **触发条件** | 试图通过shell脚本"一次性"批量创建多个文件以提高效率 |
| **因果机制** | Shell脚本批量写入虽然单次调用快，但编码问题/超时/命令长度限制导致需要多次修复，总耗时反而远超逐文件Write |
| **可操作结论** | 文件创建优先使用Write工具逐文件写入，不要为了"少调用几次工具"而使用shell批量脚本；可靠性 > 表面效率 |
| **预期结果** | 减少返工，总耗时降低 |

#### 洞察3：文档语言一致性

| 要素 | 内容 |
|------|------|
| **触发条件** | 项目面向中文用户（中文环境配置、中文AGENTS.md、中文规则文件），但README.md初始写为英文 |
| **因果机制** | 编码问题发生后，为"避免再次乱码"选择用英文写README，这是一种回避问题而非解决问题的思路；编码问题应通过正确工具解决，而非降级内容质量 |
| **可操作结论** | 面向中文用户的项目，所有面向用户的文档（README、使用说明）必须统一中文；代码注释（Containerfile/entrypoint.sh构建时）可用英文避免编码问题，但文档层面必须中文 |
| **预期结果** | 文档语言一致，用户体验连贯 |

#### 洞察4：Write工具超时≠写入失败

| 要素 | 内容 |
|------|------|
| **触发条件** | Write工具写入较大文件时出现"IDE Command timeout"错误 |
| **因果机制** | 超时是IDE等待响应的超时，不代表底层文件写入失败；文件可能已成功写入磁盘 |
| **可操作结论** | Write工具超时后，**必须先用Read工具验证文件内容**，确认是否已写入成功，再决定是否重试；避免盲目重写 |
| **预期结果** | 避免重复写入，减少不必要的工具调用 |

---

## 三、萃取（E）：可复用模式提炼

### 模式1：Windows环境文件写入安全协议（Write-First原则）

**模式名称**：windows-chinese-file-write-safety

**问题**：在Windows PowerShell环境下，通过Shell工具写入含中文内容的文件时，中文会被GBK编码污染导致乱码。

**解决方案**：
1. **所有含中文的Markdown/文本文件**：使用Write工具直接写入
2. **禁止**通过PowerShell here-string（`@'...'@`）、`echo > file`、`Set-Content`写入中文
3. 如果必须通过Shell写入文件（如脚本生成），必须显式指定UTF-8编码：`[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))`
4. Write工具超时时，先Read验证再决定是否重试

**已实施的共享工具库**：

创建了 `.agents/scripts/lib/encoding-safety.ps1` 作为统一编码安全模块，提供：
- `Write-Utf8File`：安全写入UTF-8无BOM文件（支持管道、追加、自动建目录）
- `Read-Utf8File`：安全读取UTF-8文件（自动检测并跳过BOM）
- `Test-Utf8File`：检测文件编码和乱码状态
- `Initialize-EncodingSafety`：统一设置控制台/环境变量编码

已加固的脚本：ci-check.ps1、path-migration-ci.ps1、test-wechat-extraction.ps1

**与现有模式关系**：本模式是对 [direct-file-write-over-shell-pipe](file:///d:/spaces/SpecWeave/.agents/docs/retrospective/patterns/code-patterns/direct-file-write-over-shell-pipe.md) 模式在Windows中文场景下的具体化补充。现有模式强调"不用shell管道写文件"，本模式补充了"Windows+中文"场景下的具体禁止操作和正确操作。

### 模式2：Docker-in-Docker SSH 镜像标准结构

**模式名称**：dind-ssh-image-structure

**问题**：构建一个支持SSH连接的Docker-in-Docker镜像，需要哪些标准组件和配置？

**解决方案**：
- **Containerfile 7阶段结构**：Environment → Base packages + locale → Docker Engine → Non-root user → SSH config → Docker daemon config → Finalization
- **entrypoint.sh 6步启动**：diagnose → password → host keys → sshd config → ssh keys → dockerd → sshd
- **关键配置**：tini init、daemon.json（overlay2 + json-file日志轮转 + iptables=false）、docker.sock chmod 666、SSH主机密钥启动时生成
- **诊断信息**：启动时输出OS/kernel/cgroup/Docker版本、privileged检查、cgroup挂载检查
- **错误处理**：Docker启动60秒超时，失败时输出dockerd.log最后30行+常见原因

### 模式3：子项目AGENTS.md最小可行子集

**模式名称**：subproject-agents-minimal-subset

**问题**：SpecWeave apps/下的子项目需要什么样的AGENTS.md和.agents结构？

**解决方案**：
- **AGENTS.md必须包含**：启动协议（4步）、嵌套路由关系图、上下文路由表（任务类型→规则入口）、项目特有约束、父级链接（`../../AGENTS.md`）
- **.agents/最小结构**：README.md（索引）+ rules/（项目特有规则）+ 预留目录（.gitkeep）
- **禁止重复**：全局规则、Skill、角色、命令集全部引用父级，不重复实现
- **渐进式扩展**：roles/skills/scripts/workflows/templates/docs按需填充，不用预创建空文件
- **"启动协议"关键词**：AGENTS.md必须包含此关键词以通过工作区发现协议验证

---

## 四、闭环（C）：行动项与改进

### 4.1 已完成修复

| # | 问题 | 修复状态 | 修复方式 |
|---|------|---------|---------|
| 1 | .agents/README.md中文乱码 | ✅ 已修复 | Write工具重写 |
| 2 | .agents/rules/build-test.md中文乱码 | ✅ 已修复 | Write工具重写 |
| 3 | README.md为英文 | ✅ 已修复 | 改为中文版本 |
| 4 | 临时脚本清理 | ✅ 已修复 | 已删除临时.ps1脚本 |

### 4.2 后续行动项

| # | 行动项 | 优先级 | 类型 | 说明 |
|---|--------|--------|------|------|
| A1 | 验证镜像实际可构建运行 | 高 | 测试 | `docker build` + `docker run` + SSH连接 + Docker功能完整验证 |
| A2 | 将"Windows中文写入安全协议"萃取到模式库 | 中 | 萃取 | 提交到code-patterns/目录 |
| A3 | AGENTS.md中补充"构建注释用英文"规则的明确说明 | 低 | 文档 | 当前在containerfile.md中有，AGENTS.md约束中也应提及 |

### 4.3 经验沉淀

1. **工具选择原则**：在Windows环境中做文件写入时，Write工具是第一选择，Shell脚本批量写入中文是反模式
2. **编码问题解决思路**：解决编码问题的方式是使用正确的工具和编码设置，而不是回避中文、改用英文
3. **超时处理**：Write工具超时后不要假设失败，先Read验证
4. **文档一致性**：面向中文用户的项目文档语言必须统一中文，代码注释可因技术约束使用英文
5. **子项目AGENTS原则**：最小可行子集，不重复父级规则，渐进式扩展

### 4.4 七概念方法论应用评估

| 概念 | 应用场景 | 效果 |
|------|---------|------|
| F（第一性原理） | AGENTS.md结构设计——子项目本质是轻量Docker镜像项目 | ✅ 避免过度工程，.agents/只放3个必要规则文件 |
| V（对抗审查） | 攻击3个方向：结构膨胀/无扩展位/不链接父级 | ✅ 防御了3个设计缺陷 |
| I（洞察） | 编码问题5-Whys根因分析 | ✅ 识别了Shell编码陷阱和效率悖论 |
| A（原子化） | .agents/拆分为独立规则文件+预留目录 | ✅ 每个规则单一职责，预留位支持扩展 |
| R（复盘） | 本报告——事实+分析+洞察+萃取 | ✅ 结构化沉淀经验 |
| E（萃取） | 提炼3个可复用模式 | ✅ 从具体项目经验中抽象出可迁移模式 |
| C（闭环） | 行动项追踪+经验沉淀 | ✅ 修复遗留问题，明确后续行动 |

---

## 五、wslc可选支持改造复盘（2026-07-20 下午）

> **改造主题**：支持宿主机无Docker的WSL/Windows环境，增加wslc.exe可选运行时 | **方法**：R→I→E（知识沉淀链路）

### 5.1 事实（R）：产出物清单

| 文件 | 大小 | 类型 | 说明 |
|------|------|------|------|
| scripts/check-env.sh | 6,723 bytes | 宿主机检测 | OS/WSL/Docker/wslc四合一环境检测脚本 |
| scripts/dind.sh | 11,530 bytes | 管理脚本 | 双运行时(docker/wslc)管理CLI，10个子命令 |
| entrypoint.sh（更新） | ~8,500 bytes | 启动脚本 | 新增detect_container_env()、DIND_SKIP_DOCKER、优雅降级 |
| Containerfile（更新v1.3） | ~4,800 bytes | 构建定义 | 新增DIND_SKIP_DOCKER/CONTAINER_RUNTIME环境变量 |
| README.md（更新） | ~15,000 bytes | 使用文档 | 新增前置条件/WSL指南/wslc模式/FAQ/命令参考 |

**新增环境变量**：

| 变量 | 默认值 | 功能 |
|------|--------|------|
| DIND_SKIP_DOCKER | 0 | 设为1跳过dockerd启动（wslc SSH-only模式） |
| CONTAINER_RUNTIME | auto | 显式指定容器运行时（docker/wslc/containerd） |

**关键设计决策**：
- wslc.exe为微软WSL Container API预览版，仅支持Bridged/None网络，privileged模式支持有限
- DinD在wslc下可能无法工作（privileged限制），故提供DIND_SKIP_DOCKER=1 SSH-only降级模式
- Containerfile构建时不创建`/.wslc-container`标记文件（构建时≠运行时，避免误检测）
- 容器运行时检测依赖运行时信号：CONTAINER_RUNTIME env > /.dockerenv > /proc/1/cgroup > /proc/version推断

### 5.2 洞察（I）

#### 洞察5：构建时标记 vs 运行时检测的边界混淆

| 要素 | 内容 |
|------|------|
| **陈述** | 在Containerfile构建阶段创建运行时标记文件会导致跨运行时误检测 |
| **证据** | `touch /.wslc-container`会进入镜像层，docker run也会携带该文件导致误判为wslc |
| **反常识** | "镜像支持wslc"≠"容器运行在wslc上"，构建时的属性标签不能替代运行时环境感知 |
| **下次行动** | 容器运行时环境检测必须在entrypoint中通过/proc/cgroup/环境变量等运行时信号判断 |

#### 洞察6：优雅降级 > 硬性失败

| 要素 | 内容 |
|------|------|
| **陈述** | 增强功能失败时应降级运行而非exit 1退出容器 |
| **证据** | wslc preview不支持privileged→dockerd必定失败，但SSH作为独立功能完全可用；原entrypoint直接exit 1导致完全不可用 |
| **反常识** | 部分可用 > 完全不可用；DinD是增强功能而非核心功能，SSH才是核心服务 |
| **下次行动** | entrypoint遵循"核心功能必须启动、增强功能失败降级"原则，通过SKIP_*环境变量允许显式跳过 |

#### 洞察7：宿主机预检层+容器内自适应层双层检测架构

| 要素 | 内容 |
|------|------|
| **陈述** | 多运行时支持需要双层检测，两层职责不同不可互相替代 |
| **证据** | check-env.sh在宿主机做"能不能启动"预检并给安装指引，entrypoint在容器内做"运行在什么环境"自适应 |
| **反常识** | 两层检测看似重复，实则一层是前置快速失败+引导，一层是运行时功能开关+降级 |
| **下次行动** | 多运行时项目统一采用双层检测架构 |

#### 洞察8：WSL配置三维判定矩阵

| 要素 | 内容 |
|------|------|
| **陈述** | WSL中Docker配置需先判定WSL版本×Docker来源×systemd状态三个维度，再给出对应指令 |
| **证据** | 历史经验681264/1287843等多次记录：通用Linux指令（service docker start）在WSL中频繁失效 |
| **反常识** | WSL≠"Linux在Windows上"，5种配置组合各自的Docker启动方式完全不同 |
| **下次行动** | WSL相关文档/脚本必须先判定配置组合再给出指令，禁止给出通用Linux指令 |

### 5.3 萃取（E）：新增可复用模式

#### 模式4：多运行时容器双层检测模式（multi-runtime-dual-layer-detection）

- **触发场景**：容器需支持多种运行时（Docker/containerd/wslc/podman）、跨OS平台
- **核心步骤**：宿主机预检层（OS检测→运行时检测→能力检测→安装指引→.env.detected生成）+ 容器内自适应层（运行时信号检测→功能开关→降级策略→用户覆盖优先）
- **检测信号优先级**：用户显式env > 标准标记文件（/.dockerenv）> cgroup/proc特征 > 内核推断
- **反模式**：构建时创建运行时标记文件、预检与自适应二选一、硬编码无降级路径

#### 模式5：容器入口点优雅降级模式（container-entrypoint-graceful-degradation）

- **触发场景**：容器内含多个功能模块，部分依赖特殊权限（privileged/内核模块/设备挂载）
- **核心步骤**：功能分层（核心vs增强）→ SKIP_*环境变量 → 增强功能超时启动+失败return 0（非exit 1）→ 诊断日志明确告知降级状态
- **反模式**：任何组件失败就exit 1、不区分核心/增强功能、无降级路径

#### 模式6：WSL环境配置判定矩阵模式（wsl-config-decision-matrix）

- **触发场景**：WSL环境下配置Docker或其他服务
- **核心步骤**：判定三维配置（WSL版本×Docker来源×systemd状态）→ 按矩阵给出对应指令 → 禁止通用Linux指令
- **反模式**：未判定配置就给出service/systemctl启动命令、假设WSL=Linux

### 5.4 行动项更新

| # | 行动项 | 优先级 | 说明 |
|---|--------|--------|------|
| A4 | 实际Windows WSL2环境验证wslc模式 | 中 | 需要最新WSL2（含wslc.exe）进行SSH-only模式验证 |
| A5 | 验证Containerfile v1.3在Docker下构建运行正常 | 高 | 回归测试确保docker模式不受影响 |
| A6 | 将3个新模式入库到模式库 | 中 | 提交到patterns/目录 |

---

## 附录：文件索引

| 产出物 | 路径 |
|--------|------|
| 镜像构建定义 | [Containerfile](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/Containerfile) |
| 容器启动脚本 | [entrypoint.sh](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/entrypoint.sh) |
| 使用文档（中文） | [README.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/README.md) |
| 环境检测脚本 | [check-env.sh](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/scripts/check-env.sh) |
| 容器管理脚本 | [dind.sh](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/scripts/dind.sh) |
| AI协作者入口 | [AGENTS.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/AGENTS.md) |
| AI资产索引 | [.agents/README.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/.agents/README.md) |
| Containerfile规范 | [containerfile.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/.agents/rules/containerfile.md) |
| Entrypoint规范 | [entrypoint.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/.agents/rules/entrypoint.md) |
| 构建测试规范 | [build-test.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/.agents/rules/build-test.md) |
| 选型决策文档 | [decision-dind-vs-dood.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/docs/decision-dind-vs-dood.md) |
| 项目复盘报告 | [retrospective-20260720.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/docs/retrospective-20260720.md) |

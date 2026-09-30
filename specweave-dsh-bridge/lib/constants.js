/**
 * SpecWeave DSH Bridge 常量与路由表。
 *
 * 本模块是纯数据模块：不 import 任何宿主（DeepSeek Harness）包，也不做 I/O，
 * 因此可被单元测试直接加载，也可被其他宿主复用。
 *
 * 路由表来源：`.agents/context-routing.md`（SpecWeave 上下文路由表，权威真源）。
 * 本表只做「任务关键词 → 规范路径」的快速定位索引，不复制规范内容；
 * 路径一律以仓库实际位置为准（对齐 AGENTS.md「路径引用一律以文件实际位置为准」）。
 */

/** 插件标识：与 cordis.patch.yml 的 row id 保持一致。 */
export const PLUGIN_ID = 'specweave-bridge';

/** 插件版本。 */
export const PLUGIN_VERSION = '0.1.0';

/** 工作区签名关键词：AGENTS.md 首部「启动协议」标题块必须包含该词。 */
export const SIGNATURE_KEYWORD = '启动协议';

/**
 * 工作区签名路径：至少命中其一时才认定为 SpecWeave 工作区根。
 *
 * 必要性（实测教训）：`apps/AGENTS.md`、`projects/AGENTS.md`、`vendor/AGENTS.md`
 * 同样包含「启动协议」字样（它们要指回根协议），仅凭关键词判定会把子区域误判为
 * 工作区根，导致子区域路由整体失效。上下文路由表是**根目录独有**的结构标记。
 */
export const SIGNATURE_PATHS = ['.agents/context-routing.md'];

/** 工作区入口文件名。 */
export const AGENTS_FILENAME = 'AGENTS.md';

/** SpecWeave 规范容器目录名。 */
export const AGENTS_DIR = '.agents';

/** 上下文路由表相对路径（无匹配时的兜底入口）。 */
export const ROUTING_TABLE = '.agents/context-routing.md';

/**
 * 工作区技能提供方名（`ctx.skills.registerProvider` 的 provider 名）。
 *
 * 位置纪律：提供方注册在**插件作用域**，用 `options.cwd` 做工作区过滤——
 * 不要改回「在 `agent.ctx` 上注册运行时技能」：agent 作用域上下文解析不到
 * `skills` 服务，属性探测会抛 `cannot get property "skills" without inject`，
 * 而 `agent/created` 监听器在会话创建事务内，异常会让**新建会话整体失败**。
 */
export const WORKSPACE_SKILL_PROVIDER = 'specweave';

/**
 * 工作区技能提供方优先级（数值越小越优先）。
 *
 * 参考宿主 `dsh-skill-filesystem` 的 rank：project-dsh 100 / project-agents 200 /
 * custom 300 / user-dsh 400 / user-agents 500。
 * 取 150：让 `<项目根>/.dsh/skills` 仍可压过桥接层，同时确保桥接层读到的
 * `.agents/skills` 门面技能稳定胜出（宿主 provider 在桌面构建下对同一目录返回 0 候选）。
 */
export const WORKSPACE_SKILL_RANK = 150;

/** 子区域目录名（按路由优先级排序）。 */
export const SUBREGIONS = ['apps', 'projects', 'vendor'];

/** 子区域入口路由文件（相对工作区根）。 */
export const SUBREGION_ENTRIES = {
  apps: 'apps/AGENTS.md',
  projects: 'projects/AGENTS.md',
  vendor: 'vendor/AGENTS.md',
};

/** 已废止的历史路径：任何产出物都不得写入该目录。 */
export const RETIRED_DOCS_DIR = '.agents/docs';

/** 公开内容产出物根目录。 */
export const PUBLIC_DOCS_ROOT = 'docs';

/** 私域内容产出物根目录。 */
export const PRIVATE_DOCS_ROOT = 'playground';

/**
 * 任务关键词 → 规范路径路由表。
 *
 * 匹配规则（对齐 Hermes 先例 specweave-bridge 的多命中语义）：
 * 关键词与任务文本互为子串（大小写不敏感）即命中，返回全部命中项；
 * 无命中由调用方回退到 {@link ROUTING_TABLE}。
 *
 * `spec` 指向的是「入口文件」，不一定是最终规范；入口文件本身会继续路由。
 */
export const ROUTES = [
  { keywords: ['内容敏感度', '公开内容', '私域', '敏感度预检'], spec: '.agents/rules/content-sensitivity-precheck.md', label: '内容敏感度预检' },
  { keywords: ['skill 创建', 'skill创建', '技能创建', 'skill 调试', '技能开发'], spec: '.agents/skills/README.md', label: 'Skill 门面索引' },
  { keywords: ['技能规范', 'skill 规范', 'skill-development'], spec: '.agents/rules/skill-development.md', label: 'Skill 开发补充规范' },
  { keywords: ['角色定义', '角色职责', '角色分工'], spec: '.agents/roles/README.md', label: '角色体系' },
  { keywords: ['复盘', 'retrospective'], spec: '.agents/skills/retrospective-cmd/SKILL.md', label: '复盘命令' },
  { keywords: ['洞察', 'insight'], spec: '.agents/skills/insight-cmd/SKILL.md', label: '洞察命令' },
  { keywords: ['七概念', 'seven-concepts'], spec: '.agents/skills/seven-concepts-cmd/SKILL.md', label: '七概念命令' },
  { keywords: ['ci 检查', 'ci检查', 'ci-check', '提交前验证'], spec: '.agents/skills/ci-check-cmd/SKILL.md', label: 'CI 综合检查' },
  { keywords: ['断链', '链接检查', 'link-check'], spec: '.agents/skills/link-check-cmd/SKILL.md', label: '链接有效性验证' },
  { keywords: ['原子化', '拆分文件', 'atomization'], spec: '.agents/skills/atomization-cmd/SKILL.md', label: '原子化拆分' },
  { keywords: ['原子提交', 'atomic-commit', 'git 提交'], spec: '.agents/skills/atomic-commit-cmd/SKILL.md', label: '原子提交' },
  { keywords: ['mermaid', '流程图', '架构图', '状态机'], spec: '.agents/skills/mermaid-cmd/SKILL.md', label: 'Mermaid 图表' },
  { keywords: ['知识沉淀', '萃取', 'extraction'], spec: '.agents/skills/extraction-cmd/SKILL.md', label: '知识沉淀' },
  { keywords: ['导航生成', '看板生成', 'docgen', '文档索引'], spec: '.agents/skills/docgen-cmd/SKILL.md', label: '文档索引与看板' },
  { keywords: ['重复代码', '重复检测', 'duplication'], spec: '.agents/skills/check-duplication-cmd/SKILL.md', label: '跨文件重复检测' },
  { keywords: ['导出报告', 'export-report'], spec: '.agents/skills/export-report-cmd/SKILL.md', label: '导出报告' },
  { keywords: ['token 优化', 'token优化'], spec: '.agents/skills/token-optimize-cmd/SKILL.md', label: 'Token 优化' },
  { keywords: ['spec', '规格', '需求规格'], spec: '.agents/skills/TRAE-spec-mode/SKILL.md', label: 'Spec Mode 规范工作流' },
  { keywords: ['spec 创建前预检', 'spec 位置', 'spec 格式'], spec: '.agents/rules/spec-creation-precheck.md', label: 'Spec 创建前预检' },
  { keywords: ['论坛', '发帖', 'forum'], spec: '.agents/skills/forum-posting/SKILL.md', label: '论坛发帖' },
  { keywords: ['前端', 'ui 设计', '视觉设计', 'design'], spec: '.agents/skills/frontend-design/SKILL.md', label: '前端设计' },
  { keywords: ['bug 修复', '修复闭环', '预防措施'], spec: '.agents/rules/fix-prevent-close-loop.md', label: '修复即闭环' },
  { keywords: ['阶段守卫', 'stage-guard'], spec: '.agents/rules/stage-guardrails.md', label: '阶段守卫' },
  { keywords: ['编码准则', '歧义澄清', '简约设计'], spec: '.agents/rules/ai-coding-guidelines.md', label: 'AI 编码行为准则' },
  { keywords: ['开发规范', '代码风格', '提交规范', '路径引用'], spec: 'docs/tech/references/development-standards.md', label: '完整开发规范' },
  { keywords: ['vendor', '子模块', '第三方依赖'], spec: '.agents/VENDOR-INTEGRATION.md', label: 'vendor 子模块协同' },
  { keywords: ['工作区发现', '零安装', '装载', '自举'], spec: '.agents/protocols/workspace-discovery.md', label: '工作区发现协议' },
  { keywords: ['提示词自举', '一句话装载', 'prompt-bootstrap'], spec: '.agents/protocols/prompt-bootstrap.md', label: '提示词自举协议' },
  { keywords: ['应用生命周期', 'app 迁移', '生命周期'], spec: '.agents/protocols/app-development-workflow.md', label: '应用开发生命周期' },
  { keywords: ['上下文路由', '路由表', 'context-routing'], spec: '.agents/context-routing.md', label: '上下文路由表' },
  { keywords: ['全局核心规则', 'global-core'], spec: '.agents/global-core-rules.md', label: '全局核心规则' },
  { keywords: ['能力注册', '能力清单', 'capability'], spec: '.agents/capability-registry.md', label: '能力注册中心' },
  { keywords: ['应用区', 'apps 区域', '内置应用'], spec: 'apps/AGENTS.md', label: 'apps 区域入口' },
  { keywords: ['子项目', 'projects 区域'], spec: 'projects/AGENTS.md', label: 'projects 区域入口' },
  { keywords: ['第三方仓库', 'vendor 区域'], spec: 'vendor/AGENTS.md', label: 'vendor 区域入口' },
  { keywords: ['知识库', 'okf', '知识包', 'wiki 教程'], spec: 'projects/awesome-okf-xs/doc/bundles/index.md', label: '最高可信度知识库' },
];

/**
 * 验证脚本路由表：变更类型 → 提交前应执行的校验命令。
 *
 * 插件**不代为执行**这些脚本（DSH 已提供 pwsh 工具，执行权限归会话沙箱与审批策略），
 * 只返回命令与判据，避免桥接层绕过宿主的安全边界。
 */
export const CHECK_COMMANDS = [
  {
    kinds: ['links', 'link', '断链', '链接'],
    command: 'python .agents/scripts/check-links.py --path <变更目录>',
    purpose: 'Markdown 相对路径断链与 file:/// 绝对路径检查',
  },
  {
    kinds: ['mermaid', '图表'],
    command: 'python check_mermaid.py',
    purpose: 'Mermaid 图表语法与安全编码校验',
  },
  {
    kinds: ['gitignore', '忽略规则'],
    command: 'python .agents/scripts/check-gitignore.py',
    purpose: '.gitignore 完整性检查',
  },
  {
    kinds: ['atomization', '原子化', '拆分'],
    command: 'python .agents/scripts/check-atomization-coverage.py',
    purpose: '原子化覆盖率预检',
  },
  {
    kinds: ['duplication', '重复代码', '重复'],
    command: 'python .agents/scripts/check-duplication.py',
    purpose: '跨文件重复代码检测（新增脚本前必跑）',
  },
  {
    kinds: ['traceability', '溯源', 'frontmatter'],
    command: 'python .agents/scripts/check-source-traceability.py',
    purpose: '派生产物 source 溯源字段检查',
  },
  {
    kinds: ['pwsh', 'powershell'],
    command: 'python .agents/scripts/check-pwsh7-compliance.py',
    purpose: 'Windows .ps1 必须 PowerShell 7.4+ 合规',
  },
  {
    kinds: ['ci', 'all', '全量', '提交前'],
    command: process.platform === 'win32' ? '.agents/scripts/ci-check.ps1' : '.agents/scripts/ci-check.sh',
    purpose: 'CI 综合检查（8 步流水线，提交前必跑）',
  },
];

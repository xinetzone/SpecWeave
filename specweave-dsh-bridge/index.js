/**
 * SpecWeave × DeepSeek Harness 桥接插件（Host 侧）。
 *
 * 目标：把 SpecWeave 工作区的 `AGENTS.md` + `.agents/` 规范容器变成 DSH 会话的**入口**——
 * 会话一进入 SpecWeave 工作区就自动获得启动协议提醒，并获得任务路由、状态查询与
 * 提交前校验三件能力；离开工作区则完全静默（brief 不注入）。
 *
 * 设计约束：
 * 1. **不改 system prompt**：启动协议 brief 经 `agent/pre-step` 注入到用户消息层，
 *    宿主 system prompt 保持字节级不变（对齐 Hermes 先例 specweave-bridge 的
 *    Footprint Ladder 原则与 DSH `references/practices.md` 的 context 扩展点）。
 * 2. **服务门控**：`tools` 为必需依赖；`commands`/`skills` 通过 `ctx.inject` 可选挂载，
 *    宿主没有这些服务时插件依然可用。
 * 3. **不执行脚本**：`specweave_check` 只返回校验命令，执行归会话沙箱与审批策略。
 *
 * @module @specweave/dsh-bridge
 */

import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  PLUGIN_ID,
  PLUGIN_VERSION,
  PRIVATE_DOCS_ROOT,
  PUBLIC_DOCS_ROOT,
  RETIRED_DOCS_DIR,
  SIGNATURE_KEYWORD,
  SIGNATURE_PATHS,
  WORKSPACE_SKILL_PROVIDER,
  WORKSPACE_SKILL_RANK,
} from './lib/constants.js';
import { FALLBACK_PROTOCOL, renderStartupBrief } from './lib/brief.js';
import { matchCheckCommands } from './lib/checks.js';
import { detectWorkspace } from './lib/detector.js';
import { createUserMessage, defineTool } from './lib/host-shims.js';
import { resolveRoutes } from './lib/routes.js';
import { readWorkspaceSkills } from './lib/skill-catalog.js';

/** Cordis 插件名，与 cordis.patch.yml 的 row name 一致。 */
export const name = PLUGIN_ID;

/** 必需服务：工具注册表。 */
export const inject = ['tools'];

// 说明：本插件**刻意不导入任何 `@deepseek-ai/*` 宿主包**，也不导出 `Config`。
// 原因：`plugin_manager install_bundle` 装入 profile 的 bundle 无法解析宿主包
// （宿主包只存在于 dsh 安装的 app.asar 内，profile 侧 node_modules 只有被装的包），
// 一旦 import 宿主包，行激活即 `failed to import`；官方 bundle 模板同样不含任何 import。
// 代价与对策：无 Config 即无 row config 的 schema 校验，配置项在 README 中逐项列出，
// 且 `resolveConfig` 对每个键都提供了默认值。

/** 注入消息的来源标记：用于幂等判定与宿主侧溯源。 */
const SOURCE_KIND = 'specweave-bridge';

/** 工作区检测缓存上限：超限即整体清空，避免长期宿主内的慢性增长（重探测成本极低）。 */
const MAX_DETECTION_CACHE_ENTRIES = 128;

/** 协议技能在磁盘上的相对路径。 */
const SKILL_RELATIVE_PATH = join('skills', 'specweave-protocol', 'SKILL.md');

/** 工具输出中数组条目的 JSON Schema（原生形态，含顶层 required 数组）。 */
const ROUTE_ITEM_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    label: { type: 'string' },
    spec: { type: 'string' },
    exists: { type: 'boolean' },
  },
  required: ['label', 'spec'],
};

/** 通用对象根 schema 的构造器：省去四处重复的 `type`/`additionalProperties`。 */
function objectSchema(properties, required) {
  return { type: 'object', additionalProperties: false, properties, ...(required === undefined ? {} : { required }) };
}

/** 参数表（原生 JSON Schema）：宿主 `assertSupportedJsonSchema` 只认这一子集。 */
function parametersSchema(properties, required) {
  return { type: 'object', properties, ...(required === undefined ? {} : { required }) };
}

// ── 工具结果的模型可见文本 ────────────────────────────────────────────────────
// 宿主的 `output.render` 返回值**就是**进入模型历史的工具结果内容（对齐 dsh-tool-skill 的
// `renderSkillContent` 用法）。因此 render 必须承载完整信息——只回一句摘要等于让模型拿不到答案。

/** 渲染路由工具结果。 */
function renderRouteText(value) {
  const where = value.in_workspace
    ? `工作区：${value.root}；子区域：${value.area ?? '无'}`
    : '当前不在 SpecWeave 工作区内（未做存在性校验）';
  const lines = [`SpecWeave 路由（${where}）`, `任务：${value.task}`];
  if (value.matched.length === 0) {
    lines.push(`未命中具体路由，请读取 ${value.fallback} 定位必读规范。`);
  } else {
    lines.push('命中：');
    for (const entry of value.matched) {
      const stale = entry.exists === false ? '（⚠ 路径在工作区中不存在，已 stale）' : '';
      lines.push(`- ${entry.label} → ${entry.spec}${stale}`);
    }
  }
  lines.push(value.note);
  return lines.join('\n');
}

/** 渲染状态工具结果。 */
function renderStatusText(value) {
  if (!value.in_workspace) {
    return '当前不在 SpecWeave 工作区内（未找到同时具备「AGENTS.md 含签名关键词」与「.agents/context-routing.md」的目录）。';
  }
  const lines = [
    `SpecWeave 工作区：${value.root}`,
    `子区域：${value.area ?? '无'}${value.area_entry === undefined ? '' : `（进入前先读 ${value.area_entry}）`}`,
    `入口：${value.entry}　路由表：${value.routing_table}`,
    `产出物路径：公开 → ${value.public_root}；私域 → ${value.private_root}；废止 → ${value.retired_root}`,
    `桥接版本：${value.bridge_version}`,
  ];
  return lines.join('\n');
}

/** 渲染校验命令工具结果。 */
function renderCheckText(value) {
  const lines = [`SpecWeave 提交前校验（kind=${value.kind.length === 0 ? '全量' : value.kind}）：`];
  for (const entry of value.commands) lines.push(`- ${entry.command}\n  ${entry.purpose}`);
  lines.push(value.note);
  return lines.join('\n');
}

/** 渲染协议工具结果：直接返回协议正文本身。 */
function renderProtocolText(value) {
  return value.protocol.length > 0 ? value.protocol : FALLBACK_PROTOCOL;
}

/** 解析后的配置默认值（无 Config schema 时的兜底，便于单元测试直接调用 apply）。 */
function resolveConfig(config) {
  const input = config === undefined || config === null ? {} : config;
  return {
    enabled: input.enabled !== false,
    injectBrief: input.injectBrief !== false,
    registerTools: input.registerTools !== false,
    registerCommand: input.registerCommand !== false,
    registerSkill: input.registerSkill !== false,
    maxBriefBytes: Number.isFinite(input.maxBriefBytes) ? input.maxBriefBytes : 4096,
    signatureKeyword: typeof input.signatureKeyword === 'string' && input.signatureKeyword.length > 0
      ? input.signatureKeyword
      : SIGNATURE_KEYWORD,
    signaturePaths: Array.isArray(input.signaturePaths) && input.signaturePaths.length > 0
      ? input.signaturePaths
      : [...SIGNATURE_PATHS],
    registerWorkspaceSkills: input.registerWorkspaceSkills !== false,
    skillSelection: input.skillSelection === 'all' ? 'all' : 'routes',
    workspaceSkillsDir: typeof input.workspaceSkillsDir === 'string' && input.workspaceSkillsDir.length > 0
      ? input.workspaceSkillsDir
      : '.agents/skills',
  };
}

/**
 * 读取协议技能的 SKILL.md 正文（剥离 YAML frontmatter）。
 * @param {string} pluginDir - 插件包目录绝对路径。
 * @returns {Promise<string|null>} 正文；文件缺失或读取失败返回 null。
 */
async function readProtocolSkillBody(pluginDir) {
  try {
    const raw = await readFile(join(pluginDir, SKILL_RELATIVE_PATH), { encoding: 'utf8' });
    const match = /^---\r?\n[\s\S]*?\r?\n---\r?\n?/.exec(raw);
    return (match === null ? raw : raw.slice(match[0].length)).trim();
  } catch {
    return null;
  }
}

/**
 * 扫描会话日志（surface），判断该工作区的 brief 是否已经落盘。
 *
 * 三态返回：`present` 已落盘；`absent` 确认没有；`unknown` 扫描失败——
 * 调用方对 `unknown` 必须「本轮不注入、也不置为已注入」，留待下一步重试，
 * 既避免重复注入，也避免把一次扫描失败当成"已注入"而永久丢失 brief。
 *
 * @param {object} agent - 宿主 Agent。
 * @param {string} root - 工作区根。
 * @returns {'present'|'absent'|'unknown'} 扫描结论。
 */
function scanSessionSurface(agent, root) {
  try {
    const nodes = agent?.session?.surface?.nodes;
    if (nodes === undefined) return 'absent';
    for (const seq of nodes) {
      const event = agent.session.eventAt(seq);
      const source = event?.type === 'user/message' ? event.data?.source : undefined;
      if (source?.kind === SOURCE_KIND && source.root === root) return 'present';
    }
    return 'absent';
  } catch {
    return 'unknown';
  }
}

/**
 * 判断本步消息批次里是否已带有该工作区的 brief（claim 自会话日志，等同已落盘证据）。
 * @param {object} decision - pre-step 决策对象。
 * @param {string} root - 工作区根。
 * @returns {boolean} 命中返回 true。
 */
function claimedHasBrief(decision, root) {
  const messages = Array.isArray(decision?.messages) ? decision.messages : [];
  return messages.some((message) => message?.source?.kind === SOURCE_KIND && message.source.root === root);
}

/**
 * 注册桥接插件。
 * @param {object} ctx - Cordis 上下文。
 * @param {object} [config] - 插件配置。
 */
export function apply(ctx, config) {
  const resolved = resolveConfig(config);
  if (!resolved.enabled) return;

  /** cwd → 检测结果 缓存，避免每个 step 重复探测文件系统（有上限，防长期宿主内的慢性增长）。 */
  const detections = new Map();
  /**
   * session → `{ root, confirmed }` 注入状态。
   * `confirmed: true` 表示已在会话日志中观察到 brief，之后 O(1) 跳过；
   * 未确认时下一步会重新扫描，扫描不到即重新注入（自愈），
   * 避免"pre-step 与 step 之间被中止"导致本会话永久失去 brief。
   */
  const injected = new WeakMap();
  /** 已就「日志扫描失败」告警过的会话：同会话只提示一次，避免每步刷日志。 */
  const scanWarned = new WeakSet();
  /** 已就「上限过低致注入被禁用」告警过的会话：与扫描失败告警相互独立，避免一类告警屏蔽另一类。 */
  const capWarned = new WeakSet();
  /** 工作区根 → 技能清单（读盘结果缓存；注册动作仍按 agent 作用域执行）。 */
  const workspaceSkills = new Map();
  /** 插件包目录：协议技能文件的定位基准（不依赖 import.meta.dirname 的 Node 版本门槛）。 */
  const pluginDir = fileURLToPath(new URL('.', import.meta.url));
  /** 卸载标记：异步注册（技能文件读取）在插件卸载后不得再落到已释放的上下文。 */
  let disposed = false;

  ctx.effect(() => () => {
    disposed = true;
    detections.clear();
    workspaceSkills.clear();
  }, 'specweave-bridge.cache');

  const detect = async (cwd) => {
    if (typeof cwd !== 'string' || cwd.length === 0) return null;
    if (!detections.has(cwd)) {
      if (detections.size >= MAX_DETECTION_CACHE_ENTRIES) detections.clear();
      detections.set(cwd, await detectWorkspace(cwd, {
        signatureKeyword: resolved.signatureKeyword,
        signaturePaths: resolved.signaturePaths,
      }));
    }
    return detections.get(cwd);
  };

  const cwdOf = (agent) => agent?.session?.header?.cwd;

  /**
   * 解析某个 cwd 对应的 SpecWeave 工作区根。
   * @param {string|undefined} cwd - 工作目录（技能 provider 拿到的 `options.cwd`）。
   * @returns {Promise<string|null>} 工作区根；不在工作区内或 cwd 缺失时返回 null。
   */
  const workspaceRootOf = async (cwd) => {
    const detection = await detect(cwd);
    if (detection === null || !detection.inWorkspace) return null;
    return detection.root;
  };

  /**
   * 读取（并缓存）工作区技能清单。
   * @param {string} root - 工作区根绝对路径。
   * @returns {Promise<Array<{name: string, description: string, content: string, dir: string}>>} 技能清单。
   */
  const loadWorkspaceSkills = async (root) => {
    if (!workspaceSkills.has(root)) {
      workspaceSkills.set(root, await readWorkspaceSkills(
        join(root, resolved.workspaceSkillsDir),
        { selection: resolved.skillSelection },
      ));
    }
    return workspaceSkills.get(root);
  };

  // ── 启动协议 brief：注入到用户消息层，system prompt 保持不变 ────────────────
  if (resolved.injectBrief) {
    ctx.on('agent/pre-step', async ({ agent, messages: claimedMessages, step, signal }, next) => {
      const decision = await next();
      if (decision?.kind === 'reject') return decision;
      if (signal !== undefined) signal.throwIfAborted();
      const cwd = cwdOf(agent);
      if (typeof cwd !== 'string' || cwd.length === 0) return decision;
      const entered = Array.isArray(decision.messages) ? decision.messages : [];
      // 对齐宿主护栏：空批次的一步不做任何注入
      // （dsh-agent-loop 以 messages.length === 0 判定"本回合干净结束"）。
      if (step === 1 && entered.length === 0) return decision;
      const detection = await detect(cwd);
      if (detection === null || !detection.inWorkspace) return decision;
      const root = detection.root;
      const session = agent.session;
      const state = injected.get(session);
      if (state !== undefined && state.root === root && state.confirmed) return decision;
      if (claimedHasBrief(decision, root)) {
        injected.set(session, { root, confirmed: true });
        return decision;
      }
      const scan = scanSessionSurface(agent, root);
      if (scan === 'present') {
        injected.set(session, { root, confirmed: true });
        return decision;
      }
      if (scan === 'unknown') {
        // 扫描失败：本轮不注入也不确认，下一步重试——避免重复注入与永久丢失两种坏结局。
        // 告警按会话节流一次：surface 形状长期异常时不应每个 step 刷一条日志。
        if (!scanWarned.has(session)) {
          scanWarned.add(session);
          ctx.logger.warn('specweave-bridge: 会话日志扫描失败，暂停注入并在后续 step 重试');
        }
        return decision;
      }
      const text = renderStartupBrief(detection, { maxBytes: resolved.maxBriefBytes });
      if (text.length === 0) {
        // 工作区内但被上限禁用：给出一次性诊断，避免用户把 maxBriefBytes 设太小后完全静默（R3-N1）。
        if (!capWarned.has(session)) {
          capWarned.add(session);
          ctx.logger.warn('specweave-bridge: maxBriefBytes(%d) 低于最小可用值，已禁用启动协议注入', resolved.maxBriefBytes);
        }
        return decision;
      }
      // 插入位置：紧随本步被 claim 的用户消息之后，使 brief 落在用户消息层
      // （对齐 dsh-agent-instructions 的 pre-step 改写范式）；未匹配到则追加到末尾。
      const claimed = Array.isArray(claimedMessages) ? claimedMessages : [];
      const lastClaimed = entered.findLastIndex((message) => claimed.includes(message));
      const brief = createUserMessage({
        content: [{ type: 'text', text }],
        source: { kind: SOURCE_KIND, form: 'instructions', root, area: detection.area },
      });
      // 只记"待确认"：不预置 confirmed，落盘证据由下一次 pre-step 的扫描回填（自愈）。
      injected.set(session, { root, confirmed: false });
      return {
        ...decision,
        messages: lastClaimed >= 0
          ? [...entered.slice(0, lastClaimed + 1), brief, ...entered.slice(lastClaimed + 1)]
          : [...entered, brief],
      };
    });
  }

  // ── 工具：任务路由 / 工作区状态 / 校验命令 / 协议文本 ──────────────────────
  if (resolved.registerTools) {
    ctx.tools.register(defineTool({
      name: 'specweave_route',
      description: '查询 SpecWeave 任务对应的规范入口路径。工作区外仍返回匹配到的规范路径，但不做存在性校验（exists 字段省略）。',
      parameters: parametersSchema({
        task: { type: 'string', description: '任务描述或触发词，例如「复盘」「画个架构图」「提交代码」。' },
        cwd: { type: 'string', description: '查询基准目录；缺省取当前会话工作目录。' },
      }, ['task']),
      output: {
        schema: objectSchema({
          in_workspace: { type: 'boolean' },
          task: { type: 'string' },
          root: { type: 'string' },
          area: { type: 'string' },
          matched: { type: 'array', items: ROUTE_ITEM_SCHEMA },
          stale: { type: 'array', items: { type: 'string' } },
          fallback: { type: 'string' },
          note: { type: 'string' },
        }, ['in_workspace', 'task', 'matched', 'stale', 'fallback', 'note']),
        render: (_args, value) => [{ type: 'text', text: renderRouteText(value) }],
      },
      async execute(args, exec) {
        const cwd = typeof args.cwd === 'string' && args.cwd.length > 0 ? args.cwd : cwdOf(exec?.agent);
        const detection = await detect(cwd);
        const root = detection !== null && detection.inWorkspace ? detection.root : null;
        const routes = await resolveRoutes(root, args.task);
        const staleNote = routes.stale.length > 0
          ? `以下路由目标在工作区中不存在，已标记 stale，请以 ${routes.fallback} 为准：${routes.stale.join('、')}`
          : `无命中或需完整映射时，读取 ${routes.fallback}。`;
        return {
          in_workspace: root !== null,
          task: routes.task,
          ...(root === null ? {} : { root }),
          ...(detection?.area === null || detection?.area === undefined ? {} : { area: detection.area }),
          matched: routes.matched.map((entry) => ({
            label: entry.label,
            spec: entry.spec,
            ...(entry.exists === null ? {} : { exists: entry.exists }),
          })),
          stale: routes.stale,
          fallback: routes.fallback,
          note: staleNote,
        };
      },
    }));

    ctx.tools.register(defineTool({
      name: 'specweave_status',
      description: '报告当前会话是否位于 SpecWeave 工作区、所处子区域、入口文件与产出物根目录约定。',
      parameters: parametersSchema({
        cwd: { type: 'string', description: '查询基准目录；缺省取当前会话工作目录。' },
      }),
      output: {
        schema: objectSchema({
          in_workspace: { type: 'boolean' },
          root: { type: 'string' },
          area: { type: 'string' },
          area_entry: { type: 'string' },
          entry: { type: 'string' },
          routing_table: { type: 'string' },
          public_root: { type: 'string' },
          private_root: { type: 'string' },
          retired_root: { type: 'string' },
          bridge_version: { type: 'string' },
        }, ['in_workspace', 'entry', 'routing_table', 'public_root', 'private_root', 'retired_root', 'bridge_version']),
        render: (_args, value) => [{ type: 'text', text: renderStatusText(value) }],
      },
      async execute(args, exec) {
        const cwd = typeof args.cwd === 'string' && args.cwd.length > 0 ? args.cwd : cwdOf(exec?.agent);
        const detection = await detect(cwd);
        return {
          in_workspace: detection !== null && detection.inWorkspace,
          ...(detection === null || !detection.inWorkspace ? {} : { root: detection.root }),
          ...(detection?.area === null || detection?.area === undefined ? {} : { area: detection.area }),
          ...(detection?.areaEntry === null || detection?.areaEntry === undefined ? {} : { area_entry: detection.areaEntry }),
          entry: 'AGENTS.md',
          routing_table: '.agents/context-routing.md',
          public_root: `${PUBLIC_DOCS_ROOT}/`,
          private_root: `${PRIVATE_DOCS_ROOT}/`,
          retired_root: `${RETIRED_DOCS_DIR}/`,
          bridge_version: PLUGIN_VERSION,
        };
      },
    }));

    ctx.tools.register(defineTool({
      name: 'specweave_check',
      description: '返回 SpecWeave 提交前校验命令与判据（只回答「跑什么」，不代为执行——执行请用 pwsh 工具）。',
      parameters: parametersSchema({
        kind: { type: 'string', description: '变更类型：links / mermaid / gitignore / atomization / duplication / traceability / pwsh / ci；缺省返回全量清单。' },
      }),
      output: {
        schema: objectSchema({
          kind: { type: 'string' },
          commands: {
            type: 'array',
            items: objectSchema({
              command: { type: 'string' },
              purpose: { type: 'string' },
            }, ['command', 'purpose']),
          },
          note: { type: 'string' },
        }, ['kind', 'commands', 'note']),
        render: (_args, value) => [{ type: 'text', text: renderCheckText(value) }],
      },
      execute(args) {
        const kind = typeof args?.kind === 'string' ? args.kind : '';
        const commands = matchCheckCommands(kind).map((entry) => ({ command: entry.command, purpose: entry.purpose }));
        return {
          kind,
          commands,
          note: '桥接层不代为执行校验脚本；请用 pwsh 工具在 SpecWeave 工作区根目录执行上述命令，失败即视为门禁未过。',
        };
      },
    }));

    ctx.tools.register(defineTool({
      name: 'specweave_protocol',
      description: '返回 SpecWeave 启动协议要点与产出物路径纪律（技能目录不可用时的兜底入口）。',
      parameters: parametersSchema({
        cwd: { type: 'string', description: '查询基准目录；缺省取当前会话工作目录。' },
      }),
      output: {
        schema: objectSchema({
          in_workspace: { type: 'boolean' },
          root: { type: 'string' },
          protocol: { type: 'string' },
        }, ['in_workspace', 'protocol']),
        render: (_args, value) => [{ type: 'text', text: renderProtocolText(value) }],
      },
      async execute(args, exec) {
        const cwd = typeof args.cwd === 'string' && args.cwd.length > 0 ? args.cwd : cwdOf(exec?.agent);
        const detection = await detect(cwd);
        const inWorkspace = detection !== null && detection.inWorkspace;
        // 工作区外也给与工作区无关的协议要点，避免"兜底入口在工作区外什么都不给"。
        const brief = inWorkspace
          ? renderStartupBrief(detection, { maxBytes: resolved.maxBriefBytes })
          : FALLBACK_PROTOCOL;
        return {
          in_workspace: inWorkspace,
          ...(inWorkspace ? { root: detection.root } : {}),
          protocol: brief.length > 0 ? brief : FALLBACK_PROTOCOL,
        };
      },
    }));
  }

  // ── 人机命令：/specweave status | route <任务> | help ──────────────────────
  if (resolved.registerCommand) {
    ctx.inject(['commands'], (commandCtx) => {
      commandCtx.effect(() => commandCtx.commands.register({
        name: 'specweave',
        description: 'SpecWeave 工作区入口：状态、任务路由、帮助',
        input: { hint: 'status | route <任务> | help' },
        async handler(invocation) {
          const raw = typeof invocation?.rawInput === 'string' ? invocation.rawInput.trim() : '';
          const [subcommand, ...rest] = raw.split(/\s+/).filter((part) => part.length > 0);
          const cwd = cwdOf(invocation?.agent);
          const detection = await detect(cwd);
          if (subcommand === undefined || subcommand === 'status') {
            if (detection === null || !detection.inWorkspace) {
              return { kind: 'error', text: '当前会话不在 SpecWeave 工作区内（未找到含「启动协议」的 AGENTS.md）。' };
            }
            const area = detection.area === null ? '无' : detection.area;
            return {
              kind: 'success',
              text: [
                `SpecWeave 工作区：${detection.root}`,
                `子区域：${area}${detection.areaEntry === null ? '' : `（入口 ${detection.areaEntry}）`}`,
                `入口：AGENTS.md　路由表：${detection.routingTable}`,
                `公开产出物：${PUBLIC_DOCS_ROOT}/　私域产出物：${PRIVATE_DOCS_ROOT}/　废止路径：${RETIRED_DOCS_DIR}/`,
              ].join('\n'),
            };
          }
          if (subcommand === 'route') {
            const task = rest.join(' ');
            if (task.length === 0) return { kind: 'error', text: '用法：/specweave route <任务描述>' };
            const root = detection !== null && detection.inWorkspace ? detection.root : null;
            const routes = await resolveRoutes(root, task);
            if (routes.matched.length === 0) {
              return { kind: 'success', text: `未命中具体路由，请读取 ${routes.fallback} 定位必读规范。` };
            }
            const lines = routes.matched.map((entry) => `- ${entry.label} → ${entry.spec}${entry.exists === false ? '（⚠ 路径不存在，已 stale）' : ''}`);
            return { kind: 'success', text: [`任务：${task}`, ...lines, `兜底：${routes.fallback}`].join('\n') };
          }
          if (subcommand === 'skill') {
            // 承接中文触发词：DSH 的 `/name` 手势只认 ASCII kebab 技能名，
            // 因此把「触发词 → 技能名」的解析放在本子命令里，并把技能正文排队进下一步。
            const query = rest.join(' ').trim();
            if (query.length === 0) return { kind: 'error', text: '用法：/specweave skill <触发词或技能名>' };
            const root = detection !== null && detection.inWorkspace ? detection.root : null;
            const routes = await resolveRoutes(root, query);
            const fromRoute = routes.matched
              .map((entry) => /^\.agents\/skills\/([^/]+)\/SKILL\.md$/.exec(entry.spec)?.[1])
              .filter((name) => name !== undefined);
            const direct = /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(query) ? query : undefined;
            const target = fromRoute[0] ?? direct;
            if (target === undefined) {
              return {
                kind: 'error',
                text: `未找到与「${query}」对应的技能。可用 /specweave route ${query} 查看命中项，或直接给出技能名（如 /specweave skill seven-concepts-cmd）。`,
              };
            }
            const skills = root === null ? [] : await loadWorkspaceSkills(root);
            const skill = skills.find((entry) => entry.name === target);
            const agent = invocation?.agent;
            if (skill !== undefined && typeof agent?.inject === 'function') {
              agent.inject(createUserMessage({
                content: [{ type: 'text', text: `<skill_content name="${skill.name}">\n${skill.content}\n</skill_content>` }],
                source: { kind: SOURCE_KIND, form: 'instructions', skill: skill.name },
              }));
              return {
                kind: 'success',
                text: `已把技能 ${skill.name} 排入下一步（${skill.dir}）；下一条消息起生效。`,
              };
            }
            return {
              kind: 'success',
              text: `触发词「${query}」对应技能 ${target}；请让智能体用 skill 工具加载它，或读取 .agents/skills/${target}/SKILL.md。`,
            };
          }
          if (subcommand === 'help') {
            return {
              kind: 'success',
              text: [
                'SpecWeave 工作区入口命令：',
                '/specweave status — 报告工作区根、子区域与产出物路径纪律',
                '/specweave route <任务> — 查询任务对应的规范入口',
                '/specweave skill <触发词> — 由中文触发词解析技能并把技能正文排入下一步',
                '/specweave help — 显示本帮助',
                '模型侧工具：specweave_route / specweave_status / specweave_check / specweave_protocol',
              ].join('\n'),
            };
          }
          return { kind: 'error', text: `未知子命令：${subcommand}（可用 status | route | skill | help）` };
        },
      }), 'specweave-bridge.command');
    });
  }

  // ── 只读协议技能：技能目录不可用时仍有 specweave_protocol 工具兜底 ──────────
  if (resolved.registerSkill) {
    ctx.inject(['skills'], (skillCtx) => {
      readProtocolSkillBody(pluginDir).then((content) => {
        if (disposed) return;
        if (content === null || content.length === 0) {
          ctx.logger.warn('specweave-bridge: protocol skill file missing, skill not registered');
          return;
        }
        skillCtx.effect(() => skillCtx.skills.register({
          name: 'specweave-protocol',
          description: 'SpecWeave 启动协议、内容敏感度分流与产出物路径纪律参考；进入 SpecWeave 工作区执行任务前先加载。',
          whenToUse: '会话工作目录位于 SpecWeave 工作区，且任务涉及规范读取、产出物落盘位置或子区域路由时。',
          content,
          source: PLUGIN_ID,
          invocation: { modelInvocable: true, userInvocable: true },
          provider: PLUGIN_ID,
        }), 'specweave-bridge.skill');
      }).catch((error) => {
        ctx.logger.warn('specweave-bridge: protocol skill registration failed: %o', error);
      });
    });
  }

  // ── 工作区技能提供方：绕开失效的宿主文件系统 provider，按 cwd 过滤 ────────────
  // 背景：桌面构建下 `dsh-skill-filesystem` 对本工作区 `.agents/skills` 返回 0 候选，
  // 导致 `.agents/skills` 里的技能无法被 `/name` 手势或 `skill` 工具命中。
  // 做法：在**插件作用域**注册 provider，用 `options.cwd` 判定工作区根，命中才给候选。
  //
  // 教训（2026-09-30「新建会话失败：cannot get property "skills" without inject」）：
  // 早期实现把工作区技能注册到 `agent.ctx`。agent 作用域上下文解析不到 `skills` 服务，
  // `agentCtx?.skills === undefined` 这句属性探测**直接抛错**；而 `agent/created`
  // 监听器位于会话创建事务内，异常会让整个 `session/new` 失败——现象就是
  // 「SpecWeave 工作区新建会话必失败，非工作区的默认工作区却一切正常」。
  // 宿主规范要求可选服务一律走 `ctx.inject([...])`，禁止用属性探测；
  // provider 方案同时消掉了「技能按 agent 泄漏到其它工作区」的风险：候选按 cwd 过滤。
  if (resolved.registerWorkspaceSkills) {
    ctx.inject(['skills'], (skillCtx) => {
      skillCtx.effect(() => skillCtx.skills.registerProvider(() => ({
        name: WORKSPACE_SKILL_PROVIDER,
        async list(options = {}) {
          options.signal?.throwIfAborted?.();
          const root = await workspaceRootOf(options.cwd);
          if (root === null) return [];
          const skills = await loadWorkspaceSkills(root);
          options.signal?.throwIfAborted?.();
          return skills.map((skill) => toWorkspaceSkillCandidate(skill));
        },
        async get(candidate, options = {}) {
          options.signal?.throwIfAborted?.();
          const root = await workspaceRootOf(options.cwd);
          if (root === null) return undefined;
          const skills = await loadWorkspaceSkills(root);
          const skill = skills.find((entry) => entry.name === candidate.name);
          if (skill === undefined) return undefined;
          return {
            ...toWorkspaceSkillCandidate(skill),
            path: join(skill.dir, 'SKILL.md'),
            content: skill.content,
          };
        },
      })), 'specweave-bridge.workspace-skills');
    });
  }
}

/**
 * 把工作区技能条目映射为宿主 provider 候选（摘要层，不含正文）。
 * @param {{name: string, description: string, dir: string}} skill - 技能条目。
 * @returns {object} 宿主 provider 候选（name/description/whenToUse/invocation/source/rank/provider）。
 */
function toWorkspaceSkillCandidate(skill) {
  return {
    name: skill.name,
    description: skill.description,
    whenToUse: `SpecWeave 工作区技能（${skill.dir}）；任务命中该技能描述时加载。`,
    invocation: { modelInvocable: true, userInvocable: true },
    source: WORKSPACE_SKILL_PROVIDER,
    rank: WORKSPACE_SKILL_RANK,
    provider: WORKSPACE_SKILL_PROVIDER,
  };
}

/**
 * SpecWeave DSH 桥接插件自测套件。
 *
 * 运行：node --test tests/bridge.test.js
 * （等价于在插件目录执行 `node --run test` / `pnpm test`，见 package.json scripts.test）
 *
 * 覆盖范围：
 * 1. 工作区检测（签名命中、向上回溯、子区域判定）；
 * 2. 路由匹配与存在性校验；
 * 3. 校验命令解析；
 * 4. brief 渲染（框架标记、转义、字节上限）；
 * 5. 插件契约（导出、工具/命令/技能注册）；
 * 6. pre-step 注入（命中注入一次、非工作区静默、reject 透传）；
 * 7. 工具执行 + 输出 schema 一致性（由 stub 的 defineTool 强制校验）；
 * 8. 协议技能文件与 frontmatter 合规。
 */

import { readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import assert from 'node:assert/strict';
import test from 'node:test';

import * as pluginModule from '../index.js';
import { apply, inject as pluginInject, name as pluginName } from '../index.js';
import { FRAME_BYTES, MIN_BRIEF_BYTES, renderStartupBrief, truncateUtf8 } from '../lib/brief.js';
import { matchCheckCommands } from '../lib/checks.js';
import { detectSubregion, detectWorkspace, findSpecweaveRoot, isSpecweaveWorkspace } from '../lib/detector.js';
import { matchRoutes, resolveRoutes } from '../lib/routes.js';
import { parseSkillFrontmatter, readWorkspaceSkills } from '../lib/skill-catalog.js';
import { validateValue } from './lib/schema-validator.js';

/** 插件目录与仓库根（测试从插件目录运行）。 */
const PLUGIN_DIR = join(import.meta.dirname, '..');
const REPO_ROOT = join(PLUGIN_DIR, '..');

/**
 * 构造一个最小 Cordis 上下文，用于断言注册行为。
 * @param {string[]} services - 可用服务名列表。
 * @returns {{ctx: object, tools: Map<string, object>, commands: object[], skills: object[], providers: object[], listeners: Map<string, Function[]>}} 测试夹具。
 */
function createHarness(services = ['tools', 'commands', 'skills']) {
  const tools = new Map();
  const commands = [];
  const skills = [];
  const providers = [];
  const listeners = new Map();
  const disposers = [];
  const warnings = [];
  const ctx = {
    logger: { warn: (...args) => warnings.push(args) },
    effect(fn) {
      const disposer = fn();
      const dispose = () => {
        if (typeof disposer === 'function') disposer();
      };
      disposers.push(dispose);
      return dispose;
    },
    on(event, handler) {
      const list = listeners.get(event) ?? [];
      list.push(handler);
      listeners.set(event, list);
    },
    inject(deps, callback) {
      if (deps.every((dependency) => services.includes(dependency))) return callback(ctx);
      return () => {};
    },
    tools: {
      register(tool) {
        tools.set(tool.name, tool);
        return () => tools.delete(tool.name);
      },
    },
    commands: {
      register(definition) {
        commands.push(definition);
        return () => {};
      },
    },
    skills: {
      register(definition) {
        skills.push(definition);
        return () => {};
      },
      registerProvider(factory) {
        const provider = factory({ invalidate() {} });
        providers.push(provider);
        return () => {
          const index = providers.indexOf(provider);
          if (index >= 0) providers.splice(index, 1);
        };
      },
    },
  };
  return { ctx, tools, commands, skills, providers, listeners, disposers, warnings };
}

/**
 * 构造一个最小 Agent 夹具。
 * @param {string} cwd - 会话工作目录。
 * @returns {object} Agent 夹具。
 */
function createAgent(cwd) {
  const agent = {
    injected: [],
    session: {
      header: { cwd },
      surface: { nodes: [] },
      eventAt: () => undefined,
    },
    inject(message) {
      agent.injected.push(message);
    },
    ctx: {
      skills: {
        registered: [],
        register(definition) {
          agent.ctx.skills.registered.push(definition);
          return () => {};
        },
      },
      effect(fn) {
        const disposer = fn();
        return () => {
          if (typeof disposer === 'function') disposer();
        };
      },
    },
  };
  return agent;
}

/** 等待一个宏任务，供异步注册（技能文件读取）落地。 */
function settle() {
  return new Promise((resolve) => setTimeout(resolve, 50));
}

/**
 * 执行一个已注册工具，并按它声明的 `output.schema` 校验返回值。
 * 宿主在真实执行边界做同样的校验，这里在测试侧独立复现，防止 schema 与返回值漂移。
 * @param {Map<string, object>} tools - 已注册工具表。
 * @param {string} toolName - 工具名。
 * @param {object} args - 参数。
 * @param {object} exec - 执行上下文（至少含 `agent`）。
 * @returns {Promise<object>} 校验通过的返回值。
 */
async function runTool(tools, toolName, args, exec) {
  const tool = tools.get(toolName);
  assert.ok(tool, `未注册工具 ${toolName}`);
  const value = await tool.execute(args, exec);
  const violations = validateValue(value, tool.output.schema);
  assert.deepEqual(violations, [], `${toolName} 返回值不符合 output.schema：${violations.join('; ')}`);
  return value;
}

test('检测：仓库根被识别为 SpecWeave 工作区', async () => {
  assert.equal(await isSpecweaveWorkspace(REPO_ROOT), true);
  assert.equal(await isSpecweaveWorkspace(tmpdir()), false);
});

test('检测：含「启动协议」但缺路由表的子区域不得被误判为工作区根', async () => {
  // 回归防线：apps/projects/vendor 的 AGENTS.md 同样含「启动协议」字样，
  // 仅凭关键词判定会让子区域路由整体失效（本用例即当初暴露的真实缺陷）。
  for (const subregion of ['apps', 'projects', 'vendor']) {
    assert.equal(
      await isSpecweaveWorkspace(join(REPO_ROOT, subregion)),
      false,
      `${subregion}/ 不应被识别为工作区根`,
    );
    assert.equal(await findSpecweaveRoot(join(REPO_ROOT, subregion)), REPO_ROOT);
  }
});

test('检测：从子目录向上回溯到工作区根', async () => {
  const nested = join(REPO_ROOT, '.agents', 'skills');
  assert.equal(await findSpecweaveRoot(nested), REPO_ROOT);
  assert.equal(await findSpecweaveRoot(tmpdir()), null);
});

test('检测：子区域判定（apps/projects/vendor）与根区域', async () => {
  assert.equal(detectSubregion(join(REPO_ROOT, 'apps'), REPO_ROOT), 'apps');
  assert.equal(detectSubregion(join(REPO_ROOT, 'apps', 'dev-tools'), REPO_ROOT), 'apps');
  assert.equal(detectSubregion(join(REPO_ROOT, 'vendor', 'flexloop'), REPO_ROOT), 'vendor');
  assert.equal(detectSubregion(REPO_ROOT, REPO_ROOT), null);
  assert.equal(detectSubregion(tmpdir(), REPO_ROOT), null);
});

test('检测：detectWorkspace 汇总工作区根、子区域与入口文件', async () => {
  const root = await detectWorkspace(REPO_ROOT);
  assert.equal(root.inWorkspace, true);
  assert.equal(root.root, REPO_ROOT);
  assert.equal(root.area, null);
  assert.equal(root.routingTable, '.agents/context-routing.md');

  const inApps = await detectWorkspace(join(REPO_ROOT, 'apps'));
  assert.equal(inApps.area, 'apps');
  assert.equal(inApps.areaEntry, 'apps/AGENTS.md');

  const outside = await detectWorkspace(tmpdir());
  assert.equal(outside.inWorkspace, false);
  assert.equal(outside.root, null);
});

test('路由：关键词多命中与无命中回退', () => {
  const review = matchRoutes('给我做个复盘');
  assert.ok(review.some((entry) => entry.spec === '.agents/skills/retrospective-cmd/SKILL.md'));

  const diagram = matchRoutes('画个架构图');
  assert.ok(diagram.some((entry) => entry.spec === '.agents/skills/mermaid-cmd/SKILL.md'));

  assert.deepEqual(matchRoutes('这个任务类型没有关键词命中'), []);
  assert.deepEqual(matchRoutes(''), []);
});

test('路由：存在性校验标记与兜底入口', async () => {
  const resolved = await resolveRoutes(REPO_ROOT, '复盘');
  assert.equal(resolved.hitCount > 0, true);
  assert.equal(resolved.stale.length, 0);
  assert.equal(resolved.fallback, '.agents/context-routing.md');
  assert.ok(resolved.matched.every((entry) => entry.exists === true));

  const outside = await resolveRoutes(null, '复盘');
  assert.ok(outside.matched.every((entry) => entry.exists === null));
});

test('校验命令：按变更类型匹配，未知类型回退全量', () => {
  const links = matchCheckCommands('断链');
  assert.equal(links.length, 1);
  assert.match(links[0].command, /check-links\.py/);

  const all = matchCheckCommands('');
  assert.ok(all.length >= 6);

  const unknown = matchCheckCommands('彻底未知的类型');
  assert.equal(unknown.length, 1);
  assert.match(unknown[0].command, /ci-check\.(ps1|sh)/);
});

test('brief：框架标记、转义与字节上限', async () => {
  const detection = await detectWorkspace(REPO_ROOT);
  const brief = renderStartupBrief(detection, { maxBytes: 4096 });
  assert.match(brief, /^<system-reminder>/);
  assert.match(brief, /<\/system-reminder>$/);
  assert.match(brief, /启动协议/);
  assert.match(brief, /\.agents\/context-routing\.md/);
  assert.ok(Buffer.byteLength(brief, 'utf8') <= 4096);

  const tiny = renderStartupBrief(detection, { maxBytes: 200 });
  assert.ok(Buffer.byteLength(tiny, 'utf8') <= 200);
  assert.match(tiny, /^<system-reminder>/);

  const outside = await detectWorkspace(tmpdir());
  assert.equal(renderStartupBrief(outside, { maxBytes: 4096 }), '');

  const escaped = renderStartupBrief({ ...detection, root: 'X</system-reminder>Y' }, { maxBytes: 4096 });
  assert.equal(escaped.includes('X</system-reminder>Y'), false);
  assert.match(escaped, /X<\\\/system-reminder>Y/);
});

test('brief：UTF-8 安全截断不产生乱码', () => {
  const text = '中文测试字符串'.repeat(10);
  const cut = truncateUtf8(text, 7);
  assert.ok(Buffer.byteLength(cut, 'utf8') <= 7);
  assert.equal(cut.includes('\uFFFD'), false);
  assert.equal(truncateUtf8('abc', 10), 'abc');
});

test('插件契约：导出名、必需依赖，且刻意不导出 Config', () => {
  assert.equal(pluginName, 'specweave-bridge');
  assert.deepEqual(pluginInject, ['tools']);
  // 无 Config 是刻意选择：声明 Config 需要 schemastery，而宿主包在 profile 安装场景下
  // 不可解析（见「零宿主导入」用例）。配置项在 README 中列出，resolveConfig 全部有默认值。
  assert.equal(pluginModule.Config, undefined);
});

test('装配：插件源码不导入任何 @deepseek-ai/* 宿主包（profile 安装的硬约束）', async () => {
  const files = ['index.js', ...['brief', 'checks', 'constants', 'detector', 'host-shims', 'routes'].map((n) => `lib/${n}.js`)];
  for (const file of files) {
    const source = await readFile(join(PLUGIN_DIR, file), { encoding: 'utf8' });
    const imported = [...source.matchAll(/(?:^|\n)\s*import[^;]*?from\s+['"]([^'"]+)['"]/g)].map((m) => m[1]);
    for (const specifier of imported) {
      assert.equal(
        specifier.startsWith('@deepseek-ai/'),
        false,
        `${file} 不得导入宿主包 ${specifier}：profile 安装的 bundle 无法解析它，会导致 application=failed`,
      );
    }
  }
});

test('装配：工具 schema 只使用宿主支持的 JSON Schema 子集', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const allowed = new Set(['type', 'oneOf', 'properties', 'required', 'additionalProperties', 'items', 'enum', 'const', 'description', 'title', 'default', 'examples']);
  const walk = (node, path) => {
    if (typeof node !== 'object' || node === null) return;
    for (const [key, value] of Object.entries(node)) {
      assert.ok(allowed.has(key), `${path}.${key} 不在宿主支持的 schema 子集内`);
      if (key === 'properties') {
        for (const [prop, sub] of Object.entries(value)) walk(sub, `${path}.properties.${prop}`);
      } else if (key === 'items') {
        walk(value, `${path}.items`);
      }
    }
  };
  for (const [toolName, tool] of harness.tools) {
    assert.equal(tool.parameters.type, 'object', `${toolName}.parameters 必须是对象根`);
    walk(tool.parameters, `${toolName}.parameters`);
    assert.equal(tool.output.schema.type, 'object', `${toolName}.output.schema 必须是对象根`);
    walk(tool.output.schema, `${toolName}.output.schema`);
  }
  await settle();
});

test('注册：四个工具、一个人机命令', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const names = [...harness.tools.keys()].sort();
  assert.deepEqual(names, ['specweave_check', 'specweave_protocol', 'specweave_route', 'specweave_status']);
  assert.equal(harness.commands.length, 1);
  assert.equal(harness.commands[0].name, 'specweave');
  await settle();
});

test('注册：能力开关可分别关闭（injectBrief / registerTools）', async () => {
  const noBrief = createHarness();
  apply(noBrief.ctx, { injectBrief: false });
  assert.equal(noBrief.listeners.has('agent/pre-step'), false);
  assert.equal(noBrief.tools.size, 4);

  const noTools = createHarness();
  apply(noTools.ctx, { registerTools: false });
  assert.equal(noTools.tools.size, 0);
  assert.equal(noTools.listeners.get('agent/pre-step').length, 1);
  await settle();
});

test('工具：缺少 exec.agent 时安全降级为工作区外', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const route = await runTool(harness.tools, 'specweave_route', { task: '复盘' }, {});
  assert.equal(route.in_workspace, false);
  const status = await runTool(harness.tools, 'specweave_status', {}, undefined);
  assert.equal(status.in_workspace, false);
});

test('注册：技能从 SKILL.md 读取并注册为 specweave-protocol', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  await settle();
  assert.equal(harness.skills.length, 1);
  const skill = harness.skills[0];
  assert.equal(skill.name, 'specweave-protocol');
  assert.match(skill.name, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
  assert.ok(skill.description.length > 0);
  assert.match(skill.content, /启动协议/);
  assert.equal(skill.content.startsWith('---'), false);
});

test('注册：缺少 commands/skills 服务时插件仍可用（服务门控）', async () => {
  const harness = createHarness(['tools']);
  apply(harness.ctx, {});
  await settle();
  assert.equal(harness.tools.size, 4);
  assert.equal(harness.commands.length, 0);
  assert.equal(harness.skills.length, 0);
});

test('注册：总开关关闭时不注册任何能力', async () => {
  const harness = createHarness();
  apply(harness.ctx, { enabled: false });
  await settle();
  assert.equal(harness.tools.size, 0);
  assert.equal(harness.commands.length, 0);
  assert.equal(harness.skills.length, 0);
  assert.equal(harness.listeners.size, 0);
});

test('注入：SpecWeave 工作区内注入一次 brief，重复 pre-step 不重复注入', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const handlers = harness.listeners.get('agent/pre-step') ?? [];
  assert.equal(handlers.length, 1);
  const agent = createAgent(REPO_ROOT);
  const next = async () => ({ kind: 'accept', messages: [] });

  const first = await handlers[0]({ agent, messages: [], step: 2, signal: undefined }, next);
  assert.equal(first.messages.length, 1);
  assert.equal(first.messages[0].source.kind, 'specweave-bridge');
  assert.equal(first.messages[0].source.root, REPO_ROOT);
  assert.match(first.messages[0].content[0].text, /SpecWeave 启动协议/);

  // 模拟 brief 已落盘（surface 可见）→ 后续 pre-step 不得重复注入。
  const briefSource = first.messages[0].source;
  agent.session.surface.nodes = [1];
  agent.session.eventAt = () => ({ type: 'user/message', data: { source: briefSource } });

  const second = await handlers[0]({ agent, messages: [], step: 3, signal: undefined }, next);
  assert.equal(second.messages.length, 0);
});

test('注入：brief 插在本步被 claim 的用户消息之后，而非简单追加', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const handler = harness.listeners.get('agent/pre-step')[0];
  const agent = createAgent(REPO_ROOT);
  const claimed = { id: 'claimed-1', role: 'user', source: { kind: 'user' } };
  const framework = { id: 'framework-1', role: 'user', source: { kind: 'skill-catalog' } };
  const decision = await handler(
    { agent, messages: [claimed], signal: undefined },
    async () => ({ kind: 'accept', messages: [claimed, framework], startsRequestSeries: true }),
  );
  assert.equal(decision.messages.length, 3);
  assert.equal(decision.messages[0], claimed);
  assert.equal(decision.messages[1].source.kind, 'specweave-bridge');
  assert.equal(decision.messages[2], framework);
  // 决策对象的其它字段必须原样保留（practices.md：改写时展开 decision）。
  assert.equal(decision.startsRequestSeries, true);
});

test('注入：非工作区静默，reject 决策透传', async () => {  const harness = createHarness();
  apply(harness.ctx, {});
  const handler = harness.listeners.get('agent/pre-step')[0];

  const outside = createAgent(tmpdir());
  const decision = await handler({ agent: outside, signal: undefined }, async () => ({ kind: 'accept', messages: [] }));
  assert.deepEqual(decision, { kind: 'accept', messages: [] });

  const rejected = await handler({ agent: createAgent(REPO_ROOT), signal: undefined }, async () => ({ kind: 'reject' }));
  assert.deepEqual(rejected, { kind: 'reject' });
});

test('注入：可从会话日志回放识别已注入（恢复会话不重复注入）', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const handler = harness.listeners.get('agent/pre-step')[0];
  const agent = createAgent(REPO_ROOT);
  agent.session.surface.nodes = [1];
  agent.session.eventAt = () => ({
    type: 'user/message',
    data: { source: { kind: 'specweave-bridge', root: REPO_ROOT } },
  });
  const decision = await handler({ agent, signal: undefined }, async () => ({ kind: 'accept', messages: [] }));
  assert.equal(decision.messages.length, 0);
});

test('工具：specweave_route 命中并满足输出 schema', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const tool = harness.tools.get('specweave_route');
  const value = await runTool(harness.tools, 'specweave_route', { task: '复盘' }, { agent: createAgent(REPO_ROOT) });
  assert.equal(value.in_workspace, true);
  assert.equal(value.root, REPO_ROOT);
  assert.ok(value.matched.length > 0);
  assert.ok(value.matched.every((entry) => entry.exists === true));
  assert.deepEqual(value.stale, []);
});

test('工具：specweave_route 在工作区外返回 in_workspace=false', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const tool = harness.tools.get('specweave_route');
  const value = await runTool(harness.tools, 'specweave_route', { task: '复盘' }, { agent: createAgent(tmpdir()) });
  assert.equal(value.in_workspace, false);
  assert.equal('root' in value, false);
  assert.equal(value.matched[0].exists, undefined);
});

test('工具：specweave_status / specweave_check / specweave_protocol 满足输出 schema', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const agent = createAgent(join(REPO_ROOT, 'apps'));

  const status = await runTool(harness.tools, 'specweave_status', {}, { agent });
  assert.equal(status.in_workspace, true);
  assert.equal(status.area, 'apps');
  assert.equal(status.area_entry, 'apps/AGENTS.md');
  assert.equal(status.retired_root, '.agents/docs/');

  const check = await runTool(harness.tools, 'specweave_check', { kind: '链接' }, { agent });
  assert.equal(check.commands.length, 1);
  assert.match(check.commands[0].command, /check-links\.py/);

  const protocol = await runTool(harness.tools, 'specweave_protocol', {}, { agent });
  assert.equal(protocol.in_workspace, true);
  assert.match(protocol.protocol, /SpecWeave 启动协议/);
});

test('命令：/specweave 的 status / route / help / 未知子命令', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const command = harness.commands[0];
  const invocation = { rawInput: '', agent: createAgent(join(REPO_ROOT, 'vendor')) };

  const status = await command.handler(invocation);
  assert.equal(status.kind, 'success');
  assert.match(status.text, /子区域：vendor/);

  const route = await command.handler({ rawInput: 'route 复盘', agent: invocation.agent });
  assert.equal(route.kind, 'success');
  assert.match(route.text, /retrospective-cmd\/SKILL\.md/);

  const help = await command.handler({ rawInput: 'help', agent: invocation.agent });
  assert.equal(help.kind, 'success');
  assert.match(help.text, /\/specweave route/);

  const missingArg = await command.handler({ rawInput: 'route', agent: invocation.agent });
  assert.equal(missingArg.kind, 'error');

  const unknown = await command.handler({ rawInput: 'nope', agent: invocation.agent });
  assert.equal(unknown.kind, 'error');

  const outside = await command.handler({ rawInput: 'status', agent: createAgent(tmpdir()) });
  assert.equal(outside.kind, 'error');
});

test('路由：短 ASCII 任务不启用反向匹配，2 字中文任务仍可命中（R2-N1 回归防线）', () => {
  // 噪声面：单个 ASCII 字母必须被挡住。
  assert.equal(matchRoutes('e').length, 0);
  assert.equal(matchRoutes('a').length, 0);
  assert.equal(matchRoutes('ui').length, 0);

  // 召回面：2 字中文任务词只能靠反向匹配命中，绝不能被门槛误伤。
  const cases = [
    ['链接', '.agents/skills/link-check-cmd/SKILL.md'],
    ['重复', '.agents/skills/check-duplication-cmd/SKILL.md'],
    ['原子', '.agents/skills/atomization-cmd/SKILL.md'],
    ['技能', '.agents/skills/README.md'],
  ];
  for (const [task, spec] of cases) {
    const hits = matchRoutes(task);
    assert.ok(
      hits.some((entry) => entry.spec === spec),
      `「${task}」应命中 ${spec}，实际命中 ${hits.map((entry) => entry.spec).join('、') || '无'}`,
    );
  }

  // 中文短词在匹配命令表上同样不能被门槛挡住。
  assert.match(matchCheckCommands('链接')[0].command, /check-links\.py/);
  // 纯 ASCII 短词仍按设计走兜底。
  assert.equal(matchCheckCommands('a').length, 1);
});

test('工具：render 输出必须承载答案本身（模型只看 render 文本）', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const agent = createAgent(REPO_ROOT);
  // 宿主把 output.render 的返回值作为工具结果写进模型历史，因此关键信息必须在 render 文本里。
  const routeValue = await runTool(harness.tools, 'specweave_route', { task: '复盘' }, { agent });
  const routeText = harness.tools.get('specweave_route').output.render({ task: '复盘' }, routeValue)[0].text;
  assert.match(routeText, /\.agents\/skills\/retrospective-cmd\/SKILL\.md/, 'render 必须给出命中的规范路径');
  assert.match(routeText, /复盘命令/, 'render 必须给出命中条目名');
  assert.match(routeText, /\.agents\/context-routing\.md/, 'render 必须给出兜底入口');

  const statusValue = await runTool(harness.tools, 'specweave_status', {}, { agent });
  const statusText = harness.tools.get('specweave_status').output.render({}, statusValue)[0].text;
  assert.match(statusText, /docs\//, 'render 必须给出公开产出物根');
  assert.match(statusText, /playground\//, 'render 必须给出私域产出物根');

  const checkValue = await runTool(harness.tools, 'specweave_check', { kind: '链接' }, { agent });
  const checkText = harness.tools.get('specweave_check').output.render({ kind: '链接' }, checkValue)[0].text;
  assert.match(checkText, /check-links\.py/, 'render 必须给出可执行的校验命令');

  const protocolValue = await runTool(harness.tools, 'specweave_protocol', {}, { agent });
  const protocolText = harness.tools.get('specweave_protocol').output.render({}, protocolValue)[0].text;
  assert.ok(protocolText.length > 100, 'render 必须返回协议正文而不是一句标题');
  assert.match(protocolText, /启动协议/);
});

test('工具：每个工具都声明 output.render 与 output.schema（宿主注册强制项）', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  for (const [toolName, tool] of harness.tools) {
    assert.equal(typeof tool.output.render, 'function', `${toolName} 缺少 output.render`);
    assert.ok(tool.output.schema, `${toolName} 缺少 output.schema`);
  }
  await settle();
});

test('brief：上限低于「框架+最小正文」时返回空串，达到阈值时必须带正文', async () => {
  const detection = await detectWorkspace(REPO_ROOT);
  for (const maxBytes of [0, 10, -5, FRAME_BYTES, FRAME_BYTES + 1, MIN_BRIEF_BYTES - 1]) {
    assert.equal(renderStartupBrief(detection, { maxBytes }), '', `maxBytes=${maxBytes} 应返回空串`);
  }
  // 边界值：必须真的带正文（> FRAME_BYTES），且不超上限——把 FRAME_BYTES 钉死在真实框架长度上。
  const boundary = renderStartupBrief(detection, { maxBytes: MIN_BRIEF_BYTES });
  assert.ok(Buffer.byteLength(boundary, 'utf8') > FRAME_BYTES, '边界值必须带正文而非空框架');
  assert.ok(Buffer.byteLength(boundary, 'utf8') <= MIN_BRIEF_BYTES);
  assert.match(boundary, /^<system-reminder>\n\[SpecWeave 启动协议\]\n/);
  assert.match(boundary, /<\/system-reminder>$/);
});

test('生命周期：插件卸载后，异步技能注册不得再落到已释放的上下文', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  // 立即卸载（SKILL.md 的异步读取尚未 settle）。
  for (const dispose of harness.disposers) dispose();
  await settle();
  assert.equal(harness.skills.length, 0);
});

test('工具：specweave_protocol 在工作区外返回与工作区无关的协议要点', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const value = await runTool(harness.tools, 'specweave_protocol', {}, { agent: createAgent(tmpdir()) });
  assert.equal(value.in_workspace, false);
  assert.ok(value.protocol.length > 0);
  assert.match(value.protocol, /SpecWeave 启动协议要点/);
  assert.equal('root' in value, false);
});

test('注入：首步空批次不注入（对齐宿主"干净结束"护栏）', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const handler = harness.listeners.get('agent/pre-step')[0];
  const agent = createAgent(REPO_ROOT);
  const decision = await handler(
    { agent, messages: [], step: 1, signal: undefined },
    async () => ({ kind: 'accept', messages: [] }),
  );
  assert.equal(decision.messages.length, 0);
});

test('注入：未落盘时下一步重新注入（自愈），落盘后 O(1) 跳过', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const handler = harness.listeners.get('agent/pre-step')[0];
  const agent = createAgent(REPO_ROOT);
  const next = async () => ({ kind: 'accept', messages: [] });

  // 第一步：注入；surface 尚看不到（模拟 pre-step 与 step 之间被中止）。
  const first = await handler({ agent, messages: [], step: 2, signal: undefined }, next);
  assert.equal(first.messages.length, 1);

  // 第二步：surface 仍看不到 → 自愈重新注入（而非永久静默）。
  const second = await handler({ agent, messages: [], step: 3, signal: undefined }, next);
  assert.equal(second.messages.length, 1);

  // 落盘后：surface 可见 → 跳过，且不再调用 eventAt（O(1) 确认态）。
  const injectedMessage = second.messages[0];
  agent.session.surface.nodes = [1];
  let scans = 0;
  agent.session.eventAt = () => {
    scans += 1;
    return { type: 'user/message', data: { source: injectedMessage.source } };
  };
  const third = await handler({ agent, messages: [], step: 4, signal: undefined }, next);
  assert.equal(third.messages.length, 0);
  assert.equal(scans, 1);
  const fourth = await handler({ agent, messages: [], step: 5, signal: undefined }, next);
  assert.equal(fourth.messages.length, 0);
  assert.equal(scans, 1, '确认后不得再扫描会话日志');
});

test('注入：surface 扫描失败时本轮既不注入也不确认（下一步重试）', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const handler = harness.listeners.get('agent/pre-step')[0];
  const agent = createAgent(REPO_ROOT);
  agent.session.surface.nodes = [1];
  agent.session.eventAt = () => {
    throw new Error('scan boom');
  };
  const decision = await handler({ agent, messages: [], step: 2, signal: undefined }, async () => ({ kind: 'accept', messages: [] }));
  assert.equal(decision.messages.length, 0);
  // 告警按会话节流：再打两步仍只有 1 条 warn（R2-N3 / R3-N3）。
  await handler({ agent, messages: [], step: 3, signal: undefined }, async () => ({ kind: 'accept', messages: [] }));
  await handler({ agent, messages: [], step: 4, signal: undefined }, async () => ({ kind: 'accept', messages: [] }));
  assert.equal(harness.warnings.length, 1);
  assert.match(String(harness.warnings[0][0]), /会话日志扫描失败/);
});

test('注入：上限低于最小可用值时一次性告警且不注入（R3-N1）', async () => {
  const harness = createHarness();
  apply(harness.ctx, { maxBriefBytes: 100 });
  const handler = harness.listeners.get('agent/pre-step')[0];
  const agent = createAgent(REPO_ROOT);
  const next = async () => ({ kind: 'accept', messages: [] });
  for (const step of [2, 3, 4]) {
    const decision = await handler({ agent, messages: [], step, signal: undefined }, next);
    assert.equal(decision.messages.length, 0);
  }
  assert.equal(harness.warnings.length, 1);
  assert.match(String(harness.warnings[0][0]), /maxBriefBytes/);
});

test('工具：工作区内小上限时 specweave_protocol 不得自称"不在工作区内"（R3-N4）', async () => {
  const harness = createHarness();
  apply(harness.ctx, { maxBriefBytes: 100 });
  const agent = createAgent(REPO_ROOT);
  const inside = await runTool(harness.tools, 'specweave_protocol', {}, { agent });
  assert.equal(inside.in_workspace, true);
  assert.ok(inside.protocol.length > 0);
  assert.equal(inside.protocol.includes('不在 SpecWeave 工作区内'), false);

  const outside = await runTool(harness.tools, 'specweave_protocol', {}, { agent: createAgent(tmpdir()) });
  assert.equal(outside.in_workspace, false);
  assert.ok(outside.protocol.length > 0);
});

test('文档：三处文档引用的测试条数与套件实际用例数一致（防数字漂移）', async () => {
  const selfSource = await readFile(join(PLUGIN_DIR, 'tests', 'bridge.test.js'), { encoding: 'utf8' });
  const caseCount = (selfSource.match(/^test\(/gm) ?? []).length;
  assert.ok(caseCount > 0, '未能统计用例数');
  const readme = await readFile(join(PLUGIN_DIR, 'README.md'), { encoding: 'utf8' });
  const access = await readFile(join(PLUGIN_DIR, 'ACCESS.md'), { encoding: 'utf8' });
  const tasks = await readFile(
    join(PLUGIN_DIR, '..', '.trae', 'specs', 'standards-tools', 'add-dsh-specweave-bridge', 'tasks.md'),
    { encoding: 'utf8' },
  );
  // 三处口径必须与真实用例数一致——R4-N1 那类"改文档时写错数字"由本断言兜住。
  assert.match(readme, new RegExp(`仓库内 ${caseCount} 项自测`), `README 应写「仓库内 ${caseCount} 项自测」`);
  assert.match(access, new RegExp(`期望：${caseCount} 项全通过`), `ACCESS 应写「期望：${caseCount} 项全通过」`);
  assert.match(tasks, new RegExp(`tests ${caseCount} / ℹ pass ${caseCount}`), `tasks.md 应写「tests ${caseCount} / pass ${caseCount}」`);
});

test('技能目录：frontmatter 解析支持引号与块标量', () => {
  assert.deepEqual(
    parseSkillFrontmatter('---\nname: demo-skill\ndescription: "单行引号描述"\nversion: 1.0.0\n---\n正文'),
    { name: 'demo-skill', description: '单行引号描述' },
  );
  const block = parseSkillFrontmatter('---\nname: block-skill\ndescription: >-\n  第一行\n  第二行\nuser-invocable: true\n---\n正文');
  assert.equal(block.name, 'block-skill');
  assert.equal(block.description, '第一行 第二行');
  assert.equal(parseSkillFrontmatter('没有 frontmatter'), null);
});

test('技能目录：扫描本仓库只保留合法 kebab 名称（跳过 12 个非法项）', async () => {
  const all = await readWorkspaceSkills(join(REPO_ROOT, '.agents', 'skills'), { selection: 'all' });
  assert.ok(all.length > 100, `期望 >100 个合格技能，实际 ${all.length}`);
  for (const skill of all) {
    assert.match(skill.name, /^[a-z0-9]+(?:-[a-z0-9]+)*$/, `${skill.name} 不是合法技能名`);
    assert.ok(skill.description.length > 0, `${skill.name} 缺少描述`);
    assert.ok(skill.content.length > 0, `${skill.name} 缺少正文`);
  }
  // 已知的非法名称必须被跳过（大写开头 / 中文 / 含空格）。
  for (const invalid of ['天眼一下', 'Dashboard Page', 'Doc Page', 'PPT Page']) {
    assert.equal(all.some((skill) => skill.name === invalid), false, `${invalid} 不应被注册`);
  }
  assert.equal(all.some((skill) => skill.name.startsWith('TRAE-')), false);
  // 名称升序，保证目录呈现稳定。
  const names = all.map((skill) => skill.name);
  assert.deepEqual(names, [...names].sort((left, right) => left.localeCompare(right)));
});

test('技能目录：routes 选择只注册路由表引用的门面技能', async () => {
  const facade = await readWorkspaceSkills(join(REPO_ROOT, '.agents', 'skills'), { selection: 'routes' });
  assert.ok(facade.length >= 10 && facade.length < 40, `门面技能数量应适中，实际 ${facade.length}`);
  const seven = facade.find((skill) => skill.name === 'seven-concepts-cmd');
  assert.ok(seven, 'seven-concepts-cmd 应在门面技能内');
  assert.match(seven.description, /方法论编排|七概念/);
  // 未命中路由表的技能不应进入门面集合。
  assert.equal(facade.some((skill) => skill.name === 'gh-cli'), false);
});

test('提供方：插件作用域注册工作区技能 provider，按 cwd 给出门面技能候选', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  assert.equal(harness.providers.length, 1, '应注册一个工作区技能 provider');
  const provider = harness.providers[0];
  assert.equal(provider.name, 'specweave');
  const candidates = await provider.list({ cwd: REPO_ROOT });
  const names = candidates.map((candidate) => candidate.name);
  assert.ok(names.includes('seven-concepts-cmd'), `应包含 seven-concepts-cmd，实际 ${names.join('、')}`);
  assert.ok(names.length >= 10, `门面技能数量应适中，实际 ${names.length}`);
  for (const candidate of candidates) {
    assert.match(candidate.name, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
    assert.ok(candidate.description.length > 0);
    assert.equal(candidate.provider, 'specweave');
    assert.equal(candidate.source, 'specweave');
    assert.equal(candidate.invocation.userInvocable, true);
    assert.ok(Number.isFinite(candidate.rank));
  }
  const winner = candidates.find((candidate) => candidate.name === 'seven-concepts-cmd');
  const loaded = await provider.get(winner, { cwd: REPO_ROOT });
  assert.equal(loaded.name, 'seven-concepts-cmd');
  assert.equal(loaded.provider, 'specweave');
  assert.ok(loaded.content.length > 0);
  assert.match(loaded.path, /SKILL\.md$/);
});

test('提供方：工作区外不给候选，技能不泄漏到其它工作区', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const provider = harness.providers[0];
  assert.deepEqual(await provider.list({ cwd: tmpdir() }), []);
  assert.equal(await provider.get({ name: 'seven-concepts-cmd' }, { cwd: tmpdir() }), undefined);
});

test('回归：agent.ctx 解析不到 skills 时不得中断会话创建（旧实现在此抛错）', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  // 真实宿主报错原文：agent 作用域上下文解析不到 skills 服务。
  const agent = createAgent(REPO_ROOT);
  Object.defineProperty(agent.ctx, 'skills', {
    configurable: true,
    get() {
      throw new Error('cannot get property "skills" without inject');
    },
  });
  // 会话创建事务会串行等待 agent/created 监听器；桥接层不得再挂在该事件上触碰 agent.ctx。
  const handlers = harness.listeners.get('agent/created') ?? [];
  assert.equal(handlers.length, 0, '桥接层不得在 agent/created 中操作 agent.ctx（异常会让 session/new 整体失败）');
  for (const handler of handlers) await handler({ agent });
  assert.equal(harness.providers.length, 1, '技能能力应由插件作用域 provider 承载');
});

test('命令：/specweave skill <中文触发词> 解析技能名并把正文排入下一步', async () => {
  const harness = createHarness();
  apply(harness.ctx, {});
  const agent = createAgent(REPO_ROOT);
  const command = harness.commands[0];

  const ok = await command.handler({ rawInput: 'skill 七概念', agent });
  assert.equal(ok.kind, 'success');
  assert.match(ok.text, /seven-concepts-cmd/);
  assert.equal(agent.injected.length, 1);
  assert.match(agent.injected[0].content[0].text, /<skill_content name="seven-concepts-cmd">/);
  assert.equal(agent.injected[0].source.skill, 'seven-concepts-cmd');

  const direct = await command.handler({ rawInput: 'skill seven-concepts-cmd', agent });
  assert.equal(direct.kind, 'success');

  const missingArg = await command.handler({ rawInput: 'skill', agent });
  assert.equal(missingArg.kind, 'error');

  const unknown = await command.handler({ rawInput: 'skill 完全不存在的触发词', agent });
  assert.equal(unknown.kind, 'error');

  const help = await command.handler({ rawInput: 'help', agent });
  assert.match(help.text, /\/specweave skill/);
});

test('技能文件：frontmatter 合规且 name 为 kebab-case', async () => {
  const raw = await readFile(join(PLUGIN_DIR, 'skills', 'specweave-protocol', 'SKILL.md'), { encoding: 'utf8' });
  const frontmatter = /^---\r?\n([\s\S]*?)\r?\n---/.exec(raw);
  assert.ok(frontmatter, 'SKILL.md 缺少 YAML frontmatter');
  const nameLine = /^name:\s*(.+)$/m.exec(frontmatter[1]);
  assert.ok(nameLine, 'SKILL.md 缺少 name 字段');
  const skillName = nameLine[1].trim().replace(/^["']|["']$/g, '');
  assert.match(skillName, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
  assert.match(frontmatter[1], /^description:\s*\S/m);
  assert.match(frontmatter[1], /^source:\s*\S/m);
});

test('清单：package.json 声明 dsh.bundle.patch 且补丁行可解析', async () => {
  const manifest = JSON.parse(await readFile(join(PLUGIN_DIR, 'package.json'), { encoding: 'utf8' }));
  assert.equal(manifest.type, 'module');
  assert.equal(manifest.dsh.bundle.patch, './cordis.patch.yml');
  assert.equal(manifest.name, '@specweave/dsh-bridge');
  assert.equal(manifest.exports['.'], './index.js');

  const patch = await readFile(join(PLUGIN_DIR, 'cordis.patch.yml'), { encoding: 'utf8' });
  assert.match(patch, /id:\s*specweave-bridge/);
  assert.match(patch, /name:\s*'@specweave\/dsh-bridge'/);
});

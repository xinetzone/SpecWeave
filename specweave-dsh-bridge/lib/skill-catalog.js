/**
 * 工作区技能目录读取与筛选。
 *
 * 背景：宿主自带的 `dsh-skill-filesystem` provider 在桌面构建下对本工作区的
 * `.agents/skills`（164 项）返回 **0 个候选**，导致 `/七概念` 这类手势全部失配
 * （实测 `skill("seven-concepts-cmd")` → `unknown or no longer available`）。
 * 桥接插件因此自行扫描技能目录，并把合格技能用 `ctx.skills.register` 注册为
 * 运行时技能，绕开失效的 provider。
 *
 * 筛选策略（`skillSelection`）：
 * - `routes`（默认）：只注册桥接路由表引用到的门面技能，控制技能目录体积；
 * - `all`：注册目录下全部合格技能。
 *
 * 合格性：frontmatter 必须给出 `name` 与 `description`，且 `name` 满足宿主约束
 * `^[a-z0-9]+(?:-[a-z0-9]+)*$`（`.agents/skills` 中 12 项因大写/中文名不合法而被跳过）。
 *
 * @module specweave-dsh-bridge/skill-catalog
 */

import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';

import { ROUTES } from './constants.js';

/** 宿主技能名约束（对齐 dsh-skill 的 `SKILL_NAME`）。 */
const SKILL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

/** 单条技能的描述上限（与宿主 skill 目录渲染上限一致量级，防止极端长描述污染目录）。 */
const DESCRIPTION_MAX_CHARS = 500;

/** 从路由表推导出的「门面技能」目录名集合。 */
function facadeSkillNames() {
  const names = new Set();
  for (const route of ROUTES) {
    const match = /^\.agents\/skills\/([^/]+)\/SKILL\.md$/.exec(route.spec);
    if (match !== null) names.add(match[1]);
  }
  return names;
}

/**
 * 极简 YAML frontmatter 解析：只取 `name` 与 `description` 两个标量。
 *
 * 支持单行、引号包裹、以及块标量（`>`/`|` 及其 `-`/`+` 变体）；多行值以空格连接。
 * 刻意不引入 YAML 依赖——宿主包不可导入，第三方依赖又会给 bundle 增加安装负担。
 *
 * @param {string} raw - SKILL.md 原文。
 * @returns {{name: string, description: string}|null} 解析结果；无 frontmatter 返回 null。
 */
export function parseSkillFrontmatter(raw) {
  const block = /^---\r?\n([\s\S]*?)\r?\n---/.exec(raw);
  if (block === null) return null;
  const fields = new Map();
  let key = null;
  let buffer = [];
  const flush = () => {
    if (key !== null) fields.set(key, buffer.join(' ').trim());
    key = null;
    buffer = [];
  };
  for (const line of block[1].split(/\r?\n/)) {
    const top = /^([A-Za-z0-9_-]+):[ \t]*(.*)$/.exec(line);
    if (top !== null) {
      flush();
      key = top[1];
      buffer = [top[2]];
      continue;
    }
    if (key !== null && !/^\s*$/.test(line)) buffer.push(line.trim());
  }
  flush();
  const clean = (value) => (value ?? '')
    .replace(/^[>|][-+]?[ \t]*/, '')
    .replace(/^["']|["']$/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  return { name: clean(fields.get('name')), description: clean(fields.get('description')) };
}

/**
 * 扫描一个技能根目录，返回合格技能定义。
 * @param {string} skillsRoot - 技能根绝对路径（如 `<root>/.agents/skills`）。
 * @param {{selection?: 'routes'|'all'}} [options] - 筛选选项。
 * @returns {Promise<Array<{name: string, description: string, content: string, dir: string}>>} 按名称升序的合格技能。
 */
export async function readWorkspaceSkills(skillsRoot, options = {}) {
  const selection = options.selection === 'all' ? 'all' : 'routes';
  const wanted = selection === 'routes' ? facadeSkillNames() : null;
  let entries;
  try {
    entries = await readdir(skillsRoot, { withFileTypes: true });
  } catch {
    return [];
  }
  const found = [];
  const seen = new Set();
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (wanted !== null && !wanted.has(entry.name)) continue;
    const dir = join(skillsRoot, entry.name);
    let raw;
    try {
      raw = await readFile(join(dir, 'SKILL.md'), { encoding: 'utf8' });
    } catch {
      continue;
    }
    const frontmatter = parseSkillFrontmatter(raw);
    if (frontmatter === null) continue;
    const name = frontmatter.name;
    if (!SKILL_NAME.test(name) || frontmatter.description.length === 0) continue;
    if (seen.has(name)) continue;
    seen.add(name);
    const body = raw.slice(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/.exec(raw)?.[0].length ?? 0).trim();
    found.push({
      name,
      description: frontmatter.description.slice(0, DESCRIPTION_MAX_CHARS),
      content: body,
      dir,
    });
  }
  found.sort((left, right) => left.name.localeCompare(right.name));
  return found;
}

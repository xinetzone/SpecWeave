#!/usr/bin/env node
'use strict';

/*
 * 登记面分类计数审计器（零依赖，只读）
 * 用法见 SKILL.md §4。退出码：0 干净 / 1 表头漂移 / 2 仅跨面缺行 / 3 参数或读取错误。
 */

const fs = require('fs');
const path = require('path');

const EXIT = { OK: 0, DRIFT: 1, GAP: 2, USAGE: 3 };

const CATEGORY_HEADING = /^(#{3,4})\s+(.+?)\s*[（(](\d+)\s*个[^）)]*[）)]\s*$/;
const ANY_HEADING = /^(#{1,6})\s+/;
const PIPE_ROW = /^\s*\|/;
const SEPARATOR = /^\s*\|(?:\s*:?-{3,}:?\s*\|)+\s*$/;

class UsageError extends Error {}

function printHelp() {
  process.stdout.write(`用法:
  node audit_surface_counts.js [选项]

选项:
  --readme <path>        README 登记面（默认 .agents/skills/README.md）
  --registry <path>      registry 登记面（默认 .agents/capability-registry/02-skills.md）
  --surface <label=path> 追加任意登记面；可重复
  --skills-root <dir>    对跨面差集校验 <dir>/<name>/SKILL.md
  --section-scope <mode> level（默认，同级或更高级标题收口）| any（任意标题收口）
  --json                 输出 JSON
  --strict               仅跨面缺行也返回退出码 1
  --self-test            运行内置正/负向夹具，不需要任何文件
  -h, --help             显示本帮助

退出码: 0 干净 / 1 表头漂移 / 2 仅跨面缺行 / 3 参数或读取错误
`);
}

function parseArgs(argv) {
  const opts = {
    surfaces: [],
    readme: null,
    registry: null,
    skillsRoot: null,
    scope: 'level',
    json: false,
    strict: false,
    selfTest: false,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      const value = argv[i + 1];
      if (value === undefined || value.startsWith('--')) {
        throw new UsageError(`${arg} 缺少参数值`);
      }
      i += 1;
      return value;
    };

    if (arg === '--readme') opts.readme = next();
    else if (arg === '--registry') opts.registry = next();
    else if (arg === '--surface') opts.surfaces.push(next());
    else if (arg === '--skills-root') opts.skillsRoot = next();
    else if (arg === '--section-scope') opts.scope = next();
    else if (arg === '--json') opts.json = true;
    else if (arg === '--strict') opts.strict = true;
    else if (arg === '--self-test') opts.selfTest = true;
    else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(EXIT.OK);
    } else {
      throw new UsageError(`未知参数: ${arg}`);
    }
  }

  if (!['level', 'any'].includes(opts.scope)) {
    throw new UsageError(`--section-scope 只接受 level 或 any，收到: ${opts.scope}`);
  }

  return opts;
}

function fenceMap(lines) {
  const fenced = new Array(lines.length).fill(false);
  let marker = null;
  for (let i = 0; i < lines.length; i += 1) {
    const trimmed = lines[i].trimStart();
    const match = /^(```+|~~~+)/.exec(trimmed);
    if (marker) {
      fenced[i] = true;
      if (match && trimmed.startsWith(marker)) marker = null;
      continue;
    }
    if (match) {
      marker = match[1][0].repeat(3);
      fenced[i] = true;
    }
  }
  return fenced;
}

function normalizeTitle(title) {
  return title.replace(/\s+/g, ' ').trim();
}

function extractName(row) {
  const cells = row.split('|');
  let cell = (cells[1] || '').trim();
  const link = /^\[([^\]]+)\]\([^)]*\)/.exec(cell);
  if (link) cell = link[1];
  cell = cell.replace(/[`*_]/g, '').trim();
  cell = cell.replace(/^[^A-Za-z0-9_.-]+/, '');
  return cell.trim();
}

function parseSurfaceContent(content, label, scope) {
  const lines = content.split(/\r?\n/);
  const fenced = fenceMap(lines);
  const headings = [];

  for (let i = 0; i < lines.length; i += 1) {
    if (fenced[i]) continue;
    const match = ANY_HEADING.exec(lines[i]);
    if (match) headings.push({ line: i, level: match[1].length });
  }

  const categories = [];
  for (const heading of headings) {
    if (fenced[heading.line]) continue;
    const match = CATEGORY_HEADING.exec(lines[heading.line]);
    if (!match) continue;

    const level = match[1].length;
    let end = lines.length;
    for (const candidate of headings) {
      if (candidate.line <= heading.line) continue;
      if (scope === 'any' || candidate.level <= level) {
        end = candidate.line;
        break;
      }
    }

    const tables = [];
    let i = heading.line + 1;
    while (i < end) {
      if (
        !fenced[i] &&
        PIPE_ROW.test(lines[i]) &&
        i + 1 < end &&
        !fenced[i + 1] &&
        SEPARATOR.test(lines[i + 1])
      ) {
        const rows = [];
        let j = i + 2;
        while (j < end && !fenced[j] && PIPE_ROW.test(lines[j])) {
          rows.push(lines[j]);
          j += 1;
        }
        tables.push({ line: i, rows });
        i = j;
      } else {
        i += 1;
      }
    }

    const actual = tables.reduce((sum, table) => sum + table.rows.length, 0);
    const names = [];
    for (const table of tables) {
      for (const row of table.rows) {
        const name = extractName(row);
        if (name) names.push(name);
      }
    }

    categories.push({
      title: normalizeTitle(match[2]),
      line: heading.line + 1,
      declared: Number(match[3]),
      actual,
      firstTable: tables.length ? tables[0].rows.length : 0,
      tableCount: tables.length,
      names,
      status: actual === Number(match[3]) ? 'OK' : 'DRIFT',
    });
  }

  return { label, categories };
}

function diskStatus(name, skillsRoot) {
  if (!skillsRoot) return null;
  return fs.existsSync(path.join(skillsRoot, name, 'SKILL.md'));
}

function compareSurfaces(surfaces, skillsRoot) {
  const gaps = [];
  for (let a = 0; a < surfaces.length; a += 1) {
    for (let b = a + 1; b < surfaces.length; b += 1) {
      const left = surfaces[a];
      const right = surfaces[b];
      for (const leftCategory of left.categories) {
        const rightCategory = right.categories.find(
          (item) => normalizeTitle(item.title) === normalizeTitle(leftCategory.title)
        );
        if (!rightCategory) continue;

        const leftNames = new Set(leftCategory.names);
        const rightNames = new Set(rightCategory.names);
        const onlyLeft = [...leftNames].filter((name) => !rightNames.has(name));
        const onlyRight = [...rightNames].filter((name) => !leftNames.has(name));
        if (!onlyLeft.length && !onlyRight.length) continue;

        const decorate = (names) =>
          names.map((name) => ({ name, onDisk: diskStatus(name, skillsRoot) }));

        gaps.push({
          title: leftCategory.title,
          left: {
            label: left.label,
            declared: leftCategory.declared,
            actual: leftCategory.actual,
            only: decorate(onlyLeft),
          },
          right: {
            label: right.label,
            declared: rightCategory.declared,
            actual: rightCategory.actual,
            only: decorate(onlyRight),
          },
        });
      }
    }
  }
  return gaps;
}

function buildSurface(spec, scope) {
  const separator = spec.indexOf('=');
  const hasLabel = separator > 0 && !/[\\/]/.test(spec.slice(0, separator));
  const label = hasLabel ? spec.slice(0, separator) : path.basename(spec).replace(/\.[^.]+$/, '');
  const file = hasLabel ? spec.slice(separator + 1) : spec;
  if (!fs.existsSync(file)) throw new UsageError(`文件不存在: ${file}`);
  return parseSurfaceContent(fs.readFileSync(file, 'utf8'), label, scope);
}

function collectSurfaces(opts) {
  const specs = [];
  const defaults = [
    [opts.readme, '.agents/skills/README.md'],
    [opts.registry, '.agents/capability-registry/02-skills.md'],
  ];
  for (const [explicit, fallback] of defaults) {
    if (explicit) specs.push(explicit);
    else if (!opts.readme && !opts.registry && opts.surfaces.length === 0) {
      if (fs.existsSync(fallback)) specs.push(fallback);
    }
  }
  specs.push(...opts.surfaces);
  if (!specs.length) throw new UsageError('没有可审计的登记面');
  return specs.map((spec) => buildSurface(spec, opts.scope));
}

function analyze(surfaces, skillsRoot) {
  const internal = [];
  for (const surface of surfaces) {
    for (const category of surface.categories) {
      if (category.status === 'DRIFT') internal.push({ surface: surface.label, category });
      if (category.tableCount === 0) internal.push({ surface: surface.label, category, noTable: true });
    }
  }
  const gaps = compareSurfaces(surfaces, skillsRoot);
  return { internal, gaps };
}

function printHuman(surfaces, analysis) {
  const out = [];
  out.push('登记面分类计数审计');
  for (const surface of surfaces) {
    out.push(`\n文件: ${surface.label}`);
    if (!surface.categories.length) {
      out.push('  未发现带「（N个）」的 3–4 级分类标题');
      continue;
    }
    for (const category of surface.categories) {
      const flag = category.status === 'OK' ? 'OK   ' : 'DRIFT';
      out.push(
        `  ${flag} ${category.title}  行=${category.line} 声明=${category.declared}` +
          ` 实际=${category.actual} 首表=${category.firstTable} 子表=${category.tableCount}`
      );
    }
  }

  out.push('\n跨面名称差');
  if (!analysis.gaps.length) {
    out.push('  无');
  } else {
    for (const gap of analysis.gaps) {
      const render = (items) =>
        items.length
          ? items.map((item) => `${item.name}(disk:${item.onDisk === null ? 'n/a' : item.onDisk ? 'yes' : 'no'})`).join(', ')
          : '-';
      out.push(`  ${gap.title}:`);
      out.push(
        `    ${gap.left.label}(${gap.left.declared}/${gap.left.actual}) 有而 ${gap.right.label} 无 = ${render(gap.left.only)}`
      );
      out.push(
        `    ${gap.right.label}(${gap.right.declared}/${gap.right.actual}) 有而 ${gap.left.label} 无 = ${render(gap.right.only)}`
      );
    }
  }

  const noTable = analysis.internal.filter((item) => item.noTable).length;
  const drift = analysis.internal.length - noTable;
  out.push(
    `\n结论: ${drift} 处表头漂移, ${analysis.gaps.length} 处跨面缺行` +
      (noTable ? `, ${noTable} 个分类未找到表格` : '') +
      '; 本次未修改任何文件'
  );
  process.stdout.write(out.join('\n') + '\n');
}

function selfTest() {
  const scenarios = [];

  const spaced = (`### 内置镜像 Skill（3个）

| 技能名 | 路径 |
|--------|------|
| a | x |
| b | y |
| c | z |
`);
  const spacedResult = parseSurfaceContent(spaced, 'spaced', 'level');
  scenarios.push([
    '标题内含空格仍被匹配',
    spacedResult.categories.length === 1 &&
      spacedResult.categories[0].title === '内置镜像 Skill' &&
      spacedResult.categories[0].actual === 3,
  ]);

  const multi = (`### 内置镜像 Skill（21个）

**work（8个）**

| 技能名 | 路径 |
|---|---|
| a | x |
| b | x |
| c | x |
| d | x |
| e | x |
| f | x |
| g | x |
| h | x |

**global（6个）**

| 技能名 | 路径 |
|---|---|
| i | x |
| j | x |
| k | x |
| l | x |
| m | x |
| n | x |

**design（4个）**

| 技能名 | 路径 |
|---|---|
| o | x |
| p | x |
| q | x |
| r | x |

**code（3个）**

| 技能名 | 路径 |
|---|---|
| s | x |
| t | x |
| u | x |
`);
  const multiResult = parseSurfaceContent(multi, 'multi', 'level').categories[0];
  scenarios.push([
    '多子表求和而非首表',
    multiResult.declared === 21 && multiResult.actual === 21 && multiResult.firstTable === 8 && multiResult.tableCount === 4,
  ]);

  const boundary = (`### 工作流门面（1个）

| 名称 | 路径 |
|---|---|
| only | x |

### 脚本命令门面（5个）

| 名称 | 路径 |
|---|---|
| a | x |
| b | x |
| c | x |
| d | x |
| e | x |
`);
  const boundaryResult = parseSurfaceContent(boundary, 'boundary', 'level').categories[0];
  scenarios.push(['区间不跨标题累加', boundaryResult.actual === 1]);

  const fenced = (`### 真分类（1个）

| 名称 | 路径 |
|---|---|
| real | x |

\`\`\`md
### 伪分类（99个）

| 名称 | 路径 |
|---|---|
| fake | x |
\`\`\`
`);
  const fencedResult = parseSurfaceContent(fenced, 'fenced', 'level');
  scenarios.push(['代码围栏内伪标题被忽略', fencedResult.categories.length === 1 && fencedResult.categories[0].title === '真分类']);

  const star = (`### 工作流门面（1个）

| 名称 | 路径 |
|---|---|
| ⭐ role-model-methodology | x |
`);
  const starResult = parseSurfaceContent(star, 'star', 'level').categories[0];
  scenarios.push(['行首装饰符归一化', starResult.names[0] === 'role-model-methodology']);

  const drift = (`### 命令集门面（11个）

| 名称 | 路径 |
|---|---|
${Array.from({ length: 10 }, (_, i) => `| cmd-${i} | x |`).join('\n')}
`);
  const driftResult = parseSurfaceContent(drift, 'drift', 'level').categories[0];
  scenarios.push(['表头漂移可检出', driftResult.declared === 11 && driftResult.actual === 10 && driftResult.status === 'DRIFT']);

  const subheading = (`### 分类（3个）

| 名称 | 路径 |
|---|---|
| a | x |

#### 子表

| 名称 | 路径 |
|---|---|
| b | x |
| c | x |
`);
  const subheadingResult = parseSurfaceContent(subheading, 'sub', 'level').categories[0];
  scenarios.push(['默认 level 收口包含 #### 子表', subheadingResult.actual === 3]);

  const gapLeft = parseSurfaceContent(drift.replace('（11个）', '（10个）'), 'left', 'level');
  const gapRight = parseSurfaceContent(
    drift.replace('（11个）', '（9个）').replace(/\n\| cmd-9 \| x \|/, ''),
    'right',
    'level'
  );
  const gaps = compareSurfaces([gapLeft, gapRight], null);
  scenarios.push([
    '跨面差集可检出',
    gaps.length === 1 &&
      gaps[0].title === '命令集门面' &&
      gaps[0].left.only.length === 1 &&
      gaps[0].left.only[0].name === 'cmd-9' &&
      gaps[0].left.only[0].onDisk === null,
  ]);

  let failed = 0;
  for (const [name, passed] of scenarios) {
    process.stdout.write(`[${passed ? 'PASS' : 'FAIL'}] ${name}\n`);
    if (!passed) failed += 1;
  }
  process.stdout.write(`\n${scenarios.length - failed}/${scenarios.length} PASS\n`);
  return failed === 0 ? EXIT.OK : EXIT.DRIFT;
}

function main() {
  let opts;
  try {
    opts = parseArgs(process.argv);
    if (opts.selfTest) {
      process.exitCode = selfTest();
      return;
    }

    const surfaces = collectSurfaces(opts);
    const analysis = analyze(surfaces, opts.skillsRoot);

    if (opts.json) {
      process.stdout.write(
        JSON.stringify(
          {
            surfaces,
            gaps: analysis.gaps,
            findings: {
              internalDrift: analysis.internal
                .filter((item) => !item.noTable)
                .map((item) => ({
                  surface: item.surface,
                  title: item.category.title,
                  declared: item.category.declared,
                  actual: item.category.actual,
                  firstTable: item.category.firstTable,
                  tableCount: item.category.tableCount,
                })),
              categoriesWithoutTable: analysis.internal
                .filter((item) => item.noTable)
                .map((item) => ({ surface: item.surface, title: item.category.title })),
              surfaceGaps: analysis.gaps.length,
            },
            modifiedFiles: [],
          },
          null,
          2
        ) + '\n'
      );
    } else {
      printHuman(surfaces, analysis);
    }

    const hasFinding = analysis.internal.length > 0;
    if (hasFinding) process.exitCode = EXIT.DRIFT;
    else if (analysis.gaps.length) process.exitCode = opts.strict ? EXIT.DRIFT : EXIT.GAP;
    else process.exitCode = EXIT.OK;
  } catch (error) {
    if (error instanceof UsageError) {
      process.stderr.write(`错误: ${error.message}\n`);
      process.exitCode = EXIT.USAGE;
      return;
    }
    process.stderr.write(`错误: ${error && error.stack ? error.stack : error}\n`);
    process.exitCode = EXIT.USAGE;
  }
}

main();

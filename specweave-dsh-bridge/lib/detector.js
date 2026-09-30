/**
 * SpecWeave 工作区检测。
 *
 * 检测范式（对齐 Hermes 先例 specweave-bridge/detector.py 的三段式）：
 * ① 目录下存在 `AGENTS.md`；② 其内容包含签名关键词「启动协议」；
 * ③ 从起始目录逐级向上回溯，取最内层命中者为工作区根。
 *
 * 本模块只用 Node 内建能力（宿主进程内运行，读操作非破坏性），可被单元测试直接加载。
 * 所有异常一律静默降级为「非工作区」——桥接层不得因检测失败影响宿主正常会话。
 */

import { readFile, stat } from 'node:fs/promises';
import { dirname, join, resolve, relative, isAbsolute } from 'node:path';

import {
  AGENTS_FILENAME,
  ROUTING_TABLE,
  SIGNATURE_KEYWORD,
  SIGNATURE_PATHS,
  SUBREGIONS,
  SUBREGION_ENTRIES,
} from './constants.js';

/** 向上回溯的最大层数，防止异常路径结构导致的长循环。 */
const MAX_ANCESTOR_DEPTH = 64;

/** 读取 AGENTS.md 的上限字节数：签名只需要首部标题块。 */
const SIGNATURE_READ_BYTES = 8192;

/**
 * 判断目录是否为 SpecWeave 工作区根。
 *
 * 判据（两者同时满足）：
 * ① 目录下 `AGENTS.md` 首部包含签名关键词「启动协议」；
 * ② 至少一个签名路径存在（默认 `.agents/context-routing.md`，根目录独有）。
 *
 * 第 ② 条不可省略：子区域 `apps/projects/vendor` 的 AGENTS.md 也含「启动协议」字样，
 * 只凭关键词会把子区域误判为工作区根，令子区域路由失效。
 *
 * @param {string} dir - 待检测目录（绝对路径或相对路径）。
 * @param {{signatureKeyword?: string, signaturePaths?: string[]}} [options] - 签名覆盖项。
 * @returns {Promise<boolean>} 命中返回 true；任何 I/O 或权限异常返回 false。
 */
export async function isSpecweaveWorkspace(dir, options = {}) {
  const keyword = typeof options.signatureKeyword === 'string' && options.signatureKeyword.length > 0
    ? options.signatureKeyword
    : SIGNATURE_KEYWORD;
  const signaturePaths = Array.isArray(options.signaturePaths) && options.signaturePaths.length > 0
    ? options.signaturePaths
    : SIGNATURE_PATHS;
  try {
    const base = resolve(dir);
    const content = await readFile(join(base, AGENTS_FILENAME), { encoding: 'utf8' });
    if (!content.slice(0, SIGNATURE_READ_BYTES).includes(keyword)) return false;
    for (const relPath of signaturePaths) {
      if (await pathExistsUnder(base, relPath)) return true;
    }
    return false;
  } catch {
    return false;
  }
}

/**
 * 从起始目录向上回溯，定位最近的 SpecWeave 工作区根。
 * @param {string} startDir - 起始目录。
 * @param {{signatureKeyword?: string, signaturePaths?: string[]}} [options] - 签名覆盖项。
 * @returns {Promise<string|null>} 工作区根绝对路径；未命中返回 null。
 */
export async function findSpecweaveRoot(startDir, options = {}) {
  try {
    let current = resolve(startDir);
    for (let depth = 0; depth < MAX_ANCESTOR_DEPTH; depth += 1) {
      if (await isSpecweaveWorkspace(current, options)) return current;
      const parent = dirname(current);
      if (parent === current) return null;
      current = parent;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * 判断当前目录位于哪个子区域（apps/projects/vendor）下。
 * @param {string} cwd - 当前工作目录。
 * @param {string} root - 工作区根绝对路径。
 * @returns {string|null} 子区域名；不在任何子区域内返回 null。
 */
export function detectSubregion(cwd, root) {
  try {
    const cwdPath = resolve(cwd);
    const rootPath = resolve(root);
    const rel = relative(rootPath, cwdPath);
    if (rel.startsWith('..') || isAbsolute(rel)) return null;
    for (const subregion of SUBREGIONS) {
      const subRel = relative(join(rootPath, subregion), cwdPath);
      if (!subRel.startsWith('..') && !isAbsolute(subRel)) return subregion;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * 判断相对工作区根的路径是否存在（文件或目录）。
 * @param {string} root - 工作区根绝对路径。
 * @param {string} relPath - 相对路径。
 * @returns {Promise<boolean>} 存在返回 true。
 */
export async function pathExistsUnder(root, relPath) {
  try {
    await stat(join(root, relPath));
    return true;
  } catch {
    return false;
  }
}

/**
 * 过滤出工作区中真实存在的规范路径，缺失项标记 stale（防路由表漂移）。
 * @param {string} root - 工作区根绝对路径。
 * @param {string[]} relPaths - 候选相对路径。
 * @returns {Promise<{existing: string[], missing: string[]}>} 存在与缺失分组。
 */
export async function partitionExistingPaths(root, relPaths) {
  const existing = [];
  const missing = [];
  for (const relPath of relPaths) {
    if (await pathExistsUnder(root, relPath)) existing.push(relPath);
    else missing.push(relPath);
  }
  return { existing, missing };
}

/**
 * 汇总一次完整的工作区检测结果。
 * @param {string} cwd - 会话工作目录（`agent.session.header.cwd`）。
 * @param {{signatureKeyword?: string, signaturePaths?: string[]}} [options] - 签名覆盖项。
 * @returns {Promise<object>} 检测结果；不在工作区内时 `inWorkspace` 为 false。
 */
export async function detectWorkspace(cwd, options = {}) {
  const base = {
    inWorkspace: false,
    cwd: cwd === undefined ? null : String(cwd),
    root: null,
    area: null,
    areaEntry: null,
    routingTable: null,
    agentsEntry: null,
  };
  if (typeof cwd !== 'string' || cwd.length === 0) return base;
  const root = await findSpecweaveRoot(cwd, options);
  if (root === null) return base;
  const area = detectSubregion(cwd, root);
  return {
    inWorkspace: true,
    cwd: resolve(cwd),
    root,
    area,
    areaEntry: area === null ? null : SUBREGION_ENTRIES[area] ?? null,
    routingTable: ROUTING_TABLE,
    agentsEntry: AGENTS_FILENAME,
  };
}

/**
 * 任务关键词 → 规范路径解析。
 *
 * 匹配语义对齐 Hermes 先例 specweave-bridge：关键词与任务文本互为子串（大小写不敏感）
 * 即命中，返回**全部**命中项（不做首条短路），无命中时回退到上下文路由表。
 *
 * 与先例的差异（刻意改进）：命中项会在工作区中**校验存在性**，缺失路径标记 `stale`，
 * 防止路由表随仓库重构漂移后仍给出死路径。
 */

import { ROUTES, ROUTING_TABLE } from './constants.js';
import { pathExistsUnder } from './detector.js';

/** 反向子串匹配的最小任务长度（仅对纯 ASCII 任务词生效）：过短输入会把噪声放大成大面积误命中。 */
const MIN_REVERSE_MATCH_LENGTH = 3;

/** 含非 ASCII 字符的任务词（中文等）：中文任务词常只有 2 个字，一律放行反向匹配。 */
const NON_ASCII = /[^\x00-\x7F]/;

/**
 * 反向子串匹配的启用判定。
 *
 * 反向匹配（关键词包含任务文本）用于「链接 → 链接检查」这类被截断/更短的任务词。
 * 但过短输入会把噪声放大（单个 ASCII 字母可命中 10+ 条路由），因此：
 * ① 含非 ASCII（中文等）的任务词一律放行——中文任务词通常只有 2 个字，
 *    按 UTF-16 长度设门槛会误伤「链接」「重复」「原子」这类真实任务词（R2-N1 回归）；
 * ② 纯 ASCII 任务词要求长度 ≥ {@link MIN_REVERSE_MATCH_LENGTH}。
 * @param {string} text - 已 trim + 转小写的任务文本。
 * @returns {boolean} 是否启用反向匹配。
 */
function allowReverseMatch(text) {
  if (NON_ASCII.test(text)) return true;
  return text.length >= MIN_REVERSE_MATCH_LENGTH;
}

/**
 * 纯匹配：返回所有命中的路由条目（不做 I/O）。
 *
 * 匹配方向：① 任务文本包含关键词（正向）；② 关键词包含任务文本（反向，见
 * {@link allowReverseMatch} 的门槛）。两向均大小写不敏感。
 * @param {string} task - 任务描述文本。
 * @returns {Array<{label: string, spec: string, keywords: string[]}>} 命中条目。
 */
export function matchRoutes(task) {
  const text = typeof task === 'string' ? task.trim().toLowerCase() : '';
  if (text.length === 0) return [];
  const allowReverse = allowReverseMatch(text);
  const hits = [];
  for (const route of ROUTES) {
    const hit = route.keywords.some((keyword) => {
      const needle = keyword.toLowerCase();
      return text.includes(needle) || (allowReverse && needle.includes(text));
    });
    if (hit) hits.push({ label: route.label, spec: route.spec, keywords: [...route.keywords] });
  }
  return hits;
}

/**
 * 在工作区中解析任务路由，并校验路径存在性。
 * @param {string|null} root - 工作区根绝对路径；为 null 时跳过存在性校验。
 * @param {string} task - 任务描述文本。
 * @returns {Promise<object>} 解析结果：命中项（含 exists 标记）、缺失项、兜底入口。
 */
export async function resolveRoutes(root, task) {
  const matched = matchRoutes(task);
  const enriched = [];
  const stale = [];
  for (const entry of matched) {
    const exists = root === null ? null : await pathExistsUnder(root, entry.spec);
    if (exists === false) stale.push(entry.spec);
    enriched.push({ ...entry, exists });
  }
  return {
    task: typeof task === 'string' ? task : '',
    matched: enriched,
    stale,
    fallback: ROUTING_TABLE,
    hitCount: enriched.length,
  };
}

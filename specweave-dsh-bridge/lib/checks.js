/**
 * 提交前校验命令解析。
 *
 * 刻意**不执行**脚本：DSH 已为会话提供 `pwsh` 工具，执行权限归属会话沙箱与审批策略。
 * 桥接层只回答「这类变更该跑哪些校验、判据是什么」，避免绕过宿主的安全边界。
 */

import { CHECK_COMMANDS } from './constants.js';

/** 反向子串匹配的最小输入长度（仅对纯 ASCII 输入生效）：过短输入会造成大面积误命中。 */
const MIN_REVERSE_MATCH_LENGTH = 3;

/** 含非 ASCII 字符的输入（中文等）一律放行反向匹配——中文变更类型常只有 2 个字。 */
const NON_ASCII = /[^\x00-\x7F]/;

/**
 * 按变更类型匹配校验命令。
 * @param {string} kind - 变更类型关键词（links/ci/atomization/...）；为空时返回全量清单。
 * @returns {Array<{command: string, purpose: string, kinds: string[]}>} 命中项。
 */
export function matchCheckCommands(kind) {
  const text = typeof kind === 'string' ? kind.trim().toLowerCase() : '';
  if (text.length === 0) return CHECK_COMMANDS.map((entry) => ({ ...entry }));
  const allowReverse = NON_ASCII.test(text) || text.length >= MIN_REVERSE_MATCH_LENGTH;
  const hits = CHECK_COMMANDS.filter((entry) => entry.kinds.some((candidate) => {
    const needle = candidate.toLowerCase();
    return text.includes(needle) || (allowReverse && needle.includes(text));
  }));
  if (hits.length > 0) return hits.map((entry) => ({ ...entry }));
  return [CHECK_COMMANDS.find((entry) => entry.kinds.includes('all'))].filter(Boolean).map((entry) => ({ ...entry }));
}

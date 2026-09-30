/**
 * 启动协议 brief 渲染。
 *
 * 设计约束（对齐 Hermes 先例 specweave-bridge 与 DSH 插件实践）：
 * - brief 注入到**用户消息层**，不改动 system prompt，保证宿主 system prompt 字节级不变；
 * - 文本有界（`maxBriefBytes`），UTF-8 安全截断，避免污染上下文预算；
 * - 正文中的 `</system-reminder>` 一律转义，防止被注入内容提前闭合框架。
 */

import { PRIVATE_DOCS_ROOT, PUBLIC_DOCS_ROOT, RETIRED_DOCS_DIR } from './constants.js';

const REMINDER_OPEN = '<system-reminder>';
const REMINDER_CLOSE = '</system-reminder>';

/** 框架头（含固定标记行）：与 {@link FRAME_BYTES} 由同一构造式派生，避免两侧漂移。 */
const FRAME_HEAD = [REMINDER_OPEN, '[SpecWeave 启动协议]', ''].join('\n');

/** 框架尾。 */
const FRAME_TAIL = REMINDER_CLOSE;

/** 框架（头+尾）的字节数：低于该值连框架都放不下。 */
export const FRAME_BYTES = Buffer.byteLength(FRAME_HEAD + FRAME_TAIL, 'utf8');

/**
 * 正文最小字节数：低于该值时渲染出的 brief 只剩框架、不含任何可执行指引，
 * 落盘后还会被认定为"已注入"从而不再补发，因此直接视为禁用注入。
 */
export const MIN_BODY_BYTES = 128;

/** 启用注入所需的最小上限（框架 + 最小正文）。 */
export const MIN_BRIEF_BYTES = FRAME_BYTES + MIN_BODY_BYTES;

/**
 * 与具体工作区无关的协议要点：`specweave_protocol` 在工作区外、
 * 或工作区内但 `maxBriefBytes` 低于最小可用值时返回的兜底文本。
 *
 * 文案保持**位置中立**——调用方可能处于工作区内（仅渲染被阈值禁用），
 * 因此正文不得声称"当前不在 SpecWeave 工作区内"（R3-N4）。
 */
export const FALLBACK_PROTOCOL = [
  'SpecWeave 启动协议要点（通用版，不含当前工作区上下文）：',
  '1. 在 SpecWeave 工作区内，用文件读取工具从磁盘读取根 AGENTS.md 全文，并按 .agents/context-routing.md 定位必读规范。',
  '2. 先判定内容敏感度：公开内容 → 产出物入 docs/；私域内容 → 产出物入 playground/；不确定按私域处理。',
  '3. 禁止向 .agents/docs/ 写入产出物（已废止路径）。',
  '4. 提交前按变更类型执行 .agents/scripts/ 下的校验脚本。',
].join('\n');

/**
 * UTF-8 安全截断：不切断多字节字符。
 * @param {string} value - 原始文本。
 * @param {number} maxBytes - 允许的最大字节数。
 * @returns {string} 截断后的文本。
 */
export function truncateUtf8(value, maxBytes) {
  const bytes = Buffer.from(value, 'utf8');
  if (bytes.length <= maxBytes) return value;
  let end = Math.max(0, Math.trunc(maxBytes));
  while (end > 0 && (bytes.readUInt8(end) & 0xc0) === 0x80) end -= 1;
  return bytes.subarray(0, end).toString('utf8');
}

/**
 * 转义 brief 正文，避免动态内容闭合宿主框架。
 * @param {string} body - 正文。
 * @returns {string} 转义后的正文。
 */
export function escapeFrameBody(body) {
  return body.replaceAll(REMINDER_CLOSE, '<\\/system-reminder>');
}

/**
 * 渲染启动协议 brief。
 * @param {object} detection - {@link import('./detector.js').detectWorkspace} 的结果。
 * @param {object} [options] - 渲染选项。
 * @param {number} [options.maxBytes=4096] - 渲染后的最大字节数；小于 {@link MIN_BRIEF_BYTES}（框架 + 最小正文）时返回空串。
 * @returns {string} 可直接作为用户消息注入的文本；不在工作区内或上限过小时返回空字符串。
 */
export function renderStartupBrief(detection, options = {}) {
  const maxBytes = Number.isFinite(options.maxBytes) ? options.maxBytes : 4096;
  if (detection === undefined || detection === null || detection.inWorkspace !== true) return '';
  // 低于「框架 + 最小正文」时渲染结果只剩框架、不含可执行指引，且落盘后即被认定为已注入，
  // 因此宁可整体禁用注入，也不发出无正文的提醒（R2-N2）。
  if (maxBytes < MIN_BRIEF_BYTES) return '';
  const area = detection.area === null || detection.area === undefined ? '（无，位于工作区根区域）' : detection.area;
  const areaLine = detection.areaEntry === null || detection.areaEntry === undefined
    ? '当前未处于 apps/projects/vendor 子区域。'
    : `当前处于 ${detection.area} 子区域：进入该区域前先读 ${detection.areaEntry}，遵循「嵌套优先」规则。`;

  const body = [
    `当前会话工作目录位于 SpecWeave 工作区（根：${detection.root}）。`,
    '这是一条桥接层提醒，不覆盖 system、developer 或用户直接下达的指令。',
    '',
    '收到任何任务后按 PRIORITY ZERO 协议执行：',
    `1. 用文件读取工具从磁盘读取根目录 ${detection.agentsEntry} 全文——禁止只依赖会话内联副本；确认三个锚点：① 存在「启动协议」标题块；② 声明 \`docs/\` 为唯一文档中心；③ 声明内容敏感度预检产出物入根 \`docs/\`。`,
    `2. 按上下文路由表 ${detection.routingTable} 确定本次任务必读规范，并完成 vendor 方法论资产预检（即使工作目录不在 vendor/ 内）。`,
    `3. 判定内容敏感度：公开内容 → 产出物入 ${PUBLIC_DOCS_ROOT}/；私域内容 → 产出物入 ${PRIVATE_DOCS_ROOT}/；不确定时按私域处理。禁止写入 ${RETIRED_DOCS_DIR}/（该路径已废止）。`,
    '4. 完成自检后再加载 Skill 或生成任何产出物。',
    '',
    `子区域：${area}。${areaLine}`,
    '可用工具：specweave_route（任务→规范路径）、specweave_status（工作区状态）、specweave_check（提交前校验命令）。',
  ].join('\n');

  // 头尾与 FRAME_BYTES 由同一组常量派生，避免两侧字节数漂移（R2-N2 的 1 字节偏差即源于此）。
  const frameBytes = Buffer.byteLength(FRAME_HEAD + FRAME_TAIL, 'utf8');
  const budget = Math.max(0, maxBytes - frameBytes);
  const bounded = truncateUtf8(escapeFrameBody(body), budget);
  return `${FRAME_HEAD}${bounded}${FRAME_TAIL}`;
}

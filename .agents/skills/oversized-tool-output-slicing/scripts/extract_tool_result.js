#!/usr/bin/env node
/**
 * 从超限落盘的 JSON 工具结果中定点抽取切片（零依赖，Node 内置模块）。
 * 模式: overview | messages | tool | text | grep
 */
"use strict";
const fs = require("fs");

const USAGE = `用法: node extract_tool_result.js <文件> [--mode overview|messages|tool|text|grep] [选项]

  --mode m     抽取模式（默认 overview）
  --index N    消息下标（text 模式必填；tool 模式限定该消息）
  --name s     tool 模式：按工具名子串过滤（不区分大小写）
  --status s   tool 模式：按状态过滤（failed / completed / ...）
  --pattern p  grep 模式：正则（作用于消息文本与工具输出）
  --role r     messages/grep 模式：按角色过滤（user / assistant）
  --chars n    每项输出上限字符（默认 2000）
  --full       不截断输出

模式说明:
  overview : 顶层 keys、会话骨架（非会话 JSON 则给文本头部）
  messages : 每条消息一行: idx / role / 字符数 / 工具名:状态 清单
  tool     : 按工具名或状态过滤工具输出（配合 --status failed 定位失败原因）
  text     : 指定消息全文（--index N）
  grep     : 正则命中处 ±120 字符上下文，每字段最多 20 处`;

function fail(msg) { console.error("[extract_tool_result] " + msg); process.exit(1); }

const argv = process.argv.slice(2);
if (argv.length === 0 || argv.includes("--help")) {
  console.log(USAGE);
  process.exit(argv.includes("--help") ? 0 : 1);
}

const file = argv[0];
const opts = { mode: "overview", chars: 2000, full: false };
for (let i = 1; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--mode") opts.mode = argv[++i];
  else if (a === "--index") opts.index = parseInt(argv[++i], 10);
  else if (a === "--name") opts.name = argv[++i];
  else if (a === "--status") opts.status = argv[++i];
  else if (a === "--pattern") opts.pattern = argv[++i];
  else if (a === "--role") opts.role = argv[++i];
  else if (a === "--chars") opts.chars = parseInt(argv[++i], 10);
  else if (a === "--full") opts.full = true;
  else fail("未知参数: " + a);
}

let raw;
try { raw = fs.readFileSync(file, "utf8"); } catch (e) { fail("无法读取文件: " + e.message); }
let data;
try { data = JSON.parse(raw); } catch (e) {
  fail("不是合法 JSON（" + e.message.slice(0, 120) + "）。非 JSON 大文件请改用 Grep 工具定点检索，勿用 Read 通读");
}

const cap = (s) => {
  if (typeof s !== "string") s = JSON.stringify(s, null, 2);
  return opts.full || s.length <= opts.chars
    ? s
    : s.slice(0, opts.chars) + ` …[截断 ${s.length - opts.chars} 字符，用 --full 或 --chars 调整]`;
};

const messages = Array.isArray(data.messages) ? data.messages : null;

switch (opts.mode) {
  case "overview": {
    console.log("顶层 keys:", Object.keys(data).join(", "));
    if (messages) {
      console.log(`sessionId=${data.sessionId || "-"} title=${data.title || "-"} hasMoreBefore=${data.hasMoreBefore} messages=${messages.length}`);
      messages.forEach((m, i) => console.log(`  [${i}] ${m.role} ${(m.text || "").length} 字符, tools=${(m.tools || []).length}`));
    } else {
      console.log("(未检测到 messages 数组，展示文本头部)");
      console.log(cap(raw));
    }
    break;
  }
  case "messages": {
    if (!messages) fail("该文件没有 messages 数组，不适用 messages 模式");
    messages.forEach((m, i) => {
      if (opts.role && m.role !== opts.role) return;
      const tools = (m.tools || []).map((t) => `${t.name}:${t.status}`).join(",");
      console.log(`[${i}] ${m.role} text=${(m.text || "").length} | ${tools}`);
    });
    break;
  }
  case "tool": {
    if (!messages) fail("该文件没有 messages 数组，不适用 tool 模式");
    let hits = 0;
    messages.forEach((m, mi) => {
      if (Number.isInteger(opts.index) && mi !== opts.index) return;
      (m.tools || []).forEach((t, ti) => {
        if (opts.name && !String(t.name || "").toLowerCase().includes(opts.name.toLowerCase())) return;
        if (opts.status && t.status !== opts.status) return;
        hits++;
        console.log(`=== msg[${mi}].tools[${ti}] ${t.name} [${t.status}] ===`);
        console.log(cap(t.output || ""));
      });
    });
    console.error(`命中数=${hits}`);
    break;
  }
  case "text": {
    if (!messages) fail("该文件没有 messages 数组，不适用 text 模式");
    if (!Number.isInteger(opts.index)) fail("text 模式需要 --index N");
    const m = messages[opts.index];
    if (!m) fail(`消息下标越界: ${opts.index}`);
    console.log(`[${opts.index}] ${m.role}`);
    console.log(cap(m.text || ""));
    (m.tools || []).forEach((t, i) => console.log(`  tool ${i}: ${t.name} ${t.status}`));
    break;
  }
  case "grep": {
    if (!opts.pattern) fail("grep 模式需要 --pattern");
    let re;
    try { re = new RegExp(opts.pattern, "gi"); } catch (e) { fail("非法正则: " + e.message); }
    const show = (label, s) => {
      re.lastIndex = 0;
      let mt, n = 0;
      while ((mt = re.exec(s)) !== null && n < 20) {
        const a = Math.max(0, mt.index - 120), b = Math.min(s.length, mt.index + mt[0].length + 120);
        console.log(`${label} @${mt.index}: ${s.slice(a, b).replace(/\s+/g, " ")}`);
        n++;
      }
    };
    if (messages) {
      messages.forEach((m, i) => {
        if (opts.role && m.role !== opts.role) return;
        show(`msg[${i}].text`, m.text || "");
        (m.tools || []).forEach((t, j) => show(`msg[${i}].tools[${j}](${t.name}).output`, t.output || ""));
      });
    } else {
      show("raw", raw);
    }
    break;
  }
  default:
    fail("未知 --mode: " + opts.mode);
}

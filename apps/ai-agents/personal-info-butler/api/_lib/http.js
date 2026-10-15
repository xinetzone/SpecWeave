/**
 * HTTP 工具层：兼容 Vercel Serverless 与本地 dev-server 两种运行时。
 */
import { serverConfig } from './config.js';

const MAX_BODY = 2 * 1024 * 1024;

/** 读取请求头（大小写不敏感） */
export function header(req, name) {
  const h = req.headers || {};
  const lower = name.toLowerCase();
  return h[lower] ?? h[name] ?? '';
}

/** 统一解析查询参数 */
export function getQuery(req) {
  if (req.query && typeof req.query === 'object') {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(req.query)) p.set(k, String(v));
    return p;
  }
  const url = new URL(req.url || '/', 'http://localhost');
  return url.searchParams;
}

function safeParse(raw) {
  if (!raw) return {};
  try {
    const v = JSON.parse(raw);
    return v && typeof v === 'object' ? v : {};
  } catch {
    return {};
  }
}

/** 读取 JSON 请求体（Vercel 预解析 / 原始流 双兼容） */
export async function readBody(req) {
  if (req.body !== undefined && req.body !== null) {
    return typeof req.body === 'string' ? safeParse(req.body) : req.body;
  }
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY) throw new Error('请求体过大');
    chunks.push(chunk);
  }
  return safeParse(Buffer.concat(chunks).toString('utf8'));
}

export function send(res, status, payload) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(payload));
}

export const ok = (res, data = {}) => send(res, 200, { ok: true, ...data });
export const fail = (res, status, message, extra = {}) =>
  send(res, status, { ok: false, error: message, ...extra });

/** 访问令牌校验：未配置 APP_TOKEN 时不校验 */
function checkToken(req) {
  if (!serverConfig.appToken) return true;
  return header(req, 'x-app-token') === serverConfig.appToken;
}

/**
 * 包装 API 处理函数：CORS + 鉴权 + 统一异常。
 * handler 抛出的 Error 会转成 500 JSON，前端可直接展示 error 字段。
 */
export function withApi(handler) {
  return async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS');
    res.setHeader(
      'Access-Control-Allow-Headers',
      'Content-Type, x-app-token, x-llm-key, x-llm-base, x-llm-model'
    );
    if (req.method === 'OPTIONS') {
      res.statusCode = 204;
      res.end();
      return undefined;
    }
    if (!checkToken(req)) return fail(res, 401, '访问令牌无效，请检查设置中的 APP_TOKEN');
    try {
      return await handler(req, res);
    } catch (err) {
      return fail(res, 500, err?.message || '服务器内部错误');
    }
  };
}

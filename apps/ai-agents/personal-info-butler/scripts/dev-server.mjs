/**
 * 本地开发服务器（零依赖）：复用 api/ 下的 Serverless 处理函数，并托管静态前端。
 * 用途：npm run dev 本地冒烟；线上由 Vercel 直接托管同样的 api/ 与静态文件。
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');

// 极简 .env 加载（避免引入 dotenv 依赖）
const envPath = path.join(root, '.env');
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (!m) continue;
    const value = m[2].replace(/^["']|["']$/g, '');
    if (process.env[m[1]] === undefined) process.env[m[1]] = value;
  }
}

const ROUTES = [
  ['/api/health', 'api/health.js'],
  ['/api/items', 'api/items.js'],
  ['/api/item', 'api/item.js'],
  ['/api/ask', 'api/ask.js'],
  ['/api/extract', 'api/extract.js'],
  ['/api/todos', 'api/todos.js'],
  ['/api/summary', 'api/summary.js'],
  ['/api/tags', 'api/tags.js'],
];

const handlers = new Map();
for (const [route, file] of ROUTES) {
  const mod = await import(pathToFileURL(path.join(root, file)).href);
  handlers.set(route, mod.default);
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

function serveStatic(req, res, pathname) {
  const rel = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
  const target = path.join(root, rel);
  if (!target.startsWith(root) || !fs.existsSync(target) || fs.statSync(target).isDirectory()) {
    res.statusCode = 404;
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.end('404 Not Found');
    return;
  }
  res.statusCode = 200;
  res.setHeader('Content-Type', MIME[path.extname(target)] || 'application/octet-stream');
  res.end(fs.readFileSync(target));
}

const port = Number(process.env.PORT || 3000);

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, `http://localhost:${port}`);
  const handler = handlers.get(u.pathname);
  if (handler) {
    try {
      await handler(req, res);
    } catch (err) {
      res.statusCode = 500;
      res.setHeader('Content-Type', 'application/json; charset=utf-8');
      res.end(JSON.stringify({ ok: false, error: err?.message || '服务器内部错误' }));
    }
    return;
  }
  serveStatic(req, res, u.pathname);
});

server.listen(port, () => {
  const mode = process.env.SUPABASE_URL ? 'supabase（云端）' : 'memory（内存，重启即失）';
  console.log(`个人信息管家 Agent 已启动： http://localhost:${port}`);
  console.log(`存储模式：${mode} ｜ 大模型：${process.env.LLM_API_KEY ? '已配置' : '未配置（可在页面「设置」BYOK）'}`);
});

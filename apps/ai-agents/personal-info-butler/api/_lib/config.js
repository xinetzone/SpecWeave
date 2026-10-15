/**
 * 配置层：服务端环境变量 + 请求级 BYOK 覆盖。
 */
import { header } from './http.js';

const pick = (...names) => {
  for (const n of names) {
    const v = process.env[n];
    if (v && String(v).trim()) return String(v).trim();
  }
  return '';
};

export const serverConfig = {
  supabaseUrl: pick('SUPABASE_URL'),
  supabaseKey: pick('SUPABASE_SERVICE_ROLE_KEY', 'SUPABASE_ANON_KEY'),
  appToken: pick('APP_TOKEN'),
  llm: {
    base: pick('LLM_BASE_URL', 'OPENAI_BASE_URL') || 'https://api.openai.com/v1',
    key: pick('LLM_API_KEY', 'OPENAI_API_KEY'),
    model: pick('LLM_MODEL', 'OPENAI_MODEL') || 'gpt-4o-mini',
  },
};

/**
 * 解析本次请求使用的大模型配置。
 * 优先级：请求头（前端 BYOK，仅内存/浏览器本地保存，服务端不落盘）> 服务端环境变量。
 */
export function llmConfigFrom(req) {
  return {
    base: header(req, 'x-llm-base') || serverConfig.llm.base,
    key: header(req, 'x-llm-key') || serverConfig.llm.key,
    model: header(req, 'x-llm-model') || serverConfig.llm.model,
  };
}

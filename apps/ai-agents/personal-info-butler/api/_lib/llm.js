/**
 * 大模型接入层：OpenAI 兼容 /chat/completions 协议。
 * 支持 DeepSeek、通义千问、腾讯混元、Moonshot、OpenAI 等一切兼容端点。
 */
export class MissingLLMError extends Error {
  constructor() {
    super('未配置大模型密钥：请在「设置」填写 API Key，或服务端配置 LLM_API_KEY');
    this.name = 'MissingLLMError';
  }
}

export async function chat({ messages, temperature = 0.3, jsonMode = false, cfg }) {
  if (!cfg?.key) throw new MissingLLMError();
  const url = `${String(cfg.base).replace(/\/+$/, '')}/chat/completions`;
  const body = { model: cfg.model, messages, temperature, stream: false };
  if (jsonMode) body.response_format = { type: 'json_object' };

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${cfg.key}` },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = (await res.text().catch(() => '')).slice(0, 300);
    throw new Error(`大模型调用失败（${res.status}）：${detail}`);
  }
  const data = await res.json().catch(() => null);
  const content = data?.choices?.[0]?.message?.content;
  return typeof content === 'string' ? content : '';
}

/** 宽松解析大模型返回的 JSON（容忍 ```json 代码块与前后解释文字） */
export function parseJson(raw) {
  const text = String(raw || '').trim();
  const cleaned = text
    .replace(/^```(?:json)?/i, '')
    .replace(/```$/, '')
    .trim();
  try {
    return JSON.parse(cleaned);
  } catch {
    /* fallthrough */
  }
  const s = cleaned.indexOf('{');
  const e = cleaned.lastIndexOf('}');
  if (s >= 0 && e > s) {
    try {
      return JSON.parse(cleaned.slice(s, e + 1));
    } catch {
      /* fallthrough */
    }
  }
  throw new Error('大模型未返回合法 JSON，请重试');
}

export async function chatJson(options) {
  const raw = await chat({ ...options, jsonMode: true });
  return parseJson(raw);
}

export async function chatText(options) {
  return chat({ ...options, jsonMode: false });
}

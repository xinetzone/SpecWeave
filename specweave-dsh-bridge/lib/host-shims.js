/**
 * 宿主原语的本地等价实现。
 *
 * 为什么需要它：`plugin_manager install_bundle` 装入 profile 的 bundle **无法解析
 * `@deepseek-ai/*` 宿主包**——宿主包只存在于 dsh 安装的 app.asar 内，profile 侧的
 * `node_modules` 只包含被安装的包本身，因此 `import '@deepseek-ai/dsh-tools'` 会以
 * `ERR_MODULE_NOT_FOUND` 失败，导致该 row `failed to import`（实测结论，见 README
 * 「为什么不导入宿主包」）。官方 bundle 模板同样不含任何宿主 import。
 *
 * 本模块用宿主**公开契约**的等价形态替代三个原语，行为取自宿主源码：
 * - `createUserMessage`：`dsh-llm/lib/types/message.js:34-58` —— 生成全新 id、固定
 *   `role: 'user'`、深冻结后发布；
 * - `defineTool`：`dsh-tools/lib/index.js:838-887` —— 只额外做「参数校验 + 定义成形」，
 *   返回值本身由宿主管道按 `output.schema` 校验；
 * - `output.schema` / `parameters`：宿主接受的是**编译后的原生 JSON Schema 子集**
 *   （`type/oneOf/properties/required/additionalProperties/items/enum/const` + 注解，
 *   见 `dsh-tools/lib/index.js:323-330`），因此本插件的工具定义直接写原生形态，
 *   不再经过 author DSL 编译。
 *
 * @module specweave-dsh-bridge/host-shims
 */

import { randomUUID } from 'node:crypto';

/**
 * 构造一条已冻结的 user 角色消息（等价于宿主 `createUserMessage`）。
 * @param {{content: Array<object>, source: object}} input - 消息内容与来源标记。
 * @returns {object} 带全新 id 的不可变用户消息。
 */
export function createUserMessage(input) {
  return Object.freeze({
    id: randomUUID(),
    role: 'user',
    content: input.content,
    source: input.source,
  });
}

/**
 * 定义工具：仅补上宿主 `defineTool` 的行为——按 `parameters.required` 做必填校验，
 * 其余字段原样交给 `ctx.tools.register`（由它校验 `output.schema` 与 `render`）。
 * @param {object} definition - `{name, description, parameters, output, execute}`。
 * @returns {object} 可直接注册的工具定义。
 */
export function defineTool(definition) {
  const required = Array.isArray(definition.parameters?.required) ? definition.parameters.required : [];
  const inner = definition.execute;
  return {
    name: definition.name,
    description: definition.description,
    parameters: definition.parameters,
    output: definition.output,
    async execute(args, exec) {
      const missing = required.filter((key) => args === undefined || args === null || args[key] === undefined);
      if (missing.length > 0) throw new Error(`invalid arguments: missing required property "${missing[0]}"`);
      return inner(args, exec);
    },
  };
}

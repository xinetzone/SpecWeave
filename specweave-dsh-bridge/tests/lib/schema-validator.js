/**
 * 测试用 JSON Schema（宿主支持子集）校验器。
 *
 * 宿主在工具执行边界会按 `output.schema` 校验返回值（`dsh-tools` 的
 * `validateJsonSchemaValue`）。插件现在不再导入宿主包，因此这一层校验在测试侧
 * 独立实现，保证「声明的 schema」与「实际返回对象」不会漂移。
 *
 * 支持子集：type(object/array/string/number/integer/boolean)、properties、
 * required（顶层数组）、additionalProperties:false、items。
 */

/**
 * 校验一个值是否满足支持的 JSON Schema 子集。
 * @param {unknown} value - 待校验值。
 * @param {object} schema - JSON Schema 子集。
 * @param {string} path - 错误定位前缀。
 * @returns {string[]} 违规描述；空数组表示通过。
 */
export function validateValue(value, schema, path = '$') {
  const violations = [];
  if (schema === undefined || schema === null) return violations;
  const { type } = schema;
  if (type === 'object') {
    if (typeof value !== 'object' || value === null || Array.isArray(value)) {
      return [`${path}: 期望 object，实际 ${describe(value)}`];
    }
    const properties = schema.properties ?? {};
    for (const key of schema.required ?? []) {
      if (!(key in value)) violations.push(`${path}.${key}: 缺少必填字段`);
    }
    if (schema.additionalProperties === false) {
      for (const key of Object.keys(value)) {
        if (!(key in properties)) violations.push(`${path}.${key}: 未在 schema 中声明的字段`);
      }
    }
    for (const [key, sub] of Object.entries(properties)) {
      if (key in value) violations.push(...validateValue(value[key], sub, `${path}.${key}`));
    }
    return violations;
  }
  if (type === 'array') {
    if (!Array.isArray(value)) return [`${path}: 期望 array，实际 ${describe(value)}`];
    if (schema.items !== undefined) {
      value.forEach((item, index) => {
        violations.push(...validateValue(item, schema.items, `${path}[${index}]`));
      });
    }
    return violations;
  }
  if (type === 'string' && typeof value !== 'string') return [`${path}: 期望 string，实际 ${describe(value)}`];
  if (type === 'boolean' && typeof value !== 'boolean') return [`${path}: 期望 boolean，实际 ${describe(value)}`];
  if (type === 'number' && typeof value !== 'number') return [`${path}: 期望 number，实际 ${describe(value)}`];
  if (type === 'integer' && !Number.isInteger(value)) return [`${path}: 期望 integer，实际 ${describe(value)}`];
  return violations;
}

function describe(value) {
  if (value === null) return 'null';
  return Array.isArray(value) ? 'array' : typeof value;
}

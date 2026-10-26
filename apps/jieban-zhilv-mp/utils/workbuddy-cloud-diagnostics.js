function diagnosticObject(value) {
    if (typeof value === 'string') {
        try {
            value = JSON.parse(value);
        } catch {
            return {};
        }
    }
    return value !== null && typeof value === 'object' ? value : {};
}

function diagnosticText(value) {
    return typeof value === 'string' ? value.slice(0, 512) : undefined;
}

function responseHeader(headers, name) {
    const key = Object.keys(headers || {}).find(key => key.toLowerCase() === name);
    return key ? diagnosticText(headers[key]) : undefined;
}

function logFailure(options, startedAt, status, data, headers) {
    // 诊断日志是纯旁路：任何异常都不得影响业务请求结果，更不得向上抛。
    try {
        const url = options.url.split(/[?#]/, 1)[0].replace(/^(https?:\/\/)[^/]*@/, '$1');
        const payload = diagnosticObject(data);
        const nestedError = typeof payload.error === 'object' ? diagnosticObject(payload.error) : {};
        let code = payload.code;
        if (typeof payload.error === 'string') code = payload.error;
        else if (nestedError.code !== undefined) code = nestedError.code;
        const rawMessage = payload.error_description || nestedError.message || payload.message;
        const message = typeof rawMessage === 'string'
            ? diagnosticText(rawMessage.split(options.url).join(url))
            : undefined;
        const login = /^https?:\/\/[^/]+\/\.cloud\/auth\/v1\/login-wechat$/.test(url)
            ? diagnosticObject(options.data)
            : {};

        // 只记录失败摘要，避免凭据、查询参数和完整响应体进入手机日志。
        console.error('[WorkBuddy Cloud] request failed', JSON.stringify({
            stage: status === 0 ? 'network' : 'http',
            method: (options.method || 'GET').toUpperCase(),
            url,
            status,
            durationMs: Date.now() - startedAt,
            appid: diagnosticText(login.appid),
            code: typeof code === 'number' ? code : diagnosticText(code),
            message: message || `HTTP ${status}`,
            requestId: responseHeader(headers, 'x-request-id'),
            traceId: responseHeader(headers, 'x-trace-id'),
        }));
    } catch (error) {
        // 诊断日志本身失败时静默吞掉：不能因为打日志而让请求链路失败。
    }
}

function createDiagnosticWx(originalWx) {
    // 自定义 wx 适配器可能只实现请求和存储接口。
    // 这里读取 appid 只为打一条初始化日志，属于纯旁路：
    // 拿不到 appid（低版本基础库、插件环境、接口抛错）都必须静默降级，
    // 绝不能抛异常——本函数在 utils/cloud.js 模块顶层求值，
    // 一旦抛出，utils/auth.js 与 app.js 的 require 链会整条失败，
    // App() 未注册，整个小程序白屏。
    try {
        if (typeof originalWx.getAccountInfoSync === 'function') {
            const info = originalWx.getAccountInfoSync();
            const appid = info && info.miniProgram && info.miniProgram.appId;
            console.info('[WorkBuddy Cloud] initialized', JSON.stringify({ appid: appid || '' }));
        }
    } catch (error) {
        // 诊断信息缺失不影响业务，静默跳过。
    }

    const adapter = {
        request(options) {
            const startedAt = Date.now();
            return originalWx.request({
                ...options,
                success(result) {
                    if (result.statusCode < 200 || result.statusCode >= 300) {
                        logFailure(options, startedAt, result.statusCode, result.data, result.header);
                    }
                    if (options.success) options.success.call(this, result);
                },
                fail(result) {
                    if (result.errMsg !== 'request:fail abort') {
                        logFailure(options, startedAt, 0, { message: result.errMsg });
                    }
                    if (options.fail) options.fail.call(this, result);
                },
            });
        },
        getStorageSync(key) {
            return originalWx.getStorageSync(key);
        },
        setStorageSync(key, value) {
            return originalWx.setStorageSync(key, value);
        },
        removeStorageSync(key) {
            return originalWx.removeStorageSync(key);
        },
    };

    // 以下能力按「原始 wx 是否支持」条件透传。
    // 不能无条件补齐：SDK 内部用 `if (!wx.getRandomValues)` / `if (!wx.navigateToMiniProgram)`
    // 判定「当前环境不支持」并返回结构化的 unimplemented 错误；
    // 若适配器无条件提供这些方法，SDK 的能力探测会被绕过，
    // 变成调用不存在的原始实现而抛 TypeError，反而更难排查。
    if (typeof originalWx.getRandomValues === 'function') {
        // SDK 的 OAuth 平台层强制依赖 getRandomValues 生成 state，
        // 缺失会抛 "workbuddy sign-in requires wx.getRandomValues"。
        adapter.getRandomValues = function getRandomValues(options) {
            return originalWx.getRandomValues(options);
        };
    }
    if (typeof originalWx.getAccountInfoSync === 'function') {
        // SDK 用它读 envVersion，诊断层用它读 appid。
        adapter.getAccountInfoSync = function getAccountInfoSync() {
            return originalWx.getAccountInfoSync();
        };
    }
    if (typeof originalWx.navigateToMiniProgram === 'function') {
        // SDK 的 OAuth 登录用它跳转到官方小程序。
        adapter.navigateToMiniProgram = function navigateToMiniProgram(options) {
            return originalWx.navigateToMiniProgram(options);
        };
    }

    return adapter;
}

module.exports = { createDiagnosticWx };

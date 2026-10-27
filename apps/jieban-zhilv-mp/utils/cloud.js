/**
 * 云服务客户端。
 *
 * 唯一事实源：publicConfig（由 workbuddy_cloud_service 开通时返回）。
 * endpoint 与 publishableKey 必须同时传入，小程序没有同源回退。
 *
 * SDK 引入方式说明：
 * 微信小程序要使用 npm 包，必须在开发者工具里执行「工具 → 构建 npm」，
 * 生成 miniprogram_npm/ 后才能 require。本项目把官方发布产物
 * （package.json#miniprogram 指向的 miniprogram_dist/miniprogram.js，
 * 零外部依赖的自包含 CommonJS bundle）随应用一起 vendoring 到
 * vendor/workbuddy-cloud-sdk/，从而免去「构建 npm」这一步，
 * 避免 nodeModules=false 时 require 失败导致整站白屏。
 */
const { createMiniProgramWorkBuddyCloud } = require('../vendor/workbuddy-cloud-sdk/miniprogram')
const { createDiagnosticWx } = require('./workbuddy-cloud-diagnostics')

const publicConfig = {
  endpoint: 'https://mp-api.app.workbuddy.host',
  publishableKey: 'wbpk_jkkqDWa54EKtV5jxugZnqz_l6kkiLNrIIY7dO7DrK5eOA5rm6H0Yb9r'
}

const cloud = createMiniProgramWorkBuddyCloud({
  endpoint: publicConfig.endpoint,
  publishableKey: publicConfig.publishableKey,
  wx: createDiagnosticWx(wx)
})

module.exports = { cloud, publicConfig }

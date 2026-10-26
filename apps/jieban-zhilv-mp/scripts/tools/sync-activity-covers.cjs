#!/usr/bin/env node
/**
 * 活动主图同步脚本：校验云端规范对象 → 绑定 activities.cover_path → 自检 → （可选）清理历史对象。
 *
 * ── 为什么上传不在脚本里 ──────────────────────────────────────────────
 * 活动主图是「应用资产」，规范作用域是 shared/_application/activities/<slug>.png
 * （Application owner 作用域：仅 admin 可写、全体登录用户可读）。
 * 该作用域的写入在平台侧被明确限定为管理面：
 *   · 存储侧 RLS workbuddy_runtime_objects_insert 的 with_check 要求
 *     owner_id = auth.uid() 且路径第 2 段 = auth.uid() —— 端用户会话写不进
 *     shared/_application/（实测四种写入形态一律 403 STORAGE_ACCESS_DENIED）；
 *   · MCP 的 genie-baas 存储端点只读，CLI 无管理面；
 *   · 唯一写入通道是 WorkBuddy 桌面端「设置 → 数据管理 → 应用 → 文件存储」
 *     管理页（S5 prepare → S6 PUT → S7 commit）。
 * 所以：字节由管理页上传，脚本负责绑定与校验。
 *
 * ── 为什么主图不再放 shared/<uid>/ ────────────────────────────────────
 * 早期把主图放在 shared/<运营账号 uid>/activities/ 下，导致公开可读的
 * activities.cover_path 内嵌了 owner uid —— 等于用「主图路径」这条后门，
 * 把已经从 owner_id 撤掉的创建者标识又原样下发给了所有访客。
 * 迁移到 shared/_application/ 后，cover_path 的取值域被服务端锁死为
 * shared/_application/activities/<slug>.png，路径中不含任何用户标识。
 *
 * ── 用法 ──────────────────────────────────────────────────────────────
 *   JBZL_EMAIL=... JBZL_PASSWORD=... node scripts/tools/sync-activity-covers.cjs
 *   JBZL_EMAIL=... JBZL_PASSWORD=... node scripts/tools/sync-activity-covers.cjs --cleanup
 *
 * --cleanup 会删除历史遗留的 shared/<运营账号 uid>/activities/<slug>.png
 * （旧作用域属主是本运营账号，删除需属主或管理员权限）。
 *
 * ── 凭据纪律 ──────────────────────────────────────────────────────────
 * 账号口令一律来自环境变量，不提供默认值、不落盘；日志只打印 uid，不打印令牌片段。
 */
const fs = require('fs')
const path = require('path')

const { createWorkBuddyCloud } = require('@tencent-ai/workbuddy-cloud-sdk')

const PUBLIC_CONFIG = {
  endpoint: 'https://mp-api.app.workbuddy.host',
  publishableKey: 'wbpk_jkkqDWa54EKtV5jxugZnqz_l6kkiLNrIIY7dO7DrK5eOA5rm6H0Yb9r',
}

/** 小程序来源的 Origin：网关按此判定客户端。 */
const MINI_ORIGIN = 'https://servicewechat.com'

const REPO_DIR = path.resolve(__dirname, '../..')
const COVERS_DIR = path.join(REPO_DIR, 'assets/covers')

/** 主图规范作用域（Application owner）：路径不含任何用户标识。 */
const APP_SCOPE = 'shared/_application/activities'

/** 活动清单：本地主图文件名与 slug 同名，与云端路径规则一致。 */
const TARGETS = [
  { slug: 'dawn-trek', file: 'dawn-trek.png' },
  { slug: 'night-market', file: 'night-market.png' },
  { slug: 'island-week', file: 'island-week.png' },
]

/** 最小 wx/浏览器 stub：SDK 在 Node 下需要 storage 抽象与 wx 探测。 */
function createStubStorage() {
  const mem = new Map()
  return {
    getItem: (k) => (mem.has(k) ? mem.get(k) : null),
    setItem: (k, v) => mem.set(k, v),
    removeItem: (k) => mem.delete(k),
  }
}

/**
 * SDK 的 fetch 走 globalThis.fetch，但注入 Origin 头。
 * createCloudFetch 会自行加 publishableKey 头与 Authorization。
 */
function createCloud() {
  const origFetch = globalThis.fetch.bind(globalThis)
  const patched = (url, init = {}) => {
    // SDK 用 Headers 实例传进来，这里统一转成普通对象再补 Origin。
    const raw = init.headers
    const headers = {}
    if (raw) {
      if (typeof raw.forEach === 'function') {
        raw.forEach((v, k) => { headers[k] = v })
      } else {
        Object.assign(headers, raw)
      }
    }
    if (!headers.Origin && !headers.origin) headers.Origin = MINI_ORIGIN
    return origFetch(url, { ...init, headers })
  }
  const cloud = createWorkBuddyCloud({
    ...PUBLIC_CONFIG,
    storage: createStubStorage(),
    fetch: patched,
  })
  return { cloud }
}

/** 从错误对象里取出可读原因（PostgREST 形如 {code,message,details}）。 */
function readError(error) {
  if (!error) return '未知错误'
  const message = error.message || error.msg || error.error || ''
  const code = error.code ? `${error.code} ` : ''
  return `${code}${message}`.trim() || JSON.stringify(error).slice(0, 240)
}

async function main() {
  // 账号一律由环境变量提供：脚本里不保留任何默认邮箱，避免凭据落到版本库。
  const email = process.env.JBZL_EMAIL
  const password = process.env.JBZL_PASSWORD
  if (!email) {
    console.error('缺少环境变量 JBZL_EMAIL（运营账号邮箱，不提供默认值）')
    process.exit(1)
  }
  if (!password) {
    console.error('缺少环境变量 JBZL_PASSWORD（运营账号口令，不提供默认值）')
    process.exit(1)
  }
  const doCleanup = process.argv.includes('--cleanup')

  const { cloud } = createCloud()
  try {
    // ---------- 1. 登录 ----------
    console.log('== 1. 登录 ==')
    const signIn = await cloud.auth.signInWithPassword({ email, password })
    if (signIn.error) {
      console.error('  登录失败:', readError(signIn.error))
      process.exit(1)
    }
    const uid = signIn.data.user.id
    console.log('  登录成功 uid =', uid)

    // ---------- 2. 读取活动 ----------
    console.log('\n== 2. 读取活动 ==')
    // 不读 owner_id：activities 采用列级授权，owner_id 不授予 authenticated
    // （微信 uid 含 openid 片段，不该下发给任何客户端）。
    const { data: acts, error: actsErr } = await cloud.database
      .from('activities')
      .select('id, slug, title, cover_path')
      .order('id')
    if (actsErr) {
      console.error('  读取活动失败:', readError(actsErr))
      process.exit(1)
    }
    console.log('  活动列表:', acts.map((a) => `${a.id}/${a.slug}`).join(', '))

    const results = []
    for (const target of TARGETS) {
      const activity = acts.find((a) => a.slug === target.slug)
      if (!activity) {
        console.error(`  !! 找不到 slug=${target.slug}`)
        results.push({ slug: target.slug, ok: false, stage: 'lookup' })
        continue
      }
      const filePath = path.join(COVERS_DIR, target.file)
      if (!fs.existsSync(filePath)) {
        console.error(`  !! 本地主图缺失: assets/covers/${target.file}`)
        results.push({ slug: target.slug, ok: false, stage: 'local' })
        continue
      }
      const bytes = fs.readFileSync(filePath)
      const objectPath = `${APP_SCOPE}/${target.slug}.png`

      console.log(`\n== ${target.slug} ==`)
      console.log('  本地文件:', target.file, bytes.length, 'B')
      console.log('  规范路径:', objectPath)

      // ---------- 3. 绑定 cover_path ----------
      // 目标路径由服务端拼出，调用方无法指定；对象尚未上传时服务端会拒绝。
      const bind = await cloud.database.rpc('sync_activity_cover', {
        p_slug: target.slug,
      })
      if (bind.error) {
        console.error('  绑定失败:', readError(bind.error))
        if (String(bind.error.message || '').includes('主图尚未上传')) {
          console.error('  → 请先在 WorkBuddy「设置 → 数据管理 → 应用 → 文件存储」中，')
          console.error(`     进入 ${APP_SCOPE} 并上传 ${target.file}（文件名须等于 slug）`)
        }
        results.push({ slug: target.slug, ok: false, stage: 'bind', error: bind.error })
        continue
      }
      const boundPath = (bind.data && bind.data[0]) || bind.data
      console.log('  sync_activity_cover OK ->', boundPath)

      // ---------- 4. 字节自检 ----------
      const signed = await cloud.storage.createSignedUrl(objectPath, 300)
      if (signed.error) {
        console.error('  签名失败:', readError(signed.error))
        results.push({ slug: target.slug, ok: false, stage: 'sign', error: signed.error })
        continue
      }
      const url = signed.data.signedUrl
      const res = await fetch(url)
      const got = Buffer.from(await res.arrayBuffer())
      const ct = res.headers.get('content-type') || ''
      const same = got.length === bytes.length && got.equals(bytes)
      console.log(`  自检: HTTP ${res.status} | content-type=${ct} | 字节 ${got.length}/${bytes.length} | 完全一致=${same}`)
      if (!same || res.status !== 200) {
        results.push({ slug: target.slug, ok: false, stage: 'verify', status: res.status, ct, len: got.length })
        continue
      }
      results.push({ slug: target.slug, ok: true, path: objectPath, bytes: bytes.length, status: res.status, ct })
    }

    // ---------- 5. 清理历史遗留对象（可选） ----------
    if (doCleanup) {
      console.log('\n== 5. 清理历史遗留对象 ==')
      const legacy = TARGETS.map((t) => `shared/${uid}/activities/${t.slug}.png`)
      const existed = []
      for (const p of legacy) {
        const check = await cloud.storage.exists(p)
        if (check.data === true) existed.push(p)
      }
      if (!existed.length) {
        console.log('  无历史遗留对象')
      } else {
        const removed = await cloud.storage.remove(existed)
        if (removed && removed.error) {
          console.error('  删除失败:', readError(removed.error))
        } else {
          existed.forEach((p) => console.log('  已删除', p))
        }
      }
    }

    // ---------- 6. 复核数据库 ----------
    console.log('\n== 6. 复核 activities.cover_path ==')
    const { data: after } = await cloud.database
      .from('activities')
      .select('id, slug, cover_path')
      .order('id')
    for (const a of after || []) {
      const ok = a.cover_path && a.cover_path.startsWith(`${APP_SCOPE}/`)
      console.log(`  id=${a.id} slug=${a.slug} cover_path=${a.cover_path}${ok ? '' : '  <-- 不在规范作用域'}`)
    }

    console.log('\n== 汇总 ==')
    for (const r of results) {
      console.log(`  ${r.ok ? '成功' : '失败'}  ${r.slug}${r.ok ? `  ${r.path}  ${r.bytes}B  HTTP ${r.status} ${r.ct}` : `  卡在 ${r.stage}`}`)
    }
    const failed = results.filter((r) => !r.ok)
    console.log(`\n成功 ${results.length - failed.length}/${results.length}`)
    process.exit(failed.length ? 1 : 0)
  } catch (error) {
    console.error('脚本异常:', readError(error))
    process.exit(1)
  }
}

main()

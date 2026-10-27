const app = getApp()
const api = require('../../utils/api')
const format = require('../../utils/format')

Page({
  data: {
    loading: true,
    errorText: '',
    activities: [],
    templates: [],
    signedIn: false,
    userName: ''
  },

  onLoad() {
    this.loadActivities()
  },

  async onShow() {
    // 登录态可能在上次 onLaunch 后才异步恢复完成，等它确定再渲染。
    const signedIn = await app.ensureSession()
    this.setData({
      signedIn,
      userName: app.globalData.user ? app.globalData.user.name || '' : ''
    })
  },

  onPullDownRefresh() {
    this.loadActivities().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  async loadActivities() {
    this.setData({ loading: true, errorText: '' })
    try {
      // 活动列表是核心数据；报名人数是增强信息；模板是平台内容。
      // 三者用 allSettled 隔离：任一增强信息加载失败不应让整个列表消失，
      // 但也不能静默当成「0 人已报名」——那会误导用户。
      const [listResult, statsResult, templatesResult] = await Promise.allSettled([
        api.listActivities(),
        api.getRegistrationStats(),
        api.listTemplates()
      ])
      if (listResult.status === 'rejected') {
        throw listResult.reason
      }
      const list = listResult.value || []
      const stats = statsResult.status === 'fulfilled' ? statsResult.value : null
      const activities = list.map((item) => {
        const known = stats ? stats[item.id] !== undefined : false
        const signedUp = known ? stats[item.id] : 0
        return {
          id: item.id,
          slug: item.slug,
          title: item.title,
          summary: item.summary,
          location: item.location,
          startsAt: format.formatEventTime(item.starts_at),
          endsAt: format.formatEndTime(item.ends_at),
          countdown: format.formatCountdown(item.starts_at),
          capacity: item.capacity,
          signedUp,
          quotaKnown: known,
          quotaText: known
            ? format.quotaText(item.capacity, signedUp)
            : '人数待刷新',
          percent: known ? format.percent(item.capacity, signedUp) : 0,
          priceNote: item.price_note,
          cover: format.activityCover(item.cover_path, item.cover_slug)
        }
      })
      const templates = templatesResult.status === 'fulfilled'
        ? (templatesResult.value || []).map((item) => ({
            id: item.id,
            title: item.title,
            summary: item.summary || '',
            cover: format.activityCover('', item.cover_slug),
            defaultCapacity: item.default_capacity,
            defaultDuration: item.default_duration_minutes
          }))
        : []
      this.setData({ activities, templates, loading: false })
      this.loadCovers(list)
    } catch (error) {
      this.setData({
        loading: false,
        errorText: (error && error.message) || '活动加载失败，请稍后重试'
      })
    }
  },

  /** 拉取云端主图签名地址；失败保留本地降级图。 */
  async loadCovers(list) {
    const withCover = list.filter((item) => item.cover_path)
    if (!withCover.length) {
      return
    }
    try {
      const storage = require('../../utils/storage')
      const updates = []
      for (const item of withCover) {
        // 单张主图失败时沿用内置占位图，不影响其他活动。
        const url = await storage.signedUrl(item.cover_path, 3600)
        if (url) {
          updates.push({ id: item.id, cover: url })
        }
      }
      if (!updates.length) {
        return
      }
      const map = {}
      updates.forEach((row) => {
        map[row.id] = row
      })
      this.setData({
        activities: this.data.activities.map((row) =>
          map[row.id] ? Object.assign({}, row, map[row.id]) : row
        )
      })
    } catch (error) {
      // 主图是增强信息，失败时沿用内置占位图
    }
  },

  /**
   * 内置主图缺失时降级到随包分发的默认图。
   *
   * 内置主图路径按 slug 规则推导（utils/format.js），新增活动若忘了把
   * `<slug>.png` 放进 assets/covers/，<image> 会加载失败并触发本事件；
   * 没有它就会留下一个裂图占位。
   */
  onCoverError(event) {
    const id = event && event.currentTarget ? event.currentTarget.dataset.id : undefined
    const fallback = format.defaultCover()
    this.setData({
      activities: this.data.activities.map((row) =>
        row.id === id && row.cover !== fallback
          ? Object.assign({}, row, { cover: fallback })
          : row
      )
    })
  },

  onTapActivity(event) {
    const id = Number(event.currentTarget.dataset.id)
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  /** 用某个模板发起活动：跳发布页并带上模板 id。 */
  onTapUseTemplate(event) {
    const id = Number(event.currentTarget.dataset.id)
    wx.navigateTo({ url: `/pages/publish/publish?templateId=${id}` })
  },

  /** 发起活动入口。 */
  onTapPublish() {
    wx.switchTab({ url: '/pages/publish/publish' })
  },

  async onTapSignIn() {
    const result = await app.signIn()
    if (!result.ok) {
      wx.showToast({ title: result.message || '授权失败', icon: 'none' })
      return
    }
    this.setData({ signedIn: true, userName: (result.user && result.user.name) || '' })
    wx.showToast({ title: '授权成功', icon: 'success' })
  }
})

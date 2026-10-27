const app = getApp()
const api = require('../../utils/api')
const format = require('../../utils/format')

Page({
  data: {
    loading: true,
    errorText: '',
    signedIn: false,
    signingIn: false,
    activities: [],
    operatingId: 0
  },

  onLoad() {
    this.refreshSession()
  },

  async onShow() {
    const signedIn = await app.ensureSession()
    this.setData({ signedIn })
    if (signedIn) {
      this.loadActivities()
    } else {
      this.setData({ loading: false, activities: [] })
    }
  },

  async refreshSession() {
    const signedIn = await app.ensureSession()
    this.setData({ signedIn })
  },

  async loadActivities() {
    this.setData({ loading: true, errorText: '' })
    try {
      const list = await api.listMyActivities()
      const activities = list.map((item) => {
        const status = format.activityStatus(item.published, item.endsAt, item.startsAt)
        return {
          id: item.id,
          title: item.title,
          summary: item.summary || '',
          location: item.location || '',
          startsAt: format.formatEventTime(item.startsAt),
          startsAtIso: item.startsAt,
          endsAtIso: item.endsAt,
          countdown: format.formatCountdown(item.startsAt),
          capacity: item.capacity,
          signedUp: item.signedUp,
          quotaText: format.quotaText(item.capacity, item.signedUp),
          priceNote: item.priceNote || '',
          coverSlug: item.coverSlug,
          cover: format.activityCover('', item.coverSlug),
          highlights: item.highlights || [],
          notes: item.notes || [],
          published: item.published,
          status: status,
          statusClass: format.activityStatusClass(status)
        }
      })
      this.setData({ activities, loading: false })
    } catch (error) {
      this.setData({
        loading: false,
        errorText: (error && error.message) || '我的活动加载失败，请稍后重试'
      })
    }
  },

  async onTapSignIn() {
    this.setData({ signingIn: true })
    const result = await app.signIn()
    this.setData({ signingIn: false })
    if (!result.ok) {
      wx.showToast({ title: result.message || '授权失败', icon: 'none' })
      return
    }
    this.setData({ signedIn: true })
    this.loadActivities()
  },

  /** 编辑：跳发布页并带上活动 id。 */
  onTapEdit(event) {
    const id = Number(event.currentTarget.dataset.id)
    wx.navigateTo({ url: `/pages/publish/publish?id=${id}` })
  },

  /** 下架 / 重新上架。 */
  onTapToggle(event) {
    const id = Number(event.currentTarget.dataset.id)
    const target = this.data.activities.find((item) => item.id === id)
    if (!target || this.data.operatingId) {
      return
    }
    const next = !target.published
    // 已结束的活动不再提供「重新上架」：过期活动复活没有意义，
    // 服务端也会以「开始时间必须晚于当前时间」拒绝。
    if (next && target.status === '已结束') {
      wx.showToast({ title: '已结束的活动无法重新上架', icon: 'none' })
      return
    }
    wx.showModal({
      title: next ? '重新上架' : '下架活动',
      content: next
        ? '重新上架后，其他人会再次看到这场活动。'
        : '下架后其他人将看不到这场活动，已报名的人不受影响。',
      confirmText: next ? '重新上架' : '确认下架',
      cancelText: '再想想',
      confirmColor: next ? '#2f6bff' : '#e05a5a',
      success: async (res) => {
        if (!res.confirm) {
          return
        }
        this.setData({ operatingId: id })
        try {
          // 下架只改发布状态：服务端对 published=false 走短路，
          // 不受内容与时间校验约束（已结束的活动也必须能下架）。
          //
          // 字段一律传原值：重新上架走的是完整编辑路径，
          // 若这里传空值会把亮点与须知清空。
          const ok = await api.updateActivity({
            activityId: id,
            title: target.title,
            summary: target.summary,
            location: target.location,
            startsAt: target.startsAtIso,
            endsAt: target.endsAtIso,
            capacity: target.capacity,
            priceNote: target.priceNote,
            highlights: target.highlights,
            notes: target.notes,
            coverSlug: target.coverSlug,
            published: next
          })
          if (!ok) {
            wx.showToast({ title: '操作失败，请稍后重试', icon: 'none' })
          } else {
            wx.showToast({ title: next ? '已重新上架' : '已下架', icon: 'success' })
          }
          this.loadActivities()
        } catch (error) {
          wx.showToast({ title: (error && error.message) || '操作失败，请稍后重试', icon: 'none' })
        } finally {
          this.setData({ operatingId: 0 })
        }
      }
    })
  },

  onTapGoPublish() {
    wx.switchTab({ url: '/pages/publish/publish' })
  }
})

const app = getApp()
const api = require('../../utils/api')
const format = require('../../utils/format')

const MAX_TITLE = 40
const MAX_SUMMARY = 200
const MAX_LOCATION = 60
const MAX_PRICE = 40
const MAX_LINES = 8
const MAX_LINE_LENGTH = 60

Page({
  data: {
    loading: true,
    errorText: '',
    submitting: false,
    signedIn: false,
    signingIn: false,

    // 编辑态：activityId 非 0 表示正在编辑已有活动
    activityId: 0,
    editing: false,

    // 模板
    templates: [],
    selectedTemplateId: 0,
    selectedTemplateName: '',

    // 封面
    coverSlugs: format.COVER_SLUGS,
    coverSlug: 'default',

    // 表单
    title: '',
    summary: '',
    location: '',
    startsAtDate: '',
    startsAtTime: '',
    endsAtDate: '',
    endsAtTime: '',
    capacity: 20,
    capacityInput: '20',
    priceNote: '',
    highlightsText: '',
    notesText: '',

    // 校验态
    titleError: '',
    locationError: '',
    timeError: '',
    formError: '',

    // 供 picker 使用
    minDate: '',
    maxDate: ''
  },

  onLoad(options) {
    const id = Number(options.id || 0)
    const templateId = Number(options.templateId || 0)
    this.setData({ activityId: id, editing: !!id })
    this.prepareDates()
    this.loadTemplates()
    if (id) {
      this.loadActivityForEdit(id)
    } else if (templateId) {
      this.applyTemplateById(templateId)
    }
  },

  async onShow() {
    const signedIn = await app.ensureSession()
    this.setData({ signedIn })
  },

  /** picker 的可选日期范围：今天 ~ 一年后。 */
  prepareDates() {
    const now = new Date()
    const min = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const max = new Date(now.getFullYear() + 1, now.getMonth(), now.getDate())
    this.setData({
      minDate: toDateText(min),
      maxDate: toDateText(max)
    })
  },

  async loadTemplates() {
    this.setData({ loading: true, errorText: '' })
    try {
      const templates = await api.listTemplates()
      this.setData({
        loading: false,
        templates: templates.map((item) => ({
          id: item.id,
          title: item.title,
          summary: item.summary || '',
          coverSlug: item.cover_slug,
          defaultCapacity: item.default_capacity,
          defaultDuration: item.default_duration_minutes,
          highlights: item.highlights || [],
          notes: item.notes || []
        }))
      })
    } catch (error) {
      this.setData({
        loading: false,
        errorText: (error && error.message) || '模板加载失败，请稍后重试'
      })
    }
  },

  /**
   * 编辑态：载入待编辑活动的字段。
   *
   * 为什么不能只靠 my_activities 的结果：那个列表是聚合视图，
   * 载入时用它做预填最省事，但服务端仍会再次校验归属——
   * 客户端预填不是授权，授权判定始终在服务端。
   */
  async loadActivityForEdit(id) {
    try {
      const mine = await api.listMyActivities()
      const row = mine.find((item) => item.id === id)
      if (!row) {
        this.setData({ loading: false, errorText: '活动不存在或无权修改' })
        return
      }
      this.setData({
        loading: false,
        title: row.title || '',
        summary: row.summary || '',
        location: row.location || '',
        startsAtDate: datePart(row.startsAt),
        startsAtTime: timePart(row.startsAt),
        endsAtDate: datePart(row.endsAt),
        endsAtTime: timePart(row.endsAt),
        capacity: row.capacity,
        capacityInput: String(row.capacity),
        priceNote: row.priceNote || '',
        highlightsText: format.joinLines(row.highlights),
        notesText: format.joinLines(row.notes),
        coverSlug: row.coverSlug || 'default',
        titleError: '',
        locationError: '',
        timeError: '',
        formError: ''
      })
    } catch (error) {
      this.setData({
        loading: false,
        errorText: (error && error.message) || '活动加载失败，请稍后重试'
      })
    }
  },

  /** 套用模板：把模板内容预填进表单（预填值全部可编辑）。 */
  applyTemplateById(templateId) {
    const template = this.data.templates.find((item) => item.id === templateId)
    if (!template) {
      return
    }
    this.setData({
      selectedTemplateId: template.id,
      selectedTemplateName: template.title,
      title: template.title,
      summary: template.summary,
      coverSlug: template.coverSlug || 'default',
      capacity: template.defaultCapacity,
      capacityInput: String(template.defaultCapacity),
      highlightsText: format.joinLines(template.highlights),
      notesText: format.joinLines(template.notes),
      titleError: '',
      formError: ''
    })
  },
  onTapTemplate(event) {
    const id = Number(event.currentTarget.dataset.id)
    this.applyTemplateById(id)
  },

  onTapFreeStart() {
    this.setData({
      selectedTemplateId: 0,
      selectedTemplateName: '',
      titleError: '',
      formError: ''
    })
  },

  onTapCover(event) {
    const slug = event.currentTarget.dataset.slug
    if (!format.isAllowedCover(slug)) {
      return
    }
    this.setData({ coverSlug: slug })
  },

  onInputTitle(event) {
    this.setData({ title: event.detail.value, titleError: '' })
  },

  onInputSummary(event) {
    this.setData({ summary: event.detail.value })
  },

  onInputLocation(event) {
    this.setData({ location: event.detail.value, locationError: '' })
  },

  onInputCapacity(event) {
    const raw = String(event.detail.value || '').replace(/[^\d]/g, '')
    this.setData({ capacityInput: raw })
  },

  onInputPriceNote(event) {
    this.setData({ priceNote: event.detail.value })
  },

  onInputHighlights(event) {
    this.setData({ highlightsText: event.detail.value })
  },

  onInputNotes(event) {
    this.setData({ notesText: event.detail.value })
  },

  onChangeStartsDate(event) {
    this.setData({ startsAtDate: event.detail.value, timeError: '' })
  },

  onChangeStartsTime(event) {
    this.setData({ startsAtTime: event.detail.value, timeError: '' })
  },

  onChangeEndsDate(event) {
    this.setData({ endsAtDate: event.detail.value })
  },

  onChangeEndsTime(event) {
    this.setData({ endsAtTime: event.detail.value })
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
    wx.showToast({ title: '授权成功', icon: 'success' })
  },

  /** 提交前本地预校验（与服务端规则同源，减少无效请求）。 */
  validate() {
    const title = (this.data.title || '').trim()
    const location = (this.data.location || '').trim()
    let titleError = ''
    let locationError = ''
    let timeError = ''

    if (title.length < 2) {
      titleError = '请填写活动名称（至少 2 个字）'
    } else if (title.length > MAX_TITLE) {
      titleError = '活动名称不能超过 40 字'
    }
    if (location.length < 2) {
      locationError = '请填写活动地点'
    } else if (location.length > MAX_LOCATION) {
      locationError = '活动地点不能超过 60 字'
    }
    if (!this.data.startsAtDate || !this.data.startsAtTime) {
      timeError = '请选择活动开始时间'
    }

    this.setData({ titleError, locationError, timeError })
    return !titleError && !locationError && !timeError
  },

  async onSubmit() {
    if (this.data.submitting) {
      return
    }
    if (!this.data.signedIn) {
      wx.showToast({ title: '请先完成微信授权登录', icon: 'none' })
      return
    }
    if (!this.validate()) {
      return
    }

    const highlights = format.parseLines(this.data.highlightsText)
    const notes = format.parseLines(this.data.notesText)
    if (highlights.length > MAX_LINES || notes.length > MAX_LINES) {
      this.setData({ formError: '亮点与报名须知各最多 8 条' })
      return
    }
    const tooLong = highlights.concat(notes).some((line) => line.length > MAX_LINE_LENGTH)
    if (tooLong) {
      this.setData({ formError: '每条亮点或须知需在 60 字以内' })
      return
    }

    const capacityRaw = String(this.data.capacityInput || '').trim()
    const capacity = capacityRaw === '' ? 0 : Number(capacityRaw)
    if (!Number.isFinite(capacity) || capacity < 0) {
      this.setData({ formError: '名额不能为负数' })
      return
    }

    const payload = {
      templateId: this.data.selectedTemplateId || null,
      title: (this.data.title || '').trim(),
      summary: (this.data.summary || '').trim(),
      location: (this.data.location || '').trim(),
      startsAt: toIso(this.data.startsAtDate, this.data.startsAtTime),
      endsAt: this.data.endsAtDate && this.data.endsAtTime
        ? toIso(this.data.endsAtDate, this.data.endsAtTime)
        : null,
      capacity: capacity,
      priceNote: (this.data.priceNote || '').trim(),
      highlights: highlights,
      notes: notes,
      coverSlug: this.data.coverSlug
    }

    this.setData({ submitting: true, formError: '' })
    try {
      if (this.data.editing) {
        await api.updateActivity({
          activityId: this.data.activityId,
          title: payload.title,
          summary: payload.summary,
          location: payload.location,
          startsAt: payload.startsAt,
          endsAt: payload.endsAt,
          capacity: payload.capacity,
          priceNote: payload.priceNote,
          highlights: payload.highlights,
          notes: payload.notes,
          coverSlug: payload.coverSlug,
          published: true
        })
        wx.showToast({ title: '已保存', icon: 'success' })
        setTimeout(() => {
          wx.switchTab({ url: '/pages/mine/mine' })
        }, 800)
      } else {
        const created = await api.createActivity(payload)
        if (!created) {
          throw new Error('发布失败，请稍后重试')
        }
        wx.showToast({ title: '发布成功', icon: 'success' })
        setTimeout(() => {
          wx.switchTab({ url: '/pages/mine/mine' })
        }, 800)
      }
    } catch (error) {
      this.setData({ submitting: false })
      wx.showToast({ title: (error && error.message) || '操作失败，请稍后重试', icon: 'none' })
    }
  }
})

/** Date → 'YYYY-MM-DD' */
function toDateText(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/** ISO 字符串 → 'YYYY-MM-DD'（本地时区），无值返回空串。 */
function datePart(value) {
  if (!value) {
    return ''
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  return toDateText(date)
}

/** ISO 字符串 → 'HH:mm'（本地时区），无值返回空串。 */
function timePart(value) {
  if (!value) {
    return ''
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  const hh = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')
  return hh + ':' + mm
}

/**
 * 'YYYY-MM-DD' + 'HH:mm' → ISO 字符串。
 *
 * 必须显式按本地时区构造 Date，不能用 new Date('YYYY-MM-DD HH:mm')：
 * 后者在部分实现里按 UTC 解析，会导致时间偏移 8 小时。
 */
function toIso(dateText, timeText) {
  if (!dateText) {
    return null
  }
  const dateParts = String(dateText).split('-')
  const timeParts = String(timeText || '00:00').split(':')
  const y = Number(dateParts[0])
  const m = Number(dateParts[1])
  const d = Number(dateParts[2])
  const hh = Number(timeParts[0] || 0)
  const mm = Number(timeParts[1] || 0)
  if (!y || !m || !d) {
    return null
  }
  const date = new Date(y, m - 1, d, hh, mm, 0, 0)
  if (Number.isNaN(date.getTime())) {
    return null
  }
  return date.toISOString()
}

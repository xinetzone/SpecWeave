Page({
  onTapUploadCover() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      success: (res) => { console.log(res.tempFiles) }
    })
  },
  onTapPickFile() {
    wx.chooseMessageFile({ count: 1 })
  }
})

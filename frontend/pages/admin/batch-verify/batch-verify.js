// pages/admin/batch-verify/batch-verify.js
const { get, post } = require('../../../utils/request.js')

Page({
  data: {
    filePath: '',
    uploading: false,
    result: null
  },

  chooseFile() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      success: (res) => {
        const file = res.tempFiles[0]
        this.setData({ filePath: file.path })
      }
    })
  },

  async uploadFile() {
    const { filePath } = this.data
    if (!filePath) {
      wx.showToast({ title: '请选择文件', icon: 'none' })
      return
    }

    this.setData({ uploading: true })

    try {
      const res = await post('/api/admin/verify/batch-import', {
        file: filePath
      })
      this.setData({
        result: res,
        uploading: false
      })
      wx.showToast({ title: '导入成功', icon: 'success' })
    } catch (error) {
      console.error('批量导入失败:', error)
      this.setData({ uploading: false })
      wx.showToast({ title: error.message || '导入失败', icon: 'none' })
    }
  },

  downloadTemplate() {
    wx.downloadFile({
      url: '/api/admin/verify/template',
      success: (res) => {
        wx.openDocument({
          filePath: res.tempFilePath,
          showMenu: true
        })
      }
    })
  }
})

// pages/admin/verify-list/verify-list.js
const { get, post } = require('../../../utils/request.js')

Page({
  data: {
    verifyList: [],
    page: 1,
    pageSize: 20,
    loading: false,
    hasMore: true
  },

  onLoad() {
    this.loadVerifyList()
  },

  async loadVerifyList() {
    const { page, pageSize, verifyList, loading } = this.data
    if (loading) return

    this.setData({ loading: true })

    try {
      const res = await get('/api/admin/verify/list', {
        page: page,
        page_size: pageSize
      })

      const newList = page === 1 ? res.list : [...verifyList, ...res.list]

      this.setData({
        verifyList: newList,
        page: page + 1,
        loading: false,
        hasMore: newList.length < res.total
      })
    } catch (error) {
      console.error('加载认证列表失败:', error)
      this.setData({ loading: false })
      wx.showToast({ title: error.message || '加载失败', icon: 'none' })
    }
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadVerifyList()
    }
  },

  async approveVerify(e) {
    const { verifyId } = e.currentTarget.dataset
    wx.showModal({
      title: '确认通过',
      content: '确定通过该用户的认证申请吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await post(`/api/admin/verify/${verifyId}/approve`, {})
            wx.showToast({ title: '已通过', icon: 'success' })
            this.setData({ page: 1, verifyList: [], hasMore: true })
            this.loadVerifyList()
          } catch (error) {
            wx.showToast({ title: error.message || '操作失败', icon: 'none' })
          }
        }
      }
    })
  },

  async rejectVerify(e) {
    const { verifyId } = e.currentTarget.dataset
    wx.showModal({
      title: '确认拒绝',
      content: '确定拒绝该用户的认证申请吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await post(`/api/admin/verify/${verifyId}/reject`, {})
            wx.showToast({ title: '已拒绝', icon: 'success' })
            this.setData({ page: 1, verifyList: [], hasMore: true })
            this.loadVerifyList()
          } catch (error) {
            wx.showToast({ title: error.message || '操作失败', icon: 'none' })
          }
        }
      }
    })
  }
})

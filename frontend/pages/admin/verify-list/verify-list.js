// pages/admin/verify-list/verify-list.js
const { get, post } = require('../../../../utils/request.js')

Page({
  data: {
    verifyList: [],
    pendingCount: 0,
    loading: false,
    page: 1,
    pageSize: 20
  },

  onLoad(options) {
    this.loadVerifyList()
  },

  onShow() {
    // 刷新列表
    this.loadVerifyList()
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      verifyList: []
    })
    this.loadVerifyList().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  /**
   * 加载审核列表
   */
  async loadVerifyList() {
    const { page, pageSize, verifyList } = this.data
    
    this.setData({ loading: true })
    
    try {
      const res = await get('/api/admin/verify/pending', {
        page: page,
        page_size: pageSize
      })
      
      this.setData({
        verifyList: page === 1 ? res.users : [...verifyList, ...res.users],
        pendingCount: res.total,
        loading: false
      })
    } catch (error) {
      console.error('加载审核列表失败:', error)
      this.setData({ loading: false })
      
      wx.showToast({
        title: error.message || '加载失败',
        icon: 'none'
      })
    }
  },

  /**
   * 跳转到详情页
   */
  goToDetail(e) {
    const user = e.currentTarget.dataset.user
    wx.navigateTo({
      url: `/pages/admin/verify-detail/verify-detail?user_id=${user.user_id}`
    })
  },

  /**
   * 通过审核
   */
  async approveVerify(e) {
    const user = e.currentTarget.dataset.user
    
    wx.showModal({
      title: '审核通过',
      content: `确定要通过用户"${user.nickname || '微信用户'}"的认证申请吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '处理中...' })
            
            await post('/api/admin/verify/approve', {
              user_id: user.user_id
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: '已通过',
              icon: 'success'
            })
            
            // 从列表中移除
            const verifyList = this.data.verifyList.filter(
              item => item.user_id !== user.user_id
            )
            this.setData({
              verifyList,
              pendingCount: this.data.pendingCount - 1
            })
            
          } catch (error) {
            wx.hideLoading()
            console.error('审核通过失败:', error)
            wx.showToast({
              title: error.message || '操作失败',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  /**
   * 拒绝审核
   */
  async rejectVerify(e) {
    const user = e.currentTarget.dataset.user
    
    wx.showModal({
      title: '审核拒绝',
      editable: true,
      placeholderText: '请输入拒绝原因（至少 10 字）',
      success: async (res) => {
        if (res.confirm) {
          const reason = res.content || ''
          
          if (reason.length < 10) {
            wx.showToast({
              title: '拒绝原因至少 10 字',
              icon: 'none'
            })
            return
          }
          
          try {
            wx.showLoading({ title: '处理中...' })
            
            await post('/api/admin/verify/reject', {
              user_id: user.user_id,
              reason: reason
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: '已拒绝',
              icon: 'success'
            })
            
            // 从列表中移除
            const verifyList = this.data.verifyList.filter(
              item => item.user_id !== user.user_id
            )
            this.setData({
              verifyList,
              pendingCount: this.data.pendingCount - 1
            })
            
          } catch (error) {
            wx.hideLoading()
            console.error('审核拒绝失败:', error)
            wx.showToast({
              title: error.message || '操作失败',
              icon: 'none'
            })
          }
        }
      }
    })
  }
})

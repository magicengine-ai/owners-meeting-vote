// pages/admin/batch-verify/batch-verify.js
const { get, post } = require('../../../../utils/request.js')

Page({
  data: {
    verifyList: [],
    selectedIds: [],
    selectAll: false,
    pendingCount: 0,
    loading: false,
    page: 1,
    pageSize: 20
  },

  onLoad(options) {
    this.loadVerifyList()
  },

  onShow() {
    this.loadVerifyList()
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      verifyList: [],
      selectedIds: [],
      selectAll: false
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
   * 切换选择
   */
  toggleSelect(e) {
    const userId = e.currentTarget.dataset.userId
    let { selectedIds } = this.data
    
    const index = selectedIds.indexOf(userId)
    if (index > -1) {
      selectedIds.splice(index, 1)
    } else {
      selectedIds.push(userId)
    }
    
    this.setData({
      selectedIds,
      selectAll: selectedIds.length === this.data.verifyList.length && this.data.verifyList.length > 0
    })
  },

  /**
   * 全选/取消全选
   */
  toggleSelectAll() {
    const { selectAll, verifyList } = this.data
    
    if (selectAll) {
      this.setData({
        selectedIds: [],
        selectAll: false
      })
    } else {
      this.setData({
        selectedIds: verifyList.map(item => item.user_id),
        selectAll: true
      })
    }
  },

  /**
   * 批量通过
   */
  async batchApprove() {
    const { selectedIds } = this.data
    
    if (selectedIds.length === 0) {
      wx.showToast({
        title: '请选择要审核的用户',
        icon: 'none'
      })
      return
    }
    
    wx.showModal({
      title: '批量通过',
      content: `确定要通过选中的 ${selectedIds.length} 个用户的认证申请吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '处理中...' })
            
            const result = await post('/api/admin/verify/batch', {
              user_ids: selectedIds,
              action: 'approve'
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: `成功${result.success_count}个，失败${result.failed_count}个`,
              icon: 'success'
            })
            
            // 刷新列表
            this.setData({
              selectedIds: [],
              selectAll: false
            })
            this.loadVerifyList()
            
          } catch (error) {
            wx.hideLoading()
            console.error('批量通过失败:', error)
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
   * 批量拒绝
   */
  async batchReject() {
    const { selectedIds } = this.data
    
    if (selectedIds.length === 0) {
      wx.showToast({
        title: '请选择要审核的用户',
        icon: 'none'
      })
      return
    }
    
    wx.showModal({
      title: '批量拒绝',
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
            
            const result = await post('/api/admin/verify/batch', {
              user_ids: selectedIds,
              action: 'reject',
              reason: reason
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: `成功${result.success_count}个，失败${result.failed_count}个`,
              icon: 'success'
            })
            
            // 刷新列表
            this.setData({
              selectedIds: [],
              selectAll: false
            })
            this.loadVerifyList()
            
          } catch (error) {
            wx.hideLoading()
            console.error('批量拒绝失败:', error)
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

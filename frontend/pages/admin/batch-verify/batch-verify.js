// pages/admin/batch-verify/batch-verify.js
const { get, post } = require('../../../utils/request.js')

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
   * 鍔犺浇瀹℃牳鍒楄〃
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
      console.error('鍔犺浇瀹℃牳鍒楄〃澶辫触:', error)
      this.setData({ loading: false })
      
      wx.showToast({
        title: error.message || '鍔犺浇澶辫触',
        icon: 'none'
      })
    }
  },

  /**
   * 鍒囨崲閫夋嫨
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
   * 鍏ㄩ€?鍙栨秷鍏ㄩ€?
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
   * 鎵归噺閫氳繃
   */
  async batchApprove() {
    const { selectedIds } = this.data
    
    if (selectedIds.length === 0) {
      wx.showToast({
        title: '璇烽€夋嫨瑕佸鏍哥殑鐢ㄦ埛',
        icon: 'none'
      })
      return
    }
    
    wx.showModal({
      title: '鎵归噺閫氳繃',
      content: `纭畾瑕侀€氳繃閫変腑鐨?${selectedIds.length} 涓敤鎴风殑璁よ瘉鐢宠鍚楋紵`,
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '澶勭悊涓?..' })
            
            const result = await post('/api/admin/verify/batch', {
              user_ids: selectedIds,
              action: 'approve'
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: `鎴愬姛${result.success_count}涓紝澶辫触${result.failed_count}涓猔,
              icon: 'success'
            })
            
            // 鍒锋柊鍒楄〃
            this.setData({
              selectedIds: [],
              selectAll: false
            })
            this.loadVerifyList()
            
          } catch (error) {
            wx.hideLoading()
            console.error('鎵归噺閫氳繃澶辫触:', error)
            wx.showToast({
              title: error.message || '鎿嶄綔澶辫触',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  /**
   * 鎵归噺鎷掔粷
   */
  async batchReject() {
    const { selectedIds } = this.data
    
    if (selectedIds.length === 0) {
      wx.showToast({
        title: '璇烽€夋嫨瑕佸鏍哥殑鐢ㄦ埛',
        icon: 'none'
      })
      return
    }
    
    wx.showModal({
      title: '鎵归噺鎷掔粷',
      editable: true,
      placeholderText: '璇疯緭鍏ユ嫆缁濆師鍥狅紙鑷冲皯 10 瀛楋級',
      success: async (res) => {
        if (res.confirm) {
          const reason = res.content || ''
          
          if (reason.length < 10) {
            wx.showToast({
              title: '鎷掔粷鍘熷洜鑷冲皯 10 瀛?,
              icon: 'none'
            })
            return
          }
          
          try {
            wx.showLoading({ title: '澶勭悊涓?..' })
            
            const result = await post('/api/admin/verify/batch', {
              user_ids: selectedIds,
              action: 'reject',
              reason: reason
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: `鎴愬姛${result.success_count}涓紝澶辫触${result.failed_count}涓猔,
              icon: 'success'
            })
            
            // 鍒锋柊鍒楄〃
            this.setData({
              selectedIds: [],
              selectAll: false
            })
            this.loadVerifyList()
            
          } catch (error) {
            wx.hideLoading()
            console.error('鎵归噺鎷掔粷澶辫触:', error)
            wx.showToast({
              title: error.message || '鎿嶄綔澶辫触',
              icon: 'none'
            })
          }
        }
      }
    })
  }
})

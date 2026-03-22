// pages/admin/verify-list/verify-list.js
const { get, post } = require('../../../utils/request.js')

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
    // 鍒锋柊鍒楄〃
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
   * 璺宠浆鍒拌鎯呴〉
   */
  goToDetail(e) {
    const user = e.currentTarget.dataset.user
    wx.navigateTo({
      url: `/pages/admin/verify-detail/verify-detail?user_id=${user.user_id}`
    })
  },

  /**
   * 閫氳繃瀹℃牳
   */
  async approveVerify(e) {
    const user = e.currentTarget.dataset.user
    
    wx.showModal({
      title: '瀹℃牳閫氳繃',
      content: `纭畾瑕侀€氳繃鐢ㄦ埛"${user.nickname || '寰俊鐢ㄦ埛'}"鐨勮璇佺敵璇峰悧锛焋,
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '澶勭悊涓?..' })
            
            await post('/api/admin/verify/approve', {
              user_id: user.user_id
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: '宸查€氳繃',
              icon: 'success'
            })
            
            // 浠庡垪琛ㄤ腑绉婚櫎
            const verifyList = this.data.verifyList.filter(
              item => item.user_id !== user.user_id
            )
            this.setData({
              verifyList,
              pendingCount: this.data.pendingCount - 1
            })
            
          } catch (error) {
            wx.hideLoading()
            console.error('瀹℃牳閫氳繃澶辫触:', error)
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
   * 鎷掔粷瀹℃牳
   */
  async rejectVerify(e) {
    const user = e.currentTarget.dataset.user
    
    wx.showModal({
      title: '瀹℃牳鎷掔粷',
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
            
            await post('/api/admin/verify/reject', {
              user_id: user.user_id,
              reason: reason
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: '宸叉嫆缁?,
              icon: 'success'
            })
            
            // 浠庡垪琛ㄤ腑绉婚櫎
            const verifyList = this.data.verifyList.filter(
              item => item.user_id !== user.user_id
            )
            this.setData({
              verifyList,
              pendingCount: this.data.pendingCount - 1
            })
            
          } catch (error) {
            wx.hideLoading()
            console.error('瀹℃牳鎷掔粷澶辫触:', error)
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

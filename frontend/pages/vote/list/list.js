// pages/vote/list/list.js
const { get } = require('../../../utils/request.js')

Page({
  data: {
    voteList: [],
    totalCount: 0,
    currentStatus: '',
    page: 1,
    pageSize: 10,
    loading: false,
    hasMore: true
  },

  onLoad(options) {
    this.loadVoteList()
  },

  onShow() {
    // 鍒锋柊鍒楄〃
    this.setData({
      page: 1,
      voteList: [],
      hasMore: true
    })
    this.loadVoteList()
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      voteList: [],
      hasMore: true
    })
    this.loadVoteList().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadVoteList()
    }
  },

  /**
   * 鍒囨崲鐘舵€佺瓫閫?
   */
  changeStatus(e) {
    const status = e.currentTarget.dataset.status
    this.setData({
      currentStatus: status,
      page: 1,
      voteList: [],
      hasMore: true
    })
    this.loadVoteList()
  },

  /**
   * 鍔犺浇鎶曠エ鍒楄〃
   */
  async loadVoteList() {
    const { page, pageSize, voteList, currentStatus, loading } = this.data
    
    if (loading) return
    
    this.setData({ loading: true })
    
    try {
      const res = await get('/api/vote/list', {
        page: page,
        page_size: pageSize,
        status: currentStatus || undefined
      })
      
      const newVotes = page === 1 ? res.votes : [...voteList, ...res.votes]
      
      this.setData({
        voteList: newVotes,
        totalCount: res.total,
        page: page + 1,
        loading: false,
        hasMore: newVotes.length < res.total
      })
    } catch (error) {
      console.error('鍔犺浇鎶曠エ鍒楄〃澶辫触:', error)
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
    const voteId = e.currentTarget.dataset['vote-id']
    wx.navigateTo({
      url: `/pages/vote/detail/detail?vote_id=${voteId}`
    })
  }
})

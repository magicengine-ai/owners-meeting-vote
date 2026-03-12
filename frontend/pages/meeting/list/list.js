// pages/meeting/list/list.js
const { get } = require('../../../../utils/request.js')

Page({
  data: {
    meetingList: [],
    totalCount: 0,
    currentStatus: '',
    page: 1,
    pageSize: 10,
    loading: false,
    hasMore: true
  },

  onLoad(options) {
    this.loadMeetingList()
  },

  onShow() {
    // 刷新列表
    this.setData({
      page: 1,
      meetingList: [],
      hasMore: true
    })
    this.loadMeetingList()
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      meetingList: [],
      hasMore: true
    })
    this.loadMeetingList().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMeetingList()
    }
  },

  /**
   * 切换状态筛选
   */
  changeStatus(e) {
    const status = e.currentTarget.dataset.status
    this.setData({
      currentStatus: status,
      page: 1,
      meetingList: [],
      hasMore: true
    })
    this.loadMeetingList()
  },

  /**
   * 加载会议列表
   */
  async loadMeetingList() {
    const { page, pageSize, meetingList, currentStatus, loading } = this.data
    
    if (loading) return
    
    this.setData({ loading: true })
    
    try {
      const res = await get('/api/meeting/list', {
        page: page,
        page_size: pageSize,
        status: currentStatus || undefined
      })
      
      const newMeetings = page === 1 ? res.meetings : [...meetingList, ...res.meetings]
      
      this.setData({
        meetingList: newMeetings,
        totalCount: res.total,
        page: page + 1,
        loading: false,
        hasMore: newMeetings.length < res.total
      })
    } catch (error) {
      console.error('加载会议列表失败:', error)
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
    const meetingId = e.currentTarget.dataset['meeting-id']
    wx.navigateTo({
      url: `/pages/meeting/detail/detail?meeting_id=${meetingId}`
    })
  }
})

// pages/index/index.js
Page({
  data: {
    userInfo: null,
    notices: [],
    activeVotes: [],
    upcomingMeetings: []
  },

  onLoad: function () {
    this.loadUserInfo();
    this.loadNotices();
    this.loadActiveVotes();
    this.loadUpcomingMeetings();
  },

  onShow: function() {
    // 每次显示时刷新数据
    this.refreshData();
  },

  // 加载用户信息
  loadUserInfo: function() {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({ userInfo });
    }
  },

  // 加载公告
  loadNotices: function() {
    // TODO: 从 API 加载公告
    this.setData({
      notices: [
        {
          id: 1,
          title: '关于召开 2026 年第一次业主大会的通知',
          date: '2026-03-10',
          isRead: false
        },
        {
          id: 2,
          title: '小区电梯维修基金使用公示',
          date: '2026-03-08',
          isRead: true
        }
      ]
    });
  },

  // 加载进行中的投票
  loadActiveVotes: function() {
    // TODO: 从 API 加载投票
    this.setData({
      activeVotes: [
        {
          id: 1,
          title: '关于聘请新物业公司的投票',
          endTime: '2026-03-20 23:59:59',
          totalVotes: 156,
          totalHouseholds: 500,
          progress: 31.2
        }
      ]
    });
  },

  // 加载即将召开的会议
  loadUpcomingMeetings: function() {
    // TODO: 从 API 加载会议
    this.setData({
      upcomingMeetings: [
        {
          id: 1,
          title: '2026 年第一次业主大会',
          time: '2026-03-25 14:00',
          location: '小区活动中心'
        }
      ]
    });
  },

  // 刷新数据
  refreshData: function() {
    this.loadNotices();
    this.loadActiveVotes();
    this.loadUpcomingMeetings();
  },

  // 下拉刷新
  onPullDownRefresh: function() {
    this.refreshData();
    wx.stopPullDownRefresh();
  },

  // 跳转到公告详情
  goToNoticeDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/notice/detail?id=${id}`
    });
  },

  // 跳转到投票详情
  goToVoteDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/vote/detail?id=${id}`
    });
  },

  // 跳转到会议详情
  goToMeetingDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/meeting/detail?id=${id}`
    });
  },

  // 去认证
  goToAuth: function() {
    wx.navigateTo({
      url: '/pages/auth/auth'
    });
  }
})

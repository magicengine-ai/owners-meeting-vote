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
    this.refreshData();
  },

  loadUserInfo: function() {
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({ userInfo });
    }
  },

  loadNotices: function() {
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

  loadActiveVotes: function() {
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

  loadUpcomingMeetings: function() {
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

  refreshData: function() {
    this.loadNotices();
    this.loadActiveVotes();
    this.loadUpcomingMeetings();
  },

  onPullDownRefresh: function() {
    this.refreshData();
    wx.stopPullDownRefresh();
  },

  goToNoticeList: function() {
    wx.showToast({ title: '功能开发中', icon: 'none' });
  },

  goToNoticeDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.showToast({ title: '功能开发中', icon: 'none' });
  },

  goToVoteList: function() {
    wx.switchTab({
      url: '/pages/vote/list/list'
    });
  },

  goToVoteDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: '/pages/vote/detail/detail?vote_id=' + id
    });
  },

  goToMeetingList: function() {
    wx.switchTab({
      url: '/pages/meeting/list/list'
    });
  },

  goToMeetingDetail: function(e) {
    wx.showToast({ title: '功能开发中', icon: 'none' });
  },

  goToAuth: function() {
    wx.navigateTo({
      url: '/pages/auth/login/login'
    });
  }
})

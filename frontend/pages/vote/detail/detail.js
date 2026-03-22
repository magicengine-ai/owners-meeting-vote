// pages/vote/detail/detail.js
const { get, post } = require('../../../utils/request.js')

// 开发环境：使用模拟数据
const USE_MOCK_DATA = true

const MOCK_VOTE_DETAIL = {
  id: 1,
  title: '关于聘请新物业公司的投票',
  description: '本小区现有物业服务合同即将到期，经业委会研究，拟聘请新的物业公司提供服务。请各位业主参与投票。',
  status: 'active',
  start_time: 1710921600,
  end_time: 1711785600,
  total_votes: 156,
  has_voted: false,
  vote_type: 'single',
  min_votes: 1,
  max_votes: 1,
  options: ['同意', '反对', '弃权'],
  total_households: 500
}

const MOCK_VOTE_RESULT = {
  results: [
    { option: '同意', count: 120, percentage: 0.77 },
    { option: '反对', count: 25, percentage: 0.16 },
    { option: '弃权', count: 11, percentage: 0.07 }
  ],
  total_votes: 156,
  passed: true
}

Page({
  data: {
    voteId: '',
    voteDetail: null,
    selectedOptions: [],
    canSubmit: false,
    showResult: false,
    voteResults: null
  },

  onLoad(options) {
    const voteId = options.vote_id
    this.setData({ voteId })
    this.loadVoteDetail()
  },

  async loadVoteDetail() {
    const { voteId } = this.data
    
    if (USE_MOCK_DATA) {
      // 使用模拟数据
      const res = MOCK_VOTE_DETAIL
      this.setData({
        voteDetail: {
          ...res,
          statusText: res.status === 'active' ? '进行中' : '已结束',
          startTimeText: res.start_time ? this.formatDate(res.start_time) : '',
          endTimeText: res.end_time ? this.formatDate(res.end_time) : '',
          totalVotes: res.total_votes || 0,
          hasVoted: res.has_voted || false,
          options: res.options || []
        },
        showResult: res.has_voted || res.status !== 'active'
      })
      return
    }
    
    try {
      const res = await get(`/api/vote/detail/${voteId}`)
      this.setData({
        voteDetail: {
          ...res,
          statusText: res.status === 'active' ? '进行中' : '已结束',
          startTimeText: res.start_time ? this.formatDate(res.start_time) : '',
          endTimeText: res.end_time ? this.formatDate(res.end_time) : '',
          totalVotes: res.total_votes || 0,
          hasVoted: res.has_voted || false,
          options: res.options || []
        },
        showResult: res.has_voted || res.status !== 'active'
      })
      if (res.has_voted || res.status !== 'active') {
        this.loadVoteResult()
      }
    } catch (error) {
      console.error('加载投票详情失败:', error)
      wx.showToast({ title: error.message || '加载失败', icon: 'none' })
    }
  },

  async loadVoteResult() {
    if (USE_MOCK_DATA) {
      const res = MOCK_VOTE_RESULT
      const voteResults = res.results.map(item => ({
        ...item,
        percentageText: (item.percentage * 100).toFixed(1)
      }))
      this.setData({ voteResults })
      return
    }
    
    try {
      const res = await get(`/api/vote/result/${this.data.voteId}`)
      const voteResults = res.results.map(item => ({
        ...item,
        percentageText: (item.percentage * 100).toFixed(1)
      }))
      this.setData({ voteResults })
    } catch (error) {
      console.error('加载投票结果失败:', error)
    }
  },

  formatDate(timestamp) {
    const date = new Date(timestamp * 1000)
    return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${date.getMinutes()}`
  },

  toggleOption(e) {
    const { selectedOptions } = this.data
    const { option } = e.currentTarget.dataset
    const index = selectedOptions.indexOf(option)
    if (index > -1) {
      selectedOptions.splice(index, 1)
    } else {
      const { voteDetail } = this.data
      if (voteDetail.max_votes && selectedOptions.length >= voteDetail.max_votes) {
        wx.showToast({ title: `最多选择${voteDetail.max_votes}项`, icon: 'none' })
        return
      }
      selectedOptions.push(option)
    }
    const canSubmit = selectedOptions.length >= voteDetail.min_votes && selectedOptions.length <= voteDetail.max_votes
    this.setData({ selectedOptions, canSubmit })
  },

  async submitVote() {
    const { voteId, selectedOptions } = this.data
    wx.showModal({
      title: '确认投票',
      content: `确定要提交您的投票吗？\n\n您选择了：${selectedOptions.join('、')}`,
      success: async (res) => {
        if (res.confirm) {
          if (USE_MOCK_DATA) {
            wx.showToast({ title: '投票成功（模拟）', icon: 'success' })
            this.setData({ showResult: true })
            this.loadVoteResult()
            return
          }
          
          try {
            await post(`/api/vote/${voteId}/submit`, { options: selectedOptions })
            wx.showToast({ title: '投票成功', icon: 'success' })
            this.setData({ showResult: true })
            this.loadVoteResult()
          } catch (error) {
            wx.showToast({ title: error.message || '投票失败', icon: 'none' })
          }
        }
      }
    })
  },

  viewResult() {
    this.setData({ showResult: true })
  },

  assignProxy() {
    wx.showToast({ title: '功能开发中', icon: 'none' })
  }
})

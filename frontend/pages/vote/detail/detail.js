// pages/vote/detail/detail.js
const { get, post } = require('../../../utils/request.js')

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
    try {
      const res = await get(`/api/vote/detail/${voteId}`)
      this.setData({
        voteDetail: {
          ...res,
          statusText: res.status === 'active' ? '杩涜涓? : '宸茬粨鏉?,
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
      console.error('鍔犺浇鎶曠エ璇︽儏澶辫触:', error)
      wx.showToast({ title: error.message || '鍔犺浇澶辫触', icon: 'none' })
    }
  },

  async loadVoteResult() {
    try {
      const res = await get(`/api/vote/result/${this.data.voteId}`)
      const voteResults = res.results.map(item => ({
        ...item,
        percentageText: (item.percentage * 100).toFixed(1)
      }))
      this.setData({ voteResults })
    } catch (error) {
      console.error('鍔犺浇鎶曠エ缁撴灉澶辫触:', error)
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
        wx.showToast({ title: `鏈€澶氶€夋嫨${voteDetail.max_votes}椤筦, icon: 'none' })
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
      title: '纭鎶曠エ',
      content: `纭畾瑕佹彁浜ゆ偍鐨勬姇绁ㄥ悧锛焅n\n鎮ㄩ€夋嫨浜嗭細${selectedOptions.join('銆?)}`,
      success: async (res) => {
        if (res.confirm) {
          try {
            await post(`/api/vote/${voteId}/submit`, { options: selectedOptions })
            wx.showToast({ title: '鎶曠エ鎴愬姛', icon: 'success' })
            this.setData({ showResult: true })
            this.loadVoteResult()
          } catch (error) {
            wx.showToast({ title: error.message || '鎶曠エ澶辫触', icon: 'none' })
          }
        }
      }
    })
  },

  viewResult() {
    this.setData({ showResult: true })
  },

  assignProxy() {
    wx.showToast({ title: '鍔熻兘寮€鍙戜腑', icon: 'none' })
  }
})

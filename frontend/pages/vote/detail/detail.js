// pages/vote/detail/detail.js
const { get, post } = require('../../../../utils/request.js')

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
    this.setData({ voteId: voteId })
    this.loadVoteDetail()
  },

  /**
   * 加载投票详情
   */
  async loadVoteDetail() {
    const { voteId } = this.data
    
    try {
      const res = await get(`/api/vote/detail/${voteId}`)
      
      this.setData({
        voteDetail: res,
        showResult: res.has_voted || res.status !== 'active'
      })
      
      // 如果已投票或已结束，加载结果
      if (res.has_voted || res.status !== 'active') {
        this.loadVoteResult()
      }
    } catch (error) {
      console.error('加载投票详情失败:', error)
      wx.showToast({
        title: error.message || '加载失败',
        icon: 'none'
      })
    }
  },

  /**
   * 加载投票结果
   */
  async loadVoteResult() {
    const { voteId } = this.data
    
    try {
      const res = await get(`/api/vote/result/${voteId}`)
      this.setData({
        voteResults: res
      })
    } catch (error) {
      console.error('加载投票结果失败:', error)
    }
  },

  /**
   * 切换选项
   */
  toggleOption(e) {
    const option = e.currentTarget.dataset.option
    const { selectedOptions, voteDetail } = this.data
    
    const index = selectedOptions.indexOf(option)
    
    if (index > -1) {
      // 取消选择
      selectedOptions.splice(index, 1)
    } else {
      // 选择
      if (voteDetail.vote_type === 'single') {
        // 单选
        selectedOptions = [option]
      } else {
        // 多选
        if (selectedOptions.length >= voteDetail.max_votes) {
          wx.showToast({
            title: `最多选择${voteDetail.max_votes}项`,
            icon: 'none'
          })
          return
        }
        selectedOptions.push(option)
      }
    }
    
    // 检查是否可以提交
    const canSubmit = selectedOptions.length >= voteDetail.min_votes && 
                      selectedOptions.length <= voteDetail.max_votes
    
    this.setData({
      selectedOptions,
      canSubmit
    })
  },

  /**
   * 提交投票
   */
  async submitVote() {
    const { voteId, selectedOptions } = this.data
    
    wx.showModal({
      title: '确认投票',
      content: `确定要提交您的投票吗？\n\n您选择了：${selectedOptions.join('、')}`,
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '提交中...' })
            
            await post('/api/vote/submit', {
              vote_id: voteId,
              options: selectedOptions
            })
            
            wx.hideLoading()
            
            wx.showToast({
              title: '投票成功',
              icon: 'success'
            })
            
            // 刷新详情
            this.setData({
              selectedOptions: [],
              canSubmit: false
            })
            this.loadVoteDetail()
            
          } catch (error) {
            wx.hideLoading()
            console.error('投票失败:', error)
            wx.showToast({
              title: error.message || '投票失败',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  /**
   * 查看结果
   */
  viewResult() {
    this.setData({
      showResult: true
    })
    this.loadVoteResult()
  },

  /**
   * 设置委托人
   */
  assignProxy() {
    wx.showModal({
      title: '委托投票',
      content: '请选择您要委托的业主（功能开发中）',
      showCancel: false,
      confirmText: '我知道了'
    })
  }
})

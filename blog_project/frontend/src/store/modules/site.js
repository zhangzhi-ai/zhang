import axios from 'axios'

const state = {
  config: {
    site_name: '个人博客系统',
    site_description: '专注于个人生活内容分享的博客系统',
    site_keywords: 'Python,Django,Vue.js,Web开发',
    allow_register: true,
    comment_need_audit: false
  },
  statistics: {
    article_count: 0,
    user_count: 0,
    comment_count: 0,
    category_count: 0,
    tag_count: 0
  }
}

const mutations = {
  SET_SITE_CONFIG(state, config) {
    state.config = { ...state.config, ...config }
  },
  SET_STATISTICS(state, statistics) {
    state.statistics = statistics
  }
}

const actions = {
  async getSiteConfig({ commit }) {
    try {
      const response = await axios.get('/api/system/config/')
      commit('SET_SITE_CONFIG', response.data)
      return response.data
    } catch (error) {
      console.error('获取网站配置失败:', error)
    }
  },

  async getStatistics({ commit }) {
    try {
      const response = await axios.get('/api/blog/statistics/')
      commit('SET_STATISTICS', response.data)
      return response.data
    } catch (error) {
      console.error('获取统计信息失败:', error)
    }
  }
}

const getters = {
  siteConfig: state => state.config,
  statistics: state => state.statistics,
  siteName: state => state.config.site_name,
  siteDescription: state => state.config.site_description,
  allowRegister: state => state.config.allow_register
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
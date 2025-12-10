import axios from 'axios'

const state = {
  articles: [],
  currentArticle: null,
  categories: [],
  tags: [],
  loading: false,
  pagination: {
    current: 1,
    total: 0,
    pageSize: 10
  }
}

const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ARTICLES(state, { results, count, current = 1 }) {
    state.articles = results
    state.pagination.total = count
    state.pagination.current = current
  },
  SET_CURRENT_ARTICLE(state, article) {
    state.currentArticle = article
  },
  SET_CATEGORIES(state, categories) {
    state.categories = categories
  },
  SET_TAGS(state, tags) {
    state.tags = tags
  },
  UPDATE_ARTICLE_LIKE(state, { articleId, isLiked, likeCount }) {
    if (state.currentArticle && state.currentArticle.id === articleId) {
      state.currentArticle.like_count = likeCount
    }
    const article = state.articles.find(a => a.id === articleId)
    if (article) {
      article.like_count = likeCount
    }
  }
}

const actions = {
  async fetchArticles({ commit }, params = {}) {
    commit('SET_LOADING', true)
    try {
      const response = await axios.get('/api/blog/articles/', { params })
      commit('SET_ARTICLES', {
        results: response.data.results,
        count: response.data.count,
        current: params.page || 1
      })
      return response.data
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchArticleDetail({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      const response = await axios.get(`/api/blog/articles/${id}/`)
      commit('SET_CURRENT_ARTICLE', response.data)
      return response.data
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchCategories({ commit }) {
    try {
      const response = await axios.get('/api/blog/categories/')
      commit('SET_CATEGORIES', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async fetchTags({ commit }) {
    try {
      const response = await axios.get('/api/blog/tags/')
      commit('SET_TAGS', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async createArticle(_, articleData) {
    try {
      const response = await axios.post('/api/blog/articles/create/', articleData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async updateArticle(_, { id, articleData }) {
    try {
      const response = await axios.patch(`/api/blog/articles/${id}/update/`, articleData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async deleteArticle(_, id) {
    try {
      const response = await axios.delete(`/api/blog/articles/${id}/delete/`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async likeArticle({ commit }, articleId) {
    try {
      const response = await axios.post(`/api/blog/articles/${articleId}/like/`)
      commit('UPDATE_ARTICLE_LIKE', {
        articleId,
        isLiked: response.data.is_liked,
        likeCount: response.data.like_count
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  async fetchRecommendArticles() {
    try {
      const response = await axios.get('/api/blog/articles/recommend/')
      return response.data
    } catch (error) {
      throw error
    }
  },

  async fetchHotArticles() {
    try {
      const response = await axios.get('/api/blog/articles/hot/')
      return response.data
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  articles: state => state.articles,
  currentArticle: state => state.currentArticle,
  categories: state => state.categories,
  tags: state => state.tags,
  loading: state => state.loading,
  pagination: state => state.pagination
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
import axios from 'axios'

const state = {
  currentUser: null,
  isAuthenticated: false
}

const mutations = {
  SET_USER(state, user) {
    state.currentUser = user
    state.isAuthenticated = !!user
  },
  CLEAR_USER(state) {
    state.currentUser = null
    state.isAuthenticated = false
  }
}

const actions = {
  async login({ commit }, credentials) {
    try {
      const response = await axios.post('/api/users/login/', credentials)
      commit('SET_USER', response.data.user)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async register({ commit }, userData) {
    try {
      const response = await axios.post('/api/users/register/', userData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async logout({ commit }) {
    try {
      await axios.post('/api/users/logout/')
    } catch (error) {
      // 即使请求失败也要清除本地状态
    } finally {
      commit('CLEAR_USER')
    }
  },

  async getCurrentUser({ commit }) {
    try {
      const response = await axios.get('/api/users/current/')
      commit('SET_USER', response.data)
      return response.data
    } catch (error) {
      commit('CLEAR_USER')
      return null
    }
  },

  async updateProfile({ commit }, profileData) {
    try {
      const response = await axios.patch('/api/users/profile/', profileData)
      commit('SET_USER', response.data)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async changePassword(_, passwordData) {
    try {
      const response = await axios.post('/api/users/change-password/', passwordData)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  currentUser: state => state.currentUser,
  isAuthenticated: state => state.isAuthenticated,
  userId: state => state.currentUser?.id,
  username: state => state.currentUser?.username,
  displayName: state => state.currentUser?.nickname || state.currentUser?.username
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
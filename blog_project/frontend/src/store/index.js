import { createStore } from 'vuex'
import user from './modules/user'
import blog from './modules/blog'
import site from './modules/site'

export default createStore({
  modules: {
    user,
    blog,
    site
  }
})
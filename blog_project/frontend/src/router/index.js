import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/article/:id',
    name: 'ArticleDetail',
    component: () => import('../views/ArticleDetail.vue'),
    props: true
  },
  {
    path: '/category/:name',
    name: 'Category',
    component: () => import('../views/Category.vue'),
    props: true
  },
  {
    path: '/tag/:id',
    name: 'Tag',
    component: () => import('../views/Tag.vue'),
    props: true
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/user',
    name: 'UserCenter',
    component: () => import('../views/User/UserCenter.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/profile',
    name: 'UserProfile',
    component: () => import('../views/User/UserProfile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/articles',
    name: 'UserArticles',
    component: () => import('../views/User/UserArticles.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/comments',
    name: 'UserComments',
    component: () => import('../views/User/UserComments.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/write',
    name: 'WriteArticle',
    component: () => import('../views/WriteArticle.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit/:id',
    name: 'EditArticle',
    component: () => import('../views/EditArticle.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: () => import('../views/Admin/UserManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/categories',
    name: 'CategoryManage',
    component: () => import('../views/Admin/CategoryManage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

let isFetchingUser = false

router.beforeEach(async (to, from, next) => {
  // 检查是否需要登录
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters['user/isAuthenticated'] && !isFetchingUser) {
      isFetchingUser = true
      await store.dispatch('user/getCurrentUser')
      isFetchingUser = false
    }
    if (!store.getters['user/isAuthenticated']) {
      return next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  }
  
  // 检查是否需要管理员权限
  if (to.matched.some(record => record.meta.requiresAdmin)) {
    const user = store.getters['user/currentUser']
    if (!user || !user.is_staff) {
      return next({
        path: '/',
        query: { error: '您没有权限访问此页面' }
      })
    }
  }
  
  next()
})

export default router
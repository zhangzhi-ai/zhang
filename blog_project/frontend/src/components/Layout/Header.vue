<template>
  <header class="header">
    <div class="container">
      <div class="header-content">
        <div class="logo">
          <router-link to="/" class="logo-link">
            <h1>{{ siteName }}</h1>
          </router-link>
        </div>
        
        <nav class="nav">
          <router-link to="/" class="nav-link">首页</router-link>
          <el-dropdown @command="handleCategoryCommand">
            <span class="nav-link dropdown-link">
              分类 <el-icon><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item 
                  v-for="category in categories" 
                  :key="category.id"
                  :command="category.name"
                >
                  {{ category.name }} ({{ category.article_count }})
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </nav>
        
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索文章..."
            @keyup.enter="handleSearch"
            class="search-input"
          >
            <template #append>
              <el-button @click="handleSearch" :icon="Search" />
            </template>
          </el-input>
        </div>
        
        <div class="user-menu">
          <template v-if="isAuthenticated">
            <el-dropdown @command="handleUserCommand">
              <span class="user-info">
                <el-avatar :size="32" :src="currentUser.avatar" />
                <span class="username">{{ displayName }}</span>
                <el-icon><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="center">个人中心</el-dropdown-item>
                  <el-dropdown-item command="write">写文章</el-dropdown-item>
                  <el-dropdown-item command="articles">我的文章</el-dropdown-item>
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item 
                    v-if="currentUser && currentUser.is_staff" 
                    divided 
                    command="userManage"
                  >
                    用户管理
                  </el-dropdown-item>
                  <el-dropdown-item 
                    v-if="currentUser && currentUser.is_staff" 
                    command="categoryManage"
                  >
                    分类管理
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <router-link to="/login" class="auth-link">登录</router-link>
            <router-link to="/register" class="auth-link" v-if="allowRegister">注册</router-link>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { Search, ArrowDown } from '@element-plus/icons-vue'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Header',
  components: {
    Search,
    ArrowDown
  },
  data() {
    return {
      searchKeyword: ''
    }
  },
  computed: {
    ...mapGetters('user', ['currentUser', 'isAuthenticated', 'displayName']),
    ...mapGetters('blog', ['categories']),
    ...mapGetters('site', ['siteName', 'allowRegister'])
  },
  async created() {
    await this.fetchCategories()
  },
  methods: {
    ...mapActions('user', ['logout']),
    ...mapActions('blog', ['fetchCategories']),
    
    handleSearch() {
      if (this.searchKeyword.trim()) {
        this.$router.push({
          name: 'Search',
          query: { keyword: this.searchKeyword.trim() }
        })
      }
    },
    
    handleCategoryCommand(categoryName) {
      this.$router.push({
        name: 'Category',
        params: { name: categoryName }
      })
    },
    
    async handleUserCommand(command) {
      switch (command) {
        case 'center':
          this.$router.push('/user')
          break
        case 'write':
          this.$router.push('/write')
          break
        case 'articles':
          this.$router.push('/user/articles')
          break
        case 'profile':
          this.$router.push('/user/profile')
          break
        case 'userManage':
          this.$router.push('/admin/users')
          break
        case 'categoryManage':
          this.$router.push('/admin/categories')
          break
        case 'logout':
          await this.logout()
          this.$message.success('退出登录成功')
          this.$router.push('/')
          break
      }
    }
  }
}
</script>

<style scoped>
.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.logo-link {
  text-decoration: none;
  color: #409eff;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.nav {
  display: flex;
  align-items: center;
  gap: 30px;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #409eff;
}

.dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-box {
  flex: 1;
  max-width: 300px;
  margin: 0 30px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-weight: 500;
}

.auth-link {
  text-decoration: none;
  color: #409eff;
  font-weight: 500;
  padding: 8px 16px;
  border: 1px solid #409eff;
  border-radius: 4px;
  transition: all 0.3s;
}

.auth-link:hover {
  background-color: #409eff;
  color: white;
}

@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    height: auto;
    padding: 10px 20px;
  }
  
  .search-box {
    order: 3;
    flex-basis: 100%;
    margin: 10px 0 0 0;
    max-width: none;
  }
  
  .nav {
    gap: 15px;
  }
}
</style>
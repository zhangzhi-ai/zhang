<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-info">
          <h3>{{ siteName }}</h3>
          <p>{{ siteDescription }}</p>
        </div>
        
        <div class="footer-stats">
          <div class="stat-item">
            <span class="stat-number">{{ statistics.article_count }}</span>
            <span class="stat-label">文章</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ statistics.user_count }}</span>
            <span class="stat-label">用户</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ statistics.comment_count }}</span>
            <span class="stat-label">评论</span>
          </div>
        </div>
        
        <div class="footer-links">
          <router-link to="/" class="footer-link">首页</router-link>
          <router-link to="/write" class="footer-link" v-if="isAuthenticated">写文章</router-link>
          <a href="#" class="footer-link">关于</a>
          <a href="#" class="footer-link">联系</a>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; {{ currentYear }} {{ siteName }}. All rights reserved.</p>
        <p>专注于技术分享与内容创作的博客平台</p>
      </div>
    </div>
  </footer>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Footer',
  computed: {
    ...mapGetters('site', ['siteName', 'siteDescription', 'statistics']),
    ...mapGetters('user', ['isAuthenticated']),
    currentYear() {
      return new Date().getFullYear()
    }
  },
  async created() {
    await this.getStatistics()
  },
  methods: {
    ...mapActions('site', ['getStatistics'])
  }
}
</script>

<style scoped>
.footer {
  background: #2c3e50;
  color: white;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 40px;
  padding: 40px 0;
}

.footer-info h3 {
  margin-bottom: 10px;
  color: #409eff;
}

.footer-info p {
  color: #bdc3c7;
  line-height: 1.6;
}

.footer-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  min-width: 40px;
}

.stat-label {
  color: #bdc3c7;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.footer-link {
  color: #bdc3c7;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-link:hover {
  color: #409eff;
}

.footer-bottom {
  border-top: 1px solid #34495e;
  padding: 20px 0;
  text-align: center;
  color: #95a5a6;
}

.footer-bottom p {
  margin: 5px 0;
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: 30px;
    text-align: center;
  }
  
  .footer-stats {
    flex-direction: row;
    justify-content: center;
    gap: 30px;
  }
  
  .stat-item {
    flex-direction: column;
    gap: 5px;
  }
  
  .footer-links {
    flex-direction: row;
    justify-content: center;
    gap: 20px;
  }
}
</style>
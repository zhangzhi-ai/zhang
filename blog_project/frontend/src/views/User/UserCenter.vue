<template>
  <div class="user-dashboard">
    <div class="container" v-loading="loading">
      <el-card class="profile-card" v-if="user">
        <div class="profile-info">
          <el-avatar :size="80" :src="user.avatar" />
          <div class="profile-text">
            <h2>{{ user.nickname || user.username }}</h2>
            <p>{{ user.bio || '这个人很神秘，还没有填写个人简介~' }}</p>
            <div class="profile-meta">
              <el-tag type="success" v-if="user.is_staff">管理员</el-tag>
              <span>加入时间：{{ formatDate(user.date_joined) }}</span>
            </div>
          </div>
          <el-button type="primary" @click="$router.push('/user/profile')">编辑资料</el-button>
        </div>
      </el-card>

      <el-empty v-else description="未获取到用户信息" />

      <div class="stats-grid" v-if="statistics">
        <el-card>
          <div class="stat-number">{{ statistics.article_count }}</div>
          <div class="stat-label">文章</div>
        </el-card>
        <el-card>
          <div class="stat-number">{{ statistics.comment_count }}</div>
          <div class="stat-label">评论</div>
        </el-card>
        <el-card>
          <div class="stat-number">{{ statistics.user_count }}</div>
          <div class="stat-label">用户</div>
        </el-card>
        <el-card>
          <div class="stat-number">{{ statistics.tag_count }}</div>
          <div class="stat-label">标签</div>
        </el-card>
      </div>

      <div class="actions-grid">
        <el-card class="action-card" @click="$router.push('/write')">
          <h3>写文章</h3>
          <p>记录你的技术灵感</p>
          <el-button type="primary" text>立即前往</el-button>
        </el-card>
        <el-card class="action-card" @click="$router.push('/user/articles')">
          <h3>我的文章</h3>
          <p>管理你发布的内容</p>
          <el-button type="primary" text>查看列表</el-button>
        </el-card>
        <el-card class="action-card" @click="$router.push('/user/comments')">
          <h3>我的评论</h3>
          <p>查看历史互动</p>
          <el-button type="primary" text>立即查看</el-button>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()
const loading = ref(false)
const user = computed(() => store.getters['user/currentUser'])
const statistics = computed(() => store.getters['site/statistics'])

const loadData = async () => {
  loading.value = true
  await Promise.all([
    store.dispatch('user/getCurrentUser'),
    store.dispatch('site/getStatistics')
  ])
  loading.value = false
}

const formatDate = (value) => {
  if (!value) return '未知'
  return new Date(value).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.user-dashboard {
  padding: 24px 0;
}

.profile-card {
  margin-bottom: 24px;
}

.profile-info {
  display: flex;
  gap: 20px;
  align-items: center;
}

.profile-text h2 {
  margin: 0 0 8px;
}

.profile-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  color: #909399;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  color: #909399;
  margin-top: 8px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.action-card {
  cursor: pointer;
}

.action-card h3 {
  margin: 0 0 8px;
}
</style>

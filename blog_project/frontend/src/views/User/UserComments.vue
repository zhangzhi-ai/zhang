<template>
  <div class="user-comments-page">
    <div class="container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>我的评论</span>
          </div>
        </template>

        <el-timeline v-if="comments.length" v-loading="loading">
          <el-timeline-item
            v-for="comment in comments"
            :key="comment.id"
            :timestamp="formatDate(comment.created_at)"
          >
            <div class="comment-item">
              <div class="comment-article">
                于
                <router-link :to="`/article/${comment.article.id}`">
                  《{{ comment.article.title }}》
                </router-link>
                中留言：
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              <div class="comment-meta">
                <span>点赞 {{ comment.like_count }}</span>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>

        <el-empty v-if="!comments.length && !loading" description="还没有发表过评论" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const comments = ref([])
const loading = ref(false)

const fetchComments = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/comments/my/')
    comments.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('加载评论失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (value) => {
  if (!value) return ''
  return new Date(value).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.user-comments-page {
  padding: 24px 0;
}

.comment-item {
  border: 1px solid #f0f2f5;
  padding: 12px 16px;
  border-radius: 8px;
  background: #fafafa;
}

.comment-article {
  margin-bottom: 8px;
  color: #909399;
}

.comment-content {
  font-size: 15px;
  margin-bottom: 8px;
}

.comment-meta {
  font-size: 12px;
  color: #909399;
}
</style>


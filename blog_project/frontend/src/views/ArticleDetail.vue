<template>
  <div class="article-detail">
    <div class="container">
      <div class="content-wrapper" v-loading="loading">
        <article class="article-main card" v-if="article">
          <!-- 文章封面 -->
          <div class="article-cover" v-if="article.cover_image">
            <img :src="article.cover_image" :alt="article.title" />
          </div>
          
          <!-- 文章头部 -->
          <header class="article-header">
            <h1 class="article-title">{{ article.title }}</h1>
            
            <div class="article-meta">
              <div class="meta-left">
                <el-avatar :size="40" :src="article.author?.avatar" />
                <div class="author-info">
                  <div class="author-name">{{ article.author?.nickname || article.author?.username }}</div>
                  <div class="publish-time">{{ formatDate(article.published_at) }}</div>
                </div>
              </div>
              
              <div class="meta-right">
                <span class="meta-item">
                  <el-icon><View /></el-icon>
                  {{ article.view_count }}
                </span>
                <span class="meta-item">
                  <el-icon><Star /></el-icon>
                  {{ article.like_count }}
                </span>
                <span class="meta-item">
                  <el-icon><ChatDotRound /></el-icon>
                  {{ article.comment_count }}
                </span>
              </div>
            </div>
            
            <div class="article-tags" v-if="article.tags && article.tags.length">
              <el-tag
                v-for="tag in article.tags"
                :key="tag.id"
                :color="tag.color"
                size="small"
                class="tag"
              >
                {{ tag.name }}
              </el-tag>
            </div>
          </header>
          
          <!-- 文章内容 -->
          <div class="article-content" v-html="article.content"></div>
          
          <!-- 文章操作 -->
          <div class="article-actions">
            <el-button
              type="primary"
              :icon="isLiked ? StarFilled : Star"
              @click="handleLike"
              :disabled="!isAuthenticated"
            >
              {{ isLiked ? '已点赞' : '点赞' }} ({{ article.like_count }})
            </el-button>
          </div>
        </article>
        
        <!-- 评论区 -->
        <div class="comments-section card">
          <h2 class="section-title">评论 ({{ comments.length }})</h2>
          
          <!-- 发表评论 -->
          <div class="comment-form" v-if="isAuthenticated">
            <el-input
              v-model="commentContent"
              type="textarea"
              :rows="4"
              placeholder="写下你的评论..."
              maxlength="500"
              show-word-limit
            />
            <div class="form-actions">
              <el-button type="primary" @click="submitComment" :loading="submitting">
                发表评论
              </el-button>
            </div>
          </div>
          
          <div class="login-tip" v-else>
            <el-alert
              title="请先登录后再发表评论"
              type="info"
              :closable="false"
            >
              <template #default>
                <router-link to="/login" class="login-link">立即登录</router-link>
              </template>
            </el-alert>
          </div>
          
          <!-- 评论列表 -->
          <div class="comments-list" v-loading="loadingComments">
            <div v-if="comments.length === 0" class="no-comments">
              暂无评论，快来发表第一条评论吧！
            </div>
            
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <el-avatar :size="40" :src="comment.user?.avatar" />
              <div class="comment-content">
                <div class="comment-header">
                  <span class="username">{{ comment.user?.nickname || comment.user?.username }}</span>
                  <span class="time">{{ formatDate(comment.created_at) }}</span>
                </div>
                <div class="comment-text">{{ comment.content }}</div>
                <div class="comment-actions">
                  <el-button
                    text
                    size="small"
                    @click="handleCommentLike(comment)"
                    :disabled="!isAuthenticated"
                  >
                    <el-icon><Star /></el-icon>
                    {{ comment.like_count }}
                  </el-button>
                  <el-button text size="small" @click="replyTo(comment)">
                    回复
                  </el-button>
                </div>
                
                <!-- 回复列表 -->
                <div v-if="comment.replies && comment.replies.length" class="replies">
                  <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                    <el-avatar :size="32" :src="reply.user?.avatar" />
                    <div class="reply-content">
                      <div class="reply-header">
                        <span class="username">{{ reply.user?.nickname || reply.user?.username }}</span>
                        <span class="time">{{ formatDate(reply.created_at) }}</span>
                      </div>
                      <div class="reply-text">{{ reply.content }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { View, Star, StarFilled, ChatDotRound } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'ArticleDetail',
  components: {
    View, Star, StarFilled, ChatDotRound
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    
    const loading = ref(false)
    const loadingComments = ref(false)
    const submitting = ref(false)
    const article = ref(null)
    const comments = ref([])
    const commentContent = ref('')
    const isLiked = ref(false)
    const replyToComment = ref(null)
    
    const isAuthenticated = computed(() => store.getters['user/isAuthenticated'])
    
    // 加载文章详情
    const loadArticle = async () => {
      loading.value = true
      try {
        const response = await axios.get(`/api/blog/articles/${route.params.id}/`)
        article.value = response.data
      } catch (error) {
        ElMessage.error('加载文章失败')
        router.push('/')
      } finally {
        loading.value = false
      }
    }
    
    // 加载评论
    const loadComments = async () => {
      loadingComments.value = true
      try {
        const response = await axios.get(`/api/comments/articles/${route.params.id}/`)
        comments.value = response.data.results || response.data
      } catch (error) {
        console.error('加载评论失败:', error)
      } finally {
        loadingComments.value = false
      }
    }
    
    // 点赞文章
    const handleLike = async () => {
      if (!isAuthenticated.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      try {
        const response = await axios.post(`/api/blog/articles/${article.value.id}/like/`)
        article.value.like_count = response.data.like_count
        isLiked.value = response.data.is_liked
        ElMessage.success(response.data.message)
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
    
    // 发表评论
    const submitComment = async () => {
      if (!commentContent.value.trim()) {
        ElMessage.warning('请输入评论内容')
        return
      }
      
      submitting.value = true
      try {
        const data = {
          content: commentContent.value,
          parent: replyToComment.value?.id || null
        }
        
        await axios.post(`/api/comments/articles/${route.params.id}/create/`, data)
        ElMessage.success('评论发表成功')
        commentContent.value = ''
        replyToComment.value = null
        loadComments()
        
        // 更新文章评论数
        if (article.value) {
          article.value.comment_count += 1
        }
      } catch (error) {
        if (error.response?.data?.code === 'login_required') {
          ElMessage.warning(error.response.data.message)
          router.push('/login')
        } else {
          ElMessage.error('评论发表失败')
        }
      } finally {
        submitting.value = false
      }
    }
    
    // 回复评论
    const replyTo = (comment) => {
      replyToComment.value = comment
      commentContent.value = `@${comment.user?.nickname || comment.user?.username} `
    }
    
    // 点赞评论
    const handleCommentLike = async (comment) => {
      if (!isAuthenticated.value) {
        ElMessage.warning('请先登录')
        return
      }
      
      try {
        const response = await axios.post(`/api/comments/${comment.id}/like/`)
        comment.like_count = response.data.like_count
        ElMessage.success(response.data.message)
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    onMounted(() => {
      loadArticle()
      loadComments()
    })
    
    return {
      loading,
      loadingComments,
      submitting,
      article,
      comments,
      commentContent,
      isLiked,
      isAuthenticated,
      handleLike,
      submitComment,
      replyTo,
      handleCommentLike,
      formatDate
    }
  }
}
</script>

<style scoped>
.article-detail {
  padding: 20px 0;
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 0;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.article-cover {
  width: 100%;
  height: 400px;
  overflow: hidden;
  background: #f5f5f5;
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.article-header {
  border-bottom: 1px solid #eee;
  padding: 30px 30px 20px;
  margin-bottom: 0;
}

.article-title {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.meta-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 500;
  color: #333;
}

.publish-time {
  font-size: 12px;
  color: #999;
}

.meta-right {
  display: flex;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 14px;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  cursor: pointer;
}

.article-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 30px;
  padding: 0 30px;
}

.article-content >>> h2 {
  font-size: 24px;
  margin: 30px 0 15px;
  color: #333;
}

.article-content >>> p {
  margin-bottom: 15px;
}

.article-actions {
  text-align: center;
  padding: 20px 30px;
  border-top: 1px solid #eee;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.comment-form {
  margin-bottom: 30px;
}

.form-actions {
  margin-top: 10px;
  text-align: right;
}

.login-tip {
  margin-bottom: 30px;
}

.login-link {
  color: #409eff;
  text-decoration: none;
  margin-left: 10px;
}

.login-link:hover {
  text-decoration: underline;
}

.no-comments {
  text-align: center;
  padding: 40px;
  color: #999;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.username {
  font-weight: 500;
  color: #333;
}

.time {
  font-size: 12px;
  color: #999;
}

.comment-text {
  color: #666;
  line-height: 1.6;
  margin-bottom: 10px;
}

.comment-actions {
  display: flex;
  gap: 10px;
}

.replies {
  margin-top: 15px;
  padding-left: 20px;
  border-left: 2px solid #f0f0f0;
}

.reply-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
}

.reply-content {
  flex: 1;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.reply-text {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .card {
    padding: 20px;
  }
  
  .article-title {
    font-size: 24px;
  }
  
  .article-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>
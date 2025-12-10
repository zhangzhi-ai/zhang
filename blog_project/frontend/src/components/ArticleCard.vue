<template>
  <div class="article-card" @click="goToDetail">
    <div class="article-header" v-if="article.cover_image">
      <img :src="article.cover_image" :alt="article.title" class="cover-image" />
    </div>
    
    <div class="article-content">
      <div class="article-meta">
        <el-tag v-if="showRecommendBadge && article.is_recommend" type="danger" size="small">
          推荐
        </el-tag>
        <el-tag v-if="article.is_top" type="warning" size="small">
          置顶
        </el-tag>
        <span class="category">{{ article.category.name }}</span>
        <span class="author">{{ article.author.display_name || article.author.username }}</span>
        <span class="date">{{ formatDate(article.published_at) }}</span>
      </div>
      
      <h3 class="article-title">{{ article.title }}</h3>
      
      <p class="article-summary" v-if="article.summary">
        {{ article.summary }}
      </p>
      
      <div class="article-tags" v-if="article.tags && article.tags.length">
        <el-tag
          v-for="tag in article.tags"
          :key="tag.id"
          size="small"
          :color="tag.color"
          class="tag"
        >
          {{ tag.name }}
        </el-tag>
      </div>
      
      <div class="article-stats">
        <span class="stat-item">
          <el-icon><View /></el-icon>
          {{ article.view_count }}
        </span>
        <span class="stat-item">
          <el-icon><Star /></el-icon>
          {{ article.like_count }}
        </span>
        <span class="stat-item">
          <el-icon><ChatDotRound /></el-icon>
          {{ article.comment_count }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import { View, Star, ChatDotRound } from '@element-plus/icons-vue'

export default {
  name: 'ArticleCard',
  components: {
    View,
    Star,
    ChatDotRound
  },
  props: {
    article: {
      type: Object,
      required: true
    },
    showRecommendBadge: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    goToDetail() {
      this.$router.push(`/article/${this.article.id}`)
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.article-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.cover-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.article-content {
  padding: 20px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 12px;
  color: #999;
}

.category {
  background-color: #409eff;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
}

.article-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-summary {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-tags {
  margin-bottom: 15px;
}

.tag {
  margin-right: 8px;
  margin-bottom: 5px;
}

.article-stats {
  display: flex;
  align-items: center;
  gap: 20px;
  color: #999;
  font-size: 14px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
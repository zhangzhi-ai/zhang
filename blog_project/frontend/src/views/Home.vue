<template>
  <div class="home">
    <div class="container">
      <div class="home-content">
        <!-- 主要内容区域 -->
        <div class="main-content">
          <!-- 推荐文章 -->
          <section class="recommend-section" v-if="recommendArticles.length">
            <h2 class="section-title">推荐文章</h2>
            <div class="recommend-articles">
              <article-card 
                v-for="article in recommendArticles" 
                :key="article.id"
                :article="article"
                :show-recommend-badge="true"
              />
            </div>
          </section>
          
          <!-- 最新文章 -->
          <section class="articles-section">
            <div class="section-header">
              <h2 class="section-title">最新文章</h2>
              <div class="sort-options">
                <el-select v-model="sortBy" @change="handleSortChange" size="small">
                  <el-option label="发布时间" value="-published_at" />
                  <el-option label="浏览量" value="-view_count" />
                  <el-option label="点赞数" value="-like_count" />
                  <el-option label="评论数" value="-comment_count" />
                </el-select>
              </div>
            </div>
            
            <div class="articles-list" v-loading="loading">
              <article-card 
                v-for="article in articles" 
                :key="article.id"
                :article="article"
              />
            </div>
            
            <!-- 分页 -->
            <div class="pagination-wrapper" v-if="pagination.total > 0">
              <el-pagination
                v-model:current-page="pagination.current"
                :page-size="pagination.pageSize"
                :total="pagination.total"
                layout="prev, pager, next, jumper, total"
                @current-change="handlePageChange"
              />
            </div>
          </section>
        </div>
        
        <!-- 侧边栏 -->
        <aside class="sidebar">
          <!-- 热门文章 -->
          <div class="sidebar-widget">
            <h3 class="widget-title">热门文章</h3>
            <div class="hot-articles">
              <div 
                v-for="(article, index) in hotArticles" 
                :key="article.id"
                class="hot-article-item"
                @click="$router.push(`/article/${article.id}`)"
              >
                <span class="hot-rank" :class="`rank-${index + 1}`">{{ index + 1 }}</span>
                <div class="hot-article-info">
                  <h4 class="hot-article-title">{{ article.title }}</h4>
                  <div class="hot-article-meta">
                    <span>{{ article.view_count }} 浏览</span>
                    <span>{{ article.like_count }} 点赞</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 标签云 -->
          <div class="sidebar-widget">
            <h3 class="widget-title">标签云</h3>
            <div class="tag-cloud">
              <el-tag
                v-for="tag in tags"
                :key="tag.id"
                :color="tag.color"
                class="tag-item"
                @click="$router.push(`/tag/${tag.id}`)"
              >
                {{ tag.name }} ({{ tag.use_count }})
              </el-tag>
            </div>
          </div>
          
          <!-- 分类 -->
          <div class="sidebar-widget">
            <h3 class="widget-title">文章分类</h3>
            <div class="categories">
              <div 
                v-for="category in categories"
                :key="category.id"
                class="category-item"
                @click="$router.push(`/category/${category.name}`)"
              >
                <span class="category-name">{{ category.name }}</span>
                <span class="category-count">{{ category.article_count }}</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import ArticleCard from '../components/ArticleCard.vue'

export default {
  name: 'Home',
  components: {
    ArticleCard
  },
  data() {
    return {
      sortBy: '-published_at',
      recommendArticles: [],
      hotArticles: []
    }
  },
  computed: {
    ...mapGetters('blog', ['articles', 'categories', 'tags', 'loading', 'pagination'])
  },
  async created() {
    await this.loadData()
  },
  methods: {
    ...mapActions('blog', [
      'fetchArticles', 'fetchCategories', 'fetchTags', 
      'fetchRecommendArticles', 'fetchHotArticles'
    ]),
    
    async loadData() {
      try {
        // 并行加载数据
        await Promise.all([
          this.fetchArticles({ ordering: this.sortBy }),
          this.fetchCategories(),
          this.fetchTags(),
          this.loadRecommendArticles(),
          this.loadHotArticles()
        ])
      } catch (error) {
        this.$message.error('加载数据失败')
      }
    },
    
    async loadRecommendArticles() {
      try {
        this.recommendArticles = await this.fetchRecommendArticles()
      } catch (error) {
        console.error('加载推荐文章失败:', error)
      }
    },
    
    async loadHotArticles() {
      try {
        this.hotArticles = await this.fetchHotArticles()
      } catch (error) {
        console.error('加载热门文章失败:', error)
      }
    },
    
    async handleSortChange() {
      await this.fetchArticles({ 
        ordering: this.sortBy,
        page: 1 
      })
    },
    
    async handlePageChange(page) {
      await this.fetchArticles({ 
        ordering: this.sortBy,
        page 
      })
    }
  }
}
</script>

<style scoped>
.home-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 30px;
}

.section-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.recommend-section {
  margin-bottom: 40px;
}

.recommend-articles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-widget {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.widget-title {
  font-size: 18px;
  margin-bottom: 15px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.hot-article-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.hot-article-item:hover {
  background-color: #f8f9fa;
}

.hot-article-item:last-child {
  border-bottom: none;
}

.hot-rank {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
}

.rank-1 { background-color: #ff4757; }
.rank-2 { background-color: #ff6b7a; }
.rank-3 { background-color: #ffa502; }
.hot-rank:not(.rank-1):not(.rank-2):not(.rank-3) { 
  background-color: #95a5a6; 
}

.hot-article-info {
  flex: 1;
}

.hot-article-title {
  font-size: 14px;
  margin-bottom: 5px;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hot-article-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 10px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.tag-item:hover {
  transform: scale(1.05);
}

.categories {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.category-item:hover {
  background-color: #f0f9ff;
}

.category-name {
  color: #333;
}

.category-count {
  background-color: #409eff;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
}

@media (max-width: 768px) {
  .home-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .recommend-articles {
    grid-template-columns: 1fr;
  }
}
</style>
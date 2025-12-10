<template>
  <div class="list-page">
    <div class="container">
      <div class="search-header">
        <el-input
          v-model="keyword"
          placeholder="请输入关键字搜索文章"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
        <p class="tips">支持按标题、摘要、正文内容搜索</p>
      </div>

      <el-empty v-if="!keyword && !loading" description="请输入关键字开始搜索" />

      <div v-else v-loading="loading">
        <div class="result-info" v-if="keyword">
          找到 {{ pagination.total }} 条包含 “<strong>{{ keyword }}</strong>” 的文章
        </div>

        <div class="article-list">
          <article-card
            v-for="article in articles"
            :key="article.id"
            :article="article"
          />
        </div>

        <el-empty v-if="!loading && articles.length === 0 && keyword" description="未找到匹配的文章" />

        <div class="pagination-wrapper" v-if="pagination.total > pagination.pageSize">
          <el-pagination
            layout="prev, pager, next"
            :current-page="pagination.current"
            :page-size="pagination.pageSize"
            :total="pagination.total"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import ArticleCard from '../components/ArticleCard.vue'

const route = useRoute()
const router = useRouter()
const store = useStore()

const keyword = ref(route.query.keyword || '')
const loading = ref(false)
const articles = ref([])
const pagination = reactive({
  current: 1,
  total: 0,
  pageSize: 10
})

const fetchArticles = async (page = 1) => {
  if (!keyword.value.trim()) {
    articles.value = []
    pagination.total = 0
    return
  }
  loading.value = true
  try {
    const data = await store.dispatch('blog/fetchArticles', {
      keyword: keyword.value.trim(),
      ordering: '-published_at',
      page
    })
    articles.value = data.results
    pagination.total = data.count
    pagination.current = page
  } catch (error) {
    ElMessage.error('搜索失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  router.replace({
    name: 'Search',
    query: keyword.value ? { keyword: keyword.value.trim() } : {}
  })
}

const handlePageChange = (page) => {
  fetchArticles(page)
}

watch(
  () => route.query.keyword,
  (value) => {
    keyword.value = value || ''
    fetchArticles(1)
  },
  { immediate: true }
)
</script>

<style scoped>
.list-page {
  padding: 24px 0;
}

.search-header {
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.tips {
  margin-top: 12px;
  color: #909399;
  font-size: 13px;
}

.result-info {
  margin-bottom: 16px;
  color: #666;
}

.result-info strong {
  color: #409eff;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pagination-wrapper {
  margin: 30px auto 0;
  text-align: center;
}
</style>


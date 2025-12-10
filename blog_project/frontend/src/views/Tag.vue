<template>
  <div class="list-page">
    <div class="container">
      <div class="page-header" v-if="tag">
        <div>
          <h1>
            <el-tag :color="tag.color" effect="dark">{{ tag.name }}</el-tag>
          </h1>
          <p class="description">共 {{ tag.use_count }} 篇文章</p>
        </div>
      </div>

      <el-empty v-if="!tag && !loading" description="标签不存在" />

      <div v-loading="loading">
        <div class="article-list">
          <article-card
            v-for="article in articles"
            :key="article.id"
            :article="article"
          />
        </div>

        <el-empty v-if="!loading && articles.length === 0 && tag" description="该标签暂无文章" />

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
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import ArticleCard from '../components/ArticleCard.vue'

const store = useStore()
const route = useRoute()

const tag = ref(null)
const articles = ref([])
const loading = ref(false)
const pagination = reactive({
  current: 1,
  total: 0,
  pageSize: 10
})

const loadTag = async () => {
  loading.value = true
  try {
    await store.dispatch('blog/fetchTags')
    const list = store.getters['blog/tags']
    const tagId = Number(route.params.id)
    tag.value = list.find(item => item.id === tagId)
    if (!tag.value) {
      ElMessage.error('标签不存在')
      articles.value = []
      pagination.total = 0
      return
    }
    await fetchArticles(1)
  } catch (error) {
    ElMessage.error('加载标签失败')
  } finally {
    loading.value = false
  }
}

const fetchArticles = async (page = 1) => {
  if (!tag.value) return
  loading.value = true
  try {
    const data = await store.dispatch('blog/fetchArticles', {
      tag_id: tag.value.id,
      page,
      ordering: '-published_at'
    })
    articles.value = data.results
    pagination.total = data.count
    pagination.current = page
  } catch (error) {
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  fetchArticles(page)
}

watch(
  () => route.params.id,
  () => loadTag(),
  { immediate: true }
)
</script>

<style scoped>
.list-page {
  padding: 24px 0;
}

.page-header {
  margin-bottom: 24px;
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.description {
  color: #666;
  margin-top: 12px;
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

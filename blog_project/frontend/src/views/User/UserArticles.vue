<template>
  <div class="user-articles-page">
    <div class="container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>我的文章</span>
            <el-button type="primary" @click="$router.push('/write')">写文章</el-button>
          </div>
        </template>

        <el-table :data="articles" v-loading="loading">
          <el-table-column prop="title" label="标题" min-width="240">
            <template #default="{ row }">
              <div class="title-cell">
                <span class="main-title">{{ row.title }}</span>
                <div class="meta">
                  发布于：{{ formatDate(row.published_at) || '未发布' }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="category.name" label="分类" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'">
                {{ row.status === 1 ? '已发布' : '草稿' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="统计" width="160">
            <template #default="{ row }">
              浏览 {{ row.view_count }} / 点赞 {{ row.like_count }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text @click="viewArticle(row.id)">查看</el-button>
              <el-button size="small" text type="primary" @click="editArticle(row.id)">编辑</el-button>
              <el-button size="small" text type="danger" @click="removeArticle(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!articles.length && !loading" description="还没有写过文章" />
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const articles = ref([])
const loading = ref(false)
const router = useRouter()

const normalizeArticles = (payload) => {
  if (Array.isArray(payload)) return payload
  if (payload && Array.isArray(payload.results)) {
    return payload.results
  }
  return []
}

const fetchArticles = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/blog/articles/my/')
    articles.value = normalizeArticles(response.data)
  } catch (error) {
    articles.value = []
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

const viewArticle = (id) => {
  router.push(`/article/${id}`)
}

const editArticle = (id) => {
  router.push(`/edit/${id}`)
}

const removeArticle = (id) => {
  ElMessageBox.confirm('确定要删除这篇文章吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/blog/articles/${id}/delete/`)
      ElMessage.success('删除成功')
      fetchArticles()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const formatDate = (value) => {
  if (!value) return ''
  return new Date(value).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped>
.user-articles-page {
  padding: 24px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-cell .main-title {
  font-weight: 500;
}

.title-cell .meta {
  font-size: 12px;
  color: #909399;
}
</style>

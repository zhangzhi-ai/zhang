<template>
  <div class="editor-page">
    <div class="container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>撰写新文章</span>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">
              发布文章
            </el-button>
          </div>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="article-form"
        >
          <el-form-item label="标题" prop="title">
            <el-input v-model="form.title" maxlength="120" show-word-limit />
          </el-form-item>

          <el-form-item label="分类" prop="category">
            <el-select v-model="form.category" placeholder="请选择分类" filterable>
              <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="标签" prop="tag_names">
            <el-select
              v-model="form.tag_names"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="选择或输入标签，回车添加"
            >
              <el-option
                v-for="tag in tags"
                :key="tag.id"
                :label="tag.name"
                :value="tag.name"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="封面图">
            <div class="cover-upload">
              <el-upload
                :show-file-list="false"
                :http-request="handleCoverUpload"
                :before-upload="beforeCoverUpload"
              >
                <div class="cover-preview" :class="{ uploading: coverUploading }">
                  <img v-if="coverPreview" :src="coverPreview" alt="封面图" />
                  <div class="placeholder" v-else>上传封面</div>
                  <div class="upload-mask">点击上传</div>
                </div>
              </el-upload>
              <div class="cover-input">
                <el-input v-model="form.cover_image" placeholder="或输入封面图 URL" />
              </div>
            </div>
          </el-form-item>

          <el-form-item label="摘要" prop="summary">
            <el-input
              v-model="form.summary"
              type="textarea"
              :rows="3"
              maxlength="300"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="内容" prop="content">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="15"
              placeholder="支持 HTML / Markdown（根据后台渲染配置）"
            />
          </el-form-item>

          <div class="form-inline">
            <el-form-item label="发布状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio :value="1">发布</el-radio>
                <el-radio :value="0">草稿</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="置顶">
              <el-switch v-model="form.is_top" />
            </el-form-item>

            <el-form-item label="推荐">
              <el-switch v-model="form.is_recommend" />
            </el-form-item>
          </div>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">发布文章</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const store = useStore()
const router = useRouter()

const formRef = ref(null)
const submitting = ref(false)
const coverPreview = ref('')
const coverUploading = ref(false)
const categories = ref([])
const tags = ref([])

const form = reactive({
  title: '',
  summary: '',
  content: '',
  cover_image: '',
  category: null,
  tag_names: [],
  status: 1,
  is_top: false,
  is_recommend: false
})

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 4, message: '标题至少 4 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  summary: [
    { required: true, message: '请输入摘要', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入文章内容', trigger: 'blur' },
    { min: 20, message: '内容至少 20 个字符', trigger: 'blur' }
  ]
}

const loadMeta = async () => {
  await Promise.all([
    store.dispatch('blog/fetchCategories'),
    store.dispatch('blog/fetchTags')
  ])
  categories.value = store.getters['blog/categories']
  tags.value = store.getters['blog/tags']
}

const handleSubmit = () => {
  if (!formRef.value) return
  formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload = {
        title: form.title,
        summary: form.summary,
        content: form.content,
        cover_image: form.cover_image,
        category: form.category,
        tag_names: form.tag_names,
        status: form.status,
        is_top: form.is_top,
        is_recommend: form.is_recommend
      }
      const response = await axios.post('/api/blog/articles/create/', payload)
      ElMessage.success('文章发布成功')
      const articleId = response.data?.id
      if (articleId) {
        router.push(`/article/${articleId}`)
      } else {
        router.push('/user/articles')
      }
    } catch (error) {
      ElMessage.error('发布失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  formRef.value?.resetFields()
  form.tag_names = []
  coverPreview.value = ''
}

const beforeCoverUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt3M = file.size / 1024 / 1024 < 3
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
  }
  if (!isLt3M) {
    ElMessage.error('图片大小不能超过 3MB')
  }
  return isImage && isLt3M
}

const handleCoverUpload = async ({ file, onError, onSuccess }) => {
  if (!beforeCoverUpload(file)) {
    onError()
    return
  }
  coverUploading.value = true
  const formData = new FormData()
  formData.append('cover', file)
  try {
    const res = await axios.post('/api/blog/articles/cover/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    form.cover_image = res.data.url
    coverPreview.value = res.data.url
    ElMessage.success('封面上传成功')
    onSuccess(res.data)
  } catch (error) {
    ElMessage.error('封面上传失败')
    onError(error)
  } finally {
    coverUploading.value = false
  }
}

watch(
  () => form.cover_image,
  (val) => {
    coverPreview.value = val
  },
  { immediate: true }
)

onMounted(() => {
  loadMeta()
})
</script>

<style scoped>
.editor-page {
  padding: 24px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.article-form {
  margin-top: 12px;
}

.form-inline {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
}

.cover-upload {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cover-preview {
  width: 200px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.cover-preview.uploading {
  opacity: 0.7;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  color: #909399;
}

.upload-mask {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 12px;
  padding: 4px 0;
  text-align: center;
}
</style>

<template>
  <div class="category-manage-page">
    <div class="container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>分类管理</span>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              添加分类
            </el-button>
          </div>
        </template>

        <el-table :data="categories" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="分类名称" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="sort_order" label="排序" width="100" />
          <el-table-column prop="article_count" label="文章数" width="100" />
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 添加/编辑对话框 -->
      <el-dialog
        :title="dialogTitle"
        v-model="dialogVisible"
        width="600px"
        @close="handleDialogClose"
      >
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
        >
          <el-form-item label="分类名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入分类名称" />
          </el-form-item>
          <el-form-item label="分类描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="4"
              placeholder="请输入分类描述"
            />
          </el-form-item>
          <el-form-item label="排序号" prop="sort_order">
            <el-input-number
              v-model="form.sort_order"
              :min="0"
              :max="9999"
              placeholder="数字越小越靠前"
            />
          </el-form-item>
          <el-form-item label="状态" prop="is_active">
            <el-switch
              v-model="form.is_active"
              active-text="启用"
              inactive-text="禁用"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const store = useStore()

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加分类')
const formRef = ref(null)
const categories = ref([])
const editingId = ref(null)

const form = reactive({
  name: '',
  description: '',
  sort_order: 0,
  is_active: true
})

const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { max: 50, message: '分类名称不能超过50个字符', trigger: 'blur' }
  ],
  sort_order: [
    { type: 'number', min: 0, max: 9999, message: '排序号必须在0-9999之间', trigger: 'blur' }
  ]
}

// 检查是否为管理员
const checkAdmin = () => {
  const user = store.getters['user/currentUser']
  if (!user || !user.is_staff) {
    ElMessage.error('您没有权限访问此页面')
    router.push('/')
    return false
  }
  return true
}

// 加载分类列表
const loadCategories = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/blog/categories/manage/')
    // API可能返回数组或分页对象
    if (Array.isArray(response.data)) {
      categories.value = response.data
    } else if (response.data.results) {
      categories.value = response.data.results
    } else {
      categories.value = []
    }
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('您没有权限访问此页面')
      router.push('/')
    } else {
      ElMessage.error('加载分类列表失败')
    }
  } finally {
    loading.value = false
  }
}

// 添加分类
const handleAdd = () => {
  editingId.value = null
  dialogTitle.value = '添加分类'
  dialogVisible.value = true
  resetForm()
}

// 编辑分类
const handleEdit = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑分类'
  form.name = row.name
  form.description = row.description || ''
  form.sort_order = row.sort_order
  form.is_active = row.is_active
  dialogVisible.value = true
}

// 删除分类
const handleDelete = async (row) => {
  // 检查是否有文章
  if (row.article_count > 0) {
    ElMessageBox.alert(
      `该分类下还有 ${row.article_count} 篇文章，请先删除或移动这些文章后再删除分类`,
      '无法删除',
      {
        confirmButtonText: '知道了',
        type: 'warning'
      }
    )
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${row.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    try {
      await axios.delete(`/api/blog/categories/manage/${row.id}/`)
      ElMessage.success('删除成功')
      loadCategories()
    } catch (error) {
      let errorMsg = '删除失败'
      if (error.response?.data) {
        const data = error.response.data
        if (typeof data === 'string') {
          errorMsg = data
        } else if (data.detail) {
          errorMsg = data.detail
        } else if (Array.isArray(data) && data.length > 0) {
          errorMsg = data[0]
        } else if (data.non_field_errors) {
          errorMsg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors
        }
      }
      ElMessage.error(errorMsg)
    }
  } catch {
    // 用户取消删除
  }
}

// 提交表单
const handleSubmit = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (editingId.value) {
        // 更新
        await axios.put(`/api/blog/categories/manage/${editingId.value}/`, form)
        ElMessage.success('更新成功')
      } else {
        // 创建
        await axios.post('/api/blog/categories/manage/', form)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      loadCategories()
    } catch (error) {
      if (error.response?.data) {
        const errors = error.response.data
        if (typeof errors === 'string') {
          ElMessage.error(errors)
        } else if (errors.detail) {
          ElMessage.error(errors.detail)
        } else {
          const firstError = Object.values(errors)[0]
          ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
        }
      } else {
        ElMessage.error(editingId.value ? '更新失败' : '添加失败')
      }
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  form.name = ''
  form.description = ''
  form.sort_order = 0
  form.is_active = true
  formRef.value?.clearValidate()
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
  editingId.value = null
}

onMounted(() => {
  if (checkAdmin()) {
    loadCategories()
  }
})
</script>

<style scoped>
.category-manage-page {
  padding: 24px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>


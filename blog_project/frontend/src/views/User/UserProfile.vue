<template>
  <div class="profile-page">
    <div class="container">
      <el-card v-loading="loading">
        <template #header>
          <div class="card-header">
            <span>个人资料</span>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">
              保存修改
            </el-button>
          </div>
        </template>

        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-form-item label="头像">
            <div class="avatar-upload">
              <el-avatar :size="80" :src="avatarPreview || user?.avatar" />
              <div class="upload-actions">
                <el-upload
                  :show-file-list="false"
                  :http-request="handleAvatarUpload"
                  :before-upload="beforeAvatarUpload"
                >
                  <el-button :loading="uploadingAvatar">上传头像</el-button>
                </el-upload>
                <p class="upload-tip">支持 JPG/PNG，大小不超过 2MB</p>
              </div>
            </div>
          </el-form-item>

          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="form.nickname" />
          </el-form-item>

          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" />
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" />
          </el-form-item>

          <el-form-item label="性别">
            <el-radio-group v-model="form.gender">
              <el-radio :value="0">保密</el-radio>
              <el-radio :value="1">男</el-radio>
              <el-radio :value="2">女</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="生日">
            <el-date-picker
              v-model="form.birthday"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="个人简介">
            <el-input
              v-model="form.bio"
              type="textarea"
              :rows="5"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>

        <!-- 修改密码区域 -->
        <el-divider content-position="left">修改密码</el-divider>
        
        <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
          <el-form-item label="原密码" prop="old_password">
            <el-input
              v-model="passwordForm.old_password"
              type="password"
              placeholder="请输入原密码"
              show-password
            />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input
              v-model="passwordForm.new_password"
              type="password"
              placeholder="请输入新密码（至少6位）"
              show-password
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="new_password_confirm">
            <el-input
              v-model="passwordForm.new_password_confirm"
              type="password"
              placeholder="请再次输入新密码"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handlePasswordSubmit" :loading="passwordSubmitting">
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const store = useStore()
const formRef = ref(null)
const passwordFormRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const passwordSubmitting = ref(false)
const uploadingAvatar = ref(false)
const avatarPreview = ref('')

const user = computed(() => store.getters['user/currentUser'])

const form = reactive({
  nickname: '',
  phone: '',
  email: '',
  gender: 0,
  birthday: '',
  bio: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  new_password_confirm: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const fillForm = () => {
  if (!user.value) return
  form.nickname = user.value.nickname || user.value.username
  form.phone = user.value.phone || ''
  form.email = user.value.email
  form.gender = user.value.gender ?? 0
  form.birthday = user.value.birthday
  form.bio = user.value.bio
  avatarPreview.value = user.value.avatar
}

const loadUser = async () => {
  loading.value = true
  await store.dispatch('user/getCurrentUser')
  fillForm()
  loading.value = false
}

const beforeAvatarUpload = (file) => {
  const isImage = ['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isImage) {
    ElMessage.error('仅支持 JPG/PNG 格式的图片')
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
  }
  return isImage && isLt2M
}

const handleAvatarUpload = async ({ file, onError, onSuccess }) => {
  const formData = new FormData()
  formData.append('avatar', file)
  uploadingAvatar.value = true
  try {
    const res = await axios.post('/api/users/avatar/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    avatarPreview.value = res.data.url
    await store.dispatch('user/getCurrentUser')
    ElMessage.success('头像上传成功')
    onSuccess(res.data)
  } catch (error) {
    ElMessage.error('上传失败，请稍后再试')
    onError(error)
  } finally {
    uploadingAvatar.value = false
  }
}

const handleSubmit = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await store.dispatch('user/updateProfile', { ...form })
      ElMessage.success('资料已更新')
    } catch (error) {
      ElMessage.error('更新失败，请稍后再试')
    } finally {
      submitting.value = false
    }
  })
}

const handlePasswordSubmit = () => {
  passwordFormRef.value?.validate(async (valid) => {
    if (!valid) return
    passwordSubmitting.value = true
    try {
      await store.dispatch('user/changePassword', { ...passwordForm })
      ElMessage.success('密码修改成功')
      // 清空密码表单
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.new_password_confirm = ''
      passwordFormRef.value?.clearValidate()
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
        ElMessage.error('密码修改失败，请稍后再试')
      }
    } finally {
      passwordSubmitting.value = false
    }
  })
}

onMounted(() => {
  if (user.value) {
    fillForm()
  } else {
    loadUser()
  }
})
</script>

<style scoped>
.profile-page {
  padding: 24px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.upload-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.upload-tip {
  margin: 0;
  font-size: 12px;
  color: #909399;
}
</style>


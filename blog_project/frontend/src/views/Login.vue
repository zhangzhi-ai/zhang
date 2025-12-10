<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>欢迎回来</h2>
      <p class="subtitle">使用账号登录以继续操作</p>

      <el-alert
        v-if="errorMessage"
        type="error"
        :closable="false"
        class="mb-16"
        :title="errorMessage"
      />

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="handleSubmit"
      >
        <el-form-item label="用户名 / 手机号" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名或手机号"
            clearable
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-button
          type="primary"
          class="submit-btn"
          size="large"
          :loading="loading"
          @click="handleSubmit"
        >
          登录
        </el-button>
      </el-form>

      <div class="tips">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

const store = useStore()
const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const form = reactive({
  username: route.query.username || '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名或手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    await store.dispatch('user/login', {
      username: form.username.trim(),
      password: form.password
    })
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    const data = error.response?.data
    if (typeof data === 'string') {
      errorMessage.value = data
    } else if (Array.isArray(data?.non_field_errors)) {
      errorMessage.value = data.non_field_errors[0]
    } else if (typeof data?.detail === 'string') {
      errorMessage.value = data.detail
    } else {
      errorMessage.value = '登录失败，请检查账号和密码'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 16px;
  background: linear-gradient(135deg, #f6f9ff, #f1f5ff);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  padding: 40px 36px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(15, 44, 105, 0.12);
}

h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f56;
}

.subtitle {
  margin: 8px 0 24px;
  color: #7b88a8;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  margin-top: 12px;
}

.tips {
  text-align: center;
  margin-top: 24px;
  color: #7b88a8;
  font-size: 14px;
}

.tips a {
  color: #409eff;
  font-weight: 500;
}

.mb-16 {
  margin-bottom: 16px;
}
</style>

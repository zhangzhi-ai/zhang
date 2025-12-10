<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>创建新账号</h2>
      <p class="subtitle">填写以下信息完成注册</p>

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
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="4-20位字母或数字" clearable />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="用于登录与找回密码" clearable />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="接收通知（可选）" clearable />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="展示名称" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="password_confirm">
          <el-input
            v-model="form.password_confirm"
            type="password"
            placeholder="再次输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="图片验证码" prop="captcha_code">
          <div class="captcha-row">
            <el-input
              v-model="form.captcha_code"
              placeholder="请输入验证码"
              style="flex: 1; margin-right: 12px"
              clearable
            />
            <div class="captcha-image" @click="refreshCaptcha">
              <img v-if="captchaImageUrl" :src="captchaImageUrl" alt="验证码" />
              <span v-else>点击获取验证码</span>
            </div>
          </div>
        </el-form-item>
        <!-- 短信验证码功能已注释 -->
        <!-- <el-form-item label="短信验证码" prop="sms_code">
          <div class="sms-row">
            <el-input
              v-model="form.sms_code"
              placeholder="请输入短信验证码"
              style="flex: 1; margin-right: 12px"
              clearable
            />
            <el-button
              :disabled="smsCountdown > 0 || !form.phone || !form.captcha_code"
              @click="sendSmsCode"
              :loading="smsLoading"
            >
              {{ smsCountdown > 0 ? `${smsCountdown}秒后重试` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item> -->
        <el-button
          type="primary"
          class="submit-btn"
          size="large"
          :loading="loading"
          @click="handleSubmit"
        >
          注册
        </el-button>
      </el-form>

      <div class="tips">
        已有账号？
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const store = useStore()
const router = useRouter()

const formRef = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const captchaImageUrl = ref('')
const captchaKey = ref('')
// 注释掉短信验证码相关变量
// const smsLoading = ref(false)
// const smsCountdown = ref(0)
// let smsTimer = null

const form = reactive({
  username: '',
  phone: '',
  email: '',
  nickname: '',
  password: '',
  password_confirm: '',
  captcha_code: ''
  // sms_code: ''  // 已移除
})

const validatePasswordConfirm = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 4, max: 20, message: '用户名需要4-20个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入有效的大陆手机号',
      trigger: 'blur'
    }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  password_confirm: [
    { validator: validatePasswordConfirm, trigger: ['blur', 'change'] }
  ],
  captcha_code: [
    { required: true, message: '请输入图片验证码', trigger: 'blur' }
  ]
  // 注释掉短信验证码验证规则
  // sms_code: [
  //   { required: true, message: '请输入短信验证码', trigger: 'blur' }
  // ]
}

const resetPasswordFields = () => {
  form.password = ''
  form.password_confirm = ''
  form.captcha_code = ''
  // form.sms_code = ''  // 已移除
  refreshCaptcha()
}

// 刷新图片验证码
const refreshCaptcha = async () => {
  try {
    const response = await axios.get('/api/users/captcha/image/', {
      responseType: 'blob'
    })
    // 获取响应头中的验证码key
    const key = response.headers['x-captcha-key']
    if (!key) {
      console.error('未获取到验证码key，响应头:', response.headers)
      ElMessage.error('获取验证码失败，请刷新页面重试')
      return
    }
    captchaKey.value = key
    const blob = new Blob([response.data], { type: 'image/png' })
    captchaImageUrl.value = URL.createObjectURL(blob)
    form.captcha_code = ''
    console.log('验证码获取成功，key:', key)
  } catch (error) {
    console.error('获取验证码失败:', error)
    ElMessage.error('获取验证码失败，请刷新页面重试')
  }
}

// 注释掉发送短信验证码功能
// const sendSmsCode = async () => {
//   if (!form.phone) {
//     ElMessage.warning('请先输入手机号')
//     return
//   }
//   if (!form.captcha_code) {
//     ElMessage.warning('请先输入图片验证码')
//     return
//   }
//   
//   smsLoading.value = true
//   try {
//     const response = await axios.post('/api/users/sms/send/', {
//       phone: form.phone,
//       captcha_key: captchaKey.value,
//       captcha_code: form.captcha_code
//     })
//     ElMessage.success(response.data.message || '验证码已发送')
//     
//     // 开发环境显示验证码
//     if (response.data.code) {
//       ElMessage.info(`验证码：${response.data.code}（开发环境）`)
//     }
//     
//     // 开始倒计时
//     smsCountdown.value = 60
//     if (smsTimer) clearInterval(smsTimer)
//     smsTimer = setInterval(() => {
//       smsCountdown.value--
//       if (smsCountdown.value <= 0) {
//         clearInterval(smsTimer)
//         smsTimer = null
//       }
//     }, 1000)
//     
//     // 刷新图片验证码
//     refreshCaptcha()
//   } catch (error) {
//     const message = error.response?.data?.message || '发送失败，请稍后再试'
//     ElMessage.error(message)
//     refreshCaptcha()
//   } finally {
//     smsLoading.value = false
//   }
// }

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  if (!captchaKey.value) {
    ElMessage.warning('请先获取图片验证码')
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    // 构建提交数据，移除短信验证码字段
    const submitData = {
      username: form.username,
      phone: form.phone,
      email: form.email,
      nickname: form.nickname,
      password: form.password,
      password_confirm: form.password_confirm,
      captcha_key: captchaKey.value,
      captcha_code: form.captcha_code
    }
    
    await store.dispatch('user/register', submitData)
    ElMessage.success('注册成功，请登录')
    router.push({
      name: 'Login',
      query: { username: form.username.trim() }
    })
  } catch (error) {
    const data = error.response?.data
    if (data && typeof data === 'object') {
      const firstKey = Object.keys(data)[0]
      const message = Array.isArray(data[firstKey]) ? data[firstKey][0] : data[firstKey]
      errorMessage.value = message || '注册失败，请检查填写信息'
    } else {
      errorMessage.value = '注册失败，请稍后再试'
    }
    resetPasswordFields()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshCaptcha()
})
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
  max-width: 520px;
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

.captcha-row {
  display: flex;
  align-items: center;
  width: 100%;
}

.captcha-image {
  width: 120px;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  flex-shrink: 0;
}

.captcha-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.captcha-image span {
  font-size: 12px;
  color: #909399;
}

.sms-row {
  display: flex;
  align-items: center;
  width: 100%;
}
</style>

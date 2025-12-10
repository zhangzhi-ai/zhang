<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1 class="error-title">页面未找到</h1>
      <p class="error-description">
        抱歉，您访问的页面不存在或已被删除
      </p>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found-page {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 16px;
  background: linear-gradient(135deg, #f6f9ff, #f1f5ff);
}

.not-found-content {
  text-align: center;
  max-width: 600px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.error-title {
  font-size: 32px;
  color: #1f2f56;
  margin: 0 0 16px;
  font-weight: 600;
}

.error-description {
  font-size: 16px;
  color: #7b88a8;
  margin: 0 0 32px;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

@media (max-width: 768px) {
  .error-code {
    font-size: 80px;
  }
  
  .error-title {
    font-size: 24px;
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .error-actions .el-button {
    width: 100%;
  }
}
</style>


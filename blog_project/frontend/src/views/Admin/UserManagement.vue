<template>
  <div class="user-management">
    <div class="container">
      <div class="page-header">
        <h1>用户管理</h1>
        <p class="subtitle">管理系统中的所有用户</p>
      </div>
      
      <!-- 统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.total_users }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.active_users }}</div>
            <div class="stat-label">活跃用户</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon><UserFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.staff_users }}</div>
            <div class="stat-label">管理员</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.new_users_30d }}</div>
            <div class="stat-label">30天新增</div>
          </div>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="search-bar card">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名、手机号、邮箱..."
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          style="width: 300px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="filterStatus" placeholder="用户状态" @change="handleSearch" style="width: 150px;">
          <el-option label="全部" :value="null" />
          <el-option label="已启用" value="true" />
          <el-option label="已禁用" value="false" />
        </el-select>
        
        <el-select v-model="filterStaff" placeholder="用户类型" @change="handleSearch" style="width: 150px;">
          <el-option label="全部" :value="null" />
          <el-option label="管理员" value="true" />
          <el-option label="普通用户" value="false" />
        </el-select>
        
        <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
        <el-button @click="handleReset" :icon="Refresh">重置</el-button>
      </div>
      
      <!-- 用户列表 -->
      <div class="user-table card">
        <el-table
          :data="users"
          v-loading="loading"
          style="width: 100%"
          stripe
        >
          <el-table-column prop="id" label="ID" width="80" />
          
          <el-table-column label="用户信息" min-width="200">
            <template #default="{ row }">
              <div class="user-info-cell">
                <el-avatar :size="40" :src="row.avatar" />
                <div class="user-details">
                  <div class="username">{{ row.username }}</div>
                  <div class="nickname" v-if="row.nickname">{{ row.nickname }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="phone" label="手机号" width="120" />
          <el-table-column prop="email" label="邮箱" min-width="180" />
          
          <el-table-column label="文章/评论" width="100" align="center">
            <template #default="{ row }">
              <div>{{ row.article_count }} / {{ row.comment_count }}</div>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                {{ row.is_active ? '已启用' : '已禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_staff" type="warning" size="small">管理员</el-tag>
              <el-tag v-else type="info" size="small">普通用户</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="date_joined" label="注册时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.date_joined) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                :type="row.is_active ? 'warning' : 'success'"
                @click="toggleUserStatus(row)"
                :disabled="row.id === currentUserId"
              >
                {{ row.is_active ? '禁用' : '启用' }}
              </el-button>
              
              <el-button
                size="small"
                type="primary"
                @click="resetUserPassword(row)"
                :disabled="row.id === currentUserId"
              >
                重置密码
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="total > 0">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next, jumper, total"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, UserFilled, CircleCheck, TrendCharts, 
  Search, Refresh 
} from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'UserManagement',
  components: {
    User, UserFilled, CircleCheck, TrendCharts,
    Search, Refresh
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const users = ref([])
    const statistics = reactive({
      total_users: 0,
      active_users: 0,
      staff_users: 0,
      new_users_30d: 0,
      active_users_7d: 0
    })
    
    const searchKeyword = ref('')
    const filterStatus = ref(null)  // 默认为"已启用"
    const filterStaff = ref(null)     // 默认为"全部"
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    
    const currentUserId = computed(() => store.getters['user/userId'])
    
    // 加载统计信息
    const loadStatistics = async () => {
      try {
        const response = await axios.get('/api/users/management/statistics/')
        Object.assign(statistics, response.data)
      } catch (error) {
        console.error('加载统计信息失败:', error)
      }
    }
    
    // 加载用户列表
    const loadUsers = async () => {
      loading.value = true
      try {
        const params = {}
        
        // 只有在有值时才添加参数
        if (searchKeyword.value) {
          params.search = searchKeyword.value
        }
        if (filterStatus.value !== null && filterStatus.value !== '') {
          params.is_active = filterStatus.value
        }
        if (filterStaff.value !== null && filterStaff.value !== '') {
          params.is_staff = filterStaff.value
        }
        
        const response = await axios.get('/api/users/management/', { params })
        console.log('用户数据:', response.data)
        
        // 处理返回的数据，可能是数组或分页对象
        if (Array.isArray(response.data)) {
          users.value = response.data
          total.value = response.data.length
        } else if (response.data.results) {
          users.value = response.data.results
          total.value = response.data.count || response.data.results.length
        } else {
          users.value = []
          total.value = 0
        }
      } catch (error) {
        console.error('加载用户失败:', error)
        if (error.response?.status === 403) {
          ElMessage.error('您没有权限访问用户管理功能')
        } else if (error.response?.status === 401) {
          ElMessage.error('请先登录')
        } else {
          ElMessage.error('加载用户列表失败: ' + (error.response?.data?.detail || error.message))
        }
      } finally {
        loading.value = false
      }
    }
    
    // 搜索
    const handleSearch = () => {
      currentPage.value = 1
      loadUsers()
    }
    
    // 重置
    const handleReset = () => {
      searchKeyword.value = ''
      filterStatus.value = 'true'  // 重置为"已启用"
      filterStaff.value = null     // 重置为"全部"
      currentPage.value = 1
      loadUsers()
    }
    
    // 分页
    const handlePageChange = (page) => {
      currentPage.value = page
      loadUsers()
    }
    
    // 切换用户状态
    const toggleUserStatus = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要${user.is_active ? '禁用' : '启用'}用户 ${user.username} 吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const response = await axios.post(`/api/users/management/${user.id}/toggle-status/`)
        ElMessage.success(response.data.message)
        loadUsers()
        loadStatistics()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.message || '操作失败')
        }
      }
    }
    
    // 重置用户密码
    const resetUserPassword = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要重置用户 ${user.username} 的密码吗？密码将被重置为：123456`,
          '重置密码',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const response = await axios.post(`/api/users/management/${user.id}/reset-password/`)
        ElMessage.success(response.data.message)
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.message || '操作失败')
        }
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    onMounted(() => {
      loadStatistics()
      loadUsers()
    })
    
    return {
      loading,
      users,
      statistics,
      searchKeyword,
      filterStatus,
      filterStaff,
      currentPage,
      pageSize,
      total,
      currentUserId,
      handleSearch,
      handleReset,
      handlePageChange,
      toggleUserStatus,
      resetUserPassword,
      formatDate
    }
  }
}
</script>

<style scoped>
.user-management {
  padding: 20px 0;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 8px;
  color: #333;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 20px;
}

.user-table {
  padding: 20px;
}

.user-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  flex: 1;
}

.username {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.nickname {
  font-size: 12px;
  color: #999;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-bar .el-input,
  .search-bar .el-select {
    width: 100% !important;
  }
}
</style>
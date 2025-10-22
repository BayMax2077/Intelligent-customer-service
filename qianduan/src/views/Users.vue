<template>
  <div class="users-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon class="title-icon"><User /></el-icon>
            用户管理
          </h1>
          <p class="page-subtitle">管理系统用户、角色权限和店铺分配</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Refresh" @click="load" :loading="loading">
            刷新
          </el-button>
          <el-button type="success" :icon="Plus" @click="showAddDialog">
            新增用户
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <div class="filter-content">
        <div class="filter-left">
          <el-form :inline="true" :model="filters" class="filter-form">
            <el-form-item label="角色" class="filter-item">
              <el-select v-model="filters.role" placeholder="选择角色" clearable class="filter-select">
                <el-option label="超级管理员" value="superadmin" />
                <el-option label="店铺管理员" value="admin" />
                <el-option label="客服" value="agent" />
              </el-select>
            </el-form-item>
            <el-form-item label="店铺" class="filter-item">
              <el-select v-model="filters.shop_id" placeholder="选择店铺" clearable class="filter-select">
                <el-option label="全局" :value="null" />
                <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
        <div class="filter-right">
          <el-button type="primary" @click="load" :loading="loading" class="query-btn">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilters" class="reset-btn">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <div class="table-header">
        <div class="table-title">
          <el-icon class="table-icon"><Grid /></el-icon>
          用户列表
        </div>
        <div class="table-actions">
          <span class="data-count">共 {{ pagination.total }} 条数据</span>
        </div>
      </div>
      <div class="table-content">
        <el-table 
          :data="users" 
          v-loading="loading"
          stripe
          border
          class="data-table"
          :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
        >
          <el-table-column prop="id" label="ID" width="80" align="center" />
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column prop="role" label="角色" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getRoleType(row.role)" size="small">{{ getRoleText(row.role) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="shop_name" label="所属店铺" width="150">
            <template #default="{ row }">
              <span v-if="row.shop_id === null || row.shop_id === undefined">全局知识库</span>
              <span v-else>{{ row.shop_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              <span class="date-cell">{{ formatDate(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" type="primary" @click="editUser(row)">编辑</el-button>
                <el-button size="small" type="warning" @click="resetPassword(row)">重置密码</el-button>
                <el-button size="small" type="danger" @click="deleteUser(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="load"
        @current-change="load"
        class="pagination"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog 
      :title="dialogMode === 'add' ? '新增用户' : '编辑用户'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogMode === 'add'">
          <el-input v-model="form.password" type="password" placeholder="输入密码" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="选择角色" style="width: 100%;">
            <el-option label="超级管理员" value="superadmin" />
            <el-option label="店铺管理员" value="admin" />
            <el-option label="客服" value="agent" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属店铺" prop="shop_id">
          <el-select v-model="form.shop_id" placeholder="选择店铺" clearable style="width: 100%;">
            <el-option label="全局知识库" :value="null" />
            <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog title="重置密码" v-model="resetDialogVisible" width="400px">
      <el-form :model="resetForm" :rules="resetRules" ref="resetFormRef" label-width="100px">
        <el-form-item label="新密码" prop="password">
          <el-input v-model="resetForm.password" type="password" placeholder="输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="resetForm.confirmPassword" type="password" placeholder="确认新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmResetPassword" :loading="resetting">重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import http from '../api/http'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Refresh, Plus, Search, RefreshLeft, Grid } from '@element-plus/icons-vue'

// 数据状态
const loading = ref(false)
const saving = ref(false)
const resetting = ref(false)
const users = ref<any[]>([])
const shops = ref<any[]>([])
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
})

// 筛选条件
const filters = reactive({
  role: '',
  shop_id: null
})

// 对话框状态
const dialogVisible = ref(false)
const resetDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')

// 表单数据
const form = reactive({
  id: null,
  username: '',
  password: '',
  role: '',
  shop_id: null
})

const resetForm = reactive({
  userId: null,
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const resetRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== resetForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const formRef = ref()
const resetFormRef = ref()

// 加载数据
const load = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.page.toString(),
      per_page: pagination.per_page.toString()
    })
    
    if (filters.role) {
      params.append('role', filters.role)
    }
    if (filters.shop_id !== null) {
      params.append('shop_id', filters.shop_id.toString())
    }
    
    const res = await http.get(`/api/users?${params}`)
    users.value = res.data.users
    pagination.total = res.data.total
    pagination.pages = res.data.pages
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 加载店铺列表
const loadShops = async () => {
  try {
    const res = await http.get('/api/shops')
    shops.value = res.data
  } catch (error) {
    console.error('加载店铺列表失败:', error)
  }
}

// 获取角色类型
const getRoleType = (role: string) => {
  const roleMap: Record<string, string> = {
    'superadmin': 'danger',
    'admin': 'warning',
    'agent': 'info'
  }
  return roleMap[role] || 'info'
}

// 获取角色文本
const getRoleText = (role: string) => {
  const roleMap: Record<string, string> = {
    'superadmin': '超级管理员',
    'admin': '店铺管理员',
    'agent': '客服'
  }
  return roleMap[role] || role
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 重置筛选条件
const resetFilters = () => {
  filters.role = ''
  filters.shop_id = null
  pagination.page = 1
  load()
}

// 显示新增对话框
const showAddDialog = () => {
  dialogMode.value = 'add'
  Object.assign(form, {
    id: null,
    username: '',
    password: '',
    role: '',
    shop_id: null
  })
  dialogVisible.value = true
}

// 编辑用户
const editUser = (row: any) => {
  dialogMode.value = 'edit'
  Object.assign(form, {
    id: row.id,
    username: row.username,
    password: '',
    role: row.role,
    shop_id: row.shop_id
  })
  dialogVisible.value = true
}

// 保存用户
const saveUser = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    saving.value = true
    
    if (dialogMode.value === 'add') {
      await http.post('/api/users', form)
      ElMessage.success('用户创建成功')
    } else {
      await http.put(`/api/users/${form.id}`, form)
      ElMessage.success('用户更新成功')
    }
    
    dialogVisible.value = false
    load()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 删除用户
const deleteUser = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用户吗？', '确认删除', {
      type: 'warning'
    })
    
    await http.delete(`/api/users/${row.id}`)
    ElMessage.success('删除成功')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 重置密码
const resetPassword = (row: any) => {
  resetForm.userId = row.id
  resetForm.password = ''
  resetForm.confirmPassword = ''
  resetDialogVisible.value = true
}

// 确认重置密码
const confirmResetPassword = async () => {
  if (!resetFormRef.value) return
  
  try {
    await resetFormRef.value.validate()
    
    resetting.value = true
    
    await http.post(`/api/users/${resetForm.userId}/reset_password`, {
      password: resetForm.password
    })
    
    ElMessage.success('密码重置成功')
    resetDialogVisible.value = false
  } catch (error) {
    ElMessage.error('密码重置失败')
  } finally {
    resetting.value = false
  }
}

// 初始化
onMounted(() => {
  loadShops()
  load()
})
</script>

<style scoped>
/* 页面整体样式 */
.users-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  color: white;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.title-icon {
  margin-right: 12px;
  font-size: 32px;
}

.page-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 筛选卡片 */
.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filter-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.filter-left {
  flex: 1;
}

.filter-form {
  margin: 0;
}

.filter-item {
  margin-right: 20px;
  margin-bottom: 0;
}

.filter-select {
  width: 180px;
}

.filter-right {
  display: flex;
  gap: 12px;
}

.query-btn, .reset-btn {
  padding: 8px 16px;
}

/* 表格卡片 */
.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background: #fafbfc;
}

.table-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.table-icon {
  margin-right: 8px;
  color: #409eff;
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.data-count {
  color: #909399;
  font-size: 14px;
}

.table-content {
  padding: 0;
}

.data-table {
  width: 100%;
}

.date-cell {
  color: #606266;
  font-size: 13px;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
  justify-content: center;
}

.action-buttons .el-button {
  width: auto;
  min-width: 70px;
  margin: 0;
  padding: 6px 12px;
}

/* 分页容器 */
.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.pagination {
  background: white;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .users-page {
    padding: 12px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filter-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .filter-form {
    width: 100%;
  }
  
  .filter-item {
    margin-right: 0;
    margin-bottom: 12px;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>

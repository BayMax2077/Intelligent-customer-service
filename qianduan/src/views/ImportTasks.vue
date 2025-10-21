<template>
  <div class="import-tasks-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <div class="title-with-back">
            <el-button 
              type="text" 
              @click="goBack" 
              class="back-button"
              size="large"
            >
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <h1 class="title">
              <el-icon><Upload /></el-icon>
              导入任务中心
            </h1>
          </div>
          <p class="subtitle">
            监控导入进度，查看导入历史，管理批量导入任务
          </p>
        </div>
        <div class="header-actions">
          <el-button @click="loadTasks" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button type="primary" @click="goToImport">
            <el-icon><Plus /></el-icon>
            新建导入
          </el-button>
        </div>
      </div>
    </div>

    <!-- 当前任务状态 -->
    <div v-if="currentTask" class="current-task">
      <el-card class="task-card">
        <template #header>
          <div class="card-header">
            <span class="task-title">
              <el-icon><Loading /></el-icon>
              当前任务：{{ currentTask.task_name }}
            </span>
            <el-tag :type="getStatusType(currentTask.status)">
              {{ getStatusText(currentTask.status) }}
            </el-tag>
          </div>
        </template>
        
        <div class="task-content">
          <div class="progress-section">
            <el-progress 
              :percentage="currentTask.progress" 
              :status="currentTask.status === 'failed' ? 'exception' : undefined"
              :stroke-width="8"
            />
            <div class="progress-info">
              <span>已处理：{{ currentTask.processed_rows || 0 }} / {{ currentTask.total_rows || 0 }}</span>
              <span>成功：{{ currentTask.success_count || 0 }}</span>
              <span>失败：{{ currentTask.error_count || 0 }}</span>
            </div>
          </div>
          
          <div class="task-actions">
            <el-button 
              v-if="currentTask.status === 'processing'" 
              type="danger" 
              @click="cancelTask(currentTask.id)"
            >
              <el-icon><Close /></el-icon>
              取消任务
            </el-button>
            <el-button @click="viewTaskDetail(currentTask.id)">
              <el-icon><View /></el-icon>
              查看详情
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 任务历史列表 -->
    <div class="tasks-list">
      <div class="list-header">
        <h3>任务历史</h3>
        <div class="filters">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadTasks">
            <el-option label="全部" value="" />
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-input 
            v-model="searchText" 
            placeholder="搜索任务名称或文件名" 
            @input="handleSearch"
            style="width: 200px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
      
      <el-table 
        :data="tasks" 
        v-loading="loading"
        empty-text="暂无导入任务"
        class="tasks-table"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="task_name" label="任务名称" min-width="200">
          <template #default="{ row }">
            <div class="task-name">
              <el-icon><Document /></el-icon>
              <span>{{ row.task_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="file_name" label="文件名" min-width="150" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="120" align="center">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.progress" 
              :status="row.status === 'failed' ? 'exception' : undefined"
              :stroke-width="6"
              :show-text="false"
            />
            <span class="progress-text">{{ row.progress }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="统计" width="150" align="center">
          <template #default="{ row }">
            <div class="stats">
              <span class="success">成功: {{ row.success_count || 0 }}</span>
              <span class="error">失败: {{ row.error_count || 0 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="viewTaskDetail(row.id)">查看</el-button>
            <el-button 
              v-if="row.status === 'processing'" 
              size="small" 
              type="danger" 
              @click="cancelTask(row.id)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTasks"
          @current-change="loadTasks"
        />
      </div>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="showTaskDetail"
      :title="`任务详情 - ${selectedTask?.task_name || ''}`"
      width="800px"
      class="task-detail-dialog"
    >
      <div v-if="selectedTask" class="task-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="任务名称">{{ selectedTask.task_name }}</el-descriptions-item>
            <el-descriptions-item label="文件名">{{ selectedTask.file_name }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(selectedTask.file_size) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(selectedTask.status)">
                {{ getStatusText(selectedTask.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(selectedTask.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ formatDate(selectedTask.started_at) }}</el-descriptions-item>
            <el-descriptions-item label="完成时间">{{ formatDate(selectedTask.completed_at) }}</el-descriptions-item>
            <el-descriptions-item label="错误信息" v-if="selectedTask.error_message">
              <span class="error-text">{{ selectedTask.error_message }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 处理结果 -->
        <div class="detail-section">
          <h4>处理结果</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总行数" :value="selectedTask.total_rows || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="已处理" :value="selectedTask.processed_rows || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功" :value="selectedTask.success_count || 0" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="失败" :value="selectedTask.error_count || 0" />
            </el-col>
          </el-row>
        </div>

        <!-- 实时日志 -->
        <div class="detail-section">
          <h4>处理日志</h4>
          <div class="logs-container">
            <div 
              v-for="log in taskLogs" 
              :key="log.id" 
              :class="['log-item', `log-${log.level}`]"
            >
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span class="log-level">{{ log.level.toUpperCase() }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api/http'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Upload, Refresh, Plus, Loading, Close, View, 
  Document, Search, ArrowLeft
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const currentTask = ref<any>(null)
const tasks = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')
const searchText = ref('')
const showTaskDetail = ref(false)
const selectedTask = ref<any>(null)
const taskLogs = ref<any[]>([])

// 定时器
let refreshTimer: NodeJS.Timeout | null = null

// 生命周期
onMounted(() => {
  loadTasks()
  loadCurrentTask()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})

// 自动刷新
const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    loadCurrentTask()
    if (currentTask.value) {
      loadTasks()
    }
  }, 2000) // 每2秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 加载当前任务
const loadCurrentTask = async () => {
  try {
    const res = await http.get('/api/import/tasks/current')
    currentTask.value = res.data.task
  } catch (error) {
    console.error('加载当前任务失败:', error)
  }
}

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      status: statusFilter.value,
      search: searchText.value
    }
    const res = await http.get('/api/import/tasks', { params })
    tasks.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  loadTasks()
}

// 查看任务详情
const viewTaskDetail = async (taskId: number) => {
  try {
    const res = await http.get(`/api/import/tasks/${taskId}`)
    selectedTask.value = res.data
    showTaskDetail.value = true
    
    // 加载任务日志
    await loadTaskLogs(taskId)
  } catch (error) {
    console.error('加载任务详情失败:', error)
    ElMessage.error('加载任务详情失败')
  }
}

// 加载任务日志
const loadTaskLogs = async (taskId: number) => {
  try {
    const res = await http.get(`/api/import/tasks/${taskId}/logs`)
    taskLogs.value = res.data.items
  } catch (error) {
    console.error('加载任务日志失败:', error)
  }
}

// 取消任务
const cancelTask = async (taskId: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消这个导入任务吗？',
      '确认取消',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await http.post(`/api/import/tasks/${taskId}/cancel`)
    ElMessage.success('任务已取消')
    loadTasks()
    loadCurrentTask()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消任务失败:', error)
      ElMessage.error('取消任务失败')
    }
  }
}

// 跳转到导入页面
const goToImport = () => {
  // 跳转到知识库页面并打开导入对话框
  router.push('/kb?action=import')
}

// 返回上一页
const goBack = () => {
  // 返回到知识库管理页面
  router.push('/kb')
}

// 状态相关方法
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': 'info',
    'processing': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

// 格式化方法
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleTimeString('zh-CN')
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
/* 页面布局 */
.import-tasks-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* 页面头部 */
.page-header {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin-bottom: var(--space-lg);
  border: 1px solid var(--border-light);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-lg);
  gap: var(--space-lg);
}

.title-section {
  flex: 1;
}

.title-with-back {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
}

.back-button {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--text-secondary);
  font-size: 16px;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.back-button:hover {
  color: var(--primary);
  background: var(--bg-secondary);
}

.title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

/* 当前任务 */
.current-task {
  margin-bottom: var(--space-lg);
}

.task-card {
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.task-content {
  padding: var(--space-md) 0;
}

.progress-section {
  margin-bottom: var(--space-md);
}

.progress-info {
  display: flex;
  gap: var(--space-lg);
  margin-top: var(--space-sm);
  font-size: 14px;
  color: var(--text-secondary);
}

.task-actions {
  display: flex;
  gap: var(--space-sm);
  justify-content: flex-end;
}

/* 任务列表 */
.tasks-list {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-secondary);
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.filters {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

.tasks-table {
  border: none;
}

.task-name {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-weight: 500;
}

.progress-text {
  font-size: 12px;
  color: var(--text-secondary);
  margin-left: var(--space-xs);
}

.stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  font-size: 12px;
}

.stats .success {
  color: var(--success);
}

.stats .error {
  color: var(--danger);
}

.pagination {
  padding: var(--space-lg);
  display: flex;
  justify-content: center;
}

/* 任务详情对话框 */
.task-detail-dialog {
  .detail-section {
    margin-bottom: var(--space-lg);
  }
  
  .detail-section h4 {
    margin: 0 0 var(--space-md);
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
  
  .error-text {
    color: var(--danger);
    font-size: 12px;
  }
  
  .logs-container {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: var(--space-sm);
    background: var(--bg-secondary);
  }
  
  .log-item {
    display: flex;
    gap: var(--space-sm);
    margin-bottom: var(--space-xs);
    font-size: 12px;
    line-height: 1.4;
  }
  
  .log-time {
    color: var(--text-muted);
    min-width: 80px;
  }
  
  .log-level {
    min-width: 60px;
    font-weight: 600;
  }
  
  .log-info .log-level {
    color: var(--info);
  }
  
  .log-warning .log-level {
    color: var(--warning);
  }
  
  .log-error .log-level {
    color: var(--danger);
  }
  
  .log-message {
    flex: 1;
    color: var(--text-primary);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
  
  .filters {
    width: 100%;
    justify-content: stretch;
  }
}
</style>

<template>
  <div class="messages-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon class="title-icon"><ChatDotRound /></el-icon>
            消息列表
          </h1>
          <p class="page-subtitle">显示最近抓取的消息，支持对首条进行处理以进入审核或自动发送</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Refresh" @click="load" :loading="loading">
            刷新
          </el-button>
          <el-button type="warning" :icon="MagicStick" @click="processFirst">
            处理首条
          </el-button>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <div class="table-header">
        <div class="table-title">
          <el-icon class="table-icon"><Grid /></el-icon>
          消息列表
        </div>
        <div class="table-actions">
          <span class="data-count">共 {{ items.length }} 条数据</span>
        </div>
      </div>
      <div class="table-content">
        <el-table 
          :data="items" 
          v-loading="loading"
          stripe
          border
          class="data-table"
          :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
        >
          <el-table-column prop="id" label="ID" width="80" align="center" />
          <el-table-column prop="shop_id" label="店铺ID" width="100" align="center" />
          <el-table-column prop="customer_id" label="客户ID" width="160" />
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="220">
            <template #default="{ row }">
              <span class="date-cell">{{ formatDate(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="content_preview" label="内容" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import http from '../api/http'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Refresh, MagicStick, Grid } from '@element-plus/icons-vue'

const items = ref<any[]>([])
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    const r = await http.get('/api/messages')
    items.value = r.data
  } catch (error) {
    ElMessage.error('加载消息列表失败')
  } finally {
    loading.value = false
  }
}

const processFirst = async () => {
  if (!items.value.length) {
    ElMessage.warning('没有可处理的消息')
    return
  }
  try {
    await http.post('/api/messages/process', { message_id: items.value[0].id })
    ElMessage.success('处理成功')
    load()
  } catch (error) {
    ElMessage.error('处理失败')
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': 'warning',
    'processed': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

load()
</script>

<style scoped>
/* 页面整体样式 */
.messages-page {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .messages-page {
    padding: 12px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>


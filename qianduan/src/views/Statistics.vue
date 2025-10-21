<template>
  <div class="statistics-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon class="title-icon"><DataAnalysis /></el-icon>
            统计报表
          </h1>
          <p class="page-subtitle">查看消息处理统计、知识库命中率、AI回复效果等关键指标</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Refresh" @click="loadData" :loading="loading">
            刷新数据
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <div class="filter-content">
        <div class="filter-left">
          <el-form :inline="true" :model="filters" class="filter-form">
            <el-form-item label="时间范围" class="filter-item">
              <el-date-picker
                v-model="filters.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="loadData"
                class="date-picker"
              />
            </el-form-item>
          </el-form>
        </div>
        <div class="filter-right">
          <el-button type="primary" @click="loadData" :loading="loading" class="query-btn">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetFilters" class="reset-btn">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card stat-card-primary">
        <div class="stat-icon">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_messages || 0 }}</div>
          <div class="stat-label">总消息数</div>
          <div class="stat-trend">
            <el-icon class="trend-icon"><TrendCharts /></el-icon>
            <span class="trend-text">较昨日 +12%</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card stat-card-success">
        <div class="stat-icon">
          <el-icon><Collection /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_kb_hits || 0 }}</div>
          <div class="stat-label">知识库命中</div>
          <div class="stat-trend">
            <el-icon class="trend-icon"><TrendCharts /></el-icon>
            <span class="trend-text">命中率 {{ (summary.avg_kb_hit_rate * 100 || 0).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card stat-card-warning">
        <div class="stat-icon">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_ai_suggestions || 0 }}</div>
          <div class="stat-label">AI建议</div>
          <div class="stat-trend">
            <el-icon class="trend-icon"><TrendCharts /></el-icon>
            <span class="trend-text">建议率 {{ ((summary.total_ai_suggestions / summary.total_messages) * 100 || 0).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card stat-card-info">
        <div class="stat-icon">
          <el-icon><PieChart /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ (summary.avg_kb_hit_rate * 100 || 0).toFixed(1) }}%</div>
          <div class="stat-label">知识库命中率</div>
          <div class="stat-trend">
            <el-icon class="trend-icon"><TrendCharts /></el-icon>
            <span class="trend-text">较昨日 +5.2%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">
              <el-icon class="chart-icon"><TrendCharts /></el-icon>
              <span>消息量趋势</span>
            </div>
            <div class="chart-actions">
              <el-button size="small" text>
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </div>
          <div class="chart-content">
            <div ref="messageTrendChart" class="chart-container"></div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">
              <el-icon class="chart-icon"><PieChart /></el-icon>
              <span>处理方式分布</span>
            </div>
            <div class="chart-actions">
              <el-button size="small" text>
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </div>
          <div class="chart-content">
            <div ref="processTypeChart" class="chart-container"></div>
          </div>
        </div>
      </div>
      
      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">
              <el-icon class="chart-icon"><Collection /></el-icon>
              <span>知识库统计</span>
            </div>
            <div class="chart-actions">
              <el-button size="small" text>
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </div>
          <div class="chart-content">
            <div ref="kbStatsChart" class="chart-container"></div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">
              <el-icon class="chart-icon"><MagicStick /></el-icon>
              <span>AI模型性能</span>
            </div>
            <div class="chart-actions">
              <el-button size="small" text>
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </div>
          <div class="chart-content">
            <div ref="modelPerformanceChart" class="chart-container"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细数据表格 -->
    <div class="table-section">
      <el-card class="table-card">
        <div class="table-header">
          <div class="table-title">
            <el-icon class="table-icon"><Grid /></el-icon>
            <span>日统计数据</span>
          </div>
          <div class="table-actions">
            <el-button size="small" type="primary" :icon="Download">
              导出Excel
            </el-button>
            <el-button size="small" :icon="Refresh" @click="loadData">
              刷新
            </el-button>
          </div>
        </div>
        <div class="table-content">
          <el-table 
            :data="dailyData" 
            class="data-table"
            v-loading="loading"
            stripe
            border
            :header-cell-style="{ background: '#f8f9fa', color: '#606266' }"
          >
            <el-table-column prop="date" label="日期" width="120" align="center">
              <template #default="{ row }">
                <span class="date-cell">{{ row.date }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total_messages" label="消息总数" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="primary" size="small">{{ row.total_messages }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="kb_hits" label="知识库命中" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="success" size="small">{{ row.kb_hits }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="ai_suggestions" label="AI建议" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="warning" size="small">{{ row.ai_suggestions }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="auto_sent" label="自动发送" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="info" size="small">{{ row.auto_sent }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="manual_reviewed" label="人工审核" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="danger" size="small">{{ row.manual_reviewed }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="kb_hit_rate" label="知识库命中率" width="120" align="center">
              <template #default="{ row }">
                <div class="rate-cell">
                  <el-progress 
                    :percentage="(row.kb_hit_rate * 100).toFixed(1)" 
                    :stroke-width="8"
                    :show-text="false"
                    color="#67c23a"
                  />
                  <span class="rate-text">{{ (row.kb_hit_rate * 100).toFixed(1) }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="auto_send_rate" label="自动发送率" width="120" align="center">
              <template #default="{ row }">
                <div class="rate-cell">
                  <el-progress 
                    :percentage="(row.auto_send_rate * 100).toFixed(1)" 
                    :stroke-width="8"
                    :show-text="false"
                    color="#409eff"
                  />
                  <span class="rate-text">{{ (row.auto_send_rate * 100).toFixed(1) }}%</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import http from '../api/http'
import { ElMessage } from 'element-plus'
import { 
  DataAnalysis, 
  Refresh, 
  Search, 
  RefreshLeft, 
  ChatDotRound, 
  Collection, 
  MagicStick, 
  PieChart, 
  TrendCharts, 
  Download, 
  Grid 
} from '@element-plus/icons-vue'

// 数据状态
const loading = ref(false)
const dailyData = ref<any[]>([])
const summary = ref<any>({})
const kbStats = ref<any>({})
const performanceStats = ref<any>({})

// 筛选条件
const filters = reactive({
  dateRange: null as any
})

// 图表引用
const messageTrendChart = ref()
const processTypeChart = ref()
const kbStatsChart = ref()
const modelPerformanceChart = ref()

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.append('start_date', filters.dateRange[0])
      params.append('end_date', filters.dateRange[1])
    }
    
    // 加载日统计数据
    const dailyRes = await http.get(`/api/statistics/daily?${params}`)
    dailyData.value = dailyRes.data.daily_data
    summary.value = dailyRes.data.summary
    
    // 加载知识库统计
    const kbRes = await http.get('/api/statistics/knowledge_base')
    kbStats.value = kbRes.data
    
    // 加载性能统计
    const perfRes = await http.get('/api/statistics/performance')
    performanceStats.value = perfRes.data
    
    // 渲染图表
    await nextTick()
    renderCharts()
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选条件
const resetFilters = () => {
  filters.dateRange = null
  loadData()
}

// 渲染消息量趋势图
const renderMessageTrendChart = () => {
  if (!messageTrendChart.value) return
  
  const chart = echarts.init(messageTrendChart.value)
  const dates = dailyData.value.map(item => item.date)
  const messages = dailyData.value.map(item => item.total_messages)
  const kbHits = dailyData.value.map(item => item.kb_hits)
  const aiSuggestions = dailyData.value.map(item => item.ai_suggestions)
  
  const option = {
    title: {
      text: '消息处理趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['总消息数', '知识库命中', 'AI建议'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '总消息数',
        type: 'line',
        data: messages,
        smooth: true
      },
      {
        name: '知识库命中',
        type: 'line',
        data: kbHits,
        smooth: true
      },
      {
        name: 'AI建议',
        type: 'line',
        data: aiSuggestions,
        smooth: true
      }
    ]
  }
  
  chart.setOption(option)
}

// 渲染处理方式分布图
const renderProcessTypeChart = () => {
  if (!processTypeChart.value) return
  
  const chart = echarts.init(processTypeChart.value)
  const total = summary.value.total_messages || 1
  
  const option = {
    title: {
      text: '处理方式分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '处理方式',
        type: 'pie',
        radius: '50%',
        data: [
          { value: summary.value.total_kb_hits, name: '知识库命中' },
          { value: summary.value.total_ai_suggestions, name: 'AI建议' },
          { value: summary.value.total_manual_reviewed, name: '人工审核' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 渲染知识库统计图
const renderKbStatsChart = () => {
  if (!kbStatsChart.value) return
  
  const chart = echarts.init(kbStatsChart.value)
  
  const option = {
    title: {
      text: '知识库分类统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        name: '知识库条目',
        type: 'pie',
        radius: '50%',
        data: kbStats.value.by_category || [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 渲染AI模型性能图
const renderModelPerformanceChart = () => {
  if (!modelPerformanceChart.value) return
  
  const chart = echarts.init(modelPerformanceChart.value)
  const modelStats = performanceStats.value.model_performance || {}
  
  const models = Object.keys(modelStats)
  const counts = models.map(model => modelStats[model].count)
  const confidences = models.map(model => modelStats[model].avg_confidence)
  
  const option = {
    title: {
      text: 'AI模型使用情况',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['使用次数', '平均置信度'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: models
    },
    yAxis: [
      {
        type: 'value',
        name: '使用次数',
        position: 'left'
      },
      {
        type: 'value',
        name: '平均置信度',
        position: 'right',
        max: 1
      }
    ],
    series: [
      {
        name: '使用次数',
        type: 'bar',
        data: counts
      },
      {
        name: '平均置信度',
        type: 'line',
        yAxisIndex: 1,
        data: confidences
      }
    ]
  }
  
  chart.setOption(option)
}

// 渲染所有图表
const renderCharts = () => {
  renderMessageTrendChart()
  renderProcessTypeChart()
  renderKbStatsChart()
  renderModelPerformanceChart()
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* 页面整体样式 */
.statistics-page {
  padding: 0;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px 32px;
  margin-bottom: 24px;
  border-radius: 0 0 16px 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
  color: #ffd700;
}

.page-subtitle {
  font-size: 16px;
  margin: 0;
  opacity: 0.9;
  font-weight: 400;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 筛选条件 */
.filter-card {
  margin: 0 32px 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: none;
}

.filter-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.filter-form {
  margin: 0;
}

.filter-item {
  margin: 0;
}

.date-picker {
  width: 280px;
}

.filter-right {
  display: flex;
  gap: 12px;
}

.query-btn, .reset-btn {
  border-radius: 8px;
  font-weight: 500;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin: 0 32px 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2);
}

.stat-card-primary::before { background: linear-gradient(90deg, #409eff, #67c23a); }
.stat-card-success::before { background: linear-gradient(90deg, #67c23a, #85ce61); }
.stat-card-warning::before { background: linear-gradient(90deg, #e6a23c, #f56c6c); }
.stat-card-info::before { background: linear-gradient(90deg, #909399, #409eff); }

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.stat-card-primary .stat-icon { background: linear-gradient(135deg, #409eff, #67c23a); }
.stat-card-success .stat-icon { background: linear-gradient(135deg, #67c23a, #85ce61); }
.stat-card-warning .stat-icon { background: linear-gradient(135deg, #e6a23c, #f56c6c); }
.stat-card-info .stat-icon { background: linear-gradient(135deg, #909399, #409eff); }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #67c23a;
}

.trend-icon {
  font-size: 14px;
}

.trend-text {
  font-weight: 500;
}

/* 图表区域 */
.charts-section {
  margin: 0 32px 32px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafbfc;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.chart-icon {
  font-size: 18px;
  color: #409eff;
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.chart-content {
  padding: 20px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* 表格区域 */
.table-section {
  margin: 0 32px 32px;
}

.table-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafbfc;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.table-icon {
  font-size: 18px;
  color: #409eff;
}

.table-actions {
  display: flex;
  gap: 12px;
}

.table-content {
  padding: 0;
}

.data-table {
  border: none;
}

.date-cell {
  font-weight: 500;
  color: #2c3e50;
}

.rate-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rate-text {
  font-size: 12px;
  font-weight: 600;
  color: #2c3e50;
  min-width: 40px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    margin: 0 20px 20px;
  }
  
  .charts-section,
  .table-section {
    margin: 0 20px 20px;
  }
  
  .filter-card {
    margin: 0 20px 20px;
  }
  
  .filter-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filter-right {
    justify-content: center;
  }
}
</style>

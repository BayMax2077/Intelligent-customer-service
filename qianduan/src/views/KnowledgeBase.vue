<template>
  <div class="page">
    <h2 class="title">
      知识库管理
      <el-tooltip content="管理智能回复的知识库条目，支持批量导入导出" placement="right">
        <el-icon style="margin-left:6px;color:#909399"><WarningFilled/></el-icon>
      </el-tooltip>
    </h2>
    <p class="sub">维护问答知识库，支持向量检索和关键词匹配，提高自动回复准确率。</p>
    
    <!-- 操作栏 -->
    <el-space style="margin:8px 0 12px">
      <el-button type="primary" @click="load">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
      <el-button type="primary" @click="showCategoryManager">
        <el-icon><Setting /></el-icon>
        分类管理
      </el-button>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        新增条目
      </el-button>
      <el-button type="primary" @click="showImportDialog">
        <el-icon><Upload /></el-icon>
        批量导入
      </el-button>
      <el-button type="primary" @click="exportData">
        <el-icon><Download /></el-icon>
        导出数据
      </el-button>
      <el-button type="primary" @click="goToTaskCenter">
        <el-icon><List /></el-icon>
        导入任务中心
      </el-button>
    </el-space>



    <!-- 筛选栏 -->
    <el-card class="filter-card" style="margin-bottom: 16px;">
      <el-form :inline="true" :model="filters">
        <el-form-item label="条目归属">
          <el-select v-model="filters.shop_id" placeholder="选择条目归属" clearable style="width: 200px;">
            <el-option label="全局知识库" :value="GLOBAL_SHOP_ID" />
            <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.category" placeholder="选择分类" clearable filterable allow-create style="width: 200px;">
            <el-option v-for="category in categories" :key="category" :label="category" :value="category" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格区域 -->
    <div class="table-container">
      <!-- 表格控制栏 -->
      <div class="table-controls">
      </div>

    <!-- 数据表格 -->
      <el-table 
        :data="items" 
        style="width: 100%" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="shop_id" label="条目归属" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.shop_id" type="primary">{{ getShopName(row.shop_id) }}</el-tag>
          <el-tag v-else type="info">全局知识库</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="answer" label="答案" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="keywords" label="关键词" width="150" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editItem(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteItem(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    </div>

    <!-- 分页和全选控制 -->
    <div class="pagination-container">
      <div class="pagination-left">
        <el-checkbox 
          v-model="selectAllData" 
          @change="handleSelectAllData"
          class="select-all-checkbox"
        >
          全选 ({{ selectedItems.length }}/{{ items.length }})
        </el-checkbox>
        
        <el-button 
          v-if="selectedItems.length > 0" 
          type="danger" 
          size="small"
          @click="showBulkDeleteDialog"
          :loading="bulkDeleting"
          style="margin-left: 12px;"
        >
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedItems.length }})
        </el-button>
      </div>
      
      <div class="pagination-right">
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.per_page"
      :page-sizes="[10, 20, 50, 100]"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="load"
      @current-change="load"
    />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog 
      :title="dialogMode === 'add' ? '新增知识库条目' : '编辑知识库条目'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="条目归属" prop="shop_id">
          <el-select v-model="form.shop_id" placeholder="选择条目归属" clearable style="width: 100%;">
            <el-option label="全局知识库" :value="GLOBAL_SHOP_ID" />
            <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题" prop="question">
          <el-input v-model="form.question" type="textarea" :rows="3" placeholder="输入问题描述" />
        </el-form-item>
        <el-form-item label="答案" prop="answer">
          <el-input v-model="form.answer" type="textarea" :rows="4" placeholder="输入标准答案" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="选择分类" clearable filterable allow-create style="width: 100%;">
            <el-option v-for="category in categories" :key="category" :label="category" :value="category" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="form.keywords" placeholder="用逗号分隔，如：退款,退货,售后" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理对话框 -->
    <el-dialog title="分类管理" v-model="categoryDialogVisible" width="600px">
      <div class="category-manager">
        <div class="category-list">
          <h4>现有分类</h4>
          <div class="category-tags">
            <el-tag 
              v-for="category in categories" 
              :key="category" 
              closable 
              @close="deleteCategory(category)"
              style="margin: 4px;"
            >
              {{ category }}
            </el-tag>
            <el-tag v-if="categories.length === 0" type="info">暂无分类</el-tag>
          </div>
        </div>
        
        <el-divider />
        
        <div class="add-category">
          <h4>添加新分类</h4>
          <el-form :model="newCategoryForm" inline>
            <el-form-item label="分类名称">
              <el-input v-model="newCategoryForm.name" placeholder="输入新分类名称" style="width: 200px;" />
        </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="addCategory" :disabled="!newCategoryForm.name.trim()">添加</el-button>
        </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="refreshCategories">刷新分类</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog title="批量导入知识库" v-model="importDialogVisible" width="700px" class="import-dialog">
      <div class="import-content">
        <!-- 文件操作区域 -->
        <div class="file-operations">
          <div class="operation-section">
            <h4 class="section-title">
              <el-icon><Upload /></el-icon>
              文件操作
            </h4>
            <div class="operation-buttons">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
                accept=".xlsx,.xls"
            :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :file-list="fileList"
                :show-file-list="true"
                class="upload-component"
              >
                <el-button type="primary" size="large">
                  <el-icon><Upload /></el-icon>
                  选择Excel文件
                </el-button>
              </el-upload>
              <el-button 
                type="info" 
                size="large" 
                @click="downloadTemplate" 
                :loading="downloadingTemplate"
                class="template-btn"
              >
                <el-icon><Download /></el-icon>
                下载Excel模板
              </el-button>
            </div>
            
            <!-- 文件信息显示 -->
            <div v-if="importForm.file" class="file-info">
              <el-card class="file-card">
                <div class="file-details">
                  <div class="file-icon">
                    <el-icon size="24"><Document /></el-icon>
                  </div>
                  <div class="file-content">
                    <div class="file-name">{{ importForm.file.name }}</div>
                    <div class="file-meta">
                      <span class="file-size">{{ formatFileSize(importForm.file.size) }}</span>
                      <span class="file-type">{{ getFileType(importForm.file.name) }}</span>
                    </div>
                    <div class="file-status">
                      <el-tag type="success" size="small">已选择</el-tag>
                    </div>
                  </div>
                  <div class="file-actions">
                    <el-button 
                      type="danger" 
                      size="small" 
                      @click="removeFile"
                      :icon="Close"
                    >
                      移除
                    </el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </div>

        <!-- 帮助提示区域 -->
        <div class="help-section">
          <div class="help-items">
            <el-tooltip 
              effect="dark" 
              placement="top" 
              :show-arrow="true"
              popper-class="help-tooltip"
            >
              <template #content>
                <div class="tooltip-content">
                  <h4>📋 操作步骤</h4>
                  <ol>
                    <li>点击"下载模板"按钮，获取标准Excel模板</li>
                    <li>在模板中填写知识库数据，确保格式正确</li>
                    <li>选择填写好的Excel文件进行上传</li>
                    <li>确认导入设置，开始批量导入</li>
                  </ol>
              </div>
            </template>
              <div class="help-item">
                <el-icon><InfoFilled /></el-icon>
                <span>操作说明</span>
              </div>
            </el-tooltip>

            <el-tooltip 
              effect="dark" 
              placement="top" 
              :show-arrow="true"
              popper-class="help-tooltip"
            >
              <template #content>
                <div class="tooltip-content">
                  <h4>📋 Excel格式要求</h4>
                  <div class="format-list">
                    <div class="format-item">
                      <el-icon class="required"><Check /></el-icon>
                      <span><strong>问题（必填）</strong> - 客户可能提出的问题</span>
                    </div>
                    <div class="format-item">
                      <el-icon class="required"><Check /></el-icon>
                      <span><strong>答案（必填）</strong> - 对应问题的标准答案</span>
                    </div>
                    <div class="format-item">
                      <el-icon class="required"><Check /></el-icon>
                      <span><strong>分类（必填）</strong> - 问题分类，如：售前、售后、技术等</span>
                    </div>
                    <div class="format-item">
                      <el-icon class="optional"><Minus /></el-icon>
                      <span><strong>条目归属（可选）</strong> - 选择店铺或全局知识库</span>
                    </div>
                    <div class="format-item">
                      <el-icon class="optional"><Minus /></el-icon>
                      <span><strong>标签（可选）</strong> - 用于搜索的关键词，多个用逗号分隔</span>
                    </div>
                  </div>
                  <div class="format-note">
                    <p><strong>文件格式：</strong>.xlsx 或 .xls</p>
                  </div>
                </div>
              </template>
              <div class="help-item">
                <el-icon><Document /></el-icon>
                <span>格式要求</span>
              </div>
            </el-tooltip>

            <el-tooltip 
              effect="dark" 
              placement="top" 
              :show-arrow="true"
              popper-class="help-tooltip"
            >
              <template #content>
                <div class="tooltip-content">
                  <h4>⚠️ 重要提醒</h4>
                  <div class="warning-list">
                    <div class="warning-item">
                      <el-icon><InfoFilled /></el-icon>
                      <span>请确保Excel文件格式正确，表头与模板一致</span>
                    </div>
                    <div class="warning-item">
                      <el-icon><InfoFilled /></el-icon>
                      <span>必填字段不能为空，否则导入会失败</span>
                    </div>
                    <div class="warning-item">
                      <el-icon><InfoFilled /></el-icon>
                      <span>建议单次导入不超过1000条记录</span>
                    </div>
                    <div class="warning-item">
                      <el-icon><InfoFilled /></el-icon>
                      <span>导入过程中请勿关闭浏览器</span>
                    </div>
                  </div>
                  <div class="config-info">
                    <p><strong>系统自动配置：</strong></p>
                    <ul>
                      <li>✅ 跳过重复数据：自动跳过已存在的知识库条目</li>
                      <li>✅ 自动创建店铺：自动创建不存在的店铺</li>
                      <li>✅ 数据验证：严格验证数据格式和必填字段</li>
                      <li>✅ 生成向量：自动生成向量嵌入用于智能搜索</li>
                    </ul>
                  </div>
                </div>
              </template>
              <div class="help-item">
                <el-icon><WarningFilled /></el-icon>
                <span>注意事项</span>
              </div>
            </el-tooltip>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="importDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" @click="importData" :loading="importing" size="large">
            <el-icon><Upload /></el-icon>
            开始导入
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入任务中心 -->
    <el-dialog 
      title="导入任务中心" 
      v-model="showImportMonitor" 
      width="800px" 
      class="import-task-center-dialog"
      :close-on-click-modal="false"
    >
      <div class="monitor-content">
        <!-- 导入进度 -->
        <div class="progress-section">
          <div class="progress-header">
            <h3>导入进度</h3>
            <div class="progress-stats">
              <span v-if="importStats">
                总行数: {{ importStats.total_rows }} | 
                已处理: {{ importStats.processed_rows }} | 
                成功: {{ importStats.success_count }} | 
                失败: {{ importStats.error_count }}
              </span>
            </div>
          </div>
          <el-progress 
            :percentage="Math.round(importProgress * 10) / 10" 
            :status="importProgress === 100 ? 'success' : 'active'"
            :stroke-width="8"
            :show-text="true"
          />
          <div class="progress-text">
            {{ Math.round(importProgress * 10) / 10 }}%
          </div>
        </div>

        <!-- 性能指标 -->
        <div class="performance-section" v-if="importStats">
          <h3>性能指标</h3>
          <div class="performance-grid">
            <div class="performance-card">
              <div class="card-title">处理速度</div>
              <div class="card-value">{{ importPerformance.rows_per_second || 0 }} 行/秒</div>
            </div>
            <div class="performance-card">
              <div class="card-title">成功率</div>
              <div class="card-value">{{ importPerformance.success_rate || 0 }}%</div>
            </div>
            <div class="performance-card">
              <div class="card-title">错误率</div>
              <div class="card-value">{{ importPerformance.error_rate || 0 }}%</div>
            </div>
            <div class="performance-card">
              <div class="card-title">处理时间</div>
              <div class="card-value">{{ importStats.processing_time || 0 }}秒</div>
            </div>
            <div class="performance-card">
              <div class="card-title">向量生成</div>
              <div class="card-value">{{ importStats.vector_success || 0 }}成功 / {{ importStats.vector_failed || 0 }}失败</div>
            </div>
            <div class="performance-card">
              <div class="card-title">向量耗时</div>
              <div class="card-value">{{ importStats.vector_time || 0 }}秒</div>
            </div>
          </div>
        </div>

        <!-- 店铺统计 -->
        <div class="shop-stats-section" v-if="importStats?.shop_stats">
          <h3>店铺分布统计</h3>
          <div class="shop-stats-grid">
            <div 
              v-for="(count, shopName) in importStats.shop_stats" 
              :key="shopName"
              class="shop-stat-item"
            >
              <div class="shop-name">{{ shopName }}</div>
              <div class="shop-count">{{ count }} 条</div>
            </div>
          </div>
        </div>


        <!-- 智能错误分析 -->
        <div class="error-analysis-section" v-if="importStats?.errorAnalysis">
          <h3>智能错误分析</h3>
          <div class="analysis-content">
            <div class="analysis-summary">
              <div class="summary-item">
                <span class="summary-label">常见问题：</span>
                <span class="summary-value">{{ importStats.errorAnalysis.commonIssues.join(', ') || '无' }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">错误类型分布：</span>
                <span class="summary-value">
                  必填字段缺失: {{ importStats.errorAnalysis.errorTypes.missingFields }} | 
                  店铺不存在: {{ importStats.errorAnalysis.errorTypes.invalidShops }} | 
                  数据格式错误: {{ importStats.errorAnalysis.errorTypes.dataFormat }} | 
                  其他: {{ importStats.errorAnalysis.errorTypes.other }}
                </span>
              </div>
            </div>
            <div class="suggestions" v-if="importStats.errorAnalysis.suggestions.length > 0">
              <h4>修复建议：</h4>
              <ul>
                <li v-for="(suggestion, index) in importStats.errorAnalysis.suggestions" :key="index">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 错误详情 -->
        <div class="errors-section" v-if="importErrors.length > 0">
          <h3>错误详情 ({{ importErrors.length }} 个错误)</h3>
          <div class="errors-container">
            <div 
              v-for="(error, index) in importErrors" 
              :key="index"
              class="error-item"
            >
              {{ error }}
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="monitor-footer">
          <el-button @click="closeTaskCenter" size="large">关闭</el-button>
          <el-button 
            type="primary" 
            @click="goToTaskCenter" 
            size="large"
          >
            <el-icon><View /></el-icon>
            前往任务中心
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 全量删除确认对话框 -->
    <el-dialog
      v-model="bulkDeleteDialogVisible"
      title="全量删除确认"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="bulk-delete-content">
        <div class="warning-section">
          <el-icon size="24" color="#f56c6c"><WarningFilled /></el-icon>
          <div class="warning-text">
            <h3>⚠️ 确认全量删除</h3>
            <p>您即将删除 <strong>{{ items.length }}</strong> 条知识库条目，此操作不可恢复！</p>
          </div>
        </div>
        
        <div class="delete-warning">
          <h4>⚠️ 删除警告：</h4>
          <ul>
            <li>删除的知识库条目将无法恢复</li>
            <li>相关的向量数据也会被清除</li>
            <li>可能影响AI自动回复的准确性</li>
            <li>建议在删除前先导出备份</li>
          </ul>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="bulkDeleteDialogVisible = false">取消</el-button>
          <el-button 
            type="danger" 
            @click="confirmBulkDelete"
            :loading="bulkDeleting"
          >
            确认删除全部 {{ items.length }} 条
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量删除确认对话框 -->
    <el-dialog
      v-model="batchDeleteDialogVisible"
      title="批量删除确认"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="batch-delete-content">
        <div class="warning-section">
          <el-icon size="24" color="#f56c6c"><WarningFilled /></el-icon>
          <div class="warning-text">
            <h3>⚠️ 确认批量删除</h3>
            <p>您即将删除 <strong>{{ selectedItems.length }}</strong> 条知识库条目，此操作不可恢复！</p>
          </div>
        </div>
        
        <div class="delete-preview">
          <h4>即将删除的条目：</h4>
          <div class="preview-list">
            <div 
              v-for="item in selectedItems.slice(0, 5)" 
              :key="item.id"
              class="preview-item"
            >
              <span class="item-id">#{{ item.id }}</span>
              <span class="item-question">{{ item.question }}</span>
              <el-tag size="small" :type="item.shop_id ? 'primary' : 'info'">
                {{ item.shop_id ? getShopName(item.shop_id) : '全局知识库' }}
              </el-tag>
            </div>
            <div v-if="selectedItems.length > 5" class="more-items">
              ... 还有 {{ selectedItems.length - 5 }} 条记录
            </div>
          </div>
        </div>
        
        <div class="delete-warning">
          <h4>⚠️ 删除警告：</h4>
          <ul>
            <li>删除的知识库条目将无法恢复</li>
            <li>相关的向量数据也会被清除</li>
            <li>可能影响AI自动回复的准确性</li>
            <li>建议在删除前先导出备份</li>
          </ul>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="batchDeleteDialogVisible = false">取消</el-button>
          <el-button 
            type="danger" 
            @click="confirmBatchDelete"
            :loading="batchDeleting"
          >
            确认删除 {{ selectedItems.length }} 条
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '../api/http'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled, Download, Upload, Document, Check, Warning, InfoFilled, Setting, Close, View, Delete, Refresh, Plus, List } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

// 数据状态
const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const downloadingTemplate = ref(false)
const batchDeleting = ref(false)
const items = ref<any[]>([])
const shops = ref<any[]>([])
const categories = ref<string[]>([])
const selectedItems = ref<any[]>([])
const batchDeleteDialogVisible = ref(false)
const bulkDeleteDialogVisible = ref(false)
const selectAllData = ref(false)
const bulkDeleting = ref(false)
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
})

// 导入监控状态
const importStats = ref<any>(null)
const showImportMonitor = ref(false)
const importProgress = ref(0)
const importLogs = ref<string[]>([])
const importErrors = ref<string[]>([])
const importPerformance = ref<any>({})

// 导入配置（后端写死，前端只显示说明）
const importConfig = reactive({
  skipDuplicates: true,
  autoCreateShops: true,
  validateData: true,
  generateVectors: true
})

// 筛选条件
const filters = reactive({
  shop_id: null as number | null,
  category: ''
})

// 全局知识库的特殊值
const GLOBAL_SHOP_ID = -1

// 对话框状态
const dialogVisible = ref(false)
const importDialogVisible = ref(false)
const categoryDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')

// 表单数据
const form = reactive({
  id: null,
  shop_id: null,
  question: '',
  answer: '',
  category: '',
  keywords: ''
})

const importForm = reactive({
  file: null as File | null
})

// 文件列表
const fileList = ref<any[]>([])
const uploadRef = ref()

const newCategoryForm = reactive({
  name: ''
})

// 表单验证规则
const rules = {
  shop_id: [{ required: true, message: '请选择条目归属', trigger: 'change' }],
  question: [{ required: true, message: '请输入问题', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入答案', trigger: 'blur' }]
}

const formRef = ref()

// 加载数据
const load = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.page.toString(),
      per_page: pagination.per_page.toString()
    })
    
    if (filters.shop_id !== null && filters.shop_id !== undefined && filters.shop_id !== GLOBAL_SHOP_ID) {
      params.append('shop_id', filters.shop_id.toString())
    }
    if (filters.category) {
      params.append('category', filters.category)
    }
    
    const res = await http.get(`/api/kb?${params}`)
    items.value = res.data.items
    pagination.total = res.data.total
    pagination.pages = res.data.pages
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载条目归属列表
const loadShops = async () => {
  try {
    const res = await http.get('/api/shops')
    shops.value = res.data
  } catch (error) {
    console.error('加载条目归属列表失败:', error)
  }
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const res = await http.get('/api/kb/categories')
    categories.value = res.data
  } catch (error) {
    console.error('加载分类列表失败:', error)
  }
}

// 获取条目归属名称
const getShopName = (shopId: number) => {
  const shop = shops.value.find(s => s.id === shopId)
  return shop ? shop.name : `条目归属${shopId}`
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 重置筛选条件
const resetFilters = () => {
  filters.shop_id = null
  filters.category = ''
  pagination.page = 1
  load()
}

// 显示新增对话框
const showAddDialog = () => {
  dialogMode.value = 'add'
  Object.assign(form, {
    id: null,
    shop_id: null,
    question: '',
    answer: '',
    category: '',
    keywords: ''
  })
  dialogVisible.value = true
}

// 编辑条目
const editItem = (row: any) => {
  dialogMode.value = 'edit'
  Object.assign(form, {
    id: row.id,
    shop_id: row.shop_id === null ? GLOBAL_SHOP_ID : row.shop_id,
    question: row.question,
    answer: row.answer,
    category: row.category || '',
    keywords: row.keywords || ''
  })
  dialogVisible.value = true
}

// 保存条目
const saveItem = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    saving.value = true
    
    // 处理全局知识库的特殊值
    const formData = { ...form }
    if (formData.shop_id === GLOBAL_SHOP_ID) {
      formData.shop_id = null
    }
    
    if (dialogMode.value === 'add') {
      await http.post('/api/kb', formData)
      ElMessage.success('新增成功')
    } else {
      await http.put(`/api/kb/${form.id}`, formData)
      ElMessage.success('更新成功')
      // 就地更新前端表格数据，避免需要手动刷新才能看到变化
      const updatedShopId = form.shop_id === GLOBAL_SHOP_ID ? null : form.shop_id
      const idx = items.value.findIndex((it: any) => it.id === form.id)
      if (idx !== -1) {
        // 直接修改对象属性，确保Vue响应式系统能检测到变化
        items.value[idx].shop_id = updatedShopId
        items.value[idx].question = form.question
        items.value[idx].answer = form.answer
        items.value[idx].category = form.category
        items.value[idx].keywords = form.keywords
        
        // 如果当前筛选与更新后的归属不一致，则从当前列表移除，保持显示一致
        const filterShopId = (filters.shop_id !== null && filters.shop_id !== undefined && filters.shop_id !== GLOBAL_SHOP_ID) ? filters.shop_id : null
        if (filterShopId !== null && filterShopId !== updatedShopId) {
          items.value.splice(idx, 1)
          pagination.total = Math.max(0, pagination.total - 1)
        }
      }
    }
    
    dialogVisible.value = false
    // 后台数据为准，做一次轻量刷新以确保分页与统计正确
    await load()
    await loadCategories() // 重新加载分类列表
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 删除条目
const deleteItem = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条知识库条目吗？', '确认删除', {
      type: 'warning'
    })
    
    await http.delete(`/api/kb/${row.id}`)
    ElMessage.success('删除成功')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 处理表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedItems.value = selection
}

// 清空选择
const clearSelection = () => {
  selectedItems.value = []
  // 清空表格选择
  const table = document.querySelector('.el-table')
  if (table) {
    const checkboxes = table.querySelectorAll('input[type="checkbox"]')
    checkboxes.forEach((checkbox: any) => {
      checkbox.checked = false
    })
  }
}

// 显示批量删除对话框
const showBatchDeleteDialog = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请先选择要删除的条目')
    return
  }
  batchDeleteDialogVisible.value = true
}

// 确认批量删除
const confirmBatchDelete = async () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('没有选择要删除的条目')
    return
  }
  
  batchDeleting.value = true
  try {
    const itemIds = selectedItems.value.map(item => item.id)
    
    const response = await http.post('/api/kb/batch-delete', {
      item_ids: itemIds,
      confirm: true
    })
    
    if (response.data.ok) {
      ElMessage.success(`成功删除 ${response.data.deleted_count} 条知识库条目`)
      
      // 清空选择
      clearSelection()
      
      // 关闭对话框
      batchDeleteDialogVisible.value = false
      
      // 重新加载数据
      await load()
    } else {
      ElMessage.error(response.data.message || '批量删除失败')
    }
  } catch (error: any) {
    console.error('批量删除失败:', error)
    
    let errorMessage = '批量删除失败'
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.response?.data?.detail) {
      errorMessage = `批量删除失败：${error.response.data.detail}`
    }
    
    ElMessage.error(errorMessage)
  } finally {
    batchDeleting.value = false
  }
}

// 处理全量选择
const handleSelectAllData = (checked: boolean) => {
  if (checked) {
    selectAllData.value = true
    // 自动选择当前页面的所有条目
    selectedItems.value = [...items.value]
  } else {
    selectAllData.value = false
    selectedItems.value = []
  }
}

// 显示全量删除对话框
const showBulkDeleteDialog = () => {
  if (!selectAllData.value) {
    ElMessage.warning('请先选择全量数据')
    return
  }
  bulkDeleteDialogVisible.value = true
}

// 确认全量删除
const confirmBulkDelete = async () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('没有选择要删除的条目')
    return
  }
  
  bulkDeleting.value = true
  try {
    const itemIds = selectedItems.value.map(item => item.id)
    
    const response = await http.post('/api/kb/batch-delete', {
      item_ids: itemIds,
      confirm: true
    })
    
    if (response.data.ok) {
      ElMessage.success(`成功删除 ${response.data.deleted_count} 条知识库条目`)
      
      // 清空选择
      selectAllData.value = false
      selectedItems.value = []
      
      // 关闭对话框
      bulkDeleteDialogVisible.value = false
      
      // 重新加载数据
      await load()
    } else {
      ElMessage.error(response.data.message || '全量删除失败')
    }
  } catch (error: any) {
    console.error('全量删除失败:', error)
    
    let errorMessage = '全量删除失败'
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.response?.data?.detail) {
      errorMessage = `全量删除失败：${error.response.data.detail}`
    }
    
    ElMessage.error(errorMessage)
  } finally {
    bulkDeleting.value = false
  }
}

// 显示分类管理对话框
const showCategoryManager = () => {
  categoryDialogVisible.value = true
}

// 添加新分类
const addCategory = () => {
  if (!newCategoryForm.name.trim()) return
  
  const categoryName = newCategoryForm.name.trim()
  if (categories.value.includes(categoryName)) {
    ElMessage.warning('该分类已存在')
    return
  }
  
  // 这里只是添加到本地列表，实际分类会在创建知识库条目时自动添加
  categories.value.push(categoryName)
  categories.value.sort()
  newCategoryForm.name = ''
  ElMessage.success('分类添加成功')
}

// 删除分类
const deleteCategory = (category: string) => {
  ElMessageBox.confirm(`确定要删除分类"${category}"吗？`, '确认删除', {
    type: 'warning'
  }).then(() => {
    const index = categories.value.indexOf(category)
    if (index > -1) {
      categories.value.splice(index, 1)
      ElMessage.success('分类删除成功')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 刷新分类列表
const refreshCategories = async () => {
  await loadCategories()
  ElMessage.success('分类列表已刷新')
}

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true
  Object.assign(importForm, {
    shop_id: null,
    file: null
  })
  fileList.value = []
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 处理文件选择
const handleFileChange = (file: any) => {
  importForm.file = file.raw
  fileList.value = [file]
}

// 处理文件移除
const handleFileRemove = () => {
  importForm.file = null
  fileList.value = []
}

// 移除文件
const removeFile = () => {
  importForm.file = null
  fileList.value = []
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

// 获取文件类型
const getFileType = (filename: string) => {
  const ext = filename.split('.').pop()?.toLowerCase()
  const typeMap: Record<string, string> = {
    'xlsx': 'Excel 2007+',
    'xls': 'Excel 97-2003'
  }
  return typeMap[ext || ''] || '未知类型'
}

// 导入数据
// 下载Excel模板
const downloadTemplate = async () => {
  downloadingTemplate.value = true
  try {
    const response = await http.get('/api/kb/template', {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '知识库导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败')
  } finally {
    downloadingTemplate.value = false
  }
}

// 智能错误分析
const analyzeErrors = (errors: string[]) => {
  const analysis = {
    commonIssues: [] as string[],
    suggestions: [] as string[],
    errorTypes: {
      missingFields: 0,
      invalidShops: 0,
      dataFormat: 0,
      other: 0
    }
  }
  
  errors.forEach(error => {
    if (error.includes('必填字段')) {
      analysis.errorTypes.missingFields++
      if (!analysis.commonIssues.includes('必填字段缺失')) {
        analysis.commonIssues.push('必填字段缺失')
        analysis.suggestions.push('请检查Excel文件中的"问题"和"答案"列是否为空')
      }
    } else if (error.includes('店铺') && error.includes('不存在')) {
      analysis.errorTypes.invalidShops++
      if (!analysis.commonIssues.includes('店铺不存在')) {
        analysis.commonIssues.push('店铺不存在')
        analysis.suggestions.push('请检查"条目归属"列中的店铺名称是否正确，或先在店铺管理中创建对应店铺')
      }
    } else if (error.includes('格式') || error.includes('类型')) {
      analysis.errorTypes.dataFormat++
      if (!analysis.commonIssues.includes('数据格式错误')) {
        analysis.commonIssues.push('数据格式错误')
        analysis.suggestions.push('请检查Excel文件中的数据格式是否正确')
      }
    } else {
      analysis.errorTypes.other++
    }
  })
  
  return analysis
}

const importData = async () => {
  if (!importForm.file) {
    ElMessage.warning('请选择Excel文件')
    return
  }
  
  importing.value = true
  showImportMonitor.value = true
  importProgress.value = 0
  importLogs.value = []
  importErrors.value = []
  importStats.value = null
  
  try {
    const formData = new FormData()
    formData.append('file', importForm.file)
    formData.append('type', 'excel')  // 固定为Excel格式
    
    // 添加导入配置
    formData.append('skip_duplicates', importConfig.skipDuplicates.toString())
    formData.append('auto_create_shops', importConfig.autoCreateShops.toString())
    formData.append('validate_data', importConfig.validateData.toString())
    formData.append('generate_vectors', importConfig.generateVectors.toString())
    
    // 开始导入
    const res = await http.post('/api/kb/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    // 设置进度为100%
    importProgress.value = 100
    
    // 处理导入结果
    if (res.data.import_stats) {
      importStats.value = res.data.import_stats
      importLogs.value = res.data.import_stats.processing_log || []
      importErrors.value = res.data.import_stats.errors || []
      importPerformance.value = res.data.import_stats.performance || {}
      
      // 智能错误分析
      if (importErrors.value.length > 0) {
        const errorAnalysis = analyzeErrors(importErrors.value)
        importStats.value.errorAnalysis = errorAnalysis
      }
    }
    
    ElMessage.success(res.data.message)
    importDialogVisible.value = false
    load()
    loadCategories() // 重新加载分类列表
  } catch (error: any) {
    importProgress.value = 0
    console.error('导入失败:', error)
    
    // 处理错误响应
    if (error.response?.data) {
      const errorData = error.response.data
      
      // 显示具体的错误信息
      if (errorData.message) {
        ElMessage.error(`导入失败: ${errorData.message}`)
      } else if (errorData.error) {
        ElMessage.error(`导入失败: ${errorData.error}`)
      } else {
        ElMessage.error('导入失败: 未知错误')
      }
      
      // 如果有详细的错误信息，显示在监控面板中
      if (errorData.errors && errorData.errors.length > 0) {
        importErrors.value = errorData.errors
        importStats.value = {
          success_count: errorData.success_count || 0,
          error_count: errorData.error_count || 0,
          total_rows: errorData.total_rows || 0,
          success_rate: errorData.success_rate || 0
        }
        
        // 智能错误分析
        if (importErrors.value.length > 0) {
          const errorAnalysis = analyzeErrors(importErrors.value)
          importStats.value.errorAnalysis = errorAnalysis
        }
      }
      
      // 如果有处理日志，也显示
      if (errorData.processing_log) {
        importLogs.value = errorData.processing_log
      }
    } else {
      ElMessage.error('导入失败: 网络错误或服务器无响应')
    }
  } finally {
    importing.value = false
  }
}

// 导出数据
const exportData = async () => {
  try {
    const params = new URLSearchParams()
    if (filters.shop_id !== null) {
      params.append('shop_id', filters.shop_id.toString())
    }
    
    const response = await http.get(`/api/kb/export?${params}`, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `知识库条目_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Excel文件下载成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 关闭任务中心
const closeTaskCenter = () => {
  showImportMonitor.value = false
  ElMessage.info('任务中心已关闭，您可以通过顶部导航的"导入任务"按钮重新打开查看进度和历史')
}

// 前往任务中心
const goToTaskCenter = () => {
  showImportMonitor.value = false
  ElMessage.success('已跳转到任务中心，您可以查看导入进度和历史记录')
  // 跳转到任务中心页面
  router.push('/import-tasks')
}

// 初始化
onMounted(() => {
  loadShops()
  loadCategories()
  load()
  
  // 检查URL参数，如果action=import则打开导入对话框
  if (route.query.action === 'import') {
    showImportDialog()
    // 清除URL参数
    router.replace('/kb')
  }
})
</script>

<style scoped>
/* 紧凑布局优化 */
.page { 
  padding: 12px 16px; 
  max-height: calc(100vh - 64px);
  overflow-y: auto;
}

.title { 
  margin: 0 0 4px; 
  font-size: 18px;
}

/* 筛选栏紧凑化 */
.filter-card {
  margin-bottom: 12px !important;
}

.filter-card :deep(.el-card__body) {
  padding: 12px 16px !important;
}

/* 表格紧凑化 */
.data-table {
  margin-bottom: 12px;
}

.data-table :deep(.el-table__header) {
  height: 40px;
}

.data-table :deep(.el-table__body tr) {
  height: 36px;
}

.data-table :deep(.el-table td) {
  padding: 8px 12px !important;
}

.data-table :deep(.el-table th) {
  padding: 8px 12px !important;
}

/* 分页紧凑化 */
.pagination {
  margin-top: 12px;
  padding: 8px 0;
}

/* 对话框紧凑化 */
.dialog :deep(.el-dialog__body) {
  padding: 16px 20px !important;
}

.dialog :deep(.el-dialog__header) {
  padding: 12px 20px !important;
}

.dialog :deep(.el-dialog__footer) {
  padding: 12px 20px !important;
}

/* 表单紧凑化 */
.form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.form :deep(.el-form-item__label) {
  line-height: 1.2;
  padding-bottom: 4px;
}

/* 按钮组紧凑化 */
.toolbar {
  margin: 8px 0 12px;
  gap: 8px;
}

.toolbar .el-button {
  padding: 6px 12px;
  font-size: 13px;
}

/* 标签紧凑化 */
.el-tag {
  font-size: 12px;
  padding: 2px 6px;
  height: 20px;
  line-height: 16px;
}

/* 导入对话框紧凑化 */
.import-dialog :deep(.el-dialog__body) {
  padding: 16px !important;
}

.import-content {
  gap: 16px;
}

.file-operations {
  padding: 12px;
}

.operation-buttons {
  gap: 8px;
}

.operation-buttons .el-button {
  padding: 6px 12px;
  font-size: 13px;
}

/* 任务中心样式 */
.import-task-center-dialog :deep(.el-dialog) {
  width: 90% !important;
  max-width: 800px !important;
  max-height: 80vh !important;
}

.monitor-content {
  padding: 12px;
  gap: 12px;
  max-height: calc(80vh - 100px);
  overflow-y: auto;
}

.progress-section,
.performance-section,
.shop-stats-section,
.error-analysis-section,
.errors-section {
  padding: 12px;
}

.progress-header {
  margin-bottom: 8px;
}

.progress-stats {
  gap: 8px;
}

.stat-item {
  padding: 6px 8px;
  font-size: 12px;
}

.performance-grid {
  gap: 8px;
}

.performance-card {
  padding: 8px;
}

.performance-card h4 {
  font-size: 14px;
  margin: 0 0 4px;
}

.performance-card .value {
  font-size: 16px;
}

.shop-stats-grid {
  gap: 6px;
}

.shop-stat-card {
  padding: 6px 8px;
  font-size: 12px;
}


.analysis-content {
  gap: 8px;
}

.analysis-summary {
  padding: 8px;
}

.summary-item {
  margin-bottom: 4px;
  font-size: 12px;
}

.suggestions {
  padding: 8px;
}

.suggestions h4 {
  font-size: 14px;
  margin: 0 0 6px;
}

.suggestions li {
  font-size: 12px;
  margin-bottom: 4px;
}

.errors-container {
  max-height: 120px;
  padding: 8px;
}

.error-item {
  font-size: 12px;
  margin-bottom: 4px;
  padding: 2px 0;
}

.monitor-footer {
  padding: 8px 16px;
  gap: 8px;
}

.monitor-footer .el-button {
  padding: 6px 12px;
  font-size: 13px;
}

/* 导入对话框样式 */
.import-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.import-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.file-operations {
  background: var(--bg-secondary);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-light);
}

.operation-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.operation-buttons {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.upload-component {
  display: inline-block;
}

.upload-component .el-button {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  height: 40px;
  line-height: 1;
}

.template-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  height: 40px;
  line-height: 1;
}

.format-requirements {
  background: #f8fafc;
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-light);
}

.requirements-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.requirement-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 0;
  line-height: 1.5;
}

.requirement-icon {
  margin-top: 2px;
  flex-shrink: 0;
}

.requirement-item .el-icon.check {
  color: #67c23a;
}

.requirement-item .el-icon.warning {
  color: #e6a23c;
}

.requirement-item .el-icon.info {
  color: #409eff;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0 0;
  border-top: 1px solid var(--border-light);
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .operation-buttons {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .upload-component,
  .template-btn {
    width: 100%;
  }
  
  .upload-component .el-button,
  .template-btn {
    width: 100%;
    justify-content: flex-start;
    height: 44px;
  }
  
  .dialog-footer {
    flex-direction: column;
    gap: 12px;
  }
  
  .dialog-footer .el-button {
    width: 100%;
  }
}

/* 帮助提示区域样式 */
.help-section {
  background: var(--bg-secondary);
  border-radius: var(--radius);
  padding: 16px;
  border: 1px solid var(--border-light);
  margin-top: 16px;
}

.help-items {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.help-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--card-bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.help-item:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.help-item .el-icon {
  font-size: 14px;
}

/* 悬浮提示样式 */
:deep(.help-tooltip) {
  max-width: 400px !important;
  padding: 0 !important;
}

.tooltip-content {
  padding: 16px;
  line-height: 1.6;
}

.tooltip-content h4 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: white !important;
}

.tooltip-content ol {
  margin: 0;
  padding-left: 16px;
}

.tooltip-content li {
  margin-bottom: 6px;
  font-size: 13px;
  color: white !important;
}

.format-list {
  margin-bottom: 12px;
}

.format-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  color: white !important;
}

.format-item .el-icon.required {
  color: #67c23a;
}

.format-item .el-icon.optional {
  color: #909399;
}

.format-note {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 8px;
  margin-top: 8px;
}

.format-note p {
  margin: 4px 0;
  font-size: 12px;
  color: white !important;
}

.warning-list {
  margin-bottom: 12px;
}

.warning-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 13px;
  color: white !important;
}

.config-info {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 8px;
  margin-top: 8px;
}

.config-info p {
  margin: 4px 0 6px;
  font-size: 12px;
  color: white !important;
}

.config-info ul {
  margin: 0;
  padding-left: 16px;
}

.config-info li {
  margin-bottom: 4px;
  font-size: 12px;
  color: white !important;
}





/* 文件信息显示样式 */
.file-info {
  margin-top: 16px;
}

.file-card {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card-bg);
}

.file-details {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--primary-light);
  border-radius: var(--radius-sm);
  color: var(--primary);
}

.file-content {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  word-break: break-all;
}

.file-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.file-size {
  color: var(--text-muted);
}

.file-type {
  color: var(--primary);
  font-weight: 500;
}

.file-status {
  margin-top: 4px;
}

.file-actions {
  display: flex;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .file-content {
    width: 100%;
  }
  
  .file-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

.config-tip {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
  line-height: 1.4;
}

/* 导入监控面板样式 */
.import-monitor-dialog :deep(.el-dialog__body) {
  padding: 0;
  max-height: 80vh;
  overflow-y: auto;
}

.monitor-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 进度区域 */
.progress-section {
  background: var(--bg-secondary);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-light);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-stats {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.progress-text {
  text-align: center;
  margin-top: var(--space-xs);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 性能指标 */
.performance-section {
  background: var(--card-bg);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-light);
}

.performance-section h3 {
  margin: 0 0 16px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.performance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.performance-card {
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  padding: 16px;
  text-align: center;
  border: 1px solid var(--border-light);
  transition: all 0.2s ease;
}

.performance-card:hover {
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}

.card-title {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
}

.card-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
}

/* 店铺统计 */
.shop-stats-section {
  background: var(--card-bg);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-light);
}

.shop-stats-section h3 {
  margin: 0 0 16px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.shop-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.shop-stat-item {
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  padding: 12px;
  text-align: center;
  border: 1px solid var(--border-light);
}

.shop-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 4px;
}

.shop-count {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary);
}


/* 智能错误分析 */
.error-analysis-section {
  background: var(--card-bg);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-light);
}

.error-analysis-section h3 {
  margin: 0 0 16px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-summary {
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  padding: 16px;
  border: 1px solid var(--border-light);
}

.summary-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-label {
  font-weight: 600;
  color: var(--text-primary);
  min-width: 120px;
}

.summary-value {
  color: var(--text-secondary);
  flex: 1;
}

.suggestions {
  background: #f0f9ff;
  border-radius: var(--radius-sm);
  padding: 16px;
  border: 1px solid #b3d8ff;
}

.suggestions h4 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--primary);
}

.suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.suggestions li {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 8px;
  line-height: 1.5;
}

.suggestions li:last-child {
  margin-bottom: 0;
}

/* 错误区域 */
.errors-section {
  background: var(--card-bg);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-light);
}

.errors-section h3 {
  margin: 0 0 16px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.errors-container {
  background: #fef0f0;
  border-radius: var(--radius-sm);
  padding: 16px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #fbc4c4;
}

.error-item {
  color: #f56c6c;
  font-size: 14px;
  margin-bottom: 8px;
  padding: 4px 0;
  border-bottom: 1px solid #fde2e2;
}

.error-item:last-child {
  border-bottom: none;
}

/* 监控面板底部 */
.monitor-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-light);
  background: var(--bg-secondary);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .import-monitor-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  
  .performance-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .shop-stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
}

@media (max-width: 768px) {
  .monitor-content {
    padding: 16px;
    gap: 16px;
  }
  
  .progress-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .performance-grid {
    grid-template-columns: 1fr;
  }
  
  .shop-stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
  
  .monitor-footer {
    flex-direction: column;
  }
  
  .monitor-footer .el-button {
    width: 100%;
  }
}
.sub { margin: 0 0 16px; color:#909399; font-size: 13px; }
.filter-card { margin-bottom: 16px; }

/* 分类管理对话框样式 */
.category-manager {
  padding: 16px 0;
}

.category-manager h4 {
  margin: 0 0 12px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

.category-tags {
  min-height: 40px;
  padding: 8px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-secondary);
}

.add-category {
  margin-top: 16px;
}

.add-category .el-form {
  margin-top: 12px;
}

/* 表格容器样式 */
.table-container {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

/* 表格控制栏样式 */
.table-controls {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-light);
}

/* 分页容器样式 */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 12px 16px;
  background: var(--card-bg);
  border-radius: var(--radius);
  border: 1px solid var(--border-light);
}

.pagination-left {
  display: flex;
  align-items: center;
}

.pagination-right {
  display: flex;
  align-items: center;
}

.select-all-checkbox {
  font-weight: 600;
  color: var(--primary);
}

/* 全量删除对话框样式 */
.bulk-delete-content {
  padding: 16px 0;
}


.batch-delete-content {
  padding: 16px 0;
}

.warning-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 24px;
  padding: 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-sm);
}

.warning-text h3 {
  margin: 0 0 8px;
  color: #dc2626;
  font-size: 18px;
  font-weight: 600;
}

.warning-text p {
  margin: 0;
  color: #7f1d1d;
  font-size: 14px;
  line-height: 1.5;
}

.delete-preview {
  margin-bottom: 24px;
}

.delete-preview h4 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.preview-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--card-bg);
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
}

.preview-item:last-child {
  border-bottom: none;
}

.item-id {
  font-weight: 600;
  color: var(--primary);
  min-width: 40px;
}

.item-question {
  flex: 1;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-items {
  padding: 12px 16px;
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  background: var(--bg-secondary);
}

.delete-warning {
  background: #fef3cd;
  border: 1px solid #fde68a;
  border-radius: var(--radius-sm);
  padding: 16px;
}

.delete-warning h4 {
  margin: 0 0 12px;
  color: #92400e;
  font-size: 16px;
  font-weight: 600;
}

.delete-warning ul {
  margin: 0;
  padding-left: 20px;
  color: #92400e;
}

.delete-warning li {
  margin-bottom: 4px;
  font-size: 14px;
  line-height: 1.5;
}

.delete-warning li:last-child {
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0;
  border-top: 1px solid var(--border-light);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .batch-action-content {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .batch-actions {
    justify-content: stretch;
  }
  
  .batch-actions .el-button {
    flex: 1;
  }
  
  .preview-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .item-question {
    white-space: normal;
    overflow: visible;
    text-overflow: unset;
  }
}
</style>

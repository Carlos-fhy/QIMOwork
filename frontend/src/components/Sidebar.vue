<template>
  <div class="sidebar">
    <!-- 地区筛选 -->
    <div class="filter-section">
      <h3 class="section-title">
        <el-icon><Location /></el-icon>
        地区筛选
      </h3>
      <el-radio-group 
        v-model="selectedRegion" 
        direction="vertical" 
        @change="onRegionChange"
        class="region-radio-group"
      >
        <el-radio 
          v-for="region in regions" 
          :key="region.value" 
          :value="region.value"
          class="region-radio"
        >
          {{ region.label }}
        </el-radio>
      </el-radio-group>
    </div>

    <!-- 功能模式 -->
    <div class="filter-section">
      <h3 class="section-title">
        <el-icon><ChatDotSquare /></el-icon>
        功能模式
      </h3>
      <el-radio-group 
        v-model="mode" 
        direction="vertical" 
        @change="onModeChange"
        class="mode-radio-group"
      >
        <el-radio value="qa" class="mode-radio">智能问答</el-radio>
        <el-radio value="plan" class="mode-radio">行程规划</el-radio>
      </el-radio-group>
    </div>

    <!-- 高级设置 -->
    <div class="filter-section">
      <h3 class="section-title">
        <el-icon><Setting /></el-icon>
        高级设置
      </h3>
      
      <div class="setting-item">
        <label class="setting-label">检索数量 (Top-K)</label>
        <el-slider
          v-model="topK"
          :min="1"
          :max="10"
          :step="1"
          show-stops
          show-input
          :input-size="'small'"
          @change="onTopKChange"
        />
      </div>

      <div class="setting-item">
        <el-switch
          v-model="showSources"
          @change="onShowSourcesChange"
          active-text="显示来源"
          inactive-text="隐藏来源"
        />
      </div>

      <div class="setting-item">
        <el-switch
          v-model="streamMode"
          @change="onStreamModeChange"
          active-text="流式输出"
          inactive-text="一次输出"
        />
      </div>
    </div>

    <!-- 系统状态 -->
    <div class="filter-section">
      <h3 class="section-title">
        <el-icon><Monitor /></el-icon>
        系统状态
      </h3>
      
      <div class="status-item">
        <span class="status-label">服务状态:</span>
        <el-tag :type="healthStatus.type" size="small">
          {{ healthStatus.text }}
        </el-tag>
      </div>

      <div class="status-item" v-if="healthStatus.data">
        <span class="status-label">文档数量:</span>
        <span class="status-value">{{ healthStatus.data.document_count || 0 }}</span>
      </div>

      <el-button 
        type="primary" 
        size="small" 
        @click="checkHealth"
        :loading="healthChecking"
        style="width: 100%; margin-top: 0.5rem;"
      >
        刷新状态
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Location, ChatDotSquare, Setting, Monitor } from '@element-plus/icons-vue'
import { chatApi } from '@/api'
import { ElMessage } from 'element-plus'

// 定义emits
const emit = defineEmits(['region-change', 'mode-change', 'topk-change', 'show-sources-change', 'stream-mode-change'])

// 地区列表
const regions = ref([
  { label: '全部地区', value: 'all' },
  { label: '南京', value: '南京' },
  { label: '苏州', value: '苏州' },
  { label: '扬州', value: '扬州' },
  { label: '无锡', value: '无锡' },
  { label: '常州', value: '常州' },
  { label: '镇江', value: '镇江' },
  { label: '连云港', value: '连云港' },
  { label: '周庄', value: '周庄' },
  { label: '同里', value: '同里' }
])

// 响应式数据
const selectedRegion = ref('all')
const mode = ref('qa')
const topK = ref(3)
const showSources = ref(true)
const streamMode = ref(true)
const healthChecking = ref(false)
const healthStatus = reactive({
  type: 'info',
  text: '未检查',
  data: null
})

// 事件处理
const onRegionChange = () => {
  emit('region-change', selectedRegion.value)
}

const onModeChange = () => {
  emit('mode-change', mode.value)
}

const onTopKChange = () => {
  emit('topk-change', topK.value)
}

const onShowSourcesChange = () => {
  emit('show-sources-change', showSources.value)
}

const onStreamModeChange = () => {
  emit('stream-mode-change', streamMode.value)
}

// 健康检查
const checkHealth = async () => {
  healthChecking.value = true
  try {
    const response = await chatApi.healthCheck()
    if (response.status === 'healthy') {
      healthStatus.type = 'success'
      healthStatus.text = '正常'
      healthStatus.data = response.vector_db
    } else {
      healthStatus.type = 'danger'
      healthStatus.text = '异常'
      healthStatus.data = null
    }
  } catch (error) {
    healthStatus.type = 'danger'
    healthStatus.text = '连接失败'
    healthStatus.data = null
    ElMessage.error('无法连接到后端服务')
  }
  healthChecking.value = false
}

// 组件挂载时检查健康状态
onMounted(() => {
  checkHealth()
})
</script>

<style scoped>
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e6e6e6;
  padding: 1.5rem 1rem;
  height: 100vh;
  overflow-y: auto;
}

.filter-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.region-radio-group,
.mode-radio-group {
  width: 100%;
}

.region-radio,
.mode-radio {
  width: 100%;
  margin-bottom: 0.5rem;
  margin-right: 0;
}

.region-radio :deep(.el-radio__label),
.mode-radio :deep(.el-radio__label) {
  padding-left: 0.5rem;
}

.setting-item {
  margin-bottom: 1rem;
}

.setting-label {
  display: block;
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.status-label {
  color: #666;
}

.status-value {
  font-weight: 500;
  color: #333;
}
</style>
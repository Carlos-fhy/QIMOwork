<template>
  <div class="app-header">
    <div class="header-content">
      <div class="title-section">
        <h1 class="main-title">
          <el-icon class="title-icon"><MapLocation /></el-icon>
          江苏旅游助手
        </h1>
      </div>
    </div>
  </div>
</template>

<script setup>
import { MapLocation } from '@element-plus/icons-vue'
</script>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.title-section {
  text-align: center;
}

.main-title {
  font-size: 2rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.title-icon {
  font-size: 1.8rem;
}
</style>
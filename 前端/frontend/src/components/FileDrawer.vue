<script setup>
import { ref, computed } from 'vue';
import { IconCalendar, IconFile, IconDownload, IconCode } from '@arco-design/web-vue/es/icon';

const visible = defineModel({default: false});

const props = defineProps({
  versions_info: {
    type: Array,
    default: () => []
  },
  title: String,
});

// 处理确认按钮点击事件
function handleOk() {
  visible.value = false;
}

// 处理下载点击事件
function handleDownload(url) {
  window.open(url, '_blank');
}

// 计算是否有版本信息
const hasVersions = computed(() => props.versions_info && props.versions_info.length > 0);

// 格式化时间
function formatDate(timestamp) {
  const date = new Date(timestamp * 1000);
  return date.toLocaleString();
}

// 格式化MD5，只显示前8位和后8位
function formatMd5(md5) {
  if (!md5 || md5.length < 16) return md5;
  return `${md5.substring(0, 8)}...${md5.substring(md5.length - 8)}`;
}
</script>

<template>
  <a-drawer
    :width="700"
    :visible="visible"
    :hide-cancel="false"
    :closable="true"
    :footer="true"
    :mask-closable="true"
    @ok="handleOk"
    @cancel="handleOk"
    unmountOnClose
    class="file-version-drawer"
  >
    <template #title>
      <div class="drawer-title">
        <icon-file class="drawer-title-icon" />
        <span>{{ props.title }}</span>
      </div>
    </template>
    
    <div v-if="hasVersions" class="version-info-header">
      <div class="version-count">
        共 <a-tag color="blue">{{ props.versions_info.length }}</a-tag> 个版本
      </div>
    </div>
    
    <a-empty v-if="!hasVersions" description="暂无版本历史记录">
      <template #image>
        <icon-file-search style="fontSize: 48px; color: var(--color-text-3);" />
      </template>
    </a-empty>
    
    <a-list v-else class="version-list">
      <a-list-item v-for="(item, index) in props.versions_info" :key="index" class="version-item">
        <div class="version-item-content">
          <div class="version-item-header">
            <div class="version-item-title">
              <icon-file class="version-icon" />
              <span class="file-name">{{ item.file_name }}</span>
            </div>
            <a-button 
              type="primary" 
              size="small" 
              status="success" 
              @click="handleDownload(item.file_download_url)"
            >
              <template #icon><icon-download /></template>
              下载
            </a-button>
          </div>
          
          <div class="version-item-details">
            <a-space direction="vertical" size="small">
              <div class="detail-item">
                <icon-calendar class="detail-icon" />
                <span class="detail-label">上传时间：</span>
                <a-tag color="arcoblue">{{ formatDate(item.upload_time) }}</a-tag>
              </div>
              
              <div class="detail-item">
                <icon-code class="detail-icon" />
                <span class="detail-label">文件MD5：</span>
                <a-tooltip :content="item.md5">
                  <a-tag color="purple">{{ formatMd5(item.md5) }}</a-tag>
                </a-tooltip>
              </div>
            </a-space>
          </div>
        </div>
      </a-list-item>
    </a-list>
    
    <template #footer>
      <div class="drawer-footer">
        <a-button type="primary" @click="handleOk">关闭</a-button>
      </div>
    </template>
  </a-drawer>
</template>

<style scoped>
.file-version-drawer :deep(.arco-drawer-content) {
  background-color: var(--app-bg-primary);
  border-left: 1px solid var(--app-border-color);
}

.file-version-drawer :deep(.arco-drawer-header) {
  border-bottom: 1px solid var(--app-border-color);
  background-color: var(--app-bg-primary);
}

.file-version-drawer :deep(.arco-drawer-title) {
  color: var(--app-text-primary);
}

.file-version-drawer :deep(.arco-drawer-close-btn) {
  color: var(--app-text-secondary);
}

.file-version-drawer :deep(.arco-drawer-close-btn:hover) {
  background-color: rgba(0, 0, 0, 0.04);
  color: var(--app-text-primary);
}

.file-version-drawer :deep(.arco-drawer-body) {
  padding: 20px;
  color: var(--app-text-primary);
}

.file-version-drawer :deep(.arco-drawer-footer) {
  border-top: 1px solid var(--app-border-color);
  background-color: var(--app-bg-primary);
}

.drawer-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.drawer-title-icon {
  color: var(--app-primary);
  font-size: 20px;
}

.version-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--app-border-color);
  position: relative;
}

.version-count {
  font-size: 14px;
  color: var(--app-text-secondary);
}

.version-count :deep(.arco-tag) {
  background-color: var(--app-primary);
  border: none;
  color: white;
}

.version-list {
  border: 1px solid var(--app-border-color);
  border-radius: 4px;
  overflow: hidden;
  background-color: var(--app-bg-primary);
  box-shadow: var(--app-shadow-1);
}

.version-item {
  border-bottom: 1px solid var(--app-border-color);
  padding: 16px;
  transition: background-color 0.3s;
  position: relative;
  overflow: hidden;
}

.version-item:last-child {
  border-bottom: none;
}

.version-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.version-item-content {
  width: 100%;
}

.version-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.version-item-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.version-icon {
  color: var(--app-primary);
  font-size: 18px;
}

.file-name {
  font-weight: 500;
  color: var(--app-text-primary);
}

.version-item-details {
  padding-left: 28px;
  background-color: var(--app-bg-secondary);
  border-radius: 4px;
  padding: 12px 16px 12px 28px;
  border: 1px solid var(--app-border-color);
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--app-text-secondary);
  margin-bottom: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-icon {
  font-size: 16px;
  color: var(--app-primary);
}

.detail-label {
  font-size: 14px;
  font-weight: 500;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
}

/* Override button styles */
.version-item-header :deep(.arco-btn-primary) {
  background-color: var(--md-green);
  border-color: var(--md-green);
  transition: all 0.3s;
}

.version-item-header :deep(.arco-btn-primary:hover) {
  background-color: var(--md-light-green);
  border-color: var(--md-light-green);
  box-shadow: var(--app-shadow-1);
}

.drawer-footer :deep(.arco-btn-primary) {
  background-color: var(--app-primary);
  border-color: var(--app-primary);
  transition: all 0.3s;
}

.drawer-footer :deep(.arco-btn-primary:hover) {
  background-color: var(--app-primary-light);
  border-color: var(--app-primary-light);
  box-shadow: var(--app-shadow-1);
}

/* Override tag styles */
:deep(.arco-tag-arcoblue) {
  background-color: var(--app-accent);
  border: none;
}

:deep(.arco-tag-purple) {
  background-color: var(--md-purple);
  border: none;
}

/* Empty state styling */
:deep(.arco-empty) {
  color: var(--app-text-secondary);
  padding: 40px 0;
}

/* Material Design ripple effect for buttons */
.version-item-header :deep(.arco-btn),
.drawer-footer :deep(.arco-btn) {
  position: relative;
  overflow: hidden;
}

.version-item-header :deep(.arco-btn)::after,
.drawer-footer :deep(.arco-btn)::after {
  content: "";
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.3) 10%, transparent 10.01%);
  background-repeat: no-repeat;
  background-position: 50%;
  transform: scale(10, 10);
  opacity: 0;
  transition: transform 0.5s, opacity 1s;
}

.version-item-header :deep(.arco-btn:active)::after,
.drawer-footer :deep(.arco-btn:active)::after {
  transform: scale(0, 0);
  opacity: 0.2;
  transition: 0s;
}

/* Material Design elevation on hover */
.version-item {
  transition: box-shadow 0.3s, background-color 0.3s;
}

.version-item:hover {
  box-shadow: var(--app-shadow-2);
}
</style>

<script setup>
import FileColumns from "@/components/FileColumns.vue";
import FileUpload from "@/components/FileUpload.vue";
import {ref, onMounted} from "vue";
import {getAllFileInfo} from "@/api/file_api.js";
import {Message} from "@arco-design/web-vue";

const visible = ref(false);
const file_list_info = ref([]);
const loading = ref(false);

// 显示上传界面
function showUploadModal() {
  visible.value = true;
}

// 获取文件列表
function getFileList() {
  loading.value = true;
  getAllFileInfo().then(res => {
    file_list_info.value = res["list_info"];
    Message.success({
      content: '文件列表刷新成功',
      duration: 2000,
    });
  }).catch(err => {
    console.log(err);
    Message.error({
      content: '获取文件列表失败',
      duration: 2000,
    });
  }).finally(() => {
    loading.value = false;
  });
}

// 组件挂载时获取文件列表
onMounted(() => {
  getFileList();
});
</script>

<template>
  <div class="file-manage-container">
    <FileUpload v-model="visible"/>
    
    <div class="panel-header">
      <div class="panel-title">
        <icon-file class="panel-icon" />
        <h2>文件版本管理</h2>
      </div>
      
      <div class="panel-actions">
        <a-space>
          <a-tooltip content="刷新文件列表">
            <a-button type="primary" shape="circle" status="normal" @click="getFileList" :loading="loading">
              <icon-refresh/>
            </a-button>
          </a-tooltip>
          <a-button type="primary" @click="showUploadModal">
            <template #icon>
              <icon-upload />
            </template>
            提交文件
          </a-button>
        </a-space>
      </div>
    </div>
    
    <a-divider style="margin: 16px 0" />
    
    <div class="file-content">
      <a-spin :loading="loading" tip="加载中...">
        <FileColumns :file_list_info="file_list_info"/>
      </a-spin>
    </div>
  </div>
</template>

<style scoped>
.file-manage-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--app-border-color);
  position: relative;
}

.panel-title {
  display: flex;
  align-items: center;
}

.panel-icon {
  font-size: 24px;
  color: var(--app-primary);
  margin-right: 12px;
}

.panel-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: var(--app-text-primary);
  letter-spacing: 0.15px;
}

.panel-actions {
  display: flex;
  align-items: center;
}

.panel-actions :deep(.arco-btn) {
  transition: all 0.3s;
}

.panel-actions :deep(.arco-btn:hover) {
  box-shadow: var(--app-shadow-1);
}

.panel-actions :deep(.arco-btn-primary) {
  background-color: var(--app-primary);
  border-color: var(--app-primary);
}

.panel-actions :deep(.arco-btn-shape-circle) {
  background-color: var(--app-bg-secondary);
  border: 1px solid var(--app-border-color);
}

.panel-actions :deep(.arco-btn-shape-circle:hover) {
  background-color: rgba(0, 0, 0, 0.04);
}

.file-content {
  flex: 1;
  overflow: auto;
  position: relative;
  background-color: var(--app-bg-primary);
  border-radius: 4px;
  padding: 16px;
  box-shadow: var(--app-shadow-1);
}

/* Override Arco Design components */
:deep(.arco-divider) {
  border-color: var(--app-border-color);
  margin: 16px 0;
}

:deep(.arco-spin) {
  color: var(--app-primary);
}

:deep(.arco-spin-dot) {
  background-color: var(--app-primary);
}

/* Material Design ripple effect for buttons */
.panel-actions :deep(.arco-btn) {
  position: relative;
  overflow: hidden;
}

.panel-actions :deep(.arco-btn)::after {
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

.panel-actions :deep(.arco-btn:active)::after {
  transform: scale(0, 0);
  opacity: 0.2;
  transition: 0s;
}
</style>

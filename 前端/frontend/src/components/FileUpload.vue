<script setup>
import { reactive, ref } from 'vue';
import { md5 } from 'js-md5'
import { Message } from "@arco-design/web-vue";
import { checkFileInfo, postImage2S3, uploadFileInfo } from "@/api/file_api.js";
import { IconUpload, IconFile, IconCheckCircle, IconCloseCircle } from '@arco-design/web-vue/es/icon';

const visible = defineModel({default: false})
const form = reactive({
  file_name: '',
  file_md5: '',
  file_type: '',
});

const fileList = ref([]);
const uploadTip = ref('点击或拖拽文件到此处上传');
const isUploading = ref(false);
const uploadProgress = ref(0);
const uploadStatus = ref('idle'); // idle, calculating, ready, uploading, success, error
let current_image = null;

function handleResourceSubmit(option) {
  const { onProgress, onError, onSuccess, fileItem } = option;
  
  // 更新状态
  uploadStatus.value = 'calculating';
  uploadTip.value = '正在计算文件MD5...';
  
  current_image = fileItem.file;
  const pos = current_image.name.lastIndexOf('.');
  if (pos > 0) form.file_type = current_image.name.substring(pos);
  
  // 如果文件名为空，使用文件原名（不含扩展名）
  if (!form.file_name) {
    form.file_name = current_image.name.substring(0, pos > 0 ? pos : current_image.name.length);
  }
  
  const fileReader = new FileReader()
  fileReader.onload = e => {
    form.file_md5 = md5(e.target.result);
    uploadStatus.value = 'ready';
    uploadTip.value = '文件已准备好，点击确定上传';
  }
  
  fileReader.onerror = e => {
    Message.error({
      content: "文件MD5值计算错误",
      duration: 3000
    });
    uploadStatus.value = 'error';
    uploadTip.value = '文件处理失败，请重试';
  }
  
  fileReader.readAsArrayBuffer(current_image);
  onSuccess(true);
  return true;
}

// 处理取消操作的函数
function handleCancel() {
  resetForm();
  visible.value = false;
}

// 重置表单
function resetForm() {
  form.file_name = '';
  form.file_md5 = '';
  form.file_type = '';
  fileList.value = [];
  current_image = null;
  uploadStatus.value = 'idle';
  uploadTip.value = '点击或拖拽文件到此处上传';
  uploadProgress.value = 0;
  isUploading.value = false;
}

// 检查表单是否有效
function isFormValid() {
  if (!form.file_name) {
    Message.warning({
      content: "请输入文件名",
      duration: 3000
    });
    return false;
  }
  
  if (!form.file_md5 || !form.file_type) {
    Message.warning({
      content: "请先上传文件",
      duration: 3000
    });
    return false;
  }
  
  if (!current_image) {
    Message.warning({
      content: "未检测到文件，请重新上传",
      duration: 3000
    });
    return false;
  }
  
  return true;
}

// 检查文件信息，上传文件
function handleBeforeOk() {
  if (!isFormValid()) return false;
  
  isUploading.value = true;
  uploadStatus.value = 'uploading';
  uploadTip.value = '正在上传文件...';
  
  // 模拟上传进度
  const progressInterval = setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += 10;
    }
  }, 300);
  
  return new Promise((resolve, reject) => {
    checkFileInfo(form).then((res) => {
      const real_name = form.file_name + "-" + form.file_md5 + form.file_type;
      
      postImage2S3(res["file_path"], real_name, current_image).then((res) => {
        const upload_info = {
          file_name: real_name, 
          file_md5: form.file_md5, 
          folder_name: form.file_name, 
          file_url: res
        };
        
        uploadFileInfo(upload_info).then((res) => {
          uploadProgress.value = 100;
          uploadStatus.value = 'success';
          uploadTip.value = '上传成功！';
          
          Message.success({
            content: "文件上传成功",
            duration: 3000
          });
          
          clearInterval(progressInterval);
          setTimeout(() => {
            resetForm();
            resolve(true);
          }, 500);
        }).catch(err => {
          handleUploadError(err, progressInterval);
          reject(false);
        });
      }).catch(err => {
        handleUploadError(err, progressInterval);
        reject(false);
      });
    }).catch(err => {
      handleUploadError(err, progressInterval);
      reject(false);
    });
  });
}

// 处理上传错误
function handleUploadError(err, progressInterval) {
  console.error(err);
  clearInterval(progressInterval);
  uploadStatus.value = 'error';
  uploadTip.value = '上传失败，请重试';
  isUploading.value = false;
  
  Message.error({
    content: "文件上传失败，请重试",
    duration: 3000
  });
}

// 获取上传状态图标
function getStatusIcon() {
  switch (uploadStatus.value) {
    case 'calculating':
      return 'icon-loading';
    case 'ready':
      return IconCheckCircle;
    case 'uploading':
      return 'icon-loading';
    case 'success':
      return IconCheckCircle;
    case 'error':
      return IconCloseCircle;
    default:
      return IconUpload;
  }
}

// 获取上传状态颜色
function getStatusColor() {
  switch (uploadStatus.value) {
    case 'ready':
      return 'var(--color-success-light-4)';
    case 'success':
      return 'var(--color-success-light-4)';
    case 'error':
      return 'var(--color-danger-light-4)';
    default:
      return 'var(--color-fill-2)';
  }
}
</script>

<template>
  <a-modal
    v-model:visible="visible"
    title-align="start"
    :width="520"
    :mask-closable="false"
    :unmount-on-close="true"
    @cancel="handleCancel"
    @before-ok="handleBeforeOk"
  >
    <template #title>
      <div class="modal-title">
        <icon-upload class="modal-title-icon" />
        <span>上传文件</span>
      </div>
    </template>
    
    <a-form :model="form" layout="vertical">
      <a-form-item field="file_name" label="文件名称" required>
        <a-input
          v-model="form.file_name"
          placeholder="请输入文件名称"
          allow-clear
        >
          <template #prefix>
            <icon-file />
          </template>
        </a-input>
      </a-form-item>
      
      <a-form-item>
        <div class="upload-container" :style="{ backgroundColor: getStatusColor() }">
          <a-upload
            :file-list="fileList"
            :show-file-list="false"
            draggable
            action="/"
            :custom-request="handleResourceSubmit"
            :limit="1"
            :disabled="isUploading"
            class="custom-upload"
          >
            <template #upload-button>
              <div class="upload-content">
                <component :is="getStatusIcon()" class="upload-icon" :class="{ 'icon-spin': uploadStatus === 'calculating' || uploadStatus === 'uploading' }" />
                <div class="upload-text">{{ uploadTip }}</div>
                <div v-if="current_image" class="file-info">
                  <div class="file-name">{{ current_image.name }}</div>
                  <div class="file-size">{{ (current_image.size / 1024).toFixed(2) }} KB</div>
                </div>
              </div>
            </template>
          </a-upload>
          
          <a-progress
            v-if="uploadStatus === 'uploading'"
            :percent="uploadProgress"
            :show-text="false"
            status="normal"
            class="upload-progress"
          />
        </div>
      </a-form-item>
      
      <a-form-item v-if="form.file_md5" label="文件MD5">
        <a-input :model-value="form.file_md5" readonly>
          <template #suffix>
            <a-tooltip content="文件的唯一标识">
              <icon-info-circle />
            </a-tooltip>
          </template>
        </a-input>
      </a-form-item>
    </a-form>
    
    <template #footer>
      <div class="modal-footer">
        <a-space>
          <a-button @click="handleCancel">取消</a-button>
          <a-button type="primary" :loading="isUploading" @click="handleBeforeOk">
            {{ isUploading ? '上传中...' : '确定' }}
          </a-button>
        </a-space>
      </div>
    </template>
  </a-modal>
</template>

<style scoped>
.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-title-icon {
  color: var(--app-primary);
  font-size: 20px;
}

/* Override modal styles */
:deep(.arco-modal) {
  background-color: var(--app-bg-primary);
  border-radius: 4px;
  box-shadow: var(--app-shadow-3);
  overflow: hidden;
}

:deep(.arco-modal-header) {
  border-bottom: 1px solid var(--app-border-color);
  background-color: var(--app-bg-primary);
}

:deep(.arco-modal-title) {
  color: var(--app-text-primary);
}

:deep(.arco-modal-close-btn) {
  color: var(--app-text-secondary);
}

:deep(.arco-modal-close-btn:hover) {
  background-color: rgba(0, 0, 0, 0.04);
  color: var(--app-text-primary);
}

:deep(.arco-modal-body) {
  padding: 24px;
  color: var(--app-text-primary);
}

:deep(.arco-modal-footer) {
  border-top: 1px solid var(--app-border-color);
  background-color: var(--app-bg-primary);
}

:deep(.arco-form-item-label) {
  color: var(--app-text-secondary);
  font-weight: 500;
}

:deep(.arco-input-wrapper) {
  background-color: var(--app-bg-secondary);
  border: 1px solid var(--app-border-color);
  border-radius: 4px;
  transition: all 0.3s;
}

:deep(.arco-input-wrapper:hover),
:deep(.arco-input-wrapper:focus-within) {
  background-color: var(--app-bg-primary);
  border-color: var(--app-primary);
  box-shadow: 0 0 0 2px rgba(51, 112, 255, 0.1);
}

:deep(.arco-input) {
  color: var(--app-text-primary);
}

:deep(.arco-input-prefix .arco-icon),
:deep(.arco-input-suffix .arco-icon) {
  color: var(--app-text-secondary);
}

.upload-container {
  border: 2px dashed var(--app-border-color);
  border-radius: 4px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  background-color: var(--app-bg-secondary);
}

.upload-container:hover {
  border-color: var(--app-primary);
  background-color: rgba(51, 112, 255, 0.02);
}

.custom-upload {
  width: 100%;
}

.custom-upload :deep(.arco-upload-drag) {
  padding: 24px;
  background-color: transparent;
  border: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}

.upload-icon {
  font-size: 36px;
  color: var(--app-primary);
  margin-bottom: 12px;
}

.icon-spin {
  animation: spin 1.2s infinite linear;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.upload-text {
  font-size: 16px;
  color: var(--app-text-secondary);
  margin-bottom: 12px;
  text-align: center;
  max-width: 300px;
}

.file-info {
  text-align: center;
  margin-top: 16px;
  padding: 12px 20px;
  background-color: var(--app-bg-primary);
  border-radius: 4px;
  border: 1px solid var(--app-border-color);
  box-shadow: var(--app-shadow-1);
}

.file-name {
  font-weight: 500;
  color: var(--app-text-primary);
  margin-bottom: 6px;
  word-break: break-all;
}

.file-size {
  font-size: 12px;
  color: var(--app-text-secondary);
}

.upload-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.upload-progress :deep(.arco-progress-line-text) {
  display: none;
}

.upload-progress :deep(.arco-progress-line-bar) {
  background-color: var(--app-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}

/* Override button styles */
.modal-footer :deep(.arco-btn-primary) {
  background-color: var(--app-primary);
  border-color: var(--app-primary);
  transition: all 0.3s;
}

.modal-footer :deep(.arco-btn-primary:hover) {
  background-color: var(--app-primary-light);
  border-color: var(--app-primary-light);
  box-shadow: var(--app-shadow-1);
}

.modal-footer :deep(.arco-btn) {
  background-color: var(--app-bg-primary);
  border: 1px solid var(--app-border-color);
  color: var(--app-text-primary);
}

.modal-footer :deep(.arco-btn:hover) {
  background-color: var(--app-bg-secondary);
}

/* Status-specific styles */
.upload-container[style*="var(--color-success-light-4)"] {
  background-color: rgba(76, 175, 80, 0.05);
  border-color: var(--md-green);
}

.upload-container[style*="var(--color-danger-light-4)"] {
  background-color: rgba(244, 67, 54, 0.05);
  border-color: var(--md-red);
}

/* Material Design ripple effect for buttons */
.modal-footer :deep(.arco-btn) {
  position: relative;
  overflow: hidden;
}

.modal-footer :deep(.arco-btn)::after {
  content: "";
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  background-image: radial-gradient(circle, rgba(0, 0, 0, 0.1) 10%, transparent 10.01%);
  background-repeat: no-repeat;
  background-position: 50%;
  transform: scale(10, 10);
  opacity: 0;
  transition: transform 0.5s, opacity 1s;
}

.modal-footer :deep(.arco-btn-primary)::after {
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.3) 10%, transparent 10.01%);
}

.modal-footer :deep(.arco-btn:active)::after {
  transform: scale(0, 0);
  opacity: 0.2;
  transition: 0s;
}
</style>

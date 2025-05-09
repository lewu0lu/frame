<template>
  <div class="file-columns-container">
    <div class="table-header">
      <div class="search-container">
        <a-input-search
          v-model="searchText"
          placeholder="搜索文件名..."
          allow-clear
          @search="handleSearch"
        >
          <template #prefix>
            <icon-search />
          </template>
        </a-input-search>
      </div>
      <div class="table-info">
        共 <a-tag color="blue">{{ props.file_list_info.length }}</a-tag> 个文件
      </div>
    </div>
    
    <a-table
      :columns="columns"
      :data="paginatedData"
      :pagination="pagination"
      :loading="loading"
      :bordered="false"
      :stripe="true"
      :row-class="rowClass"
      @page-change="handlePageChange"
      class="file-table"
    >
      <template #name-filter="{ filterValue, setFilterValue, handleFilterConfirm, handleFilterReset}">
        <div class="custom-filter">
          <a-space direction="vertical">
            <a-input :model-value="filterValue[0]" @input="(value)=>setFilterValue([value])" placeholder="输入文件名过滤"/>
            <div class="custom-filter-footer">
              <a-button type="primary" size="small" @click="handleFilterConfirm">确认</a-button>
              <a-button size="small" @click="handleFilterReset">清空</a-button>
            </div>
          </a-space>
        </div>
      </template>
      
      <template #file_name="{ record }">
        <div class="file-name-cell">
          <icon-file class="file-icon" />
          <span>{{ record.file_name }}</span>
        </div>
      </template>
      
      <template #upload_time="{ record }">
        <a-tag color="arcoblue">{{ record.upload_time }}</a-tag>
      </template>
      
      <template #actions="{ record }">
        <a-space>
          <a-tooltip content="查看所有版本">
            <a-button type="text" shape="circle" @click="viewHistory(record)">
              <icon-history />
            </a-button>
          </a-tooltip>
          <a-button type="primary" size="small" status="success" @click="viewHistory(record)">
            查看版本历史
          </a-button>
        </a-space>
      </template>
      
      <template #empty>
        <div class="empty-state">
          <icon-file-search style="fontSize: 48px; color: var(--color-text-3);" />
          <p>暂无文件数据</p>
        </div>
      </template>
    </a-table>
  </div>
  
  <FileDrawer
    :title='"文件版本列表"'
    :versions_info="file_versions_info"
    v-model="drawer_visible"
  />
</template>

<script setup>
import {reactive, computed, h, ref, watch} from 'vue';
import {IconSearch, IconFile, IconHistory} from '@arco-design/web-vue/es/icon';
import FileDrawer from "@/components/FileDrawer.vue";
import {getFileVersionInfo} from "@/api/file_api.js";
import {Message} from "@arco-design/web-vue";

const drawer_visible = ref(false);
const searchText = ref('');
const loading = ref(false);

// 定义表格列配置
const columns = [
  {
    title: '文件名',
    dataIndex: 'file_name',
    slotName: 'file_name',
    width: 250,
    ellipsis: true,
    tooltip: true,
    filterable: {
      filter: (value, record) => record.file_name.toLowerCase().includes(value.toLowerCase()),
      slotName: 'name-filter',
      icon: () => h(IconSearch)
    }
  },
  {
    title: '上传时间',
    dataIndex: 'upload_time',
    slotName: 'upload_time',
    width: 200,
    sortable: {
      sortDirections: ['ascend', 'descend']
    },
  },
  {
    title: '操作',
    dataIndex: 'actions',
    width: 200,
    slotName: 'actions',
    align: 'center'
  }
];

const props = defineProps({
  file_list_info: {
    type: Array,
    default: () => []
  },
});

const file_versions_info = ref([]);

// 分页配置
const pagination = reactive({
  pageSize: 10,
  current: 1,
  total: computed(() => filteredData.value.length),
  showTotal: true,
  showJumper: true,
  showPageSize: true,
  pageSizeOptions: [10, 20, 50, 100]
});

// 过滤后的数据
const filteredData = computed(() => {
  if (!searchText.value) {
    return props.file_list_info || [];
  }
  
  return (props.file_list_info || []).filter(item => 
    item.file_name.toLowerCase().includes(searchText.value.toLowerCase())
  );
});

// 计算分页后的数据
const paginatedData = computed(() => {
  const start = (pagination.current - 1) * pagination.pageSize;
  const end = start + pagination.pageSize;
  
  return filteredData.value.slice(start, end).map(x => {
    return {
      file_name: x.file_name,
      upload_time: new Date(x.upload_time * 1000).toLocaleString(),
      raw: x
    };
  });
});

// 处理页面变化
const handlePageChange = (page) => {
  pagination.current = page;
};

// 处理搜索
const handleSearch = () => {
  pagination.current = 1;
};

// 查看文件历史版本
const viewHistory = (record) => {
  loading.value = true;
  drawer_visible.value = true;
  
  getFileVersionInfo(record).then((res) => {
    file_versions_info.value = res["version_info"];
    if (file_versions_info.value.length === 0) {
      Message.info('该文件暂无历史版本');
    }
  }).catch(err => {
    console.log(err);
    Message.error('获取版本历史失败');
  }).finally(() => {
    loading.value = false;
  });
};

// 行样式
const rowClass = (record, index) => {
  return index % 2 === 0 ? 'even-row' : 'odd-row';
};

// 监听文件列表变化，重置分页
watch(() => props.file_list_info, () => {
  pagination.current = 1;
}, { deep: true });
</script>

<style scoped>
.file-columns-container {
  width: 100%;
  background-color: var(--app-bg-primary);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--app-border-color);
  box-shadow: var(--app-shadow-1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: var(--app-bg-primary);
  border-bottom: 1px solid var(--app-border-color);
}

.search-container {
  width: 300px;
}

.search-container :deep(.arco-input-wrapper) {
  background-color: var(--app-bg-secondary);
  border: 1px solid var(--app-border-color);
  border-radius: 4px;
  transition: all 0.3s;
}

.search-container :deep(.arco-input-wrapper:hover),
.search-container :deep(.arco-input-wrapper:focus-within) {
  background-color: var(--app-bg-primary);
  border-color: var(--app-primary);
  box-shadow: 0 0 0 2px rgba(51, 112, 255, 0.1);
}

.search-container :deep(.arco-input) {
  color: var(--app-text-primary);
}

.search-container :deep(.arco-input-prefix .arco-icon) {
  color: var(--app-text-secondary);
}

.table-info {
  font-size: 14px;
  color: var(--app-text-secondary);
}

.table-info :deep(.arco-tag) {
  background-color: var(--app-primary);
  border: none;
  color: white;
}

.file-table {
  width: 100%;
}

.file-table :deep(.arco-table) {
  background-color: var(--app-bg-primary);
  color: var(--app-text-primary);
}

.file-table :deep(.arco-table-th) {
  background-color: var(--app-bg-secondary) !important;
  color: var(--app-text-primary);
  font-weight: 500;
  border-color: var(--app-border-color);
}

.file-table :deep(.arco-table-td) {
  border-color: var(--app-border-color);
  color: var(--app-text-primary);
}

.file-table :deep(.arco-table-tr) {
  transition: background-color 0.3s;
}

.file-table :deep(.arco-table-tr:hover) {
  background-color: rgba(0, 0, 0, 0.04) !important;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  color: var(--app-primary);
  font-size: 18px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: var(--app-text-secondary);
  background-color: var(--app-bg-secondary);
  border-radius: 4px;
  margin: 20px 0;
}

.even-row {
  background-color: var(--app-bg-primary);
}

.odd-row {
  background-color: var(--app-bg-secondary);
}

.custom-filter {
  padding: 16px;
  background-color: var(--app-bg-primary);
  border: 1px solid var(--app-border-color);
  border-radius: 4px;
  box-shadow: var(--app-shadow-2);
}

.custom-filter :deep(.arco-input) {
  background-color: var(--app-bg-secondary);
  border-color: var(--app-border-color);
  color: var(--app-text-primary);
}

.custom-filter :deep(.arco-input:focus) {
  border-color: var(--app-primary);
  box-shadow: 0 0 0 2px rgba(51, 112, 255, 0.1);
}

.custom-filter-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
}

/* Override pagination styles */
.file-table :deep(.arco-pagination) {
  margin-top: 16px;
  color: var(--app-text-secondary);
}

.file-table :deep(.arco-pagination-item) {
  background-color: var(--app-bg-primary);
  border-color: var(--app-border-color);
  color: var(--app-text-primary);
  transition: all 0.3s;
}

.file-table :deep(.arco-pagination-item:hover),
.file-table :deep(.arco-pagination-item-active) {
  background-color: var(--app-primary);
  color: white;
  border-color: var(--app-primary);
}

.file-table :deep(.arco-pagination-jumper .arco-input-wrapper) {
  background-color: var(--app-bg-secondary);
  border-color: var(--app-border-color);
}

.file-table :deep(.arco-pagination-jumper .arco-input) {
  color: var(--app-text-primary);
}

/* Override button styles */
.file-table :deep(.arco-btn-text) {
  color: var(--app-primary);
}

.file-table :deep(.arco-btn-text:hover) {
  background-color: rgba(51, 112, 255, 0.05);
  color: var(--app-primary-light);
}

.file-table :deep(.arco-btn-primary.arco-btn-status-success) {
  background-color: var(--md-green);
  border-color: var(--md-green);
  transition: all 0.3s;
}

.file-table :deep(.arco-btn-primary.arco-btn-status-success:hover) {
  background-color: var(--md-light-green);
  border-color: var(--md-light-green);
  box-shadow: var(--app-shadow-1);
}

/* Override tag styles */
.file-table :deep(.arco-tag-arcoblue) {
  background-color: var(--app-accent);
  border: none;
}

/* Material Design ripple effect for buttons */
.file-table :deep(.arco-btn) {
  position: relative;
  overflow: hidden;
}

.file-table :deep(.arco-btn)::after {
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

.file-table :deep(.arco-btn:active)::after {
  transform: scale(0, 0);
  opacity: 0.2;
  transition: 0s;
}

.file-table :deep(.arco-btn-primary)::after {
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.3) 10%, transparent 10.01%);
}
</style>

<template>
  <div style="max-width: 600px;margin-bottom: 16px;">
    <a-table :columns="columns" :data="paginatedData" :pagination="pagination" @page-change="handlePageChange">
      <template #package_name-filter="{ filterValue, setFilterValue, handleFilterConfirm, handleFilterReset }">
        <div class="custom-filter">
          <a-space direction="vertical">
            <a-input :model-value="filterValue[0]" @input="(value) => setFilterValue([value])"/>
            <div class="custom-filter-footer">
              <a-button @click="handleFilterConfirm">确认</a-button>
              <a-button @click="handleFilterReset">重置</a-button>
            </div>
          </a-space>
        </div>
      </template>
      <template #actions="{ record }">
        <a-button @click="uninstallPackage(record)">卸载</a-button>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import {reactive, computed, ref, h, watch} from 'vue';
import {IconSearch} from '@arco-design/web-vue/es/icon';
import {uninstall} from "@/api/package_api.js";
import {Message} from "@arco-design/web-vue";

const columns = [
  {
    title: '已安装的包',
    dataIndex: 'package_name',
    filterable: {
      filter: (value, record) => record.package_name.includes(value),
      slotName: 'package_name-filter',
      icon: () => h(IconSearch)
    }
  },
  {
    title: '版本',
    dataIndex: 'version',
    width: 200,
  },
  {
    title: '操作',
    dataIndex: 'actions',
    width: 100,
    slotName: 'actions'
  }
];

const props = defineProps({
  installed_packages: Array,
});

const searchQuery = ref('');

// 计算过滤后的包列表
const filteredPackages = computed(() => {
  if (!searchQuery.value) {
    return props.installed_packages;
  }
  return props.installed_packages.filter(pkg =>
      pkg.package_name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// 创建分页配置响应式对象
const pagination = reactive({
  pageSize: 10,
  current: 1,
  total: filteredPackages.value.length
});

// 计算当前页的数据
const paginatedData = computed(() => {
  const start = (pagination.current - 1) * pagination.pageSize;
  const end = start + pagination.pageSize;
  return filteredPackages.value.slice(start, end);
});

// 处理页面变化
const handlePageChange = (page) => {
  pagination.current = page;
};

// 处理搜索操作
const handleSearch = () => {
  pagination.current = 1;
  pagination.total = filteredPackages.value.length;
};

// 监听过滤后的包列表变化，更新总数
watch(filteredPackages, () => {
  pagination.total = filteredPackages.value.length;
});

// 卸载包的函数
const uninstallPackage = (record) => {
  uninstall(record).then((res) => {
    if (res.status) Message.success(res.message);
    else Message.warning(res.output_message);
  }).catch(err => {
    console.log(err);
    Message.error(err);
  });
  return true;
};

</script>

<style>
.custom-filter {
  padding: 20px;
  background: var(--color-bg-5);
  border: 1px solid var(--color-neutral-3);
  border-radius: var(--border-radius-medium);
  box-shadow: 0 2px 5px rgb(0 0 0 / 10%);
}

.custom-filter-footer {
  display: flex;
  justify-content: space-between;
}
</style>
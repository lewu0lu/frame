<script setup>
import {h} from "vue";
import {IconSearch} from "@arco-design/web-vue/es/icon";

const props = defineProps({
  operate_info_list: Array,
});
const emits = defineEmits(["row_click"]);

const columns = [
  {
    title: 'Name',
    dataIndex: 'task_chain_url',
    filterable: {
      filter: (value, record) => {
        if (!record.task_chain_url) return false;
        return record.task_chain_url.includes(value)
      },
      slotName: 'name-filter',
      icon: () => h(IconSearch)
    },
    width: 100
  },
  {
    title: 'StartTime',
    dataIndex: 'begin_time',
  },
  {
    title: 'EndTime',
    dataIndex: 'end_time',
  },
  {
    title: 'Uid',
    dataIndex: '_id',
  },
  {
    title: 'TaskCount',
    dataIndex: 'task_count',
  },
];

function rowClick(record, e) {
  emits("row_click", record["_id"]);
}
</script>

<template>
  <a-table
      :stripe="true"
      :columns="columns"
      :data="operate_info_list"
      :scroll="{x:'90%', y:'90%'}"
      :virtual-list-props="{height:400}"
      @rowClick="rowClick">
    <template #name-filter="{ filterValue, setFilterValue, handleFilterConfirm, handleFilterReset}">
      <div class="custom-filter">
        <a-space direction="vertical">
          <a-input :model-value="filterValue[0]" @input="(value)=>setFilterValue([value])"/>
          <div class="custom-filter-footer">
            <a-button @click="handleFilterConfirm">确认</a-button>
            <a-button @click="handleFilterReset">清空</a-button>
          </div>
        </a-space>
      </div>
    </template>
  </a-table>
</template>

<style scoped>

</style>
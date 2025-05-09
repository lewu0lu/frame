<script setup>
import {getAllOperatingRecord, getOperatingRecord} from "@/api/chain_api.js";
import {onMounted, ref} from "vue";
import RuntimeColumns from "@/components/RuntimeColumns.vue";
import {Message} from "@arco-design/web-vue";
//import RuntimeDrawer from "@/components/RuntimeDrawer.vue";

const operate_info_list = ref([]);
const modal_visible = ref(false);
const chain_id = ref("");

// 刷新请求记录
function refreshRecord() {
  getAllOperatingRecord().then(res => {
    if (res.status) operate_info_list.value = res.request_list;
    else Message.warning(res.message);
  }).catch(err => {
    console.log(err);
  });
}

// 显示链日志
function showChainLog(uid) {
  modal_visible.value = true;
  chain_id.value = uid;
}

// 组件挂载时获取所有操作记录
onMounted(() => {
  getAllOperatingRecord();
})
</script>

<template>
  <a-layout>
    <a-button-group>
      <a-space>
        <a-button @click="refreshRecord">
          <icon-refresh/>
        </a-button>
      </a-space>
    </a-button-group>
    <RuntimeColumns
        class="runtime_table"
        @row_click="showChainLog"
        :operate_info_list="operate_info_list"/>
    <RuntimeDrawer
        :chain_id="chain_id"
        v-if="modal_visible"
        v-model="modal_visible"/>
  </a-layout>
</template>

<style scoped>
.runtime_table {
  max-width: 90%;
  padding: 2px;
}
</style>
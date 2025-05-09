<script setup>
import {ref} from "vue";
import {getAllChainInfo} from "@/api/chain_api.js";
import NameSpaceTree from "@/components/NameSpaceTree.vue";
import ChainInformation from "@/components/ChainInformation.vue";
import ChainUpload from "@/components/ChainUpload.vue";

const selectedChain = ref("");
const chainTreeData = ref([]);
const targetUrl = ref("");
const modalVisible = ref(false);
const upload_mode = ref(false); // true代表覆盖，false代表新增
// 刷新链数据，获取链信息
function refreshChainData() {
  getAllChainInfo().then((res) => {
    chainTreeData.value = res;
  }).catch((err) => {
    console.log(err);
  });
}
// 显示新建链弹窗
function showNewModal(key) {
  targetUrl.value = key;
  modalVisible.value = true;
  upload_mode.value = false;
}
// 删除链
function handleChainDelete() {
  selectedChain.value = '';
  refreshChainData();
}
// 更新链
function handleChainUpdate() {
  modalVisible.value = true;
  targetUrl.value = selectedChain.value;
  upload_mode.value = true;
  selectedChain.value = '';
}
</script>

<template>
  <a-layout class="name-space-panel">
    <NameSpaceTree
        :origin_data="chainTreeData"
        @key_selected="showNewModal"
        @refresh="refreshChainData"
        v-model="selectedChain"/>
    <ChainInformation
        v-if="selectedChain"
        @chain_del="handleChainDelete"
        @chain_update="handleChainUpdate"
        :task_chain_url="selectedChain"/>
    <ChainUpload
        v-if="modalVisible"
        :selected_url="targetUrl"
        :is_update="upload_mode"
        v-model="modalVisible"/>
  </a-layout>
</template>

<style scoped>
.name-space-panel {
  display: flex;
  flex-direction: row;
  background: var(--color-bg-3);
  margin: 20px;
}
</style>
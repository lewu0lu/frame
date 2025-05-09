<script setup>
import NameSpaceTree from "@/components/NameSpaceTree.vue";
import ScriptInformation from "@/components/ScriptInformation.vue";
import ScriptUpload from "@/components/ScriptUpload.vue";
import {ref} from "vue";
import {getAllScriptInfo} from "@/api/script_api.js";

const selectedScript = ref("");
const scriptTreeData = ref([]);
const targetScript = ref("");
const modal_visible = ref(false);
// 刷新文件树，获取脚本信息
function refreshTreeData() {
  getAllScriptInfo().then((res) => {
    scriptTreeData.value = res;
  }).catch((err) => {
    console.log(err)
  });
}
// 显示新建脚本弹窗
function showNewModal(key) {
  targetScript.value = key;
  modal_visible.value = true;
}
</script>

<template>
  <a-layout class="name-space-panel">
    <NameSpaceTree
        :origin_data="scriptTreeData"
        @key_selected="showNewModal"
        @refresh="refreshTreeData"
        v-model="selectedScript"/>
    <ScriptInformation v-if="selectedScript" :script_url="selectedScript"/>
    <ScriptUpload
        v-if="modal_visible"
        :selected_script="targetScript"
        v-model="modal_visible"/>
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
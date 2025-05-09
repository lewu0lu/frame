<script setup>
import {onMounted, ref, watch} from "vue";
import ScriptDrawer from "@/components/ScriptDrawer.vue";
import {getScriptAllVersion, getScriptCurrentVersion} from "@/api/script_api.js";

const origin_version_info = ref({})
const script_versions_info = ref([]);
const drawer_visible = ref(false);
const script_info = ref([]);
const props = defineProps({
  script_url: String,
});

// 显示脚本抽屉并获取所有版本信息
function showScriptDrawer() {
  drawer_visible.value = true;
  getScriptAllVersion({script_url: props.script_url}).then(res => {
    script_versions_info.value = res["version_info"];
  }).catch(err => {
    console.log(err);
  });
}

// 格式化脚本数据
function formatScriptData(data) {
  // todo 优化显示
  return JSON.stringify(data, null);
}

// 刷新脚本信息
function refreshScriptInfo() {
  if (!props.script_url) return [];
  getScriptCurrentVersion({script_url: props.script_url}).then(res => {
    origin_version_info.value = res["version_info"];
    script_info.value = Object.keys(res["version_info"]).map(key => {
      return {label: key, value: formatScriptData(res["version_info"][key])};
    });
  }).catch(err => {
    console.log(err);
  });
}

// 监听script_url的变化，触发刷新
watch(() => props.script_url, refreshScriptInfo);
onMounted(() => {
  refreshScriptInfo();
})
</script>

<template>
  <div class="description">
    <a-descriptions :data="script_info" title="Script Info" layout="vertical" :column="1"/>
    <a-divider/>
    <a-button @click="showScriptDrawer">选择版本</a-button>
  </div>
  <ScriptDrawer
      :title="'选择脚本版本'"
      :current="origin_version_info"
      :versions_info="script_versions_info"
      v-if="drawer_visible"
      v-model="drawer_visible"/>
</template>

<style scoped>
.description {
  margin: 20px 20px 20px 40px;
  justify-content: center;
  max-width: 80%;
}

</style>
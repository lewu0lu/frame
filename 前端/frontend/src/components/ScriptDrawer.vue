<script setup>
import {ref} from "vue";
import {setScriptVersion, unsetScriptVersion} from "@/api/script_api.js";

const visible = defineModel({default: false});
const props = defineProps({
  current: Object,
  versions_info: Array,
  title: String,
});
const selected_version = ref("")

// 处理确认按钮点击事件
function handleOk() {
  if (selected_version.value === props.current["version"]) {
    const temp = {script_url: props.current["url"]};
    unsetScriptVersion(temp).then((res) => {
      console.log(res);
    }).catch(err => {
      console.log(err);
    });
  } else {
    const temp = {script_url: props.current["url"], version: selected_version.value};
    setScriptVersion(temp).then((res) => {
      console.log(res);
    }).catch(err => {
      console.log(err);
    });
  }
  visible.value = false;
}

// 处理取消按钮点击事件
function handleCancel() {
  visible.value = false;
}

// 选择目标版本
function selectTargetVersion(item) {
  if (selected_version.value === item.version) selected_version.value = "";
  else selected_version.value = item.version;
}

// 获取抽屉按钮文本
function getDrawerText() {
  if (selected_version.value === props.current["version"]) {
    return "采用默认版本设置";
  } else return "设置版本";
}
</script>

<template>
  <a-drawer
      :width="600"
      :visible="visible"
      :closable="false"
      :ok-text="getDrawerText()"
      @ok="handleOk"
      @cancel="handleCancel"
      unmountOnClose>
    <template #title>
      {{ props.title }}
    </template>
    <a-list>
      <a-list-item
          @click.stop="selectTargetVersion(item)"
          v-for="(item, idx) in versions_info">
        <a-list-item-meta
            :title="new Date(item.upload_time * 1000).toLocaleString()"
            :description="item.description">
          <template #avatar>
            <div v-if="selected_version !== current['version']">
              <icon-star-fill v-if="item.version === selected_version"/>
              <div v-if="item.version === current['version']">
                <icon-star-fill v-if="!selected_version"/>
                <icon-star v-else/>
              </div>
            </div>
          </template>
        </a-list-item-meta>
      </a-list-item>
    </a-list>
  </a-drawer>
</template>

<style scoped>

</style>

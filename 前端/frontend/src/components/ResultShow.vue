<script setup>
import {computed, onMounted, ref} from "vue";
import {getOperatingRecord, stopOperatingChain} from "@/api/chain_api.js";
import {desc_format, range} from "@/utils.js";
import {Message} from "@arco-design/web-vue";

const props = defineProps({
  chain_id: String,
});
const originChainLog = ref({});
const originTaskLog = ref([]);
const selected = ref(-1);

// 计算当前任务数量
const current = computed(() => {
  return originTaskLog.value.length + 1;
});

// 刷新任务信息
function refreshTask() {
  const temp = {request_id: props.chain_id};
  getOperatingRecord(temp).then((res) => {
    if (res.status && res.task_info.length) {
      originChainLog.value = res.task_info[0];
      originTaskLog.value = res.task_info.slice(1);
    }
  }).catch(err => {
    console.log(err);
  });
}

// 显示选中任务的详细信息
function showInfo(idx) {
  selected.value = idx;
}

// 获取取消的任务数量
function getCancelNum() {
  if (!originChainLog.value.task_count) return 0;
  else return originChainLog.value.task_count - originTaskLog.value.length;
}

// 获取任务状态
function getTaskStatus(idx) {
  const temp = originTaskLog.value[idx].status;
  if (!temp) return "finish";
  return temp;
}

// 处理取消链操作
function handleCancelChain() {
  const temp = {request_id: props.chain_id};
  stopOperatingChain(temp).then((res) => {
    if (res.status) Message.info(res.message);
  }).catch((err) => {
    console.log(err);
  });
}

// 检查任务链是否正在运行
function isRunning() {
  return originTaskLog.value.status === "pending";
}

let interval;
onMounted(() => {
  refreshTask();
  interval = setInterval(() => {
    if (isRunning()) refreshTask();
  }, 1000);
})
</script>

<template>
  <a-layout>
    <a-descriptions :data="desc_format(originChainLog, ['_id','log_msg','request_id','task_id'])"/>
    <a-button-group>
      <a-button
          @click="handleCancelChain"
          v-if="isRunning()">
        终止执行
      </a-button>
    </a-button-group>
    <a-divider/>
    <div
        class="task_detail"
        @click="()=>{selected=-1}">
      <a-steps
          :current="current"
          direction="vertical"
          changeable>
        <a-step
            v-for="(step, idx) in originTaskLog"
            :key="step.task_url"
            :status="getTaskStatus(idx)"
            @click.stop="showInfo(idx)">
          {{ step.task_url }}
        </a-step>
        <a-step
            :status="'wait'"
            v-for="i of range(getCancelNum())">
          未执行
        </a-step>
      </a-steps>
      <div
          @click.stop=""
          v-if="selected >= 0">
        <a-descriptions
            :column="2"
            :data="desc_format(originTaskLog[selected],['_id','request_id','task_id','log_msg'])"/>
        <a-card hoverable>
          {{ originTaskLog[selected].log_msg }}
        </a-card>
      </div>
    </div>
  </a-layout>
</template>

<style scoped>
.task_detail {
  display: flex;
  flex-direction: row;
}
</style>
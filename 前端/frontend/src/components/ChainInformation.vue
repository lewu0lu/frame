<script setup>
import {computed, onMounted, ref, watch} from "vue";
import {deleteTaskChain, getChainNodesInfo} from "@/api/chain_api.js";
import {Message} from "@arco-design/web-vue";

// 定义响应式变量
const current = ref(0);
const selectedTaskInfo = ref([]);
const task_info_list = ref([]);
const desc_title = ref("");

// 定义组件props
const props = defineProps({
  task_chain_url: String,
});

// 计算属性：根据选中的任务信息或任务链信息返回当前显示的信息
const currentInfo = computed(() => {
  if (selectedTaskInfo.value.length) return selectedTaskInfo.value;
  else {
    desc_title.value = "任务链信息";
    return [{label: "任务数量", value: task_info_list.value.length}];
  }
});

// 定义组件事件
const emits = defineEmits(["chain_del", "chain_update"])

// 格式化脚本数据
function formatScriptData(data) {
// todo 优化显示
  return JSON.stringify(data, null);
}

// 显示选中任务的详细信息
function showInfo(idx) {
  selectedTaskInfo.value = []
  const current = task_info_list.value[idx];
  desc_title.value = current.url + "-任务信息";
  for (let key in current) {
    if (key === "script_content") continue;
    selectedTaskInfo.value.push({label: key, value: formatScriptData(current[key])});
  }
}

// 重置选中的任务信息
function resetInfo() {
  selectedTaskInfo.value = [];
}

// 刷新任务链信息
function refreshChainNodesInfo() {
  const temp = {task_chain_url: props.task_chain_url};
  getChainNodesInfo(temp).then(res => {
    if (res.status) {
      task_info_list.value = res["task_info"];
    }
  }).catch(err => {
    console.log(err);
  });
}

// 处理删除任务链的操作
function handleChainDel() {
  const temp = {task_chain_url: props.task_chain_url};
  deleteTaskChain(temp).then(res => {
    if (res.status) {
      Message.success(res.message);
      emits("chain_del");
    } else Message.error(res.message);
  }).catch(err => {
    console.log(err);
  });
}

// 监听task_chain_url的变化，并刷新任务链节点信息
watch(() => props.task_chain_url, refreshChainNodesInfo);

// 组件挂载时刷新任务链节点信息
onMounted(() => {
  refreshChainNodesInfo();
})
</script>

<template>
  <div class="task_chain" @click="resetInfo">
    <a-button-group>
      <a-space>
        <a-button @click="emits('chain_update')">更新</a-button>
        <a-button @click="handleChainDel">删除</a-button>
      </a-space>
    </a-button-group>
    <div class="chain_info">
      <a-steps changeable :current="current">
        <a-step v-for="(task, idx) in task_info_list"
                :key='task.url'
                class="step"
                @click.stop="showInfo(idx)"
        >{{ task.url }}
        </a-step>
      </a-steps>
      <a-divider/>
      <div class="description">
        <a-descriptions :data="currentInfo" :title="desc_title" :column="1"/>
      </div>
    </div>
  </div>
</template>

<style>
.task_chain {
  padding: 20px 20px 20px 40px;
  justify-content: center;
  width: 80%;
  max-width: 80%;
}

.chain_info {
  border: 1px solid #3370ff;
}

.description {
  margin: 20px;
  justify-content: center;
  min-width: 100%;
}
</style>

<script setup>
import {onMounted, reactive, ref} from "vue";
import {Message} from "@arco-design/web-vue";
import {resetTaskChain, uploadTaskChain} from "@/api/chain_api.js";
import {getAllScriptInfo} from "@/api/script_api.js";

const visible = defineModel({default: false});
const props = defineProps({
  selected_url: String,
  is_update: Boolean,
});

// 定义响应式表单数据
const form = reactive({
  current_chain_url: "",
  selected_task_list: [],
});
const options = [
  {
    value: "script",
    label: "已注册任务",
  },
];

// 存储原始任务信息
const originTaskInfo = ref([]);

// 处理取消操作
function handleCancel() {
  visible.value = false;
  originTaskInfo.value = [];
  form.selected_task_list = [];
  form.current_chain_url = "";
}

// 处理确认操作前的验证和提交
function handleBeforeOk() {
  if (!form.selected_task_list.length) {
    Message.info("请填写需要组链的任务");
    return false;
  }

  const temp = {task_chain_url: form.current_chain_url, task_list: form.selected_task_list};
  let api_func = uploadTaskChain
  if (props.is_update) api_func = resetTaskChain;
  api_func(temp).then((res) => {
    if (!res.status) Message.warning(res.message);
    else Message.success(res.message);
  }).catch((err) => {
    console.log(err);
  });
  return true;
}

// 处理任务选择变化
function handleChange(path) {
  form.selected_task_list = path;
}

// 加载任务信息
function loadTaskInfo(option, done) {
  if (option.value === "script") {
    getAllScriptInfo().then((res) => {
      originTaskInfo.value = res;
      done(getFormatTree(res));
    }).catch((err) => {
      console.log(err)
    });
  }
}

// 格式化任务树结构
function getFormatTree(data) {
  if (!data) return [];
  return data.reduce(
      (acc, item) => {
        const item_list = item.split("/")
        let cur = acc;
        let key = ""
        item_list.forEach((name, index) => {
          if (key) key += "/" + name;
          else key = name

          if (index === item_list.length - 1) {
            cur.push({label: name, value: key, isLeaf: true});
          } else {
            let pos = cur.findIndex(x => (x.label === name));
            if (pos < 0) {
              cur.push({label: name, value: key, children: []});
              pos = cur.length - 1;
            }
            cur = cur[pos].children;
          }
        });
        return acc;
      }, []);
}

onMounted(() => {
  form.current_chain_url = props.selected_url;

})
</script>

<template>
  <a-modal
      v-model:visible="visible"
      title="设置任务链"
      @cancel="handleCancel"
      @before-ok="handleBeforeOk">
    <a-form :model="form">
      <a-form-item label="任务链url" tooltip="请输入url">
        <a-input v-model="form.current_chain_url"/>
      </a-form-item>
      <a-form-item label="任务选择" tooltip="请选择需要成链的任务">
        <a-cascader
            @change="handleChange"
            :load-more="loadTaskInfo"
            :options="options"
            allow-clear
            multiple/>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<style scoped>

</style>
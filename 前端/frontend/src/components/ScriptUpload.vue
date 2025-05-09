<!--  脚本上传表单-->
<script setup>
import {onMounted, reactive} from 'vue';
import {all} from "@/utils.js";
import {md5} from "js-md5";
import {Message} from "@arco-design/web-vue";
import {uploadScript} from "@/api/script_api.js";

const visible = defineModel({default: false});
const props = defineProps({
  selected_script: String,
});

const form = reactive({
  script_url: '',
  script_md5: '',
  script_description: '',
  is_alone: false,
});

let current_file = null;

function handleCancel() {
  visible.value = false;
  form.script_url = ''
  form.script_md5 = ''
  form.script_description = ''
}

function handleBeforeOk() {
  if (!all(Object.values(form), x => x !== "")) {
    Message.info("请填写完整配置")
    return false;
  }
  if (!current_file) {
    Message.info("请上传文件")
    return false;
  }
  // 上传脚本
  uploadScript(form, current_file).then((res) => {
    Message.info(res.message);
  }).catch(err => {
    Message.info(err.message);
  });
  return true;
}

function handleResourceSubmit(option) {
  // 这个方法是为了解决arco组件不能隐藏上传按钮的问题
  const {onProgress, onError, onSuccess, fileItem, name} = option;
  const fileReader = new FileReader()
  fileReader.onload = e => {
    form.script_md5 = md5(e.target.result);
  }
  fileReader.onerror = e => {
    Message.info("文件md5值计算错误")
  }
  current_file = fileItem.file;
  fileReader.readAsArrayBuffer(current_file);
  onSuccess(true);
  return true;
}

onMounted(() => {
  form.script_url = props.selected_script;
})
</script>

<template>
  <a-modal
      v-model:visible="visible"
      title="上传脚本"
      @cancel="handleCancel"
      @before-ok="handleBeforeOk">
    <a-form :model="form">
      <a-form-item field="脚本URL" tooltip="请输入脚本的URL" label="脚本URL">
        <a-input
            v-model="form.script_url"
            placeholder="请输入脚本的URL"
            style="width: 200px;"
        />
        <a-checkbox v-model="form.is_alone">是否暴露</a-checkbox>
      </a-form-item>
      <a-form-item>
        <a-textarea
            v-model="form.script_description"
            placeholder="请输入脚本的描述"
        />
      </a-form-item>
      <a-form-item>
        <a-upload
            draggable
            action="/"
            :custom-request="handleResourceSubmit"
            :limit="1"/>
      </a-form-item>
    </a-form>
  </a-modal>
</template>


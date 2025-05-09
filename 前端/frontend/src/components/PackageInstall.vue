<script setup>
import {reactive,ref} from "vue";
import {installPackage} from "@/api/package_api.js";
import {Message} from "@arco-design/web-vue";

const visible = defineModel({default: false})


const form = reactive({
  package_name: '',
  package_version: '',
});

// 处理取消操作的函数
function handleCancel() {
visible.value = false;
form.package_name = '';
form.package_version = '';
}

// 处理确认操作前的函数，安装包
function handleBeforeOk(){
  if (!form.package_name) return false;

  installPackage(form).then((res) => {
    if (res.status) Message.success(res.message);
    else Message.info(res.output_message);
  }).catch(err => {
    console.log(err);
    Message.error(err);
  });
  return true;
}

</script>
<template>
  <a-modal
    v-model:visible="visible"
    title="安装包"
    @cancel="handleCancel"
    @before-ok="handleBeforeOk">
    <a-form :model="form">
      <a-form-item field="安装包名字"  label="安装包名字">
        <a-input
          v-model="form.package_name"
          placeholder="请输入要安装的包"
        />
        </a-form-item>
      <a-form-item field="安装包版本"  label="安装包版本" >
        <a-input
          v-model="form.package_version"
          placeholder="请输入要安装的包版本（选填）"
        />
        </a-form-item>
    </a-form>
  </a-modal>
</template>
